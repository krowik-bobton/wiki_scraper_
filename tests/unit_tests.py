import json
import os
import sys
import unittest

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.wiki_scraper.scraper_class import Scraper
from src.wiki_scraper.scraping_manager_class import load_counter_from_json

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.json_file = "temporary_json_file.json"
        data = {"apple": 5, "banana": 10}

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        self.html_file = "temporary_html_file.html"
        html_content = """
                <html>
                    <body>
                        <div id="mw-content-text" class="mw-body-content">
                            <div class="mw-parser-output">
                                <p>this is an example of a summary.</p>
                                <a href="/wiki/first" title="first">Link 1</a>
                                <a href="/wiki/second" title="second">Link 2</a>
                            </div>
                        </div>
                    </body>
                </html>
                """
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def tearDown(self):
        if os.path.exists(self.json_file):
            os.remove(self.json_file)
        if os.path.exists(self.html_file):
            os.remove(self.html_file)

    def test_fetching_data_from_not_existing_file_throws_exception(self):
        scraper = Scraper(
            wiki_url="not_existing_file.html",
            use_local_html_file_instead=True
        )
        with self.assertRaises(FileNotFoundError):
            scraper.fetch_data_from_local_file()

    def test_load_words_from_a_json_file(self):
        counter = load_counter_from_json(self.json_file)
        self.assertEqual(counter["apple"], 5)
        self.assertEqual(counter["banana"], 10)

    def test_getting_children_links(self):
        scraper = Scraper(
            wiki_url="temporary_html_file.html",
            use_local_html_file_instead=True
        )
        phrases = scraper.get_children_phrases()
        self.assertEqual(len(phrases), 2)
        self.assertEqual(phrases, ["first", "second"])

    def test_getting_the_summary(self):
        scraper = Scraper(
            wiki_url="temporary_html_file.html",
            use_local_html_file_instead=True
        )
        summary = scraper.get_summary()
        self.assertEqual(summary, "this is an example of a summary.")

if __name__ == '__main__':
    unittest.main()
