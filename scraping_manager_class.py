import json
import os
import time
from collections import Counter
from queue import Queue
import pandas as pd
from scraper_class import Scraper

class ScrapingManager:

    def __init__(self, wiki_url, use_local_html_file_instead=False):
        """
        Initialize ScrapingManager class
        :param wiki_url: URL to the main wiki site or path to a local file.
        :param use_local_html_file_instead: Whether to use a local HTML file.
        """
        self.wiki_url = wiki_url
        self.use_local_file = use_local_html_file_instead

    def auto_count_words(self, starting_phrase, max_depth, waiting_time=0.0):
        """
        Automatically traverses through linked articles starting from the
        given phrase, counts words in each article and processes linked
        articles up to the maximum depth. Creates or updates JSON file with
        counted values.

        :param starting_phrase: The initial phrase to start processing from.
        :type starting_phrase: str
        :param max_depth: The maximum depth to traverse from the starting
                          article.
        :type max_depth: int
        :param waiting_time: number of seconds to wait between processing
                            articles.
        :type waiting_time: float
        :return: None
        """
        if self.use_local_file:
            raise ValueError("Can't use auto_count_words on a single local "
                             "file!")

        visited = set()
        waiting_phrases_queue = Queue()
        waiting_phrases_queue.put((starting_phrase, 0))

        # Load the initial content of the JSON file and update it as the BFS
        # goes. At the end of this function load new content only once to the
        # JSON file.
        json_path = './word-counts.json'
        initial_json_content = Counter()
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    initial_json_content.update(old_data)
            except (json.JSONDecodeError, ValueError):
                # If a JSON file is empty or damaged, ignore its content and
                # override it with new values.
                pass
        # This value will be updated for each processed article
        total_counts = initial_json_content

        while not waiting_phrases_queue.empty():
            (current_phrase, depth_of_current_phrase) = \
                waiting_phrases_queue.get()
            if current_phrase not in visited:
                if depth_of_current_phrase <= max_depth:
                    print(f"Currently processing: {current_phrase}")

                    # Get the data from the article for current_phrase
                    current_scraper = Scraper(self.wiki_url, current_phrase)
                    try:
                        current_scraper.fetch_data()
                    except ConnectionError as e:
                        # If error occurred skip the subtree of this phrase
                        # and don't mark the phrase as visited.
                        print(f"Error while fetching the data for "
                              f"{current_phrase}. Skipping this phrase. "
                              f"Error: {e}")
                        continue
                    # If fetching was successful, proceed to process the
                    # article for current_phrase
                    visited.add(current_phrase)
                    # Get titles of all articles linked from the current phrase
                    children_phrases = current_scraper.get_children_phrases()
                    if not children_phrases:
                        continue
                    for phrase in children_phrases:
                        if phrase not in visited and \
                           depth_of_current_phrase < max_depth:
                            # Add this phrase to the BFS queue
                            waiting_phrases_queue.put(
                                (phrase, depth_of_current_phrase + 1)
                            )

                    # Get counter of current article
                    current_counts = current_scraper.count_words()
                    if not current_counts:
                        continue

                    # Combine two Counters
                    total_counts.update(current_counts)

                    # Wait for waiting_time seconds
                    if waiting_time > 0:
                        time.sleep(waiting_time)

        # End of the BFS. Check JSON files
        try:
            with open(json_path, 'w', encoding='utf-8') as file:
                # ensure_ascii=False is crucial for dealing with non-English
                # characters.
                # indent=4 makes a file easily readable.
                json.dump(total_counts, file, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error while writing to {json_path}: {e}")

    def get_table(self, phrase, table_number, first_row_header=False):
        """
        Extracts a specified table from a webpage or local file using a
        scraper, saves it as a CSV file, and prints numbers of occurrences of
        each unique value found in the table (excluding the headers)
        :param phrase: A string used to identify and name the CSV file. All
                       spaces in the string are replaced with underscores.
        :type phrase: str
        :param table_number: The index of the table to extract. The index is
                             zero-based.
        :type table_number: int
        :param first_row_header: Indicates whether the first row of the table
                                 should be used as column headers.
        :type first_row_header: bool
        """
        my_scraper = Scraper(self.wiki_url, phrase, self.use_local_file)
        df = my_scraper.get_table(table_number, first_row_header)
        if df is not None:
            # Write df into csv file
            phrase = phrase.replace(" ", "_")
            try:
                df.to_csv(f"{phrase}.csv", index=True)
            except Exception as e:
                print(f"Couldn't save table to {phrase}.csv. Error : {e}")

            print("--- Numbers of each values in a table ---")
            # df.values converts pandas table into a numpy matrix
            # (without headers)
            # .flatten(), flatten this matrix into a single list of cells.
            cells_list = df.values.flatten()
            counts = pd.Series(cells_list).value_counts()
            results_table = counts.to_frame(name="Number of occurrences")
            print(results_table)
        else:
            print("Table couldn't be loaded")


