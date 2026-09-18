# Editorial Roundup Script Documentation

## Overview
The Editorial Roundup script automates the process of collecting and organizing content from a list of URLs. 
The script acccepts an HTML or CSV file containing URLs, then idenifies the type of content at each URL, extracts the readable content, converts it to Markdown, and saves each item as a separate Markdown file. 

The script uses different extraction methods dending on the source:
- YouTube URLs are processed with MarkItDown
- Standard web pages are processed with Trafilatura

The resulting Markdown files are organized into a dated output folder and include the article title, source URL, and roundup date. 

## Dependencies and Imports
The script uses Python's standard library along with several third-party libraries.
- `csv` -- which reads the CSV files containing URLs. 
- `re` -- which uses regular expressions to find and clean text and URLs. 
-`sys` -- Which checks command-line arguments, including the `--auto` option.
-`Path` -- wich works with files and folders using Python's path-handling tools. 
- `urlparse` -- which separates a URL into components such as its domain and path.
- `trafilatura` -- which retrieves and extracts readable content from standard web pages.
- `BeautifulSoup` -- which parses HTML and finds links within HTML documents.
- `MarkItDown` -- which converts supported web content, including YouTube content, into Markdown-compatible text.

## Working Directories

### `BASE_DIR`

`BASE_DIR` which identifies the folder containing the Python script itself.

`__file__` which refers to the current Python file. `Path()` converts that file
location into a path object. `.resolve()` obtains the full path, and `.parent`
moves from the file to its containing folder.

This allows the script to work relative to its own location rather than
depending on where the user happens to run it from.

### `ROUNDUP_OUTPUT_DIR`

`ROUNDUP_OUTPUT_DIR` defines the `Daily Roundups` folder as the location where
the script will create its output.

`/` is being used by Python's `Path` object to construct a subdirectory path.

## `safe_filename()`
The `safe_filename()` function prepares text so that it can be used as part of a filename. 

### Parameters
- `text` -- the text that will be converted into a filename. 
- `max_length` -- the maximum file text length. It defaults to 120 characters. 

### Process
The function performs three main cleanup operations:
1. Removes the characters that could cause problems in a filename. 
2. Replaces repeated whitespace with a single space and removes unnecessary whitespace from the beginning and end.
3. Limits the resulting text to the specified maximum length.

If the resulting text is empty, the function returns `untitled_article` instead. 

### Return Value
The function returns a cleand string for use in a filename. 

## `get_roundup_label()`
The `get_roundup_label()` function determines the date and idenitfying label associated with an editorial roundup file. 

### Parameter
- `path` -- the file path for the HTML or CSV file. 

### Process 
The function searches for the filename for a date in a year-month-day format. 
If a date is found, the function passes the filename through the `safe_filename()` function to create a cleaned label. 

### Return value 
The function returns either:
- The date found in the filename -- such as 2026-09-18
- A cleaned version of the filename when no date is present

## `get_auto_html_path()`
The `get_auto_html_path()` function automatically identifies the most recently modified HTML roundup file in the script's working directory. 

### Process
The function:
1. Searches the working directory for files matching `today's_roundup*.html`. 
2. Sorts the matching files by their modification time, with the most recently modified file first. 
3. Returns the most recently modified file. 

If no matching HTML files are found, the function raises a `FileNotFoundError` and identifies the directory where it expected to find the files. 

### Purpose
This function supports the script's automatic mode. As opposed to requiring the user to manually select an input file, the script can identify the latest roundup file automatically. 

## `get_input_path_from_dialog()`
The `get_input_path_from_dialog()` function opens a graphical file-selection
window that allows the user to choose an input file.

### Process
The function imports Python's `tkinter` library and its file-dialog tools.

It then opens a file-selection window configured to look for:
- HTML files
- HTM files
- CSV files

The dialog initially opens in the script's working directory.

If the user selects a file, the function converts the selected location into a
`Path` object and returns it.

If the user cancels the dialog without selecting a file, the function raises a
`FileNotFoundError`.

### Purpose
This function provides the manual input method for users who do not want to
use the script's automatic file-selection mode.

## `clean_url()`
The `clean_url()` function removes unwanted charachters and formatting from a URL before the script processes it. 

### Parameter
- `url` -- the URL that needs to be cleaned.

### Process
The function:
1. Removes whatespace from the beginning and end of the URL. 
2. Removes anything after a comma. 
3. Removes trailing punctuation, including closing parentheses, periods, commas, and semicolons.

### Return value 
The function returns the cleaned URL. 

### Purpose
Cleaning the URLs before processing helps to prevent formatting problems from interfering with URL retrieval and contxt extraction. 

## `extract_urls_from_html()`
The `extract_urls_from_html()`function finds URLs in an HTML file. 

### Parameter
- `path` -- the path to the HTML file being processed

### Process
The function first reads the HTML file and uses BeautfulSoup to parse its contents.

It then searches for HTML links and collects the links that addresses begin with `http`. 

The function also serches the HTML for URLs. This provides an additional way to identify URLs that might appear in the HTML, but are not contained in standard link elements. 

Each URL is passed through `clean_url()` before being added to the results. 

Duplicate URLs are removed while keeping their original order.

### Return value
The function returns a list of unique, cleaned URLs. 

### Purpose 
This function converts an HTML roundup into a list of URLs that the main program can process individually. 

## `fallback_title_from_url()`
The `fallback_title_from_url()` function creates a title from a URL when a title cannot be obtained from the source content. 

### Parameter 
- `url` -- the URL that the title is generated from. 

### Process
The function uses `urlparse()` to separate the URL into its components. 

It looks at the URL path and takes the URL slug -- which is the final section of that URL path.

The function then replaces hyphens and underscores with spaces and converts the result into title case.

If the URL does not contain a path, the function uses the website's domain instead. 

### Return value
The function returns a readable title generated from the URL. 

### Purpose
This provides a fallback when the source website does not provide usable title metadata. 

## `is_youtube_url()`
The `is_youtube_url()` function determines weather a URL points to Youtbe. 

### Parameter
- `url` -- the URL being checked.

### Process:
The function uses `urlparse()` to extract the URL's domain name and converts the domain to lowercase. It then checks weather the domain contains either 'youtube.com' or 'youtu.be'.

### Return value
The funtion returns a Boolean value:

Returns 'True' if the URL is a Youtube URL. 

Otherwise, returns 'False'.

### Purpose 
The 'main()" function uses this result to determine wether to process the URL with MarkItDown or Trafilatura. YouTube requires MarkItDown.

#### `extract_with_markitdown()`
The `extract_with_markitdown()` function retrieves content from a URL using the MarkItDown library and prepares the resulting text for an output in Markdown.

### Parameter 
- `url` -- the URL to be processed. 

### Process 
The function first cleans the URL using `clean_url()`.

It then creates a `MarkItDown` object and uses it to convert the content at the URL into text. 

After extraction, the function performs multiple cleanup operations:
1. Converts interviewer questions beginning with `>>` into Markdown subheadings.
2. Removes repeated words.
3. Removes the top-level `YouTube` heading if present.
4. Checks if usable text was extracted.

The function then attempts to determine a title. It uses `fallback_title_from_url()` and then searches the extracted Markdown for a heading that better suits the entry. 

If an error occurs durring extraction, then the function prints an error message and returns no context. 

### Return value
The function returns two values:
1. The extracted and clean text. 
2. The title associated with the content. 

If the extraction fails, then it returns `None` instead. 

### Purpose 
This function provides the specialized extraction workflow used for YouTube URLs that MarkItDown can process.  

## extract_with_trafilatura()`
The `extract_with_trafilatura()` function retrieves and extracts readable content from a standard web page. 

### Parameter
- `url` -- the URL of the article or web-page to be processed. 

### Process 
The function first cleans the URL. 

It then uses Trafilatura to retrieve the webpage. 

If the webpage connot be successfully retrieved, the function reports the failure and stops processing that URL. 

When the page is successfully retrieved, Trafilatura extracts the article content and converts it to MarkDown. 

The extraction is configured to preserve:
- Links.
- Tables.
- Formatting.

The fucntion then attempts to retrieve the article's title from the webpage's metadata. 

If the metadata does not provide a title, the function uses `fallback_title_from_url()` to generate one. 

### Return value 
The function returns:
- The extracted article text.
- The article title.

If the page cannot be retrieved or no article text can be extracted, the
function returns `None` values.

### Purpose

This is the primary content-extraction workflow for standard web articles.

## `article_contains_heading()`
The `article_contains_heading()` function checks whether the extracted content already contains a heading matching the article title. 

### Parameters 
- `article_text` -- the extracted article content. 
- `article_title` -- the title associated with the article.

### Process
The function converts the target title to lowercase so the comparison is not
affected by capitalization.

It then examines each line of the article and identifies lines beginning with
Markdown heading characters (`#`).

For each heading, it removes the heading characters and compares the remaining
text with the article title.

### Return value
The function returns:

- `True` if a matching heading already exists.
- `False` if no matching heading is found.

### Purpose
This prevents the script from creating a duplicate title when the extracted content already contains the article title as a Markdown heading.

## `main()`
The `main()` function controls the overall workflow of the script. 

It connects the individual functions together and determines the sequence that they are executed in. 

### Input selection
The function first determines how the input file should be selected. 

If the `--auto` command-lline argument is present, the script automatically selects the most recently modified roundup HTML file using `get_auto_html_path()`. 

Otherwise, it opens a file-selection dialog using `get_input_path_from_dialog()`.

### Output directory 
The function determines the roundup label using `get_roundup_label()`.

It then creates a dedicated output directory inside the `Daily Roundups` folder. 

The directory name includes the roundup label. 

### Input processing 
The function checks the input file's extension.

If the function file is HTML or HTM, the script uses `extract_urls_from_html()`. 

If the file name is CSV, the script uses `extract_urls_from_csv()`. 

If the file type is not supported, the funtion raises an error. 

### Processing each URL
The script then processes each URL individually.

For every URL, it:
1. Cleans the URL.
2. Displays the correct URL and its position in the processing list.
3. Determines wether the URL belongs to YouTube. 
4. Uses MarkItDown for YouTube URLs. 
5. Uses Trafilatura for standard web pages.
6. Skips the URL if content could not be extracted.
7. Creates a fallback title if necessary.
8. Generates a filename for the resulting Markdown file.
9. Checks whether the extracted content already contains the article title.
10. Adds the title if necessary.
11. Adds the source URL and roundup date.
12. Saves the resulting content as a Markdown file.

### Error handling
If an individual URL cannot be processed, the script prints a message and
continues to the next URL rather than stopping the entire roundup process. 

### Completion
After all URLs have been processed, the script prints `Done.` to indicate that
the workflow has finished.

### Purpose
`main()` serves as the central controller for the application. The individual functions perform specific tasks while `main()` determines how those tasks work together to complete the editorial roundup workflow.

## Script Entry Point
The final two lines determine what happens when the Python file is run directly. 

The script checks whether the file is being executed as the main program. If it is, it calls the `main()` function. 

This enables the functions in the file to be imported by another Python program without automatically starting the entire roundup workflow. 

## Overall workflow
The script follows this general process:
1. Select an HTML or CSV roundup file.
2. Extract URLs from the input file.
3. Clean the URLs.
4. Process each URL individually.
5. Determine whether each URL is a YouTube source or a standard webpage.
6. Use the appropriate extraction tool.
7. Extract and clean the source content.
8. Determine an article title.
9. Create a Markdown filename.
10. Add source and roundup information.
11. Save each article as an individual Markdown file.
12. Continue processing if an individual URL fails.

The overall design separates the workflow into individual functions, with each function responsible for a specific task. This makes the script easier to understand, maintain, troubleshoot, and modify.

## Testing
The script was tested using a sample HTML input file containing URLs to Python pages.

The test workflow was:
1. Create an HTML file containing article or webpage URLs.
2. Run `python roundup.py`.
3. Select the HTML file when prompted.
4. The script extracted the URLs from the HTML file.
5. The script used Trafilatura to retrieve and extract content from standard webpages.
6. The extracted content was saved as Markdown files in the `Daily Roundups` output directory.
7. The resulting Markdown files were reviewed to confirm that the content and titles were extracted successfully.

This test confirmed that the basic HTML-to-Markdown workflow operates as expected in the local development environment.