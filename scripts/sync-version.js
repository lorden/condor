#!/usr/bin/env node
// Stamp the package.json version into the extension manifests so the version
// shown in chrome://extensions always matches. package.json is the single
// source of truth; run via `npm run build` (prebuild) or `npm version`.
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const { version } = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));

for (const name of ['manifest.json', 'manifest.example.json']) {
  const file = path.join(root, name);
  if (!fs.existsSync(file)) continue; // manifest.json is gitignored; may be absent on fresh clones
  const manifest = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (manifest.version === version) continue;
  manifest.version = version;
  fs.writeFileSync(file, `${JSON.stringify(manifest, null, 2)}\n`);
  console.log(`${name}: version → ${version}`);
}
