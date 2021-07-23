from os import path
from re import search
from traceback import print_exc
from typing import Callable

from bs4 import BeautifulSoup
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (
    ElementClickInterceptedException, ElementNotInteractableException,
    StaleElementReferenceException, TimeoutException)


class IndeedCrawler:
    def __init__(
            self, number_of_jobs: int, headless_mode=False,
            driver_path='driver', debug=False,
            manually_fill_out_questions=False
            ) -> None:
        self.results = {
            'Title': [],
            'Company': [],
            'Location': [],
            'Salary': [],
            'URL': []
            }
        self._browser = None
        self._number_of_jobs = number_of_jobs
        self._headless_mode = headless_mode
        self._driver_path = driver_path
        self._main_window = ''
        self._debug = debug
        self._manually_fill_out_question = manually_fill_out_questions
        self._cache = set()
        if path.exists('cache.txt'):
            with open('cache.txt', 'r') as file:
                for line in file:
                    self._cache.add(line.strip())
        else:
            with open('cache.txt', 'w') as file:
                pass

    def _setup_real_browser(self) -> None:
        kwargs = {
            'executable_path': path.join(self._driver_path, 'geckodriver.exe'),
            'service_log_path': 'NUL'
            }
        self._browser = Firefox(**kwargs)
        return None

    def _setup_headless_browser(self) -> None:
        my_profile = FirefoxProfile()
        my_profile.set_preference('permissions.default.image', 2)
        settings = [
            '-headless', '-disable-gpu',
            '-ignore-certificate-errors',
            '-disable-extensions', '-no-sandbox',
            '-disable-dev-shm-usage'
            ]
        my_options = Options()
        for argument in settings:
            my_options.add_argument(argument)
        kwargs = {
            'executable_path': path.join(
                self._driver_path, 'geckodriver.exe'),
            'service_log_path': 'NUL',
            'firefox_profile': my_profile,
            'options': my_options
            }
        self._browser = Firefox(**kwargs)
        return None

    def setup_browser(self) -> None:
        if self._headless_mode:
            self._setup_headless_browser()
        else:
            self._setup_real_browser()
        return None

    def login(self, email: str, password: str) -> None:
        self._browser.get('https://secure.indeed.com/account/login')
        self._browser.find_element_by_xpath(
            '//input[@type="email"]'
            ).send_keys(email)
        self._browser.find_element_by_xpath(
            '//input[@type="password"]'
            ).send_keys(password)
        self._browser.find_element_by_xpath(
            '//input[@type="password"]'
            ).send_keys(Keys.RETURN)
        try:
            WebDriverWait(self._browser, 10).until(
                lambda driver: 'https://secure.indeed.com/settings' in driver.current_url
                )
        except TimeoutException:
            print('The captcha and/or two-step verification must be done manually.'
                  'Afterward, you must manually sign in.')
            WebDriverWait(self._browser, 600).until(
                lambda driver: driver.current_url == 'https://secure.indeed.com/settings?hl=en'
                )
        return None

    def _apply_for_job(self, job_url: str, wait=5) -> None:
        self._browser.execute_script('window.open()')
        tab = self._browser.window_handles[-1]
        self._browser.switch_to.window(tab)
        self._browser.get(job_url)
        WebDriverWait(self._browser, wait).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//*[@id="indeedApplyButton"]')
                )
            )
        self._browser.find_element_by_xpath('//*[@id="indeedApplyButton"]').click()
        while True:
            try:
                WebDriverWait(self._browser, wait).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH, '//button//span[text()="Continue"]')
                        )
                    )
                self._browser.find_element_by_xpath('//button//span[text()="Continue"]').click()
            except TimeoutException:
                break
        try:
            WebDriverWait(self._browser, wait).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, '//button//span[text()="Review your application"]')
                    )
                )
            self._browser.find_element_by_xpath('//button//span[text()="Review your application"]').click()
            WebDriverWait(self._browser, wait).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, '//button//span[text()="Submit your application"]')
                    )
                )
            self._browser.find_element_by_xpath('//button//span[text()="Submit your application"]').click()
        except TimeoutException:
            pass
        WebDriverWait(self._browser, wait).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button//span[text()="Return to job search"]')
                )
            )
        self._browser.find_element_by_xpath('//button//span[text()="Return to job search"]').click()
        self._browser.close()
        self._browser.switch_to.window(self._main_window)
        return None

    def search_jobs(
            self, query: str,
            past_14_days: bool = True,
            job_type: str = '',
            salary: str = '',
            exp_lvl: str = '',
            remote: bool = False,
            temp_remote: bool = False,
            location: str = ''
            ) -> None:
        if self._number_of_jobs == 0:
            return None
        start = 0
        jobs_applied_to = 0
        stop_search = False
        if remote or temp_remote:
            self._browser.get(
                'https://www.indeed.com/jobs?q={query}&fromage={days}&start={start}'
                .format(query=query, days=14, start=start)
                )
            if remote:
                remote_id = BeautifulSoup(str(self._browser.page_source), 'lxml') \
                    .select_one('a:contains("Remote")')
                if remote_id:
                    remote_id = search('(?<=remotejob=).+?(?=")', str(remote_id)).group()
            else:
                remote_id = BeautifulSoup(str(self._browser.page_source), 'lxml') \
                    .select_one('a:contains("Temporarily remote")')
                if remote_id:
                    remote_id = search('(?<=remotejob=).+?(?=")', str(remote_id)).group()
        else:
            remote_id = ''
        while True:
            self._browser.get(
                'https://www.indeed.com/jobs'
                '?q={query}'
                '{days}'
                '{start}'
                '{type}'
                '{lvl}'
                '{remote_job}'
                '{location}'
                .format(
                    query=query + ' '*bool(salary) + salary,
                    days='&fromage=14'*past_14_days,
                    start='&start=' + str(start),
                    type='&jt='*bool(job_type) + job_type,
                    lvl='&explvl='*bool(exp_lvl) + exp_lvl,
                    remote_job=(remote or temp_remote)*('&remotejob=' + str(remote_id)),
                    location='&l='*bool(location) + location
                    )
                )
            self._main_window = self._browser.current_window_handle
            mobtk = search('(?<=data-mobtk=").+?(?=")', self._browser.page_source).group()
            soup_list = BeautifulSoup(self._browser.page_source, 'lxml')\
                .findAll('a', {'data-mobtk': mobtk})
            start += len(soup_list)
            for tag in soup_list:
                quick_apply = BeautifulSoup(str(tag), 'lxml')\
                    .find('span', {'class': 'ialbl iaTextBlack'})
                if not quick_apply:
                    continue
                job_jk = search('(?<=data-jk=").+?(?=")', str(tag)).group()
                job_url = 'https://www.indeed.com/viewjob?jk={}'.format(job_jk)
                if job_jk in self._cache:
                    continue
                try:
                    self._apply_for_job(job_url)
                except (ElementClickInterceptedException,
                        ElementNotInteractableException,
                        StaleElementReferenceException,
                        TimeoutException):
                    if self._debug:
                        print_exc()
                        stop_search = True
                        break
                    if self._manually_fill_out_question:
                        WebDriverWait(self._browser, 600).until(
                            expected_conditions.element_to_be_clickable(
                                (By.XPATH, '//button//span[text()="Return to job search"]')
                                )
                            )
                        self._browser.find_element_by_xpath('//button//span[text()="Return to job search"]').click()
                        self._browser.close()
                        self._browser.switch_to.window(self._main_window)
                    else:
                        if self._browser.current_window_handle != self._main_window:
                            self._browser.close()
                            self._browser.switch_to.window(self._main_window)
                        continue
                result_content = BeautifulSoup(str(tag), 'lxml').find('td', {'class': 'resultContent'})
                job_title = BeautifulSoup(str(result_content), 'lxml')\
                    .find('h2', {'class': ['jobTitle jobTitle-color-purple jobTitle-newJob',
                                           'jobTitle jobTitle-color-purple']})
                company_name = BeautifulSoup(str(result_content), 'lxml')\
                    .find('span', {'class': 'companyName'})
                job_location = BeautifulSoup(str(result_content), 'lxml')\
                    .find('div', {'class': 'companyLocation'})
                job_salary = BeautifulSoup(str(result_content), 'lxml')\
                    .find('span', {'class': 'salary-snippet'})
                if job_title:
                    job_title = search('(?<=title=").+?(?=")', str(job_title))
                    if job_title:
                        job_title = job_title.group()
                if company_name:
                    company_name = company_name.get_text()
                if job_location:
                    job_location = job_location.get_text()
                if job_salary:
                    job_salary = job_salary.get_text()
                self.results['Title'].append(job_title)
                self.results['Company'].append(company_name)
                self.results['Location'].append(job_location)
                self.results['Salary'].append(job_salary)
                self.results['URL'].append(job_url)
                self._cache.add(job_jk)
                jobs_applied_to += 1
                with open('cache.txt', 'a') as file:
                    file.write(job_jk + '\n')
                if jobs_applied_to == self._number_of_jobs:
                    stop_search = True
                    break
            if stop_search:
                break
        return None

    def close(self) -> None:
        self._browser.quit()
        return None
