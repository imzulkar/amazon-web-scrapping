import sys, os

from scrapper.lib.search_scraper import SearchScraper


if __name__ == "__main__":
    try:
        scraper = SearchScraper()
        scraper.init_scrapper()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
