<%*
let alpha_keyword = await tp.system.prompt("Enter the alpha keyword for this note:");
if (!alpha_keyword) {
  new Notice("Alpha keyword is required.");
  return;
}

let unique_id = alpha_keyword + tp.date.now("YYYYMMDDHHmm");

let user_title = await tp.system.prompt("Enter the title for this note:");
if (!user_title) {
  new Notice("Title is required.");
  return;
}

/* Rename the current file to the unique ID */
await tp.file.rename(unique_id);
-%>
---
id: <%* tR += unique_id + '\n' %>
title: <%* tR += unique_id + ' ' + user_title + '\n' %>
reference-section-title: References
---
# <%* tR += user_title + '\n' %>

## SEE ALSO

## References
