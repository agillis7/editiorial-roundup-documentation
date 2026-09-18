# Editoral Roundup Script

## Overview 
This script extraxts content from URLs and saves the results as Markdown files. 

## Supported Sources
- Standard web articles
- Youtube videos 

## Editorial Roundup Documentation
Documentation and test environment for a Python script that collects URLs from editorial roundup files, extracts webpage content, and saves the results as Markdown files.

## What the script does
The script:
- Accepts HTML, HTM, or CSV roundup files as input.
- Extracts URLs from the input file.
- Identifies YouTube URLs and processes them separately.
- Uses Trafilatura to extract readable content from standard webpages.
- Uses MarkItDown for YouTube content.
- Cleans and formats extracted content.
- Generates article titles when necessary.
- Saves the resulting content as Markdown files.
- Continues processing when an individual URL cannot be retrieved.

## Requirements
- Python 3
- trafilatura
- beautifulsoup4
- markitdown

Dependencies are listed in `requirements.txt`.

## Running the script
From the project directory:

```text
python roundup.py