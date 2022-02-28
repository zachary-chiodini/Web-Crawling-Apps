from traceback import print_exc
from typing import List, Tuple

from pandas import DataFrame

from helper_funs import append_df_to_excel
from indeed_crawler import IndeedCrawler

TOTAL_NUMBER_OF_JOBS = 200
DEBUG = True


queries: List[str] = [
]

Location, Country = str, str
places: List[Tuple[Location, Country]] = [
    ('remote', 'united states')
]

negate_jobs: List[str] = [
]

negate_comps: List[str] = [
]

number_of_jobs = int(TOTAL_NUMBER_OF_JOBS/(len(queries) * len(places)))

while (number_of_jobs * len(queries) * len(places)) < TOTAL_NUMBER_OF_JOBS:
    number_of_jobs += 1

indeed_crawler = IndeedCrawler(
    number_of_jobs=number_of_jobs,
    debug=False,
    auto_answer_questions=True,
    manually_fill_out_questions=False
    )

indeed_crawler.setup_browser()
indeed_crawler.login(
    email='',
    password=''
    )

abort = False
for region, country in places:
    for query in queries:
        try:
            indeed_crawler.search_jobs(
                query=query,
                enforce_query=False,  # consider only jobs with the query in the job title
                job_title_negate_lst=negate_jobs,
                company_name_negate_lst=negate_comps,
                past_14_days=False,
                job_type='',  # fulltime
                min_salary='',
                enforce_salary=False,  # consider only jobs with salary listed
                exp_lvl='',  # entry_level, mid_level, #senior_level
                remote='',
                temp_remote=False,
                country=country,
                location=region,
                radius=''
                )
        except Exception as e:
            if DEBUG:
                print_exc()
            else:
                print(str(e))
        finally:
            dataframe = DataFrame(data=indeed_crawler.results)
            if not dataframe.empty:
                append_df_to_excel(dataframe, 'submissions.xlsx',
                                   sheet_name='jobs', index=False)
                indeed_crawler.reset_results()
