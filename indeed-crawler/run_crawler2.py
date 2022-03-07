from traceback import print_exc
from typing import Dict, List, Tuple

from pandas import DataFrame

from helper_funs import append_df_to_excel
from indeed_crawler import IndeedCrawler

DEBUG = False


class RunCrawler:

    Location, Country = str, str

    def __init__(
            self, email: str, password: str,
            total_number_of_jobs: int,
            queries: List[str],
            places: List[Tuple[Location, Country]],
            default_q_and_a: Dict[str, str],
            negate_jobs_list: List[str] = [],
            negate_companies_list: List[str] = [],
            auto_answer_questions=True,
            manually_fill_out_questions=False):
        self._email = email
        self._password = password
        self._queries = queries
        self._places = places
        self._negate_jobs_list = negate_jobs_list
        self._negate_companies_list = negate_companies_list
        self._total_number_of_jobs = total_number_of_jobs
        self._indeed_crawler = IndeedCrawler(
            debug=DEBUG,
            number_of_jobs=self._jobs_per_query(total_number_of_jobs),
            default_q_and_a=default_q_and_a,
            auto_answer_questions=auto_answer_questions,
            manually_fill_out_questions=manually_fill_out_questions
            )

    def _jobs_per_query(self, total_number_of_jobs: int) -> int:
        jobs_per_query = int(total_number_of_jobs / (len(self._queries) * len(self._places)))
        while (jobs_per_query * len(self._queries) * len(self._places)) < total_number_of_jobs:
            jobs_per_query += 1
        return jobs_per_query

    def start(self) -> None:
        self._indeed_crawler.setup_browser()
        self._indeed_crawler.login(email=self._email, password=self._password)

        abort = False
        last_job_count = 0
        while not abort:
            for region, country in self._places:
                for query in self._queries:
                    try:
                        self._indeed_crawler.search_jobs(
                            query=query,
                            enforce_query=False,  # consider only jobs with the query in the job title
                            job_title_negate_lst=self._negate_jobs_list,
                            company_name_negate_lst=self._negate_companies_list,
                            past_14_days=False,
                            job_type='',  # fulltime
                            min_salary='',
                            enforce_salary=False,  # consider only jobs with salary listed
                            exp_lvl='',  # entry_level, mid_level, #senior_level
                            remote=False,
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
            if (self._indeed_crawler.total_jobs_applied_to >= self._total_number_of_jobs
                    or self._indeed_crawler.total_jobs_applied_to == last_job_count):
                abort = True
            last_job_count = indeed_crawler.total_jobs_applied_to
        return None
