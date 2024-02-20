import os
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
from statistics import median

def calculate_median_word_count(word_counts):
    """Calculate the median word count from a list of word counts"""
    return median(word_counts)

def initialize_word_freq_bins(max_bin_left_endpoint=1001, bin_width=50):
    """Initialize word frequency bins"""
    word_freq_bins = {f"{i}-{i+49}": 0 for i in range(1, max_bin_left_endpoint, bin_width)}
    word_freq_bins[f"{max_bin_left_endpoint}+"] = 0
    return word_freq_bins

def categorize_word_count(word_count, word_freq_bins, max_bin_left_endpoint):
    """Categorize the Zettel based on the number of words into the word frequency bins"""
    if word_count >= max_bin_left_endpoint:
        word_freq_bins[f"{max_bin_left_endpoint}+"] += 1
    else:
        bin_label = f"{(word_count // 50) * 50 + 1}-{(word_count // 50) * 50 + 50}"
        if bin_label in word_freq_bins:
            word_freq_bins[bin_label] += 1

# Apply the ggplot style
sns.set(style="whitegrid")

# Initialize variables
word_counts = []
word_freq_bins = initialize_word_freq_bins()

# Directory processing
zettel_directory = 'C:\\Users\\fleng\\OneDrive\\Documents\\Zettelkasten'
for file in os.listdir(zettel_directory):
    full_path = os.path.join(zettel_directory, file)
    if os.path.isfile(full_path) and file.endswith('.md'):
        with open(full_path, 'r', encoding='utf-8') as f:
            text = f.read()
        word_count = len(text.split())
        word_counts.append(word_count)
        categorize_word_count(word_count, word_freq_bins, 1001)

# Visualization and statistics display functions would follow here

# Displaying word frequency bins
plt.figure(figsize=(10, 7.5)) # Set the size of the plot
plt.bar(word_freq_bins.keys(), word_freq_bins.values(), color='skyblue')
plt.title('Word Frequency Bins')
plt.xlabel('Word Count')
plt.ylabel('Number of Zettels')
plt.xticks(rotation=90)
plt.show()

# Displaying word count statistics
print(f"Total number of words: {sum(word_counts)}")
print(f"Average number of words per Zettel: {sum(word_counts) / len(word_counts) if word_counts else 0}")
print(f"Median number of words in a Zettel: {calculate_median_word_count(word_counts)}")
print(f"Minimum number of words in a Zettel: {min(word_counts, default=0)}")
print(f"Maximum number of words in a Zettel: {max(word_counts, default=0)}")
print(f"Most common word count: {Counter(word_counts).most_common(1)[0] if word_counts else 'N/A'}")
print(f"Least common word count: {Counter(word_counts).most_common()[-1] if word_counts else 'N/A'}")
