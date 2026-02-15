import sys
from scraping_manager_class import ScrapingManager

def summary_test_for_team_rocket():
    """
    Test --summary functionality with a local HTML file.
    """
    try:
        scraping_manager = ScrapingManager("Team_Rocket_test.html", True)
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

if __name__ == "__main__":
    success = summary_test_for_team_rocket()
    sys.exit(0 if success else 1)