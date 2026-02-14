import io
import os
import re
from collections import Counter
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
import pandas as pd


class Scraper:
    """
    Class for processing single page/file for provided phrase
    """

    def __init__(self, wiki_url, phrase, use_local_html_file_instead=False):
        """
        :param wiki_url: URL link to the wiki (or path to a local file)
                         which will be scraped from
        :type wiki_url: any

        :param phrase: Title of the wiki article page which will be scraped
        :type phrase: str

        :param use_local_html_file_instead: True/False if wiki_url is a path to
                                            a single local HTML file.
        :type use_local_html_file_instead: bool
        """
        # Check phrase
        if not phrase or phrase == '':
            raise ValueError(f"Invalid phrase: {phrase}")
        if not wiki_url:
            raise ValueError("Wiki URL is None!")
        if use_local_html_file_instead:
            if not os.path.exists(wiki_url):
                raise FileNotFoundError(f"File {wiki_url} doesn't exist")
        self.phrase = phrase
        self.base_url = wiki_url
        self.read_local_file = use_local_html_file_instead  # Bool value
        self.soup = None  # Page content will be loaded as a BeautifulSoup inst

        if use_local_html_file_instead:
            self.exact_url = wiki_url
        else:
            self.exact_url = f"{wiki_url}/{phrase.replace(' ', '_')}"

    def get_children_phrases(self):
        """
        Extracts and returns all relevant child phrases from the parsed HTML
        content.
        :return: A list of strings, where each string represents the title of
            an article linked from the current page, decoded and formatted.
            Returns `None` if the required container is not present in the
            HTML content.
        :rtype: list[str] | None
        """
        content = self.soup.find('div', class_='mw-parser-output')
        if not content:
            return None
        result_phrases = []
        # Get all the links to other articles. We search for links which href
        # starts with '/wiki/'
        for link in content.find_all('a', href=re.compile('^/wiki/')):
            href = link['href']
            # Get the title of the article that the link leads to
            # Some titles are percent encoded (e.g. Pokémon is encoded as
            # Pok%C3%A9mon), and the original title can be decoded using the
            # unquote function.
            link_title = href.removeprefix('/wiki/')
            link_title = unquote(link_title)
            link_title = link_title.replace('_', ' ')
            # Links to the actual wiki sites have a title parameter equal to
            # link_title. If there's no such title for the link, it means that
            # it isn't a relevant link (i.e., image)
            if link.get('title'):
                if link.get('title') == link_title:
                    result_phrases.append(link_title)
        return result_phrases

    def fetch_data_from_wiki(self):
        """
        Fetch data from Wiki page with title which is equal to Scraper's phrase
        :return: True/False depending on the success of fetching the data
        """

        headers = {"User-Agent": "John Pork"}
        try:
            response = requests.get(self.exact_url, headers=headers)
            # Check if such site exists (404 - Not Found, 200 - OK)
            if response.status_code == 404:
                print(f"{self.phrase} not found on {self.base_url}")
                return False

            # If an error occurred, return HTTPError object
            response.raise_for_status()

            # Save BeautifulSoup object
            self.soup = BeautifulSoup(response.content, "html.parser")

            return True

        except Exception as e:
            print(f"Error while fetching the data: {e}")
            return False

    def fetch_data_from_local_file(self):
        """
        Fetch data from the local HTML file
        :return: True/False depending on the success of fetching the data
        """
        try:
            with open(self.exact_url, 'r', encoding='utf-8') as f:
                self.soup = BeautifulSoup(f, "html.parser")
        except Exception as e:
            print(f"Error {e} while accessing the file: {self.exact_url}")
            return False
        return True

    def fetch_data(self):
        """
        Fetches data from either a local file or a remote URL depending on the
        `read_local_file` attribute. If `read_local_file` is set to True, it
        tries to fetch data from a local file using the
        `fetch_data_from_local_file` method. Otherwise, data is fetched from a
        remote URL using the `fetch_data_from_wiki` method. If there was an
        error, ConnectionError is raised.

        :return: `True` if data is successfully fetched and the soup object is
                 initialized.
        :rtype: bool
        :raises ConnectionError: If data loading from local file or remote URL
            fails, or if the soup object cannot be initialized.
        """
        if self.read_local_file:
            if not self.fetch_data_from_local_file():
                raise ConnectionError(f"Failed to load data from local file: "
                                      f"{self.base_url}")
        else:
            if not self.fetch_data_from_wiki():
                raise ConnectionError(f"Failed to load data from "
                                      f"{self.exact_url}")
        if not self.soup:
            raise ConnectionError(f"Couldn't load soup from {self.exact_url}")
        return True

    def get_summary(self):
        """
        Gets the first paragraph of an article corresponding with Scraper's
        phrase.
        :return: String value of the first paragraph's text or None if nothing
                 was found.
        """
        if not self.soup:
            self.fetch_data()

        # Get content of the div with "mw-parser-output" label
        content = self.soup.find('div', class_='mw-parser-output')

        if not content:
            return None

        # Find paragraphs (<p><\p>) from the previously read div
        # recursive=False means we won't enter recursively deeper
        # (i.e. when <div> <p> <p> <\p> <\p> <\div>, only on p will be found)
        paragraphs = (content.find_all('p', recursive=False))

        for p in paragraphs:
            text = p.get_text().strip()
            if text:
                # read text from paragraphs until the first non-null appears
                return text
        return None

    def get_table(self, table_number, first_row_header=False):
        """
        Extracts a specific HTML table from a processed article and converts it
        into a pandas DataFrame. Supports optionally treating the first row of
        the table as the header for the resulting DataFrame.

        :param table_number: Specifies the table index to extract (1-based
                             index).
        :type table_number: int

        :param first_row_header: Indicates whether the first row of the table
            should be used as the DataFrame's header. If True, the first row
            is used as column names; otherwise, no column headers are
            assigned. Default is False.
        :type first_row_header: bool

        :return: A pandas DataFrame object containing the desired table's data
            if successfully extracted, or None if the table is unavailable or
            an error occurs during the extraction.
        :rtype: pandas.DataFrame or None
        """

        if not self.soup:
            self.fetch_data()

        # Get all tables from BeautifulSoup
        tables = self.soup.find_all('table')

        if len(tables) < table_number:
            print(f"Asked for {table_number} table, but only {len(tables)} "
                  f"are available.")
            return None

        target_table = tables[table_number - 1]  # table_number is indexed from 1

        # Use pandas.read_html( ... ) to read from target_table
        try:
            header_arg = 0 if first_row_header else None
            html_string = str(target_table)  # convert content into a string
            html_file = io.StringIO(html_string)
            # if a header parameter is x, then xth row becomes a columns
            # header (if header == None, then there's no columns header)
            # index_col=0 treats the first column as a row header
            dfs = pd.read_html(html_file, header=header_arg, index_col=0)
            # dfs now holds objects of pandas.DataFrame type.
            if dfs:
                return dfs[0]
            else:
                return None
        except Exception as e:
            print(f"Error while reading {table_number} table from "
                  f"{self.exact_url}: {e}")
        return None

    def count_words(self):
        """
        Counts the frequency of each word in the provided article (skips
        common page elements like a menu etc.)
        :return: Counter of how many times each word occurred in the article
                 or None if couldn't find content.
        :rtype: Counter | None
        """

        if not self.soup:
            self.fetch_data()

        # Count words from both the main article content and title
        title_soup = self.soup.find("h1",
                                    class_="firstHeading mw-first-heading")
        if title_soup:
            title_text = title_soup.get_text().strip()
            if not title_text:
                title_text = ""
        else:
            title_text = ""

        main_soup = self.soup.find("div", class_="mw-parser-output")
        if not main_soup:
            print("Content not found.")
            return None
        main_text = main_soup.get_text().strip()
        # Add title text to the main text and convert resulting text to lower
        main_text = (main_text + " " + title_text).lower()

        # split main_text into a list of processed words
        raw_words = main_text.split()
        # List of all processed words of the current article to be counted
        words = []
        for word in raw_words:
            # Remove punctuation and irrelevant characters from the edges.
            # Words having non-letter characters inside (without any blank
            # space around non-letter character) are treated as a single word
            # (e.g. "II/IV" is considered one word: "II/IV", "word." is
            # processed into "word")
            cleaned = re.sub(r'^\W+|\W+$', '', word, flags=re.UNICODE)
            if cleaned:  # Only add non-empty words
                words.append(cleaned)

        current_counts = Counter(words)
        return current_counts
