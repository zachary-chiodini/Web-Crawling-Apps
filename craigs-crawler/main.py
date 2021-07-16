from pprint import pprint

from craigs_crawler import CraigsCrawler

# Nationwide search takes some time.
# This may result in a connection error.
craigs_crawler = CraigsCrawler()
results = craigs_crawler.search_cars_and_trucks(
    query='Volvo S80 V8',
    enforce_substrings=['Volvo', 'S80', 'V8']
    )
craigs_crawler.close()
pprint(results, width=4)
