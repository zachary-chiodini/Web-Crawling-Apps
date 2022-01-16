from traceback import print_exc

from indeed_crawler import IndeedCrawler

DEBUG = True

# generate or update a 'questionnaire.xlsx file

indeed_crawler = IndeedCrawler()
indeed_crawler.setup_browser()
indeed_crawler.login(
    email='',
    password=''
    )
try:
    indeed_crawler.collect_questionnaire(
        query='',
        update=False
        )
except Exception as e:
    if DEBUG:
        print_exc()
    print(str(e))
