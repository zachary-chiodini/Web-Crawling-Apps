from os import path
from re import compile as compile_regex, search
from time import sleep
from tkinter import Text
from traceback import print_exc
from typing import Callable, Dict, List, Optional, Set, Union

from bs4 import BeautifulSoup
from bs4.element import Tag
from fasttext import load_model
from numpy import apply_along_axis, argmin, array, char, float32, str_, vectorize
from numpy.typing import NDArray
from pandas import DataFrame, read_excel
from scipy.spatial import distance
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (
    ElementClickInterceptedException, ElementNotInteractableException,
    InvalidArgumentException, InvalidSelectorException, NoSuchElementException,
    NoSuchWindowException, StaleElementReferenceException, TimeoutException,
    WebDriverException)
from undetected_chromedriver import Chrome, ChromeOptions
from xlsxwriter import Workbook


class IndeedCrawler:
    """Indeed Crawler"""

    def __init__(self, number_of_jobs=0, debug=False, auto_answer_questions=False,
            manually_fill_out_questions=False, q_and_a={}, log_box: Optional[Text] = None) -> None:
        self.results = {
            'Title': [],
            'Company': [],
            'Location': [],
            'Salary': [],
            'URL': []
            }
        self.total_jobs_applied_to = 0
        self._map_country = {
            'canada': 'ca.',
            'france': 'fr.',
            'india': 'in.',
            'ireland': 'ie.',
            'netherlands': 'nl.',
            'united states': '',
            'united kingdom': 'uk.'
            }
        self._q_and_a = q_and_a
        self._log_box = log_box
        self._df = DataFrame()
        self._browser: Chrome
        # Sentence to vector model must be loaded from fasttext binary.
        self._sentence2vec: Callable[[NDArray[str_]], NDArray[float32]] = None
        self._number_of_jobs = number_of_jobs
        self._main_window = ''
        self._debug = debug
        self._auto_answer_questions = auto_answer_questions
        self._manually_fill_out_questions = manually_fill_out_questions
        self._cache = set()
        self._cache_file_name = 'cache.txt'
        if path.exists(self._cache_file_name):
            with open(self._cache_file_name) as f:
                for line in f:
                    self._cache.add(line.strip())

    '''
    def collect_questionnaire(self, query: str, country='united states', update=False) -> None:
        if update:
            self._df = read_excel('questionnaire.xlsx')
            for _, series in self._df.iterrows():
                self._q_and_a[series['Question']] = {series['Answer']}
            self._load_w2v_model()
        self._browser.get(f'https://{self._map_country[country]}indeed.com/jobs?q={query}')
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
            return self.collect_questionnaire(query, country, update)
        navigation = BeautifulSoup(
            self._browser.page_source, 'lxml'
            ).find('nav', {'role': 'navigation'})
        pages = []
        for page in navigation.find_all(['a', 'b']):
            page = page.get_text()
            if page:
                pages.append(page)
        if not pages:
            pages = [None]
        for page in pages:
            if page:
                try:
                    page_element = self._browser.find_element(
                        By.XPATH, '//nav//span[text()[contains(.,"{}")]]'.format(page))
                    page_element.click()
                except ElementClickInterceptedException:
                    ActionChains(self._browser).move_to_element(page_element).click().perform()
                    page_element.click()
                except (NoSuchElementException, ElementNotInteractableException):
                    pass
            mobtk = search('(?<=data-mobtk=").+?(?=")', self._browser.page_source).group()
            soup_list = BeautifulSoup(
                self._browser.page_source, 'lxml')\
                .find_all('a', {'data-mobtk': mobtk})
            for tag in soup_list:
                quick_apply = tag.find('span', {'class': 'ialbl iaTextBlack'})
                if not quick_apply:
                    continue
                job_jk = search('(?<=data-jk=").+?(?=")', str(tag)).group()
                job_url = 'https://www.indeed.com/viewjob?jk={}'.format(job_jk)
                try:
                    self._apply_to_job(job_url, update, collect_q_and_a=True)
                except (ElementClickInterceptedException,
                        ElementNotInteractableException,
                        NoSuchElementException,
                        NoSuchWindowException,
                        StaleElementReferenceException,
                        TimeoutException,
                        WebDriverException) as exception:
                    if self._debug:
                        self._log(print_exc())
                    if self._browser.current_window_handle != self._main_window:
                        self._browser.close()
                        self._browser.switch_to.window(self._main_window)
                    continue
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
                    row, 1, row, 1, {'validate': 'list', 'source': list(answers)})
            row += 1
        workbook.close()
        return None
    '''

    def _log(self, message: str) -> None:
        if self._log_box:
            self._log_box.configure(state='normal')
            self._log_box.insert('end', f'\n{message}')
            self._log_box.configure(state='disabled')
        else:
            print(message)
        return None

    def setup_browser(self) -> None:
        options = ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        self._browser = Chrome(options)
        return None

    def login(self, email: str, password: str) -> None:
        self._browser.get('https://secure.indeed.com/account/login')
        # Automated login is no longer possible on indeed.com.
        self._log('You must manually sign in. After signing in, navigate to your profile page.')
        WebDriverWait(self._browser, 600).until(
            lambda driver: ('https://profile.indeed.com/' in driver.current_url
                            or 'https://my.indeed.com/resume?from=login' in driver.current_url)
            )
        return None

    def _load_w2v_model(self) -> None:
        self._log('Loading fasttext pretrained sentence/document embedding model. This may take a few minutes.')
        model = load_model('fasttext-model/cc.en.300.bin')
        self._sentence2vec = vectorize(model.get_sentence_vector, otypes=[float32], signature='()->(n)')
        self._log('Model loaded successfully.')
        return None

    def _cosine_distances(self, v: NDArray[str_], s: str) -> NDArray[float32]:
        return apply_along_axis(distance.cosine, 1, self._sentence2vec(v), self._sentence2vec(s))

    def _get_answer(self, question_found: str, answers_found: NDArray[str_]) -> str:
        self._df['Cosine Distance'] = self._cosine_distances(
            self._df['Question'], question_found)
        answer_stored = str(self._df.loc[self._df['Cosine Distance'].idxmin(), 'Answer'])
        if answers_found.size:
            answers_found = char.replace(answers_found, '\n', '')
            return answers_found[argmin(self._cosine_distances(answers_found, answer_stored))]
        return answer_stored

    def _select_continue(self) -> None:
        for element in self._browser.find_elements(By.XPATH, '//button//span[text()[contains(.,"Continue")]]'):
            # Strange duplicated button html in page source.
            try:
                element.click()
                break
            except (StaleElementReferenceException, ElementNotInteractableException):
                pass
        return None

    def _answer_question(self, question_div: Tag, question_found: str, answers_found: Set[str]) -> None:
        answer = self._get_answer(question_found, array(list(answers_found), dtype=str))
        try:
            if answers_found:
                # Multiple answers implies radio input or selection.
                if question_div.find('input'):
                    div_id = question_div.get('id')
                    self._browser.find_element(By.XPATH,
                        f'//div[contains(@id, "{div_id}")]'
                        f'//span[text()[contains(.,"{answer}")]]'
                        ).click()
                elif question_div.find('select'):
                    select_id = question_div.find('select').get('id')
                    for i, chr_ in enumerate(select_id):
                        if chr_ == '{':
                            select_id = select_id[:i]
                            break
                    self._browser.find_element(
                        By.XPATH,
                        f'//select[starts-with(@id, "{select_id}")]'
                        f'//option[contains(@label, "{answer}")]'
                        ).click()
            # No answers found implies a text input type
            # or a text area
            elif question_div.find('input'):
                auto_filled = search('(?<=value=").*?(?=")', str(question_div))
                if auto_filled:
                    auto_filled = auto_filled.group().strip()
                if not auto_filled:
                    input_id = question_div.find('input').get('id')
                    self._browser.find_element(
                        By.XPATH, f'//input[@id="{input_id}"]'
                        ).send_keys(answer)
            elif question_div.find('textarea'):
                auto_filled = search('(?<=value=").*?(?=")', str(question_div))
                if auto_filled:
                    auto_filled = auto_filled.group().strip()
                if not auto_filled:
                    text_id = question_div.find('textarea').get('id')
                    self._browser.find_element(
                        By.XPATH, f'//textarea[@id="{text_id}"]'
                        ).send_keys(answer)
        except (InvalidArgumentException, InvalidSelectorException,
                NoSuchElementException, ElementNotInteractableException,
                StaleElementReferenceException):
            pass
        return None

    @staticmethod
    def _get_answers_set(labels: List[Tag]) -> Set[str]:
        answers_set = set()
        for answer_found in labels:
            if answer_found:
                answer_found = answer_found.get_text().strip()
                if answer_found:
                    answers_set.add(answer_found)
        return answers_set

    def _handle_screening_questions(self, answer_questions: bool,
            collect_q_and_a: bool, wait=5) -> None:
        for _ in range(10):
            try:
                #self._select_resume()
                if collect_q_and_a or answer_questions:
                    questions = BeautifulSoup(
                        self._browser.page_source, 'lxml'
                        ).find_all(class_=compile_regex('Questions'))
                    if questions:
                        questions.pop(0)
                        for div in questions:
                            labels = div.find_all('label')
                            if not labels:
                                self._select_continue(wait)
                                continue
                            question_found = labels.pop(0).get_text()\
                                .replace('(optional)', '').strip()
                            if not question_found:
                                self._select_continue(wait)
                                continue
                            select = div.find_all('select')
                            if select:
                                for element in select:
                                    labels = element.find_all('option')
                                    answers_found = self._get_answers_set(labels)
                                    if not answers_found:
                                        self._select_continue(wait)
                                        break
                                    if answer_questions:
                                        self._answer_question(
                                            div, question_found, answers_found)
                            else:
                                answers_found = self._get_answers_set(labels)
                                if not answers_found:
                                    self._select_continue(wait)
                                if answer_questions:
                                    self._answer_question(
                                        div, question_found, answers_found)
                            if collect_q_and_a:
                                if question_found in self._q_and_a:
                                    self._q_and_a[question_found].update(answers_found)
                                else:
                                    self._q_and_a[question_found] = answers_found
                self._select_continue(wait)
            except TimeoutException:
                break
            except NoSuchElementException:
                print('NoSuchElementException encountered!')
                break
        return None

    def _select_resume(self) -> None:
        resume_div = BeautifulSoup(self._browser.page_source, 'lxml') \
            .find('span', text=compile_regex('Last'))
        if not resume_div:
            resume_div = BeautifulSoup(self._browser.page_source, 'lxml') \
                .find('span', text=compile_regex('Uploaded'))
        if not resume_div:
            resume_div = BeautifulSoup(self._browser.page_source, 'lxml') \
                .find('span', text=compile_regex('resume'))
        if resume_div:
            resume_div = resume_div.find_parent('div', {'id': compile_regex('resume')})
            if resume_div:
                try:
                    self._browser.find_element(
                        By.XPATH, '//div[@id="{}"]'.format(resume_div.get('id'))
                        ).click()
                except ElementNotInteractableException:
                    pass
        return None

    def _apply_to_job(self, job_url: str, answer_questions=False, collect_q_and_a=False, wait=5) -> None:
        self._browser.execute_script("window.open('');")
        sleep(wait)
        self._browser.switch_to.window(self._browser.window_handles[-1])
        self._browser.get(job_url)
        sleep(wait)
        self._browser.find_element(By.ID, 'indeedApplyButton').click()
        sleep(wait)
        for tag in BeautifulSoup(self._browser.page_source, 'lxml').find_all('input'):
            if not tag.get('value'):
                self._browser.find_element(By.NAME, tag.get('name')).send_keys('hello')
        self._handle_screening_questions(answer_questions, collect_q_and_a)
        if not collect_q_and_a:
            try:
                WebDriverWait(self._browser, wait).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH,
                         '//button//span[text()="Review your application"]')
                        )
                    )
                self._browser.find_element(
                    By.XPATH, '//button//span[text()="Review your application"]').click()
            except TimeoutException:
                pass
            try:
                WebDriverWait(self._browser, wait).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH,
                         '//button//span[text()[contains(.,"Submit")]]')
                    )
                )
                self._browser.find_element(
                    By.XPATH, '//button//span[text()[contains(.,"Submit")]]').click()
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

    def _cache_job(self, job_jk: str) -> None:
        self._cache.add(job_jk)
        with open(self._cache_file_name, 'a') as file:
            file.write(f"{job_jk}\n")
        return None

    def _get_value(self, field: str, tag: Union[Tag, None]) -> str:
        if not tag:
            self._log(f"Failed to find {field}.")
            return ''
        value = tag.get_text()
        self._log(f"{field}: {value}")
        return value

    def search_jobs(
            self, query: str,
            enforce_query: bool = False,
            job_title_negate_list: List[str] = [],
            company_name_negate_list: List[str] = [],
            past_14_days: bool = False,
            job_type: str = '',
            min_salary: str = '',
            enforce_salary: bool = False,
            exp_lvl: str = '',
            remote: bool = False,
            temp_remote: bool = False,
            country: str = '',
            location: str = '',
            radius: str = ''
            ) -> None:
        if not self._number_of_jobs:
            self._log('Number of jobs is zero.')
            return None
        if self._auto_answer_questions and (not self._sentence2vec):
            if self._q_and_a:
                self._df = DataFrame(self._q_and_a.items(), columns=['Question', 'Answer'])
            else:
                self._df = read_excel('questionnaire.xlsx')
                for _, series in self._df.iterrows():
                    self._q_and_a[series['Question']] = series['Answer']
            self._load_w2v_model()
        if remote or temp_remote:
            # This block probably needs rewriting.
            self._browser.get(
                'https://{country}indeed.com/jobs?q={query}{days}'
                .format(country=self._map_country[country],
                        query=query, days='&fromage=14'*past_14_days))
            if remote:
                remote_id = BeautifulSoup(self._browser.page_source, 'lxml') \
                    .select_one('a:contains("Remote")')
                if remote_id:
                    remote_id = search('(?<=remotejob=).+?(?=")', str(remote_id)).group()
            else:
                remote_id = BeautifulSoup(self._browser.page_source, 'lxml') \
                    .select_one('a:contains("Temporarily remote")')
                if remote_id:
                    remote_id = search('(?<=remotejob=).+?(?=")', str(remote_id)).group()
        else:
            remote_id = ''
        self._browser.get(f"https://{self._map_country[country]}indeed.com/jobs?q={query}\
            {'&fromage=14' * past_14_days}{'&jt='*bool(job_type) + job_type}{'&explvl='*bool(exp_lvl) + exp_lvl}\
            {(remote or temp_remote)*('&remotejob=' + str(remote_id))}{'&l='*bool(location) + location}\
            {'&radius='*bool(radius) + radius}")
        batch_jobs_applied_to = 0
        stop_search = False
        while True:
            sleep(5)  # Waiting for page to load.
            self._main_window = self._browser.current_window_handle  # Jobs are applied to in a separate tab.
            for tag in BeautifulSoup(self._browser.page_source, 'lxml').find_all('div', {'class': 'job_seen_beacon'}):
                if not tag.find('span', string=compile_regex('Easily apply')):
                    continue
                job_jk = tag.get('data-jk')
                if not job_jk:
                    self._log('Failed to find data-jk value.')
                    continue
                job_jk = job_jk.group()
                if job_jk in self._cache:
                    self._log(f"Already applied to job: {job_jk}.")
                    continue
                self._log(f"Found new job: {job_jk}")
                title = self._get_value('Job Title', tag.find('span', {'id': f"jobTitle-{job_jk}"}))
                if enforce_query and ((query.lower() not in title.lower()) or (title.lower() not in query.lower())):
                    self._log(f"Title {title} does not match query {query}")
                    continue
                negate_word_found = False
                for word in job_title_negate_list:
                    if word.lower() in title.lower():
                        self._log(f"Found {word} in {title}.")
                        negate_word_found = True
                        break
                if negate_word_found:
                    continue
                company = self._get_value('Company Name', tag.find('span', {'data-testid': 'company-name'}))
                negate_word_found = False
                for word in company_name_negate_list:
                    if word.lower() in company.lower():
                        self._log(f"Found {word} in {company}.")
                        negate_word_found = True
                        break
                if negate_word_found:
                    continue
                salary = self._get_value('Salary', tag.find('div', {'class': compile_regex('salary')}))
                if enforce_salary and (not salary):
                    continue
                if min_salary and salary:
                    # Needs rewriting.
                    pass
                job_url = f"https://www.indeed.com/viewjob?jk={job_jk}"
                try:
                    self._log(f"Applying to job at {job_url}.")
                    self._apply_to_job(job_url, answer_questions=self._auto_answer_questions)
                except (ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException,
                        NoSuchWindowException, StaleElementReferenceException, TimeoutException,
                        WebDriverException) as exception:
                    if self._debug:
                        self._log(print_exc())
                    if self._manually_fill_out_questions:
                        try:
                            WebDriverWait(self._browser, 600).until(
                                expected_conditions.element_to_be_clickable(
                                    (By.XPATH,
                                     '//button//span[text()[contains(.,"Submit")]]')
                                    )
                                )
                            self._browser.find_element(
                                By.XPATH, '//button//span[text()[contains(.,"Submit")]]'
                                ).click()
                            WebDriverWait(self._browser, 10).until(
                                expected_conditions.element_to_be_clickable(
                                    (By.XPATH,
                                     '//button//span[text()[contains(.,"Return")]]')
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
                        if job_jk not in self._cache:
                            self._cache_job(job_jk)
                        self._log(f'FAILED to apply to job: {job_url}')
                        continue
                location = tag.find('div', {'data-testid': 'text-location'})
                if location:
                    location = location.get_text()
                else:
                    location = ''
                self.results['Title'].append(title)
                self.results['Company'].append(company)
                self.results['Location'].append(location)
                self.results['Salary'].append(salary)
                self.results['URL'].append(job_url)
                if job_jk not in self._cache:
                    self._cache_job(job_jk)
                    batch_jobs_applied_to += 1
                    self.total_jobs_applied_to += 1
                    self._log(f"You've applied to {self.total_jobs_applied_to} job(s).")
                if batch_jobs_applied_to == self._number_of_jobs:
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
                next_page_element = self._browser.find_element(
                    By.XPATH, '//nav//a[@aria-label="Next"]')
                next_page_element.click()
            except ElementClickInterceptedException:
                ActionChains(self._browser).move_to_element(next_page_element)\
                    .click().perform()
                next_page_element.click()
            except NoSuchElementException:
                break
        return None

    def reset_results(self) -> None:
        self.results = {
            'Title': [],
            'Company': [],
            'Location': [],
            'Salary': [],
            'URL': []
            }
        return None

    def close(self) -> None:
        self._browser.quit()
        return None
