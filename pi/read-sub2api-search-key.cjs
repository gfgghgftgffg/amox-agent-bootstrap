#!/usr/bin/env node
'use strict';

// Deploy beside sub2api.json. Only the resolved key is written to stdout;
// pi-web-access executes this command locally when search needs credentials.
const fs = require('node:fs');
const path = require('node:path');

try {
  const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'sub2api.json'), 'utf8'));
  let token = config.sub2api?.token;
  if (typeof token !== 'string') throw new Error('missing token');
  const reference = /^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$/.exec(token);
  if (reference) token = process.env[reference[1]];
  // Do not execute another credential command. Configure openaiApiKey directly
  // for that case instead of changing the existing provider's credential source.
  if (typeof token !== 'string' || !token.trim() || token === 'YOUR_API_KEY' ||
      token.startsWith('!') || token.startsWith('$') || /[\s\x00-\x1f\x7f]/.test(token)) {
    throw new Error('unsupported or unresolved token');
  }
  process.stdout.write(token);
} catch {
  console.error('Search credential unavailable: check adjacent sub2api.json, sub2api.token and any referenced environment variable. Command-backed tokens need a separately configured openaiApiKey.');
  process.exitCode = 1;
}
