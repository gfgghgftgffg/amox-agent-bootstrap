'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { test } = require('node:test');
const root = path.resolve(__dirname, '..');
const helper = path.join(root, 'pi/read-sub2api-search-key.cjs');

function run(t, config, env = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'bootstrap-search-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const script = path.join(dir, 'read-sub2api-search-key.cjs');
  fs.copyFileSync(helper, script);
  if (config !== undefined) fs.writeFileSync(path.join(dir, 'sub2api.json'), config);
  return spawnSync(process.execPath, [script], {
    // A different cwd checks that lookup is relative to the deployed script.
    cwd: os.tmpdir(), encoding: 'utf8', env: { ...process.env, ...env },
  });
}

test('default search route is independent, Responses-backed, and credential-free', () => {
  const c = JSON.parse(fs.readFileSync(path.join(root, 'pi/web-search.json'), 'utf8'));
  assert.deepEqual(c.searchRouting.providers, ['openai', 'exa']);
  assert.deepEqual(c.searchRouting.fallbackOn, ['unsupported', 'transient', 'quota', 'network', 'invalid-response']);
  assert.equal(c.searchRouting.useCurrentModel, undefined);
  assert.deepEqual(c.openaiSearchProviders, []);
  assert.equal(c.openaiUseAlphaSearch, false);
  assert.equal(c.openaiSearchModel, 'gpt-6.1-sol');
  assert.equal(c.workflow, 'none');
  assert.equal(c.provider, undefined);
  assert.equal(c.searchProvider, undefined);
  assert.equal(c.openaiApiKey, '!node "{{SUB2API_SEARCH_KEY_SCRIPT}}"');
  const relay = JSON.parse(fs.readFileSync(path.join(root, 'pi/sub2api.json'), 'utf8')).sub2api;
  assert.equal(relay.token, 'YOUR_API_KEY');
  assert.equal(c.openaiResponsesUrl, relay.baseURL.replace(/\/$/, '').replace(/\/v1$/, '') + '/v1/responses');
  assert.ok(!relay.serverTools?.responses?.some(tool => tool.type === 'web_search'));
});

test('literal token is read beside the helper, not from cwd', t => {
  const result = run(t, JSON.stringify({ sub2api: { token: 'fixture-not-a-real-key' } }));
  assert.equal(result.status, 0);
  assert.equal(result.stdout, 'fixture-not-a-real-key');
  assert.equal(result.stderr, '');
});

test('environment reference resolves without preferring OPENAI_API_KEY', t => {
  const result = run(t, JSON.stringify({ sub2api: { token: '${BOOTSTRAP_FIXTURE_KEY}' } }), {
    BOOTSTRAP_FIXTURE_KEY: 'fixture-env-key', OPENAI_API_KEY: 'unrelated-fixture-key',
  });
  assert.equal(result.status, 0);
  assert.equal(result.stdout, 'fixture-env-key');
  assert.equal(result.stderr, '');
});

for (const [name, config, env] of [
  ['missing file', undefined],
  ['malformed JSON', '{"secret":"fixture-must-not-leak",'],
  ['missing provider', '{}'],
  ['placeholder', JSON.stringify({ sub2api: { token: 'YOUR_API_KEY' } })],
  ['empty token', JSON.stringify({ sub2api: { token: '' } })],
  ['unresolved environment', JSON.stringify({ sub2api: { token: '${BOOTSTRAP_MISSING_KEY}' } }), { BOOTSTRAP_MISSING_KEY: '' }],
  ['command-backed token', JSON.stringify({ sub2api: { token: '!echo fixture-must-not-execute' } })],
  ['control character', JSON.stringify({ sub2api: { token: 'fixture\nkey' } })],
]) {
  test(`fails closed without leaking credentials: ${name}`, t => {
    const result = run(t, config, env);
    assert.equal(result.status, 1);
    assert.equal(result.stdout, '');
    assert.match(result.stderr, /Search credential unavailable/);
    assert.doesNotMatch(result.stderr, /fixture-must-not/);
  });
}

test('every Pi JSON template parses', () => {
  for (const file of fs.readdirSync(path.join(root, 'pi')).filter(f => f.endsWith('.json'))) {
    assert.doesNotThrow(() => JSON.parse(fs.readFileSync(path.join(root, 'pi', file), 'utf8')), file);
  }
});
