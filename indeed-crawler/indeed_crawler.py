from os import path
from re import search

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
    def __init__(self, headless_mode=False,
                 driver_path='driver') -> None:
        self.results = {}
        self._browser = None
        self._headless_mode = headless_mode
        self._driver_path = driver_path
        self._main_window = ''
        self._cache = set()
        with open('cache.txt', 'a+') as file:
            for line in file:
                self._cache.add(line)

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
            '//input[ @type="password" ]'
            ).send_keys(Keys.RETURN)
        try:
            WebDriverWait(self._browser, 10).until(
                lambda driver: driver.current_url == 'https://secure.indeed.com/settings?hl=en'
                )
        except TimeoutException:
            print('The captcha and/or two-step verification must be done manually.'
                  'Afterward, you must manually sign in.')
            WebDriverWait(self._browser, 600).until(
                lambda driver: driver.current_url == 'https://secure.indeed.com/settings?hl=en'
                )
        return None

    def _apply_for_job(self, job_jk: str) -> None:
        job_url = 'https://www.indeed.com/viewjob?jk={}'.format(job_jk)
        self._browser.execute_script('window.open()')
        tab = self._browser.window_handles[-1]
        self._browser.switch_to.window(tab)
        self._browser.get(job_url)
        WebDriverWait(self._browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//*[@id="indeedApplyButton"]')
                )
            )
        self._browser.find_element_by_xpath('//*[@id="indeedApplyButton"]').click()
        while True:
            try:
                WebDriverWait(self._browser, 10).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH, '//button//span[text()="Continue"]')
                        )
                    )
                self._browser.find_element_by_xpath('//button//span[text()="Continue"]').click()
            except TimeoutException:
                break
        WebDriverWait(self._browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button//span[text()="Review your application"]')
                )
            )
        self._browser.find_element_by_xpath('//button//span[text()="Review your application"]').click()
        WebDriverWait(self._browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button//span[text()="Submit your application"]')
                )
            )
        self._browser.find_element_by_xpath('//button//span[text()="Submit your application"]').click()
        WebDriverWait(self._browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button//span[text()="Return to job search"]')
                )
            )
        self._browser.find_element_by_xpath('//button//span[text()="Return to job search"]').click()
        self._browser.close()
        self._browser.switch_to.window(self._main_window)
        return None

    def search_jobs(self, query: str) -> None:
        start = 0
        while True:
            self._browser.get(
                'https://www.indeed.com/jobs?q={query}&fromage={days}&start={start}'
                .format(query=query, days=14, start=start))
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
                if job_jk in self._cache:
                    continue
                try:
                    self._apply_for_job(job_jk)
                except (ElementClickInterceptedException,
                        ElementNotInteractableException,
                        StaleElementReferenceException,
                        TimeoutException) as e:
                    print(str(e))
                    WebDriverWait(self._browser, 10)
                    with open('{}-ERROR.html'.format(job_jk), 'w', encoding='utf-8') as file:
                        file.write(self._browser.page_source)
                    if self._browser.current_window_handle != self._main_window:
                        self._browser.close()
                        self._browser.switch_to.window(self._main_window)
                    continue
                result_content = BeautifulSoup(str(tag), 'lxml').find('td', {'class': 'resultContent'})
                job_title = BeautifulSoup(str(result_content), 'lxml')\
                    .find('h2', {'class': 'jobTitle jobTitle-color-purple jobTitle-newJob'})
                company_name = BeautifulSoup(str(result_content), 'lxml')\
                    .find('span', {'class': 'companyName'})
                location = BeautifulSoup(str(result_content), 'lxml')\
                    .find('div', {'class': 'companyLocation'})
                salary = BeautifulSoup(str(result_content), 'lxml')\
                    .find('span', {'class': 'salary-snippet'})
                if job_title:
                    job_title = job_title.get_text()
                if company_name:
                    company_name = company_name.get_text()
                if location:
                    location = location.get_text()
                if salary:
                    salary = salary.get_text()
                result = {
                    'Title': job_title,
                    'Company': company_name,
                    'Location': location,
                    'Salary': salary
                    }
                self.results[job_jk] = result
                self._cache.add(job_jk)
                with open('cache.txt', 'a') as file:
                    file.write(job_jk + '\n')

    def close(self) -> None:
        self._browser.quit()
        return None
