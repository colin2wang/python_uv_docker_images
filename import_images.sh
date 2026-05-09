#!/bin/bash

# Docker Image Import Script
# Automatically finds all .tar files and allows interactive import

set -e

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "======================================================================"
echo "  Docker Image Import Tool"
echo "======================================================================"
echo ""

# Find all .tar files in current directory
mapfile -t tar_files < <(find . -maxdepth 1 -name "*.tar" -type f | sort)

# Check if any tar files found
if [ ${#tar_files[@]} -eq 0 ]; then
    echo -e "${RED}No .tar files found in current directory${NC}"
    exit 1
fi

echo -e "${GREEN}Found ${#tar_files[@]} Docker image archive(s):${NC}"
echo "----------------------------------------------------------------------"

# Display menu
for i in "${!tar_files[@]}"; do
    file="${tar_files[$i]}"
    filename=$(basename "$file")
    
    # Get file size in human-readable format
    size_bytes=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
    
    if [ $size_bytes -lt 1048576 ]; then
        size=$(awk "BEGIN {printf \"%.2f KB\", $size_bytes/1024}")
    elif [ $size_bytes -lt 1073741824 ]; then
        size=$(awk "BEGIN {printf \"%.2f MB\", $size_bytes/1048576}")
    else
        size=$(awk "BEGIN {printf \"%.2f GB\", $size_bytes/1073741824}")
    fi
    
    echo -e "${BLUE}$((i+1))${NC}. $filename ($size)"
done

echo "----------------------------------------------------------------------"
echo -e "${YELLOW}0${NC}. Exit"
echo ""

# Function to import docker image
import_image() {
    local file=$1
    local filename=$(basename "$file")
    
    echo ""
    echo -e "${BLUE}Importing: $filename${NC}"
    echo "----------------------------------------------------------------------"
    
    # Try docker load, if permission denied, try with sudo
    if docker load -i "$file" 2>/dev/null; then
        echo ""
        echo -e "${GREEN}✓ Successfully imported: $filename${NC}"
    elif sudo docker load -i "$file"; then
        echo ""
        echo -e "${GREEN}✓ Successfully imported (with sudo): $filename${NC}"
    else
        echo ""
        echo -e "${RED}✗ Failed to import: $filename${NC}"
        echo -e "${YELLOW}Tip: Make sure Docker is running and you have permissions${NC}"
        return 1
    fi
    
    # Ask if delete
    echo ""
    read -p "Delete $filename? (Y/n, default: Y): " delete_choice
    delete_choice=${delete_choice:-Y}
    
    if [[ "$delete_choice" =~ ^[Yy]$ ]] || [[ -z "$delete_choice" ]]; then
        rm -f "$file"
        echo -e "${GREEN}✓ Deleted: $filename${NC}"
    else
        echo -e "${YELLOW}Kept: $filename${NC}"
    fi
}

# Main loop
while true; do
    echo ""
    read -p "Enter number to import (0 to exit): " choice
    
    # Validate input is a number
    if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Invalid input. Please enter a number.${NC}"
        continue
    fi
    
    # Exit
    if [ "$choice" -eq 0 ]; then
        echo -e "${BLUE}Exiting...${NC}"
        exit 0
    fi
    
    # Check if choice is valid
    if [ "$choice" -lt 1 ] || [ "$choice" -gt ${#tar_files[@]} ]; then
        echo -e "${RED}Invalid choice. Please enter a number between 1 and ${#tar_files[@]}.${NC}"
        continue
    fi
    
    # Import selected image
    selected_file="${tar_files[$((choice-1))]}"
    import_image "$selected_file"
    
    # Refresh file list after import/delete
    mapfile -t tar_files < <(find . -maxdepth 1 -name "*.tar" -type f | sort)
    
    # If no more files, exit
    if [ ${#tar_files[@]} -eq 0 ]; then
        echo ""
        echo -e "${GREEN}All images imported. No more .tar files.${NC}"
        exit 0
    fi
    
    # Redisplay menu
    echo ""
    echo "----------------------------------------------------------------------"
    echo -e "${GREEN}Remaining archives: ${#tar_files[@]}${NC}"
    echo "----------------------------------------------------------------------"
    for i in "${!tar_files[@]}"; do
        file="${tar_files[$i]}"
        filename=$(basename "$file")
        
        size_bytes=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        
        if [ $size_bytes -lt 1048576 ]; then
            size=$(awk "BEGIN {printf \"%.2f KB\", $size_bytes/1024}")
        elif [ $size_bytes -lt 1073741824 ]; then
            size=$(awk "BEGIN {printf \"%.2f MB\", $size_bytes/1048576}")
        else
            size=$(awk "BEGIN {printf \"%.2f GB\", $size_bytes/1073741824}")
        fi
        
        echo -e "${BLUE}$((i+1))${NC}. $filename ($size)"
    done
    echo "----------------------------------------------------------------------"
    echo -e "${YELLOW}0${NC}. Exit"
done

