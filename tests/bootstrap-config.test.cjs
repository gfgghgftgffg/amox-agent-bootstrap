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
  assert.equal(settings.packages.length, 9);
  assert.equal(settings.packages.at(-1), 'npm:pi-open-tui');
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

test('bilingual READMEs link to existing local documents', () => {
  for (const file of ['README.md', 'README.zh-CN.md']) {
    const text = read(file);
    assert.ok(text.includes(skillUrl), file);
    assert.ok(text.includes('defaultTools: ["+codemode"]'), file);
    assert.ok(text.includes('node --test tests/*.test.cjs'), file);
    for (const [, target] of text.matchAll(/\]\(([^)]+)\)/g)) {
      if (/^(?:https?:|#)/.test(target)) continue;
      assert.ok(fs.existsSync(path.resolve(root, target.split('#')[0])), `${file}: ${target}`);
    }
  }
});
