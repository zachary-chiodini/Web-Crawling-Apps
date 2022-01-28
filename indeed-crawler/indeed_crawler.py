from os import path
from re import compile as compile_regex, findall, search
from time import sleep
from traceback import print_exc
from typing import Callable, List, Optional

from bs4 import BeautifulSoup
from fasttext import load_model
from numpy import apply_along_axis, argmin, array, char, float32, ndarray, vectorize
from numpy.typing import NDArray
from pandas import DataFrame, read_excel
from selenium.webdriver import ActionChains, Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (
    ElementClickInterceptedException, ElementNotInteractableException,
    InvalidArgumentException, InvalidSelectorException, NoSuchElementException,
    NoSuchWindowException, StaleElementReferenceException, TimeoutException,
    WebDriverException)
from scipy.spatial import distance
from xlsxwriter import Workbook


class IndeedCrawler:
    """
    Indeed Crawler
    """

    def __init__(
            self, number_of_jobs=0,
            headless_mode=False,
            driver_path='driver',
            debug=False,
            manually_fill_out_questions=False
            ) -> None:
        self.results = {
            'Title': [],
            'Company': [],
            'Location': [],
            'Salary': [],
            'URL': []
            }
        self._map_country = {
            'united states': '',
            'united kingdom': 'uk.',
            'canada': 'ca.',
            'netherlands': 'nl.'
            }
        self._q_and_a = {}
        self._df = DataFrame()
        self._browser = None
        self._sentence2vec = None
        self._number_of_jobs = number_of_jobs
        self._headless_mode = headless_mode
        self._driver_path = driver_path
        self._main_window = ''
        self._debug = debug
        self._manually_fill_out_questions = manually_fill_out_questions
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
        self._browser.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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
            return self._setup_headless_browser()
        return self._setup_real_browser()

    def login(self, email: str, password: str) -> None:
        self._browser.get('https://secure.indeed.com/account/login')
        try:
            self._browser.find_element_by_xpath(
                '//input[@type="email"]'
                ).send_keys(email)
        except NoSuchElementException:
            try:
                self._browser.find_element_by_xpath(
                    '//input[@autocomplete="email"]'
                    ).send_keys(email)
                self._browser.find_element_by_xpath(
                    '//input[@autocomplete="email"]'
                    ).send_keys(Keys.RETURN)
                WebDriverWait(self._browser, 10).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH, '//input[@type="password"]')
                        )
                    )
            except (NoSuchWindowException, TimeoutException):
                # A captcha was likely encountered.
                print('The captcha and/or two-step verification must be done manually.'
                      'Afterward, you must manually sign in.')
                WebDriverWait(self._browser, 600).until(
                    lambda driver: ('https://secure.indeed.com/settings' in driver.current_url
                                    or 'https://my.indeed.com/resume?from=login' in driver.current_url)
                    )
                return None
        try:
            self._browser.find_element_by_xpath(
                '//input[@type="password"]'
                ).send_keys(password)
            self._browser.find_element_by_xpath(
                '//input[@type="password"]'
                ).send_keys(Keys.RETURN)
            WebDriverWait(self._browser, 10).until(
                lambda driver: ('https://secure.indeed.com/settings' in driver.current_url
                                or 'https://my.indeed.com/resume?from=login' in driver.current_url)
                )
        except (NoSuchWindowException, TimeoutException):
            # A captcha was likely encountered.
            print('The captcha and/or two-step verification must be done manually.'
                  'Afterward, you must manually sign in.')
            WebDriverWait(self._browser, 600).until(
                lambda driver: ('https://secure.indeed.com/settings' in driver.current_url
                                or 'https://my.indeed.com/resume?from=login' in driver.current_url)
                )
        return None

    def _load_model(self) -> None:
        print('Loading fasttext pretrained sentence/document embedding model ...')
        model = load_model('fasttext-model/cc.en.300.bin')
        self._sentence2vec: Callable[[NDArray[str]], NDArray[float32]] \
            = vectorize(model.get_sentence_vector, otypes=[float32], signature='()->(n)')
        return None

    def _cosine_distances(self, v: NDArray[str], s: str) -> NDArray[float32]:
        return apply_along_axis(distance.cosine, 1, self._sentence2vec(v), self._sentence2vec(s))

    def _get_answer(self, question_found: str, answers_found: NDArray[str]) -> str:
        self._df['Cosine Distance'] = self._cosine_distances(
            self._df['Question'], question_found)
        answer_stored = str(self._df.loc[self._df['Cosine Distance'].idxmin(), 'Answer'])
        if answers_found.size:
            answers_found = char.replace(answers_found, '\n', '')
            return answers_found[argmin(self._cosine_distances(answers_found, answer_stored))]
        return answer_stored

    def collect_questionnaire(self, query: str, update=False) -> None:
        if update:
            self._df = read_excel('questionnaire.xlsx')
            for _, series in self._df.iterrows():
                self._q_and_a[series['Question']] = {series['Answer']}
            self._load_model()
        self._browser.get('https://www.indeed.com/jobs?q={}'.format(query))
        try:
            mobtk = search(
                '(?<=data-mobtk=").+?(?=")',
                self._browser.page_source).group()
        except AttributeError:
            # captcha
            current_url = self._browser.current_url
            WebDriverWait(self._browser, 600).until(
                lambda driver: driver.current_url != current_url
                )
            return self.collect_questionnaire(query, update)
        navigation = BeautifulSoup(
            self._browser.page_source, 'lxml'
            ).find('nav', {'role': 'navigation'})
        pages = []
        for page in navigation.findAll(['a', 'b']):
            page = page.get_text()
            if page:
                pages.append(page)
        if not pages:
            pages = [None]
        for page in pages:
            if page:
                try:
                    page_element = self._browser.find_element_by_xpath(
                        '//nav//span[text()[contains(.,"{}")]]'.format(page))
                    page_element.click()
                except ElementClickInterceptedException:
                    ActionChains(self._browser).move_to_element(page_element).click().perform()
                    page_element.click()
                except NoSuchElementException:
                    pass
            mobtk = search(
                '(?<=data-mobtk=").+?(?=")',
                self._browser.page_source).group()
            soup_list = BeautifulSoup(
                self._browser.page_source, 'lxml')\
                .findAll('a', {'data-mobtk': mobtk})
            for tag in soup_list:
                quick_apply = BeautifulSoup(
                    str(tag), 'lxml')\
                    .find('span', {'class': 'ialbl iaTextBlack'})
                if not quick_apply:
                    continue
                job_jk = search('(?<=data-jk=").+?(?=")', str(tag)).group()
                job_url = 'https://www.indeed.com/viewjob?jk={}'.format(job_jk)
                self._apply_to_job(job_url, update, collect_q_and_a=True)
        workbook = Workbook('questionnaire.xlsx')
        worksheet = workbook.add_worksheet('questionnaire')
        worksheet.write(0, 0, 'Question')
        worksheet.write(0, 1, 'Answer')
        worksheet.freeze_panes(1, 0)
        row = 1
        for question, answers in self._q_and_a.items():
            worksheet.write(row, 0, question)
            if update and not self._df.empty:
                stored_record = self._df[self._df['Question'] == question]
                if not stored_record.empty:
                    worksheet.write(row, 1, str(stored_record['Answer'].iloc[0]))
                    row += 1
                    continue
            if answers:
                worksheet.data_validation(
                    row, 1, row, 1, {'validate': 'list', 'source': list(answers)}
                    )
            row += 1
        workbook.close()
        return None

    def _continue(self, answer_questions: bool, collect_q_and_a: bool, wait=5) -> None:
        for _ in range(10):
            try:
                resume_div = BeautifulSoup(self._browser.page_source, 'lxml') \
                    .find('span', text=compile_regex('Last'))
                if not resume_div:
                    resume_div = BeautifulSoup(self._browser.page_source, 'lxml') \
                        .find('span', text=compile_regex('resume'))
                if resume_div:
                    resume_div = resume_div.find_parent('div', {'id': compile_regex('resume')})
                if resume_div:
                    self._browser.find_element_by_xpath(
                        '//div[@id="{}"]'.format(resume_div.get('id'))
                        ).click()
                if collect_q_and_a or answer_questions:
                    questions = BeautifulSoup(
                        self._browser.page_source, 'lxml') \
                        .findAll(class_=compile_regex('Questions'))
                    if questions:
                        questions.pop(0)
                        for div in questions:
                            labels = div.findAll('label')
                            if not labels:
                                continue
                            question_found = labels.pop(0).get_text().replace('(optional)', '').strip()
                            if not question_found:
                                continue
                            answers_set = set()
                            select = div.find('select')
                            if select:
                                labels = select.findAll('option')
                            for answer_found in labels:
                                if answer_found:
                                    answer_found = answer_found.get_text().strip()
                                    if answer_found:
                                        answers_set.add(answer_found)
                            if answer_questions:
                                answer = self._get_answer(
                                    question_found, array(list(answers_set)))
                                try:
                                    # Multiple answers found implies a radio input type
                                    # or a selection.
                                    if answers_set:
                                        if div.find('input'):
                                            div_id = div.get('id')
                                            self._browser.find_element_by_xpath(
                                                '//div[@id="{}"]//label//span[text()[contains(.,"{}")]]'
                                                .format(div_id, answer)
                                                ).click()
                                        elif div.find('select'):
                                            div_id = div.get('id')
                                            self._browser.find_element_by_xpath(
                                                '//div[@id="{}"]//option[contains(@label, "{}")]'
                                                .format(div_id, answer)
                                                ).click()
                                    # No answers found implies a text input type
                                    # or a text area
                                    elif div.find('input'):
                                        auto_filled = search('(?<=value=").+?(?=")', str(div))
                                        if not auto_filled:
                                            input_id = div.find('input').get('id')
                                            self._browser.find_element_by_xpath(
                                                '//input[@id="{}"]'.format(input_id)
                                                ).send_keys(answer)
                                    elif div.find('textarea'):
                                        auto_filled = div.find('textarea')
                                        if not auto_filled:
                                            text_id = div.find('textarea').get('id')
                                            self._browser.find_element_by_xpath(
                                                '//textarea[@id="{}"]'.format(text_id)
                                                ).send_keys(answer)
                                except (InvalidArgumentException, InvalidSelectorException,
                                        NoSuchElementException, ElementNotInteractableException,
                                        StaleElementReferenceException):
                                    pass
                            if collect_q_and_a:
                                if question_found in self._q_and_a:
                                    self._q_and_a[question_found].update(answers_set)
                                else:
                                    self._q_and_a[question_found] = answers_set
                WebDriverWait(self._browser, wait).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH,
                         '//button//span[text()[contains(.,"Continue")]]')
                        )
                    )
                self._browser.find_element_by_xpath(
                    '//button//span[text()[contains(.,"Continue")]]').click()
            except TimeoutException:
                break
            except NoSuchElementException:
                print('NoSuchElementException encountered!')
                break
        return None

    def _apply_to_job(self, job_url: str,
                      answer_questions=False,
                      collect_q_and_a=False,
                      wait=3) -> None:
        self._main_window = self._browser.current_window_handle
        self._browser.execute_script('window.open()')
        tab = self._browser.window_handles[-1]
        self._browser.switch_to.window(tab)
        self._browser.get(job_url)
        WebDriverWait(self._browser, wait).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//*[@id="indeedApplyButton"]')
                )
            )
        self._browser.find_element_by_xpath(
            '//*[@id="indeedApplyButton"]').click()
        resume_div = BeautifulSoup(self._browser.page_source, 'lxml')\
            .find('span', text=compile_regex('Last'))
        if not resume_div:
            resume_div = BeautifulSoup(self._browser.page_source, 'lxml') \
                .find('span', text=compile_regex('resume'))
        if resume_div:
            resume_div = resume_div.find_parent('div', {'id': compile_regex('resume')})
        if resume_div:
            self._browser.find_element_by_xpath(
                '//div[@id="{}"]'.format(resume_div.get('id'))
                ).click()
        self._continue(answer_questions, collect_q_and_a)
        if not collect_q_and_a:
            try:
                WebDriverWait(self._browser, wait).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH,
                         '//button//span[text()="Review your application"]')
                        )
                    )
                self._browser.find_element_by_xpath(
                    '//button//span[text()="Review your application"]').click()
                WebDriverWait(self._browser, wait).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH,
                         '//button//span[text()="Submit your application"]')
                        )
                    )
                self._browser.find_element_by_xpath(
                    '//button//span[text()="Submit your application"]').click()
            except TimeoutException:
                pass
            WebDriverWait(self._browser, wait).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH,
                     '//div//h1[text()="Your application has been submitted!"]')
                    )
                )
        self._browser.close()
        self._browser.switch_to.window(self._main_window)
        return None

    def search_jobs(
            self, query: str,
            job_title_negate_lst: List[str] = [],
            company_name_negate_lst: List[str] = [],
            past_14_days: bool = True,
            job_type: str = '',
            min_salary: str = '',
            enforce_salary: bool = False,
            exp_lvl: str = '',
            remote: bool = False,
            temp_remote: bool = False,
            country: str = '',
            location: str = '',
            radius: str = '',
            auto_answer_questions=False
            ) -> None:
        if self._number_of_jobs == 0:
            print('Number of jobs is zero.')
            return None
        if auto_answer_questions:
            self._df = read_excel('questionnaire.xlsx')
            for _, series in self._df.iterrows():
                self._q_and_a[series['Question']] = series['Answer']
            self._load_model()
        jobs_applied_to = 0
        stop_search = False
        if remote or temp_remote:
            self._browser.get(
                'https://{country}indeed.com/jobs?q={query}{days}'
                .format(country=self._map_country[country],
                        query=query, days='&fromage=14'*past_14_days)
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
        self._browser.get(
            'https://{country}indeed.com/jobs'
            '?q={query}'
            '{days}'
            '{type}'
            '{lvl}'
            '{remote_job}'
            '{location}'
            '{radius}'
            .format(
                country=self._map_country[country],
                query=query,
                days='&fromage=14' * past_14_days,
                type='&jt=' * bool(job_type) + job_type,
                lvl='&explvl=' * bool(exp_lvl) + exp_lvl,
                remote_job=(remote or temp_remote) * ('&remotejob=' + str(remote_id)),
                location='&l=' * bool(location) + location,
                radius='&radius=' * bool(radius) + radius
                )
            )
        while True:
            try:
                mobtk = search(
                    '(?<=data-mobtk=").+?(?=")',
                    self._browser.page_source).group()
            except AttributeError:
                # captcha
                current_url = self._browser.current_url
                WebDriverWait(self._browser, 600).until(
                    lambda driver: driver.current_url != current_url
                )
                continue
            self._main_window = self._browser.current_window_handle
            soup_list = BeautifulSoup(
                self._browser.page_source, 'lxml')\
                .findAll('a', {'data-mobtk': mobtk})
            for tag in soup_list:
                quick_apply = BeautifulSoup(str(tag), 'lxml')\
                    .find('span', {'class': 'ialbl iaTextBlack'})
                if not quick_apply:
                    continue
                job_jk = search('(?<=data-jk=").+?(?=")', str(tag)).group()
                if job_jk in self._cache:
                    continue
                job_url = 'https://www.indeed.com/viewjob?jk={}'\
                    .format(job_jk)
                result_content = BeautifulSoup(str(tag), 'lxml')\
                    .find('td', {'class': 'resultContent'})
                job_title = BeautifulSoup(str(result_content), 'lxml')\
                    .find('h2', {'class': compile_regex('jobTitle')})
                if job_title:
                    job_title = search('(?<=title=").+?(?=")', str(job_title))
                    if job_title:
                        job_title = job_title.group()
                if job_title_negate_lst and job_title:
                    negate_word_found = False
                    for word in job_title_negate_lst:
                        if word in job_title.lower():
                            negate_word_found = True
                            break
                    if negate_word_found:
                        continue
                job_salary = BeautifulSoup(str(result_content), 'lxml')\
                    .find(class_=compile_regex('salary'))
                if not job_salary and enforce_salary:
                    continue
                if min_salary and job_salary:
                    max_salary_found = ''
                    salary_text = job_salary.get_text()\
                        .split('-')[-1].strip().replace(',', '')\
                        .lower()
                    for chr_ in salary_text:
                        if chr_.isdigit():
                            max_salary_found += chr_
                        if chr_ == '.' and '.' not in max_salary_found:
                            max_salary_found += chr_
                    if max_salary_found.isdigit():
                        if 'hour' in salary_text:
                            max_salary_found = float(max_salary_found)*2080
                        elif 'month' in salary_text:
                            max_salary_found = int(max_salary_found)*12
                        if int(max_salary_found) < int(min_salary):
                            continue
                company_name = BeautifulSoup(str(result_content), 'lxml')\
                    .find(class_=compile_regex('companyName'))
                if company_name_negate_lst and company_name:
                    company_name_text = company_name.get_text().lower()
                    negate_word_found = False
                    for word in company_name_negate_lst:
                        if word in company_name_text:
                            negate_word_found = True
                            break
                    if negate_word_found:
                        continue
                try:
                    self._apply_to_job(
                        job_url, answer_questions=auto_answer_questions)
                except (ElementClickInterceptedException,
                        ElementNotInteractableException,
                        NoSuchElementException,
                        NoSuchWindowException,
                        StaleElementReferenceException,
                        TimeoutException,
                        WebDriverException):
                    if self._debug:
                        print_exc()
                        stop_search = True
                        break
                    if self._manually_fill_out_questions:
                        try:
                            WebDriverWait(self._browser, 600).until(
                                expected_conditions.element_to_be_clickable(
                                    (By.XPATH, '//button//span[text()="Submit your application"]')
                                    )
                                )
                            self._browser.find_element_by_xpath('//button//span[text()="Submit your application"]').click()
                            WebDriverWait(self._browser, 5).until(
                                expected_conditions.element_to_be_clickable(
                                    (By.XPATH, '//button//span[text()="Return to job search"]')
                                )
                            )
                            self._browser.close()
                            self._browser.switch_to.window(self._main_window)
                        except (NoSuchWindowException, WebDriverException, TimeoutException):
                            self._browser.switch_to.window(self._main_window)
                            continue
                    else:
                        if self._browser.current_window_handle != self._main_window:
                            self._browser.close()
                            self._browser.switch_to.window(self._main_window)
                        continue
                job_location = BeautifulSoup(str(result_content), 'lxml')\
                    .find(class_=compile_regex('companyLocation'))
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
                if job_jk not in self._cache:
                    self._cache.add(job_jk)
                    jobs_applied_to += 1
                    with open('cache.txt', 'a') as file:
                        file.write(job_jk + '\n')
                    print(f"You've applied to {jobs_applied_to} job(s).")
                if jobs_applied_to == self._number_of_jobs:
                    stop_search = True
                    break
            if stop_search:
                break
            navigation = BeautifulSoup(
                self._browser.page_source, 'lxml'
                ).find('nav', {'role': 'navigation'})
            if not navigation:
                break
            try:
                next_page_element = self._browser.find_element_by_xpath(
                    '//nav//a[@aria-label="Next"]')
                next_page_element.click()
            except ElementClickInterceptedException:
                ActionChains(self._browser).move_to_element(next_page_element)\
                    .click().perform()
                next_page_element.click()
            except NoSuchElementException:
                break
        return None

    def close(self) -> None:
        self._browser.quit()
        return None
