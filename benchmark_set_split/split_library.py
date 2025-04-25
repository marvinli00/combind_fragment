#!/usr/bin/env python3

import os
import csv
import math

def split_csv(input_file, output_dir, lines_per_file=200):
    """
    Split a CSV file into multiple files with the specified number of lines each,
    preserving the header in each file.
    
    Args:
        input_file (str): Path to the input CSV file
        output_dir (str): Directory to save the output files
        lines_per_file (int): Number of lines per output file (excluding header)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the input file to get total lines and header
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Get the header row
        rows = list(reader)  # Get all data rows
    
    # Calculate number of output files needed
    total_rows = len(rows)
    num_files = math.ceil(total_rows / lines_per_file)
    
    print(f"Splitting {input_file} into {num_files} files with {lines_per_file} lines each (plus header)")
    
    # Split the data and write to output files
    for i in range(num_files):
        start_idx = i * lines_per_file
        end_idx = min((i + 1) * lines_per_file, total_rows)
        
        output_filename = os.path.join(output_dir, f"library_part_{i+1}.csv")
        
        with open(output_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)  # Write the header
            writer.writerows(rows[start_idx:end_idx])  # Write the data rows
        
        print(f"Created {output_filename} with {end_idx - start_idx + 1} lines (including header)")

if __name__ == "__main__":
    
    #read all folders in the working directory
    folders = os.listdir()
    
    for folder in folders:
        #check if the folder is a directory
        if os.path.isdir(folder):
            #check if the folder contains a library.csv file
            if "library.csv" in os.listdir(folder):
                input_file = os.path.join(folder, "library.csv")
                output_dir = os.path.join(folder, "split_library")
                lines_per_file = 200
                split_csv(input_file, output_dir, lines_per_file) 