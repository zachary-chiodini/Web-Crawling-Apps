from pprint import pprint
import traceback

from indeed_crawler import IndeedCrawler

indeed_crawler = IndeedCrawler()
indeed_crawler.setup_browser()
indeed_crawler.login(
    email='',
    password=''
    )
try:
    indeed_crawler.search_jobs('data')
except Exception as e:
    print(str(e))
finally:
    results = indeed_crawler.results
    print('\n\nApplied to {} jobs.'.format(len(results)), end='\n\n')
    pprint(results, width=4)
