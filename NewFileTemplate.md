<%*
let alpha_keyword = await tp.system.prompt("Enter the alpha keyword for this note:");
let unique_id = alpha_keyword + tp.date.now("YYYYMMDDHHmm");
let user_title = await tp.system.prompt("Enter the title for this note:");
-%>
---
id: <%* tR += unique_id %>
title: <%* tR += unique_id %> <%* tR += user_title %>
reference-section-title: References
---

# <%* tR += user_title %>

## SEE ALSO

## References

<%* tp.file.rename(unique_id); %>
