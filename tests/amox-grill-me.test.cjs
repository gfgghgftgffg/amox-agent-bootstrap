'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');

test('both hosts install the bundled explicit-only amox-grill-me instead of upstream', () => {
  const skill = read('skills/amox-grill-me/SKILL.md');
  assert.match(skill, /^name: amox-grill-me$/m);
  assert.match(skill, /^disable-model-invocation: true$/m);
  assert.ok(skill.includes('For each question, provide your recommended answer.'));
  assert.ok(skill.includes('delegate to a sub-agent when the investigation warrants it.'));
  assert.ok(skill.includes('The decisions are mine: put each to me and wait for my answer.'));
  assert.ok(skill.includes('Do not act on the plan until I confirm we have reached a shared understanding.'));
  assert.doesNotMatch(skill, /frontier|Ask one question at a time|Ask the questions one at a time/);
  assert.match(read('skills/amox-grill-me/LICENSE'), /Copyright \(c\) 2026 Matt Pocock/);
  for (const file of ['setup.md', 'setup_for_pi.md']) {
    const guide = read(file);
    assert.ok(guide.includes('[skills/amox-grill-me/](skills/amox-grill-me/)'));
    assert.match(guide, /Set `disable-model-invocation: true`[^\n]*`amox-grill-me`/);
    assert.ok(guide.includes('back up and remove those replaced Skill copies from active discovery paths'));
    assert.doesNotMatch(guide, /https:\/\/github\.com\/mattpocock\/skills/);
  }
  for (const file of ['README.md', 'README.zh-CN.md']) {
    assert.ok(read(file).includes('`amox-grill-me`'));
    assert.doesNotMatch(read(file), /`grilling`/);
  }
});
