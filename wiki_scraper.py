import argparse
from src.wiki_scraper.web_scraper_controller_class import WebScraperController


def parse_arguments():
    """
    Parses command-line arguments for various operations.
    :return: Parsed arguments including options and their values
    :rtype: argparse.Namespace
    :raises SystemExit: If invalid arguments are given or required options are missing.
    """

    parser = argparse.ArgumentParser()

    # Mutually exclusive group - user must choose exactly one argument
    # from this group
    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        "--summary",
        metavar="ARTICLE TITLE",
        type=str,
        help="Load and print first paragraph of an article."
    )

    action_group.add_argument(
        "--table",
        metavar="ARTICLE TITLE",
        type=str,
        help="Load the table from an article to the CSV file "
             "and print numbers of occurrences of each word in the table"
             " (requires --number)"
    )

    action_group.add_argument(
        "--count-words",
        metavar="ARTICLE TITLE",
        type=str,
        help="Count words in one article and update JSON file with values."
    )

    action_group.add_argument(
        "--auto-count-words",
        metavar="ARTICLE TITLE",
        type=str,
        help="Count words in all linked articles up to provided depth"
             " (requires --depth)."
    )

    action_group.add_argument(
        "--analyze-relative-word-frequency",
        action="store_true",
        help="Analyze frequencies of words in the articles "
             " vs in the language (requires --mode and --count)"
             " (frequencies of words in the articles are taken from a JSON file with values."
    )

    # Arguments for --table
    parser.add_argument(
        "--number",
        metavar="NUMBER OF TABLE",
        type=int,
        default=None,
        help="Number of table to load (required for --table)."
    )
    parser.add_argument(
        "--first-row-is-a-header",
        action="store_true",
        help="Treat the first row of a table as a header."
    )

    # Arguments for --auto_count_words
    parser.add_argument(
        "--depth",
        metavar="INTEGER VALUE OF DEPTH",
        type=int,
        default=None,
        help="Depth of the searching tree"
             " (required for --auto-count-words)"
    )
    parser.add_argument(
        "--wait",
        metavar="NUMBER OF SECONDS",
        type=float,
        default=None,
        help="Time of waiting (in seconds) between processing sites"
             " (required for --auto-count-words)"
    )

    # Arguments for --analyze-relative-word-frequency
    parser.add_argument(
        "--mode",
        choices=["language", "article"],
        default=None,
        help="Mode of analyze (required for the analyze)."
             " required for --analyze-relative-word-frequency"
    )
    parser.add_argument(
        "--count",
        metavar="NUMBER OF TOP WORDS",
        type=int,
        default=None,
        help="Number of top words to analyze (required for the analyze)"
             " required for --analyze-relative-word-frequency"
    )
    parser.add_argument(
        "--chart",
        metavar="PATH",
        type=str,
        default=None,
        help="Path for saving the chart (optional)"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    controller = WebScraperController(args)
    controller.execute()
