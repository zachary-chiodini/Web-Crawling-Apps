from pprint import pprint
import pandas as pd
import traceback

from indeed_crawler import IndeedCrawler

DEBUG = True

if __name__ == '__main__':
    indeed_crawler = IndeedCrawler(number_of_jobs=1, debug=DEBUG)
    indeed_crawler.setup_browser()
    indeed_crawler.login(
        email='zachary.chiodini@outlook.com',
        password='12Bryant$$'
        )
    try:
        indeed_crawler.search_jobs('game')
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        print(str(e))
    finally:
        results = indeed_crawler.results
        dataframe = pd.DataFrame(data=results)
        print('\n\nApplied to {} jobs.'.format(len(dataframe)), end='\n\n')
        dataframe.to_excel('jobs_submissions.xlsx', sheet_name='jobs', index=False)
