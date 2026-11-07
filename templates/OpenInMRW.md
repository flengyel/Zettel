<%*
// Startup registration only. The action reads the current note when invoked.
// Templater 2.26 uses RunMode 5 for startup templates; refuse insertion routes.
if (tp.config.run_mode !== 5) {
  throw new Error("Register OpenInMRW as a startup template, then run Templater: Open in MRW.");
}
const application = tp.app;
const { Platform, Notice } = tp.obsidian;
const plugin = application.plugins.plugins["templater-obsidian"];
plugin.removeCommand("open-in-mrw");
plugin.addCommand({
  id: "open-in-mrw",
  name: "Open in MRW",
  icon: "external-link",
  callback: async () => {
    try {
      if (!Platform.isDesktopApp) throw new Error("This command requires desktop Obsidian.");
      const file = application.workspace.getActiveFile();
      if (!file || !/\.(md|markdown)$/i.test(file.path)) {
        throw new Error("Open the Markdown note you want to read in MRW.");
      }
      const configPath = `${application.vault.configDir}/mrw.json`;
      if (!await application.vault.adapter.exists(configPath)) {
        throw new Error(`Configure the MRW workspace and notes folder in ${configPath}. See Zettel's OpenInMRW guide.`);
      }
      const config = JSON.parse(await application.vault.adapter.read(configPath));
      const scheme = config.scheme || "vscode";
      if (!["vscode", "vscode-insiders"].includes(scheme)) throw new Error("MRW scheme must be vscode or vscode-insiders.");
      const workspace = new URL(config.workspace);
      if (!((workspace.protocol === "file:" && !workspace.host) ||
            (workspace.protocol === "vscode-remote:" && /^(wsl\+|ssh-remote\+)[a-z0-9_.+-]+$/i.test(workspace.host))) ||
          workspace.search || workspace.hash || workspace.username || workspace.password || workspace.port) {
        throw new Error("Configure a file: or WSL/SSH vscode-remote: workspace address.");
      }
      const posix = require("node:path").posix;
      if (typeof config.notes !== "string" || !posix.isAbsolute(config.notes) ||
          posix.resolve(config.notes) !== config.notes || /[\x00-\x1f\x7f\\]/.test(config.notes) ||
          posix.isAbsolute(file.path) || posix.normalize(file.path) !== file.path ||
          file.path.split("/").some(part => part === ".." || part === ".obsidian" || part === ".trash")) {
        throw new Error("Use the vault's absolute path on the MRW host and the note's relative filename.");
      }
      const target = { workspace: workspace.href, notes: config.notes, file: file.path };
      const encoded = require("node:buffer").Buffer.from(JSON.stringify(target), "utf8").toString("base64url");
      const link = `${scheme}://flengyel.mrw/note?v=1&target=${encoded}`;
      if (link.length > 20000) throw new Error("The MRW note address is too long.");
      await require("electron").shell.openExternal(link);
    } catch (error) {
      new Notice(`Open in MRW: ${error.message}`);
    }
  }
});
-%>
