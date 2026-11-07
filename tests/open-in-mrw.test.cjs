'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../templates/OpenInMRW.md'), 'utf8');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const execute = new AsyncFunction('tp', 'require', 'tR', source.slice(3, source.lastIndexOf('-%>')) + '\nreturn tR;');
const defaults = { workspace: 'vscode-remote://wsl+Debian/home/reader/Study%20%CE%B1.code-workspace', notes: '/mnt/c/Users/reader/Notes α' };
async function fixture(options = {}) {
  const opened = [], notices = [], reads = [], commands = new Map([['unrelated',{}]]);
  let current = options.file === null ? null : { path: options.file || 'Numbers/ID α😀.md' };
  const plugin = { addCommand: c => commands.set(c.id,c), removeCommand: id => commands.delete(id) };
  const application = {
    workspace: { getActiveFile: () => current },
    plugins: { plugins: { 'templater-obsidian':plugin } },
    vault: { configDir:'.obsidian', adapter: { exists:async () => options.exists !== false, read:async file => {reads.push(file);return JSON.stringify(options.config || defaults);} } }
  };
  const tp = {
    config:{run_mode:options.mode ?? 5}, app:application,
    file:{selection:() => {throw Error('Navigation must not use selection or insertion');}},
    obsidian:{Platform:{isDesktopApp:options.desktop !== false},Notice:class{constructor(message){notices.push(message);}}}
  };
  const load = name => name === 'electron' ? {shell:{openExternal:async uri => opened.push(uri)}} : require(name);
  const output = await execute(tp,load,'');
  return {opened,notices,reads,commands,output,register:() => execute(tp,load,''),current:file => {current={path:file};},run:() => commands.get('open-in-mrw').callback()};
}
test('startup registers Open in MRW without insertion, disk reads or external dispatch', async () => {
  const h=await fixture();assert.equal(h.output,'');assert.deepEqual(h.opened,[]);assert.deepEqual(h.reads,[]);
  assert.equal(h.commands.get('open-in-mrw').name,'Open in MRW');assert.ok(h.commands.has('unrelated'));
  await h.register();assert.equal(h.commands.size,2);
});
test('command uses the current note at invocation, including reading view, and preserves Unicode', async () => {
  const h=await fixture();h.current('Numbers/Another α😀.md');await h.run();assert.deepEqual(h.notices,[]);
  const uri=new URL(h.opened[0]);assert.equal(uri.host,'flengyel.mrw');assert.equal(uri.pathname,'/note');
  assert.deepEqual(JSON.parse(Buffer.from(uri.searchParams.get('target'),'base64url')),{...defaults,file:'Numbers/Another α😀.md'});
  assert.deepEqual(h.reads,['.obsidian/mrw.json']);
});
test('insertion and note-creation routes are refused before touching a note', async () => {
  for(const mode of [0,1,2,3,4]) await assert.rejects(fixture({mode}),/startup template/);
});
test('missing settings, unsupported target and traversal produce no external action', async () => {
  for(const options of [{exists:false},{file:null},{file:'paper.pdf'},{desktop:false},{config:{...defaults,scheme:'command'}},
    {config:{...defaults,workspace:'command:run'}},{config:{...defaults,notes:'C:\\Notes'}},{file:'../outside.md'}]) {
    const h=await fixture(options);await h.run();assert.deepEqual(h.opened,[]);assert.equal(h.notices.length,1);
  }
});
