
import time
from queue import Queue
from urllib.parse import unquote

from scraper_class import Scraper
import re

class ScrapingManager:

    def __init__(self, wiki_url):
        """
        Initialize ScrapingManager class
        :param wiki_url: URL to main wiki site.
        """
        self.wiki_url = wiki_url

    def auto_count_words(self, starting_phrase, max_depth, waiting_time=0.0):
        """

        :param starting_phrase:
        :param max_depth:
        :param waiting_time:
        :return:
        """
        visited = set()
        waiting_phrases_queue = Queue()
        waiting_phrases_queue.put((starting_phrase, 0))

        while not waiting_phrases_queue.empty():
            [current_phrase, depth_of_current_phrase] = waiting_phrases_queue.get()
            if current_phrase not in visited:
                if depth_of_current_phrase <= max_depth:
                    print(f"Currently processing: {current_phrase}")

                    # Get the data from the article for current_phrase
                    current_scraper = Scraper(self.wiki_url, current_phrase)
                    try:
                        current_scraper.fetch_data()
                    except ConnectionError as e:
                        # If error occurred skip the subtree of this phrase and don't mark the phrase as visited.
                        print(f"Error while fetching the data for {current_phrase}. Skipping this phrase. Error: {e}")
                        continue
                    # If fetching was successful, proceed to process the article for current_phrase
                    visited.add(current_phrase)
                    # Get titles of all articles linked from the current phrase
                    children_phrases = current_scraper.get_children_phrases()
                    if not children_phrases:
                        continue
                    for phrase in children_phrases:
                        if phrase not in visited and depth_of_current_phrase < max_depth:
                            # Add this phrase to the BFS queue
                            waiting_phrases_queue.put([phrase, depth_of_current_phrase + 1])



                    current_scraper.count_words()

                    # Wait for waiting_time seconds
                    if waiting_time > 0:
                        time.sleep(waiting_time)

