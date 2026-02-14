from scraping_manager_class import ScrapingManager
from analyze_relative_word_frequency import analyze_relative_word_frequency

class WebScraperController:
    BASE_URL = "https://bulbapedia.bulbagarden.net/wiki"

    def __init__(self, args):
        self.args = args
        # WebScraperController is only for online queries
        self.scraping_manager = ScrapingManager(self.BASE_URL,
                                             use_local_html_file_instead=False)

    def execute(self):
        """
        Starts the execution of tasks based on provided parsed arguments.
        :raises ValueError: If required arguments for a specific operation are not provided.
        """
        # 1) --summary
        if self.args.summary:
            self.scraping_manager.get_summary(self.args.summary)

        # 2) --table
        elif self.args.table:
            # --number is required
            if self.args.number is None:
                print("Argument --number is required when using --table. Returning.")
                return
            first_row_is_a_header = False
            if self.args.first_row_is_a_header:
                first_row_is_a_header = True

            self.scraping_manager.get_table(
                table_number=self.args.number,
                phrase=self.args.table,
                first_row_header=first_row_is_a_header
            )

        elif self.args.count_words:
            self.scraping_manager.count_words(self.args.count_words)

        elif self.args.analyze_relative_word_frequency:
            # --mode and --count are required
            if self.args.mode is None:
                print("Argument --mode is required. Returning")
                return
            if self.args.count is None:
                print("Argument --count is required. Returning")
                return
            chart_path=self.args.chart

            analyze_relative_word_frequency(
                mode=self.args.mode,
                count=self.args.count,
                chart_path=chart_path
            )

        elif self.args.auto_count_words:
            # --depth and --wait are required
            if self.args.depth is None:
                print("Argument --depth is required. Returning")
                return
            if self.args.wait is None:
                print("Argument --wait is required. Returning")
                return

            self.scraping_manager.auto_count_words(
                starting_phrase=self.args.auto_count_words,
                max_depth=self.args.depth,
                waiting_time=self.args.wait
            )

        else:
            print("Couldn't recognize any relevant argument.")