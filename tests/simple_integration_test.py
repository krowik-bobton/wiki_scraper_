import os
import sys

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.wiki_scraper.scraping_manager_class import ScrapingManager

# Local, temporary html file
html_file = "temporary_html_file.html"
html_content = """
        <html>
            <body>
                <div class="mw-parser-output">
                    <p>Team Rocket (Japanese: ロケット団 Rocket-dan, literally Rocket Gang) is a villainous team in pursuit of evil and the exploitation of Pokémon. The organization is based in the Kanto and Johto regions, with a small outpost in the Sevii Islands.</p>   
                    <a href="/wiki/first" title="first">Link 1</a>
                    <a href="/wiki/second" title="second">Link 2</a>
                    <a href="/wiki/third_link_no_title">Link 3</a>
                </div>
            </body>
        </html>
        """


def create_temporary_html():
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

def remove_temporary_html():
    if os.path.exists(html_file):
        os.remove(html_file)

def summary_test_for_team_rocket():
    """
    Test --summary functionality with a local HTML file.
    """
    create_temporary_html()
    try:
        scraping_manager = ScrapingManager(html_file, True)
        summary=scraping_manager.get_summary()
        assert summary.startswith("Team Rocket"), \
            f"Summary should start with 'Team Rocket', got: {summary}"
        assert summary.endswith("outpost in the Sevii Islands."), \
            f"Summary should end with 'outpost in the Sevil Islands.', got: {summary}"

        print("Integration test PASSED!")
        return True

    except AssertionError as e:
        print(f"Test FAILED: {e}")
        return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        remove_temporary_html()

if __name__ == "__main__":
    success = summary_test_for_team_rocket()
    sys.exit(0 if success else 1)