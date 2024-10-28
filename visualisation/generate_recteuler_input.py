# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 21:12:34 2024

@author: david
"""

import csv
from collections import defaultdict

def process_output_data(input_file):
    # Read the input CSV file
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        
        # Dictionary to hold data per model
        model_data = defaultdict(lambda: defaultdict(lambda: {"words": set(), "race_counts": {"NZE": 0, "Māori": 0, "Asian": 0, "Pacific": 0}}))
        
        for row in reader:
            model = row['model']
            race = row['race']
            top_ten = eval(row['top_ten'])  # Convert string representation of dict back to dict
            
            # Update the set of words and race counts
            for word in top_ten.keys():
                model_data[model][word]["words"].add(word)
                model_data[model][word]["race_counts"][race] = 1  # Mark presence of word for the race

        # Create output files for each model
        for model, words_data in model_data.items():
            output_file = f"{model}_recteuler.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                
                # Write the header
                writer.writerow(['Item', 'NZE', 'Māori', 'Asian', 'Pacific'])
                
                # Write the rows for each unique word
                for word, data in words_data.items():
                    row = [word] + [data["race_counts"][race] for race in ['NZE', 'Māori', 'Asian', 'Pacific']]
                    writer.writerow(row)
                    
    print("Processing complete!")

# Run the function with the path to your output_data.csv
process_output_data('new_output.tsv')