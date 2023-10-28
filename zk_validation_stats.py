import os
from zettel_validate import zettel_validate, validation_stats
import matplotlib.pyplot as plt

zettel_directory = 'C:\\Users\\fleng\\OneDrive\\Documents\\Zettelkasten'

# Use os.listdir to get the list of all files and directories in zettel_directory
for file in os.listdir(zettel_directory):
    # Form the full path to the file
    full_path = os.path.join(zettel_directory, file)
    
    # Check if it's a file
    if os.path.isfile(full_path):
        # Check if it has a .md extension
        if file.endswith('.md'):
            # Open and read the file
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
                # Call zettel_validate function and print the result
                print(file, zettel_validate(text, filename_without_extension=os.path.splitext(file)[0]))



# Print final stats (if needed)
print(f"Validation stats: {validation_stats}")

# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = validation_stats.keys()
sizes = validation_stats.values()

# Explode the 1st slice ('good_zettels')
explode = (0.2, 0, 0, 0, 0, 0, 0)

# Plot pie chart
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.title('Zettel Validation Stats')
plt.show()

