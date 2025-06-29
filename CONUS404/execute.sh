#!/bin/bash

#SBATCH --output=%x.%j.out
#SBATCH --error=%x.%j.err  
#SBATCH --mem=19G 
hostname 1>&2  #prints hostname to the error file

# Define how many times you want to retry
MAX_RETRIES=144
RETRY_DELAY=5  # seconds

for ((i=1; i<=MAX_RETRIES; i++))
do
    echo "Attempt $i of $MAX_RETRIES..."
    # Run your Python script
    python march.dwld.seus.py
    # Check if the script succeeded (exit code 0)
    if [ $? -eq 0 ]; then
        echo "Download completed successfully."
        break
    else
        echo "Download failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    fi
done




