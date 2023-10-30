import os
from zettel_validate import zettel_validate, validation_stats
import matplotlib.pyplot as plt
from collections import Counter

# Initialize the word frequency bins
word_freq_bins = {
    '1-20': 0,
    '21-40': 0,
    '41-60': 0,
    '61-80': 0,
    '81-100': 0,
    '101-250': 0,
    '251-500': 0,
    '501-750': 0,
    '751-1000': 0,
    '1001+': 0
}

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
                # Count the number of words in the Zettel
                word_count = len(text.split())
                
                # Categorize the Zettel based on the number of words into the word frequency bins
                if word_count <= 20:
                    word_freq_bins['1-20'] += 1
                elif 21 <= word_count <= 40:
                    word_freq_bins['21-40'] += 1
                elif 41 <= word_count <= 60:
                    word_freq_bins['41-60'] += 1
                elif 61 <= word_count <= 80:
                    word_freq_bins['61-80'] += 1
                elif 81 <= word_count <= 100:
                    word_freq_bins['81-100'] += 1
                elif 101 <= word_count <= 250:
                    word_freq_bins['101-250'] += 1
                elif 251 <= word_count <= 500:
                    word_freq_bins['251-500'] += 1
                elif 501 <= word_count <= 750:
                    word_freq_bins['501-750'] += 1
                elif 751 <= word_count <= 1000:
                    word_freq_bins['751-1000'] += 1
                else:
                    word_freq_bins['1001+'] += 1

# Display validation stats
print(f"Validation stats: {validation_stats}")

# Plot pie chart for validation stats
labels = validation_stats.keys()
sizes = validation_stats.values()
explode = (0.1, 0, 0, 0, 0, 0, 0)
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')
plt.title('Zettel Validation Stats')
plt.show()

# Plot histogram for word frequencies
labels = list(word_freq_bins.keys())
values = list(word_freq_bins.values())
plt.bar(labels, values)
plt.xlabel('Word Count Ranges')
plt.ylabel('Number of Zettels')
plt.title('Word Frequency Histogram')
plt.show()


