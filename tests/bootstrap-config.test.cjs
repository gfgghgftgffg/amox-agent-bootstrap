'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const skillUrl = 'https://github.com/github/awesome-copilot/tree/main/skills/create-readme';

test('codemode is additive and does not hide direct tools', () => {
  const settings = JSON.parse(read('pi/settings.json'));
  assert.deepEqual(settings.defaultTools, ['+codemode']);
  assert.notEqual(settings.codemode?.mode, 'only');
  assert.deepEqual(settings.packages, [
    'npm:@indexyz/pi-provider-sub2api',
    'npm:@narumitw/pi-btw',
    'npm:@gfgghgftgffg/pi-web-access-lean',
    'npm:@gfgghgftgffg/rpiv-todo-lean',
    'npm:@gfgghgftgffg/pi-subagents-lean',
    'npm:@monotykamary/pi-retry',
    'npm:pi-sync-suite',
    'npm:pi-tidy',
    'npm:pi-starline',
  ]);
  assert.equal(settings.theme, 'catppuccin-mocha');
  assert.equal(settings.hideThinkingBlock, true);
  assert.equal(settings.tidy.frameMessages, true);
  assert.equal(settings.tidy.frameUserMessages, false);
  assert.equal(fs.existsSync(path.join(root, 'pi/open-tui.json')), false);
  assert.equal(fs.existsSync(path.join(root, 'pi/pi-pretty.json')), false);
});

test('both setup guides install create-readme without making it explicit-only', () => {
  for (const file of ['setup.md', 'setup_for_pi.md']) {
    const guide = read(file);
    assert.ok(guide.includes(skillUrl), file);
    assert.match(guide, /leave `disable-model-invocation` absent or `false`/, file);
    assert.match(guide, /not the whole collection/, file);
    assert.match(guide, /humanizer.*shuorenhua/, file);
  }
  const piGuide = read('setup_for_pi.md');
  const skills = piGuide.split('## 3. Skills')[1].split('## 4. Configuration')[0];
  assert.equal((skills.match(/^\| `/gm) || []).length, 8);
  assert.match(piGuide, /Verify eight complete Skills/);
  assert.match(read('setup.md'), /All seven project \/ Skill entries/);
});

test('instruction templates end Requirement Alignment with the document rule', () => {
  const rule = 'Unless user request, document should not include historical background, troubleshooting processes, or redundant explanations.';
  for (const file of ['templates/AGENTS.md', 'pi/AGENTS.md']) {
    const text = read(file);
    const section = text.split('# Requirement Alignment\n')[1].split('\n# Workflow')[0].trim();
    assert.equal(section.split('\n').at(-1), '- ' + rule, file);
    assert.equal(text.split(rule).length - 1, 1, file);
  }
});

test('deployment guides retain the requested configuration', () => {
  const codex = read('setup.md');
  for (const value of [
    'memories = true', 'prevent_idle_sleep = true', 'multi_agent = true',
    'multi_agent_v2 = false', 'max_concurrent_threads_per_session = 30',
    'default_subagent_model = "gpt-6-luna"', 'default_subagent_reasoning_effort = "medium"',
    'daemon_auto_start = false', '"multi_agent_version": "v1"',
  ]) assert.ok(codex.includes(value), value);
  const pi = read('setup_for_pi.md');
  for (const value of [
    'toolSuccessBg: "base"', 'frameUserMessages: false', 'editorPaddingY: 0',
    'editorMetadataFormat: ""', 'syncLocalPackagePaths: false',
    'node cli.mjs install --host pi --config <absolute-routing-config> --apply',
  ]) assert.ok(pi.includes(value), value);
});

test('all Markdown links resolve to existing local documents', () => {
  function walk(dir) {
    return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
      if (entry.name === '.git') return [];
      const file = path.join(dir, entry.name);
      return entry.isDirectory() ? walk(file) : file.endsWith('.md') ? [file] : [];
    });
  }
  for (const file of walk(root)) {
    for (const [, target] of fs.readFileSync(file, 'utf8').matchAll(/\]\(([^)]+)\)/g)) {
      if (/^(?:https?:|#)/.test(target)) continue;
      assert.ok(fs.existsSync(path.resolve(path.dirname(file), target.split('#')[0])), `${file}: ${target}`);
    }
  }
});

test('starline uses the current compact layout and automatic thinking colors', () => {
  const c = JSON.parse(read('pi/starline.json'));
  assert.deepEqual(c.pill.segments, [
    'model', 'thinking', 'subagents', 'cwd', 'sessionName', 'runtime',
    'git', 'context', 'cost', 'sessionDuration', 'time', 'extensionStatus',
  ]);
  assert.equal(c.pill.segments.includes('queue'), false);
  assert.equal(c.editorMetadataFormat, '');
  assert.equal(c.editorPaddingY, 0);
  assert.deepEqual(c.pathDisplay, { mode: 'full', depth: 0 });
  assert.equal(c.colors.thinking, undefined);
  assert.equal(c.icons.mode, 'nerd');
  assert.equal(c.palette.base, '#1e1e2e');
  assert.equal(c.colors.model, 'bg:$pink fg:$base');
  assert.equal(c.colors.cwd, 'bg:$peach fg:$base');
  assert.equal(c.colors.gitBranch, 'bg:$yellow fg:$base');
  assert.equal(c.colors.contextNormal, 'bg:$blue fg:$base');
  for (const value of Object.values(c.colors)) {
    for (const [, name] of value.matchAll(/\$([A-Za-z_][A-Za-z0-9_]*)/g)) {
      assert.match(c.palette[name], /^#[0-9a-f]{6}$/i, name);
    }
  }
});

test('Mocha resolves variables and provides a concrete base for tidy diff tints', () => {
  const theme = JSON.parse(read('pi/themes/catppuccin-mocha.json'));
  assert.equal(theme.name, JSON.parse(read('pi/settings.json')).theme);
  assert.equal(theme.appearance, 'dark');
  assert.equal(theme.vars.base, '#1e1e2e');
  assert.equal(theme.vars.text, '#cdd6f4');
  const resolve = (value, seen = new Set()) => {
    if (value === '' || /^#[0-9a-f]{6}$/i.test(value)) return value;
    assert.ok(Object.hasOwn(theme.vars, value), `Unknown theme variable: ${value}`);
    assert.ok(!seen.has(value), `Cyclic theme variable: ${value}`);
    return resolve(theme.vars[value], new Set([...seen, value]));
  };
  for (const value of [...Object.values(theme.colors), ...Object.values(theme.export)]) resolve(value);
  assert.equal(resolve(theme.colors.toolSuccessBg), '#1e1e2e');
  for (const key of ['toolPendingBg', 'toolErrorBg', 'userMessageBg', 'customMessageBg']) {
    assert.equal(theme.colors[key], '', key);
  }
  assert.equal(resolve(theme.colors.thinkingMedium), '#b4befe');
  assert.equal(resolve(theme.colors.thinkingHigh), '#cba6f7');
  assert.notEqual(resolve(theme.colors.thinkingMedium), resolve(theme.colors.thinkingHigh));
});

test('appearance instructions give manual cross-platform targets, not OS automation', () => {
  for (const file of ['pi/appearance.md', 'pi/appearance.zh-CN.md']) {
    const text = read(file);
    for (const value of [
      'Catppuccin Mocha', 'Maple Mono NF CN', 'MapleMono-NF-CN-unhinted.zip',
      'https://github.com/subframe7536/maple-font/releases/latest',
      'https://catppuccin.com/ports/', '95%', '0.95', 'Windows', 'macOS', 'Linux',
    ]) assert.ok(text.includes(value), `${file}: ${value}`);
  }
  const guide = read('setup_for_pi.md');
  assert.match(guide, /must not install fonts, edit terminal profiles, write Windows registry entries/);
  assert.match(guide, /Keep `colors.thinking` absent/);
  assert.match(guide, /placing starline last/);
  assert.doesNotMatch(guide, /open-tui last|hideThinkingBlock: false|pi-pretty\.json/);
});
