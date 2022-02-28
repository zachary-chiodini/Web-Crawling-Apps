"""Generate or update a 'questionnaire.xlsx' file"""

from traceback import print_exc

from indeed_crawler import IndeedCrawler

DEBUG = True


indeed_crawler = IndeedCrawler()
indeed_crawler.setup_browser()
indeed_crawler.login(
    email='',
    password=''
    )
try:
    indeed_crawler.collect_questionnaire(
        query='',
        country='united states',
        update=False
        )
except Exception as e:
    if DEBUG:
        print_exc()
    else:
        print(str(e))
