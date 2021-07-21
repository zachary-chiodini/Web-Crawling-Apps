from pprint import pprint
import traceback

from indeed_crawler import IndeedCrawler

DEBUG = True

if __name__ == '__main__':

    indeed_crawler = IndeedCrawler(debug=DEBUG)
    indeed_crawler.setup_browser()
    indeed_crawler.login(
        email='zachary.chiodini@outlook.com',
        password='12Bryant$$'
        )
    try:
        indeed_crawler.search_jobs('poopy ding dong')
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        print(str(e))
    finally:
        results = indeed_crawler.results
        pprint(results, width=4)
        print('\n\nApplied to {} jobs.'.format(len(results)), end='\n\n')
