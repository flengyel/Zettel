import os
from zettel_validate import zettel_validate, validation_stats

# Loop through a directory of Zettels
zettel_directory = 'C:\\Users\\fleng\\OneDrive\\Documents\\Zettelkasten'
for root, dirs, files in os.walk(zettel_directory):
    for file in files:
        if file.endswith('.md'):  # Assuming your Zettels are in .md format
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                text = f.read()
                # zettel_validate() can take the filename without the extension
                print(file, zettel_validate(text, filename_without_extension=os.path.splitext(file)[0]))

# Print final stats
print(f"Validation stats: {validation_stats}")
