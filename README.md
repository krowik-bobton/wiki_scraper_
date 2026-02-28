# Wiki Scraper

A Python-based command-line tool designed for scraping content from [Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Main_Page) (a Pokémon encyclopedia) [**Creative Commons Attribution-NonCommercial-ShareAlike 2.5 License**]. This tool allows you to extract article summaries, process tables, count word frequencies across linked articles, and analyze how word usage in these articles compares to general language trends. 
**Created for educational purposes only.**

## Installation

1. Clone the repository or download the source code.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The tool is executed through `wiki_scraper.py`. It features several mutually exclusive modes of operation.

### General Command Structure
```bash
python wiki_scraper.py <MODE_ARGUMENT> [OPTIONS]
```

---

## Operating Modes

### 1. Summary Mode (`--summary`)
Loads and prints the first paragraph of the specified Bulbapedia article.

- **Usage:** `--summary "ARTICLE_TITLE"`
- **Example:**
  ```bash
  python wiki_scraper.py --summary "Pikachu"
  ```

### 2. Table Extraction Mode (`--table`)
Extracts a specific table from an article, saves it to a CSV file, and calculates the occurrences of each word/value within that table.

- **Usage:** `--table "ARTICLE_TITLE" --number <TABLE_INDEX>`
- **Required Arguments:**
  - `--table`: The title of the article.
  - `--number`: The index of the table to extract (0 for the first table, 1 for the second, etc.).
- **Optional Arguments:**
  - `--first-row-is-a-header`: If present, treats the first row of the table as column headers.
- **Example:**
  ```bash
  python wiki_scraper.py --table "List of Pokémon by base stats (Generation I)" --number 0 --first-row-is-a-header
  ```

### 3. Word Counting Mode (`--count-words`)
Counts the frequency of all words in a single article and updates a local JSON file (`data/word-counts.json`) with the results.

- **Usage:** `--count-words "ARTICLE_TITLE"`
- **Example:**
  ```bash
  python wiki_scraper.py --count-words "Bulbasaur"
  ```

### 4. Automatic Linked Word Counting (`--auto-count-words`)
A recursive scraper that starts from a given article, counts its words, and then follows links to other articles up to a specified depth. This is useful for building a large dataset of word frequencies from a specific topic area.

- **Usage:** `--auto-count-words "ARTICLE_TITLE" --depth <INT> --wait <SECONDS>`
- **Required Arguments:**
  - `--auto-count-words`: The starting article title.
  - `--depth`: How many levels of links to follow (0 = only the starting page, 1 = starting page + all linked pages, etc.).
  - `--wait`: Number of seconds to wait between requests to be respectful to the server (please provide at least 5 seconds delay (as is indicated in the robots.txt file of Bulbapedia))
- **Example:**
  ```bash
  python wiki_scraper.py --auto-count-words "Fire-type" --depth 1 --wait 6
  ```
### 5. Relative Word Frequency Analysis (`--analyze-relative-word-frequency`)
Analyzes and compares the word frequencies stored in your local JSON file against the general frequency of those words in the English language (using the `wordfreq` library).

- **Usage:** `--analyze-relative-word-frequency --mode <language|article> --count <NUMBER>`
- **Required Arguments:**
  - `--analyze-relative-word-frequency`: Triggers the analysis.
  - `--mode`: 
    - `language`: Focuses on the most common words in the English language and checks their frequency in your scraped data.
    - `article`: Focuses on the most common words in your scraped data and compares them to their general language frequency.
  - `--count`: The number of top words to include in the analysis.
- **Optional Arguments:**
  - `--chart <PATH>`: Saves a bar chart (PNG) comparing the frequencies to the specified path.
- **Example:**
  ```bash
  python wiki_scraper.py --analyze-relative-word-frequency --mode article --count 20 --chart frequency_chart.png
  ```
  
---

## Functional classes and files

- **wiki_scraper.py** Users can interact with this file through command line.
- **Scraper class:** implemented in `src/wiki_scraper/scraper_class.py`. Handles scraper logic for the single article on the Wiki. Can perform offline operations on HTML files.
- **ScrapingManager class:** implemented in `src/wiki_scraper/scraping_manager_class.py`. More high-level version of Scraper. Creates Scrapers and gets results from their methods and writes them to the desired files, handles crawler logic etc. Can perform offline operations on HTML files as well.
- **src/wiki_scraper/analyze_relative_word_frequency.py:** Contains functions responsible for analyzing data (creating charts and dataframes with comparisions of words frequencies between counted articles and English language).
- **WebScraperController class:** implemented in `src/wiki_scraper/web_scraper_controller.py`. Takes appropriate actions depending on arguments provided (most high-level module of the project)

---

## Data Storage

- **Word Counts:** Stored in `data/word-counts.json`. This file is updated whenever `--count-words` or `--auto-count-words` is used.
- **Tables:** When using `--table`, extracted data is saved to a CSV file in the `data/` directory (named based on the article title).
- **Charts:** When using `--analyze-relative-word-frequency` with `--chart`, the resulting image is saved to the specified path.

---
## Credits
* **Bulbapedia Data:** The data extracted from [Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/Main_Page) is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 2.5 License**.
* **Source Code:** The code in this repository is licensed under the **MIT License**.
