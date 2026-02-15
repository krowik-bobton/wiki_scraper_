import json
import os
import time
from collections import Counter
from queue import Queue
from scraper_class import Scraper


def save_counter_to_json(counter, json_path):
    """
    Saves a Counter object to a JSON file.
    :param counter: The Counter object to save.
    :param json_path: Path to the JSON file.
    """
    try:
        with open(json_path, 'w', encoding='utf-8') as file:
            # ensure_ascii=False is crucial for dealing with non-English
            # characters.
            # indent=4 makes a file easily readable.
            json.dump(counter, file, indent=4, ensure_ascii=False)
    except IOError as e:
        raise IOError(f"Error while writing to {json_path}: {e}")


def load_counter_from_json(json_path):
    """
    Loads a Counter object from a JSON file.
    :param json_path: Path to the JSON file.
    :return: A Counter object.
    """
    counter = Counter()
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                counter.update(old_data)
        except (json.JSONDecodeError, ValueError):
            # If a JSON file is empty or damaged, ignore its content
            pass
    return counter


class ScrapingManager:
    # Path to a JSON file which contains numbers of occurrences for words
    # encountered when running count_words
    JSON_PATH = './word-counts.json'

    def __init__(self, wiki_url, use_local_html_file_instead=False):
        """
        Initialize ScrapingManager class
        :param wiki_url: URL to the main wiki site or path to a local file.
        :param use_local_html_file_instead: Whether to use a local HTML file.
                                            Default=False
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
        total_counts = load_counter_from_json(self.JSON_PATH)

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

        # End of the BFS. Update JSON files
        save_counter_to_json(total_counts, self.JSON_PATH)

    def count_words(self, phrase=None):
        """
        Counts the occurrences of words in the specified phrase or in a locally
        provided HTML file, updates or creates the JSON file with the counter.

        :param phrase: The phrase to count words from, or None if using a local
            HTML file instead.
        :type phrase: str or None
        """
        if not self.use_local_file and phrase is None:
            raise ValueError("Phrase can only be None when "
                             "use_local_html_file_instead is set to True")
        scraper = Scraper(self.wiki_url, phrase, self.use_local_file)

        total_counter = load_counter_from_json(self.JSON_PATH)
            
        current_counter = scraper.count_words()
        
        if not current_counter:
            return
        total_counter.update(current_counter)
        save_counter_to_json(total_counter, self.JSON_PATH)

    def get_table(self, table_number, phrase=None, save_as=None, first_row_header=False):
        """
        Extracts a specified table from a webpage or local file using a
        scraper, saves it as a CSV file, and returns df of occurrences of
        each unique value found in the table (excluding the headers).
        The first column is always treated as a header of rows.
        :param table_number: The index of the table to extract. The index is
                             zero-based.
        :type table_number: int
        :param phrase: A string used to identify and name the CSV file.
                       (If using the local HTML file instead is True, this
                       value is ignored)
        :type phrase: str
        :param save_as: Base for the CSV filename. Relevant only if using
                        the local HTML file instead of connecting with webpage.
        :type save_as: str
        :param first_row_header: Indicates whether the first row of the table
                                 should be used as column headers.
        :type first_row_header: bool
        :return: DataFrame with wanted table or None if the table wasn't found
        :type: DataFrame | None
        """
        if self.use_local_file:
            # offline mode
            # phrase is not required (can and should be None)
            # save_as is required
            if not save_as:
                raise ValueError("When using local file, save_as argument is "
                                 "required to name the output CSV.")
            if phrase is not None:
                print(f"Warning, provided phrase: {phrase} for using the"
                      f" local file, ignoring this value. ")
            # Phrase to pass to the Scraper constructor
            phrase_for_scraper = None
            # Name of the CSV file that will be created/updated
            csv_name = save_as

        else:
            # online mode
            # phrase is required
            # (it will also serve as a CSV name)
            # save_as is ignored
            if not phrase:
                raise ValueError("In online mode phrase is "
                                 "required to find the article.")

            if save_as is not None:
                print(f"Warning, provided save_as: {save_as}'"
                      f" is ignored in online mode.")

            phrase_for_scraper = phrase
            csv_name = phrase

        my_scraper = Scraper(self.wiki_url, phrase_for_scraper, self.use_local_file)
        df = my_scraper.get_table(table_number, first_row_header)
        if df is not None:
            # Write df into csv file
            csv_name = csv_name.replace(" ", "_")
            try:
                df.to_csv(f"{csv_name}.csv", index=True)
            except Exception as e:
                raise Exception(f"Couldn't save table to {csv_name}.csv. Error : {e}")
        # Can be None if df is None
        return df

    def get_summary(self, phrase=None):
        """
        Returns the first paragraph from a webpage or local HTML file.
        :param phrase: Title of the Wiki article. Is ignored and can
                       be None if using the local html file.
        :return: summary text
        :rtype: str | None
        """
        if not self.use_local_file and phrase is None:
            raise ValueError("Phrase can only be None when "
                             "use_local_html_file_instead is set to True")
        scraper = Scraper(self.wiki_url, phrase, self.use_local_file)
        return scraper.get_summary()



