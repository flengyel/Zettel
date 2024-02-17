import os
from zettel_validate import ZettelValidator 
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns

def median_word_count(word_counts):
    """Calculate the median word count from a list of word counts"""
    sorted_word_counts = sorted(word_counts)
    length = len(sorted_word_counts)
    if length % 2 == 0:
        return (sorted_word_counts[length // 2 - 1] + sorted_word_counts[length // 2]) / 2
    else:
        return sorted_word_counts[length // 2]

# Define the word frequency bins
MAXBIN_LEFT_ENDPOINT = 1001
MAXBIN_LABEL = str(MAXBIN_LEFT_ENDPOINT) + '+'
BIN_WIDTH = 50
# Initialize the word frequency bins
word_freq_bins = dict()
for i in range(1, MAXBIN_LEFT_ENDPOINT, BIN_WIDTH):
    word_freq_bins[str(i) + '-' + str(i+49)] = 0
word_freq_bins[MAXBIN_LABEL] = 0


# List to store word counts
word_counts = []

# Directory where the Zettelkasten notes are stored
zettel_directory = 'C:\\Users\\fleng\\OneDrive\\Documents\\Zettelkasten'

# Apply the ggplot style
sns.set(style="whitegrid")

validator = ZettelValidator() # instantiate the ZettelValidation class


# Use os.listdir to get the list of all files and directories in zettel_directory
for file in os.listdir(zettel_directory):
    # Form the full path to the file
    full_path = os.path.join(zettel_directory, file)
    # Check if it's a file and if it has a .md extension
    if os.path.isfile(full_path) and file.endswith('.md'):
        #print(f"Processing {full_path}...")
        with open(full_path, 'r', encoding='utf-8') as f:
            text = f.read()
            # Call zettel_validate function and print the result
            validator.validate(text, fn=file.split('.md')[0])
            f.close()
            # Count the number of words in the Zettel
            word_count = len(text.split())
            word_counts.append(word_count)  # Append word count to the list
            
            # Categorize the Zettel based on the number of words into the word frequency bins
            for bin_range, count in word_freq_bins.items():
                if bin_range == MAXBIN_LABEL: 
                    if word_count >= MAXBIN_LEFT_ENDPOINT:
                        word_freq_bins[bin_range] += 1
                else:
                    lower, upper = map(int, bin_range.split('-'))
                    if lower <= word_count <= upper:
                        word_freq_bins[bin_range] += 1

# Plot pie chart for validation stats
labels = validator._stats.keys()
sizes = validator._stats.values()
explode = [0.1 if size > 0 else 0 for size in sizes]  # Explode segments with non-zero sizes

plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
plt.title('Zettel Validation Stats')
plt.show()

# Plot bar chart for word count frequency
bin_labels = []
for i in range(1, MAXBIN_LEFT_ENDPOINT, BIN_WIDTH):
    bin_labels.append(str(i) + '-' + str(i+49))
bin_labels.append(MAXBIN_LABEL)

         
bin_values = [word_freq_bins[bl] for bl in bin_labels]

plt.figure(figsize=(10, 6))
plt.bar(bin_labels, bin_values, color='skyblue', edgecolor='black')
plt.title('Word Count Frequency by Zettel')
plt.xlabel('Word Count Bins')
plt.ylabel('Number of Zettels')
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust the layout to fit the x labels
plt.show()

# Display validation stats

print(validator.statisics)
print(f"Total number of words: {sum(word_counts)}")
print(f"Average number of words per Zettel: {sum(word_counts) / len(word_counts)}")
print(f"Median number of words in a Zettel: {median_word_count(word_counts)}")   
print(f"Minimum number of words in a Zettel: {min(word_counts)}")
print(f"Maximum number of words in a Zettel: {max(word_counts)}")
print(f"Most common word count: {Counter(word_counts).most_common(1)[0]}")
print(f"Least common word count: {Counter(word_counts).most_common()[-1]}")

