'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');

test('both hosts install anti-defensive-writing as explicit-only without duplicate Skill trees', () => {
  for (const name of ['setup.md', 'setup_for_pi.md']) {
    const text = read(name);
    assert.ok(text.includes('https://github.com/Kiterlin/anti-defensive-writing'), name);
    assert.match(text, /Set `disable-model-invocation: true` in `anti-defensive-writing`/);
    assert.match(text, /only the root `SKILL.md` and license/);
    assert.match(text, /Leave `disable-model-invocation` absent or `false` in `design-taste-frontend`, `humanizer` and `shuorenhua`/i);
    assert.match(text, /Do not install `humanizer-zh` as an additional default/);
  }
});

test('global templates include the shared development and writing rules exactly once', () => {
  const sections = text => text.slice(text.indexOf('# Development\n'), text.indexOf('# Workflow\n'));
  const pi = read('pi/AGENTS.md'), codex = read('templates/AGENTS.md');
  assert.equal(sections(pi), sections(codex));
  assert.match(sections(pi), /Do not add unrelated improvements, speculative features, or future-proof abstractions/);
  assert.match(sections(pi), /Add defensive code ONLY for concrete failure modes, trust boundaries, or existing guarantees/);
  assert.match(sections(pi), /State claims and scope directly/);
  assert.match(sections(pi), /do not invent evidence or strengthen certainty/);
  for (const text of [pi, codex]) {
    assert.equal(text.split('# Development\n').length - 1, 1);
    assert.equal(text.split('# Answering and Writing\n').length - 1, 1);
    assert.ok(text.includes('{{CONDA_PATH}}'));
    assert.ok(text.includes('{{PYTHON_PATH}}'));
  }
});

test('Pi setup uses shared Router rules and scoped codemode without re-adding global routing policy', () => {
  assert.doesNotMatch(read('pi/AGENTS.md'), /pi-task-router|tr_\*|Task Router for Pi/);
  const guide = read('setup_for_pi.md');
  for (const value of [
    '<router-checkout>/AGENTS.md', 'preserve independently edited shared rules',
    'not a continuing mirror of global instructions', 'moving the checkout requires reinstalling Router',
    'skills: true', 'allowed_subagents: none', 'prompt_mode: replace', 'inherit_context: false',
    'ext:builtin:codemode/codemode', 'ext:pi-web-access-lean/web_access',
    'Keep mutation limits, denied delegation tools and permission hooks unchanged',
    'Pi Router installation does not modify global `AGENTS.md`',
    'Do not add a Router block',
  ]) assert.ok(guide.includes(value), value);
  assert.doesNotMatch(guide, /exactly one Router block|and one managed AGENTS block/);
  assert.match(read('setup.md'), /All Router parents and roles read the live `<router-checkout>\/AGENTS.md`/);
  assert.match(read('setup.md'), /If the shared file is already customized or used by Pi, preserve it/);
});
