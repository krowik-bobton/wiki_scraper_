
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

                    # Get the data from article for current_phrase
                    current_scraper = Scraper(self.wiki_url, current_phrase)
                    try:
                        current_scraper.fetch_data()
                    except ConnectionError as e:
                        # If error occurred skip the subtree of this phrase and don't mark the phrase as visited.
                        print(f"Error while fetching the data for {current_phrase}. Skipping this phrase. Error: {e}")
                        continue
                    # If fetching was successful, proceed to process the article for current_phrase
                    visited.add(current_phrase)
                    # Extract the main div of the article
                    content = current_scraper.soup.find('div', class_='mw-parser-output')
                    if not content:
                        return

                    # Get all the links to other articles. We search for links which href starts with '/wiki/'
                    for link in content.find_all('a', href=re.compile('^/wiki/')):
                        href = link['href']
                        # Get the title of the article that the link leads to
                        # Some titles are percent encoded (e.g. Pokémon is encoded as Pok%C3%A9mon), and the original
                        # title can be decoded using the unquote function.
                        link_title = href.removeprefix('/wiki/')
                        link_title = unquote(link_title)
                        link_title = link_title.replace('_', ' ')
                        # Links to the actual wiki sites have a title parameter equal to link_title.
                        # If there's no such title for the link, it means that it isn't a relevant link (i.e., image)
                        if link.get('title'):
                            if link.get('title') == link_title:
                                if link_title not in visited and depth_of_current_phrase < max_depth:
                                    # Add this phrase to the BFS queue
                                    waiting_phrases_queue.put([link_title, depth_of_current_phrase + 1])

                    current_scraper.count_words()

                    # Wait for waiting_time seconds
                    if waiting_time > 0:
                        time.sleep(waiting_time)


