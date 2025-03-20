import re
import csv
import pandas as pd
import numpy as np

# Raw data (example from your text)
with open('data.txt', 'r') as file:
    raw_data = file.read()

# Define the regular expression to extract relevant columns
pattern = r"(\d{4})\(\s*(\d+)\s*\)\s+(\d+)\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"

# Find all matches in the raw data
matches = re.findall(pattern, raw_data)

# Write the extracted data into a CSV file, adding interference
with open('channel_data_with_interference.csv', mode='w', newline='') as csv_file:
    fieldnames = ['Frequency', 'Channel', 'BSS', 'minsnr', 'maxsnr', 'NF', 'Ch_load', 'spect_load', 'sec_chan',
                  'SR_bss', 'SR_load', 'Ch_avil', 'Chan_eff', 'NearBSS', 'Med_BSS', 'Far_BSS', 'Eff_BSS', 'grade',
                  'Rank', 'Unused', 'Radar', 'Interference']  # Added 'Interference' column
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()  # Write the header
    for match in matches:
        # Calculate interference (Ch_load * (1 / (abs(minsnr) + epsilon)))
        epsilon = 1e-6  # Small value to prevent division by zero
        interference = float(match[6]) * (1 / (abs(int(match[3])) + epsilon))

        # Write the data with calculated interference
        writer.writerow({
            'Frequency': match[0],
            'Channel': match[1],
            'BSS': match[2],
            'minsnr': match[3],
            'maxsnr': match[4],
            'NF': match[5],
            'Ch_load': match[6],
            'spect_load': match[7],
            'sec_chan': match[8],
            'SR_bss': match[9],
            'SR_load': match[10],
            'Ch_avil': match[11],
            'Chan_eff': match[12],
            'NearBSS': match[13],
            'Med_BSS': match[14],
            'Far_BSS': match[15],
            'Eff_BSS': match[16],
            'grade': match[17],
            'Rank': match[18],
            'Unused': 0,  # Placeholder for Unused column
            'Radar': match[19],
            'Interference': interference  # Interference value calculated
        })

# Load your dataset (ensure the CSV file exists in the specified path)
data = pd.read_csv('channel_data_with_interference.csv')

# Optionally, sort by interference to find the highest interfering channels
sorted_data = data[['Channel', 'Frequency', 'Ch_load', 'minsnr', 'Interference']].sort_values(by='Interference', ascending=False)

# Optionally, save the results to a new CSV file
sorted_data.to_csv('sorted_channel_data.csv', index=False)

print("Data has been parsed, interference calculated, and saved to 'channel_data_with_interference.csv'")
