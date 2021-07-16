from re import search

from bs4 import BeautifulSoup

from craigs_crawler import CraigsCrawler

craigs_crawler = CraigsCrawler()  # Nationwide search takes some time.
results = craigs_crawler.search_cars_and_trucks('Volvo S80 V8')
print(results)
