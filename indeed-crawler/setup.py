"""Generate or update a 'questionnaire.xlsx' file"""

from traceback import print_exc

from indeed_crawler import IndeedCrawler

DEBUG = False


indeed_crawler = IndeedCrawler()
indeed_crawler.setup_browser()
indeed_crawler.login(
    email='@outlook.com',
    password='MY_P4$$W0RD123'
    )
try:
    indeed_crawler.collect_questionnaire(
        query='Compliance Analyst',
        country='united states',
        update=False
        )
except Exception as e:
    if DEBUG:
        print_exc()
    else:
        print(str(e))
