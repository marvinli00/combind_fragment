#!/bin/bash

# Check if source directory is provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

source_dir="$1"
dest_dir="$2"

# Check if source directory exists
if [ ! -d "$source_dir" ]; then
    echo "Error: Source directory '$source_dir' does not exist"
    exit 1
fi

# Create destination directory if it doesn't exist
#mkdir -p "$dest_dir"

# Copy the entire directory structure
cp -r "$source_dir" "$dest_dir"

# Navigate to the destination directory
#cd "$dest_dir/$(basename "$source_dir")" || exit
cd "$dest_dir" || exit
# Process each directory
for dir in */; do
    if [ -d "$dir" ]; then
        echo "Processing directory: $dir"
        
        # First, find and protect structures/raw directories by creating a temporary marker
        find "$dir" -type d -path "*/structures/raw" -exec touch {}/.keep_this \;

        # Remove all directories except structures and its raw subdirectory
        find "$dir" -mindepth 1 -type d | while read -r d; do
            if [[ "$d" != */structures ]] && [[ "$d" != */structures/raw ]]; then
                rm -rf "$d"
            fi
        done

        # Clean up the temporary markers
        find "$dir" -type f -name ".keep_this" -delete
    fi
done

echo "Processing complete!"