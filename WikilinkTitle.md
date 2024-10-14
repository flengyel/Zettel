<%*
// Get the entire content of the file and split by lines
let file_content = tp.file.content;
if (!file_content) {
  new Notice("Could not retrieve file content.");
  return;
}

let file_lines = file_content.split("\n");

// Automatically determine the current cursor line number
let editor = this.app.workspace.activeEditor.editor;
let current_line_num = editor.getCursor().line;

// Validate the line number
if (current_line_num < 0 || current_line_num >= file_lines.length) {
  new Notice("Invalid line number detected.");
  return;
}

let current_line = file_lines[current_line_num];

// Ensure the current line contains valid content
if (!current_line || current_line.trim() === "") {
  new Notice("The selected line is empty or could not be retrieved.");
  return;
}

// Match the WikiLink anywhere in the line
let note_link_match = current_line.match(/\[\[(.*?)\]\]/);
if (!note_link_match) {
  new Notice("The selected line does not contain a valid WikiLink (e.g., [[wikilink]]). ");
  return;
}

// Extract the note name from the WikiLink
let note_name = note_link_match[1];

// Find the linked note and read its content
let linked_note = await tp.file.find_tfile(note_name);
if (!linked_note) {
  new Notice("Linked note could not be found.");
  return;
}

let note_content = await app.vault.read(linked_note);

// Extract the title from the YAML front matter of the linked note
let title_match = note_content.match(/^title:\s*(.*)/m);
let note_title = title_match ? title_match[1].trim() : "Title not found";

// Remove any newlines from the extracted title
note_title = note_title.replace(/\n/g, " ").replace(/\r/g, " ").trim();

// Extract the ID from the title (first group of contiguous non-space characters)
let id_match = note_title.match(/^(\S+)/);
let title_id = id_match ? id_match[1] : null;

// Check if the extracted ID matches the WikiLink note name
if (title_id && title_id === note_name) {
  // Remove the ID from the title
  note_title = note_title.slice(title_id.length).trim();
} else if (title_id) {
  // Raise an error if the ID does not match
  new Notice(`The ID in the title (${title_id}) does not match the WikiLink ID (${note_name}). Please verify the linked note.`);
}

// Construct the updated line by inserting the title directly after the WikiLink, preserving all other content
let prefix = current_line.slice(0, note_link_match.index + note_link_match[0].length);
let suffix = current_line.slice(note_link_match.index + note_link_match[0].length);
let updated_line = prefix + ' '+ note_title + suffix;
file_lines[current_line_num] = updated_line;

// Join the updated lines and write back to the file
let updated_content = file_lines.join("\n");
let current_file = await tp.file.find_tfile(tp.file.title);

if (current_file) {
  await app.vault.modify(current_file, updated_content);
}
%>
