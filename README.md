# Web Digger (version 26.06.2024)

## Overview
This PyQt5 Web Digger is a simple yet powerful tool designed to extract URLs from a specified starting web page. It recursively or indexing gathers all unique URLs from the initial page and any connected pages. The GUI allows users to input a URL, start the scraping process, view ongoing status updates, and export the collected URLs to a text file named according to the domain of the initial URL.

## Features
- **User-Friendly GUI**: Provides an easy-to-use graphical interface to input URLs, execute/cancel the scraping process, and export results.
- **Recursive Scraping**: Capable of deep-scraping websites by following links to subsequent pages.
- **Indexing Scraping**: Capable of indexing-scraping websites by following pagination links.
- **Real-Time Updates**: Displays real-time status of the scraping process, including the number of URLs saved and remaining.
- **Export Functionality**: Exports the collected URLs to a `.txt` file, organizing them by their domain.

## Prerequisites
Before you can run the web scraper, ensure you have the following installed:
- Python 3.x
- PyQt5
- BeautifulSoup4
- requests

You can install the necessary Python packages with pip:

```bash
pip install -r requirements.txt
```

## Installation

```bash
git clone https://github.com/locphan201/web-digger.git
cd web-digger
```

## Usage

To start the web digger, run the following command from the terminal:

```bash
python app.py
```

Once the application launches:

1. Choose the type (Recursive/Indexing) to scrape
2. Enter the URL you want to scrape in the URL input field.
3. Click the `Execute` button to start the scraping process.
4. Observe the URLs being processed in real-time and view the status updates.
5. Click the `Export` button to save the collected URLs to a text file.
6. If needed, use the `Cancel` button to stop the scraping process prematurely.

## Configuration

The application allows for some configuration:

- Output Directory: Set the output directory in the script for where the URLs should be saved.

## Contributing

Contributions to the Recursive Web Digger are welcomed. Please ensure that your pull requests are well-documented.