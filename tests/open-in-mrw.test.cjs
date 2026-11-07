'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../templates/OpenInMRW.md'), 'utf8');
assert.match(source, /^<%\*[\s\S]*-\%>\n$/);
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const execute = new AsyncFunction('tp', 'require', 'tR', source.slice(3, source.lastIndexOf('-%>')) + '\nreturn tR;');
const defaults = { workspace: 'vscode-remote://wsl+Debian/home/reader/Study%20%CE%B1.code-workspace', notes: '/mnt/c/Users/reader/Notes α' };
async function run(options = {}) {
  const opened = [], notices = [], reads = [], callbacks = [];
  const tp = {
    config: { target_file: options.file === null ? null : { path: options.file || 'Numbers/ID α😀.md' }, template_file: { path: 'Templates/OpenInMRW.md' } },
    file: { selection: () => options.selection || '' },
    hooks: { on_all_templates_executed: callback => callbacks.push(callback) },
    obsidian: { Platform: { isDesktopApp: options.desktop !== false }, getFrontMatterInfo: text => ({ contentStart: text.startsWith('---\n') ? text.length : 0 }), Notice: class { constructor(message) { notices.push(message); } } },
    app: { workspace: { activeEditor: { editor: { getDoc: () => ({ listSelections: () => Array(options.cursors || 1).fill({}) }) } } }, vault: { configDir: '.obsidian', adapter: { exists: async () => options.exists !== false, read: async file => { reads.push(file); return JSON.stringify(options.config || defaults); } } } },
  };
  const load = name => name === 'electron' ? { shell: { openExternal: async uri => opened.push(uri) } } : require(name);
  const text = await execute(tp, load, '');
  assert.equal(opened.length, 0, 'navigation waits for Templater to finish inserting');
  for(const callback of callbacks) await callback();
  return { text, opened, notices, reads };
}
test('current filename and Unicode go directly to MRW, with no note text output', async () => {
  const h = await run(); assert.equal(h.text, ''); assert.deepEqual(h.notices, []);
  const uri = new URL(h.opened[0]); assert.equal(uri.protocol, 'vscode:'); assert.equal(uri.host, 'flengyel.mrw'); assert.equal(uri.pathname, '/note');
  assert.deepEqual(JSON.parse(Buffer.from(uri.searchParams.get('target'), 'base64url')), { ...defaults, file: 'Numbers/ID α😀.md' });
  assert.deepEqual(h.reads, ['.obsidian/mrw.json']);
});
test('a selected argument is returned unchanged; the URI contains no selected prose', async () => {
  const selection = 'An unfinished argument α😀\r\nSecond line.';
  const h = await run({ selection }); assert.equal(h.text, selection); assert.equal(h.opened.length, 1); assert.ok(!h.opened[0].includes('argument'));
});
test('YAML selection is refused before Templater can reinterpret it as metadata', async () => {
  await assert.rejects(run({ selection: '---\nid: ID\n---\n' }), /clear the YAML selection/);
});
test('multiple cursors are refused before replacement', async () => {
  await assert.rejects(run({ cursors:2 }), /single cursor/);
});
test('missing settings, wrong target, traversal and unsupported app schemes produce no external action', async () => {
  for(const options of [{ exists:false }, { file:null }, { file:'paper.pdf' }, { desktop:false }, { config:{ ...defaults, scheme:'command' } },
    { config:{ ...defaults, workspace:'command:run' } }, { config:{ ...defaults, notes:'C:\\Notes' } }, { file:'../outside.md' }]) {
    const h = await run(options); assert.deepEqual(h.opened, []); assert.equal(h.notices.length, 1); assert.equal(h.text, '');
  }
});
