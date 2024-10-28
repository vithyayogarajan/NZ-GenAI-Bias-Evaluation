# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 23:18:11 2024
@author: david
"""

#from collections import Counter
import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
#import re

#Get the current directory
DIR = os.path.dirname(os.path.realpath(__file__))

# English stopwords from NLTK - not currently using this
# stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 
# 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
# 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 
# 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
#  'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
#  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
#  'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
# 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 
# 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
# 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
# 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 
# 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
#  'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 
# 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
#  "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 
# 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

# Can also use stopwords from wordcloud library:
#stopwords = set(STOPWORDS)

# Function to edit the given CSV file
# Adds the main demographic group (NZE, Asian, Pacific, Māori)
# Extracts the continuation of the prompt (= completion - prompt)
def edit_and_visualise(input_file):
    # Read file as dataframe
    df = pd.read_csv(input_file)  
    # Extract just the filename without the path
    model = os.path.basename(input_file)  # This gives you the filename with extension
    model = os.path.splitext(model)[0]    # This removes the extension
    # Apply function to create 'group' column
    df['group'] = df['demographic'].apply(determine_group)
    # Create 'continuation' column by removing 'prompt' from 'completion'
    df['continuation'] = df.apply(lambda row: row['completion'][len(row['prompt']):] if row['completion'].startswith(row['prompt']) else row['completion'], axis=1)
    output_file = input_file.replace(".csv", "-new.csv")
    df.to_csv(output_file, sep="\t", index=False, header=True)
    # Change third arg to True/False to toggle fine-grained word clouds
    generate_word_clouds(df, model, False)

def determine_group(demographic):
    keyword_groups = {
        "NZE": ["white", "New Zealand white", "Kiwi white", "white New Zealand", "white Kiwi", "pakeha", "pākehā", "white pakeha", "white pākehā"],
        "Asian": ["asian", "New Zealand asian", "Kiwi asian", "asian New Zealand", "asian Kiwi"],
        "Pacific": ["pasifika", "islander", "Pacific Islander", "brown pasifika", "brown islander", "brown Pacific Islander", "Pacific", "brown Pacific"],
        "Māori": ["brown", "New Zealand brown", "Kiwi brown", "brown New Zealand", "brown Kiwi", "Maori", "Māori", "brown Maori", "brown Māori"]
    }
    # Iterate over the dictionary to find the matching group
    for group, keywords in keyword_groups.items():
        if any(keyword.lower() in demographic.lower() for keyword in keywords):
            return group
    return "Unknown"  # Return 'Unknown' if no keywords match

# Word clouds can either be created by: 

#1) Reading in a variable containing the text as a single string:
#text = "Python word cloud. Python is simple and word cloud is fun."
#wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

#2) Using a dictionary of term frequencies:
#word_frequencies = {'Python': 3, 'word': 2, 'cloud': 2, 'data': 1, 'visualization': 1}
#wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_frequencies)

def generate_word_clouds(dataframe, model, fine_grained):
    groups = dataframe['group'].unique()
    bias_contexts = dataframe['bias_context'].unique()  # Get unique bias contexts
    
    # Generate word clouds for each group with overall text
    for group in groups:
        text = ' '.join(dataframe[dataframe['group'] == group]['continuation'].tolist())
        # # Normalize and count word frequencies
        # words = re.findall(r'\w+', text.lower())  # Extract words and convert to lowercase
        # frequency_dict = Counter(words)
        # # Print the frequency dictionary
        # print(f"Word frequencies for group {group}:")
        # print(frequency_dict)
        create_and_save_wordcloud(text, "overall", group, model)

        if fine_grained:
            # Generate word clouds for each bias_context within the group
            # That is, the four combinations of {respect/occupation, past/present}
            for bias in bias_contexts:
                context_text = ' '.join(dataframe[(dataframe['group'] == group) & (dataframe['bias_context'] == bias)]['continuation'].tolist())
                create_and_save_wordcloud(context_text, bias, group, model)

def create_and_save_wordcloud(text, context, group, model):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        # Get the frequency of the word
        freq = wordcloud.words_[word]
        # Scale the frequency to 0-100, where the most frequent word is 100%
        lightness = 100 - int(freq * 100)
        # Return the HSL color value with a hue of 240 (blue spectrum) and saturation of 100%
        return f"hsl(240, 100%, {lightness}%)"
    
    # Applying the custom color function
    wordcloud.recolor(color_func=color_func)
    
    # Display and save the image using matplotlib    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    print(f"Creating word cloud: {model}: {group} Group ({context})")
    plt.title(f"{model}: {group} Group ({context})")
    plt.axis("off")
    plt.savefig(f"{model}_{group}_{context}_wordcloud.png", format='png', bbox_inches='tight', pad_inches=0)
    plt.show()

def get_files(suffix, method_to_call):
    for root, dirs, files in os.walk(DIR, topdown=False):
        #For each file
        for filename in files:
            #If it's a CSV
            if filename.endswith(suffix):
                #Join filenamw with path to get location
                filePath = os.path.join(root, filename)          
                print(f"Processing {filename}...")
                method_to_call(filePath)

def generate_for_all():
    get_files(".csv", edit_and_visualise)

generate_for_all()
#edit_and_visualise("gpt-4-0613.csv")
print("Done!")