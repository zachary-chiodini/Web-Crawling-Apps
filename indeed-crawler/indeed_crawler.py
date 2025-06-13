from math import ceil
from os import path
from re import compile as compile_regex, findall
from time import sleep, time
from tkinter import Text
from traceback import format_exc
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from bs4 import BeautifulSoup
from bs4.element import Tag
from fasttext import load_model
from numpy import append, apply_along_axis, argmin, array, char, float32, str_, vectorize
from numpy.typing import NDArray
from pandas import DataFrame, ExcelWriter
from scipy.spatial import distance
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException)
from undetected_chromedriver import Chrome, ChromeOptions


class IndeedCrawler:

    def __init__(self, total_number_of_jobs=0, debug=False, q_and_a={}, log_box: Optional[Text] = None) -> None:
        self.results = {'Title': [], 'Company': [], 'Location': [], 'Salary': [], 'URL': []}
        self.total_jobs_applied_to = 0
        self._browser: Chrome
        self._cache = set()
        self._cache_file_name = 'cache.txt'
        self._debug = debug
        self._df = DataFrame()
        self._log_box = log_box
        self._main_window = ''
        self._map_country = {'canada': 'ca.', 'france': 'fr.', 'india': 'in.', 'ireland': 'ie.',
            'netherlands': 'nl.', 'united states': '', 'united kingdom': 'uk.'}
        self._q_and_a: Dict[str, Set[str]] = q_and_a
        # Sentence to vector model must be loaded from fasttext binary.
        self._sentence2vec: Callable[[NDArray[str_]], NDArray[float32]] = None
        self._total_number_of_jobs = total_number_of_jobs
        if path.exists(self._cache_file_name):
            with open(self._cache_file_name) as f:
                for line in f:
                    self._cache.add(line.strip())

    def setup_browser(self) -> None:
        options = ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        self._browser = Chrome(options)
        return None

    def start_crawling(self, company_negate_list: List[str], job_negate_list: List[str],
            queries: List[str], regions: List[Tuple[str]]) -> None:
        start_t = time()
        self.setup_browser()
        self.login('', '')
        number_per_query = ceil(self._total_number_of_jobs // (len(queries) * len(regions)))
        for location, country in regions:
            for query in queries:
                try:
                    self._search_jobs(country, location, number_per_query, query,
                        job_negate_list=job_negate_list, company_negate_list=company_negate_list)
                except Exception:
                    self._log(format_exc(), traceback=True)
        df = DataFrame(data=self.results)
        if not df.empty:
            with ExcelWriter('submissions.xlsx', engine='openpyxl', mode='a') as writer:
                df.to_excel(writer, sheet_name='jobs', index=False)
        total_t = int(time() - start_t)
        seconds = total_t % 60
        minutes = (total_t % 3600) // 60
        hours = (total_t % 86400) // 3600
        days = total_t // 86400
        self._log('Job search has terminated.')
        self._log(f'Time elapsed: {days:02}:{hours:02}:{minutes:02}:{seconds:02}')
        return None

    def login(self, email: str, password: str) -> None:
        self._browser.get('https://secure.indeed.com/account/login')
        # Automated login is no longer possible on indeed.com.
        self._log('You must manually sign in. After signing in, navigate to your profile page.')
        WebDriverWait(self._browser, 600).until(lambda driver: 'https://profile.indeed.com/' in driver.current_url)
        return None

    def _apply_to_job(self, job_url: str, wait=5) -> bool:
        return_val = False
        self._log(f"Applying to job at {job_url}.")
        self._browser.execute_script("window.open('');")
        sleep(wait)
        self._browser.switch_to.window(self._browser.window_handles[-1])
        self._browser.get(job_url)
        sleep(wait)
        self._browser.find_element(By.XPATH, '//button//span[text()="Apply now"]').click()
        sleep(wait)
        prev_url = ''
        while prev_url != self._browser.current_url:
            for tag in BeautifulSoup(self._browser.page_source, 'lxml').find_all(class_=compile_regex('Questions-item')):
                question = tag.find('span', {'data-testid': 'rich-text'}).get_text()
                # Some questions are wrapped in double quotes.
                matches = findall('".+?"', question)
                if matches:
                    question = max(matches, key=len).strip('"')
                self._log(f"Question found: {question}")
                answer = self._df.loc[argmin(self._cosine_distance(self._df['Question'], question)), 'Answer']
                self._log(f"Answer found: {answer}.")
                self._input_answer(answer, tag)
            prev_url = self._browser.current_url
            if not self._select_continue():
                break
            sleep(wait)
        try:
            self._browser.find_element(By.XPATH, '//button//span[text()="Review"]').click()
            self._log('Reviewing application.')
            sleep(wait)
        except NoSuchElementException:
            self._log('Failed to review application.')
        try:
            self._browser.find_element(By.XPATH, '//button//span[text()[contains(.,"Submit")]]').click()
            return_val = True
            self._log(f"SUCCESS - applied to job {job_url}")
            sleep(600)
        except NoSuchElementException:
            self._log(f"FAILURE - did not apply to {job_url}")
        self._browser.close()
        self._browser.switch_to.window(self._main_window)
        return return_val

    def _cache_job(self, job_jk: str) -> None:
        self._cache.add(job_jk)
        with open(self._cache_file_name, 'a') as file:
            file.write(f"{job_jk}\n")
        return None

    def _cosine_distance(self, v: NDArray[str_], s: str) -> NDArray[float32]:
        return apply_along_axis(distance.cosine, 1, self._sentence2vec(v), self._sentence2vec(s))

    def _find_word_in_negate_list(self, string: str, negate_list: List[str]) -> bool:
        for word in negate_list:
            if word.lower() in string.lower():
                self._log(f"Found {word} in {string}.")
                return True
        return False

    def _get_value(self, field: str, tag: Union[Tag, None]) -> str:
        if not tag:
            self._log(f"Failed to find {field}.")
            return ''
        value = tag.get_text()
        self._log(f"{field}: {value}")
        return value

    def _input_answer(self, answer: str, tag: Tag) -> None:
        selections = set()
        input_0 = tag.find('input')
        print()
        print('tag =', tag)
        print()
        if input_0:
            input_type = input_0.get('type')
            self._log(f"Input type found: {input_type}.")
            if input_type == 'text' and (not input_0.get('value')):
                input_element = self._browser.find_element(By.XPATH, f'//input')
                input_element.click()
                input_element.send_keys(answer)
            elif input_type == 'radio':
                for input_i in tag.find_all('input'):
                    text = input_i.find_next_sibling('span').get_text().strip()
                    if text:
                        selections.add(text)
                answer = self._select_answer(answer, selections)
                self._browser.find_element(
                    By.XPATH, f'//span[text()="{answer}"]/preceding::input[1]').click()
        elif tag.find('select'):
            self._log(f"Input type found: selection.")
            for option_i in tag.find_all('option'):
                if option_i.get('value'):
                    text = option_i.get_text()
                    if text:
                        selections.add(text)
                answer = self._select_answer(answer, selections)
                self._browser.find_element(By.XPATH, f'//select//option[text()="{answer}")]').click()
        elif tag.find('textarea'):
            self._log(f"Input type found: textarea.")
            if not tag.find('textarea').get('value'):
                text_element = self._browser.find_element(By.XPATH, f'//textarea')
                text_element.click()
                text_element.send_keys(answer)
        else:
            self._log(f"Input type found: unknown.")
        return None

    def _load_s2v_model(self) -> None:
        self._log('Loading fasttext pretrained sentence/document embedding model. This may take a few minutes.')
        model = load_model('fasttext-model/cc.en.300.bin')
        self._sentence2vec = vectorize(model.get_sentence_vector, otypes=[float32], signature='()->(n)')
        self._log('Model loaded successfully.')
        return None

    def _log(self, message: str, traceback: bool = False) -> None:
        if len(message) > 255 and (not traceback):
            message = f"{message[:251]} ..."
        if self._log_box:
            self._log_box.configure(state='normal')
            self._log_box.insert('end', f'\n{message}')
            self._log_box.configure(state='disabled')
        else:
            print(message)
        return None

    def _search_jobs(self, country: str, location: str, number_of_jobs: int, query: str, enforce_query: bool = False,
            job_negate_list: List[str] = [], company_negate_list: List[str] = [], past_14_days: bool = False,
            job_type: str = '', min_salary: str = '', enforce_salary: bool = False, exp_lvl: str = '',
            remote: bool = False, radius: str = '') -> None:
        if not number_of_jobs:
            self._log('Number of jobs is zero.')
            return None
        if not self._sentence2vec:
            self._df = DataFrame(self._q_and_a.items(), columns=['Question', 'Answer'])
            self._load_s2v_model()
        if remote:
            # This block needs rewriting.
            remote_id = ''
        else:
            remote_id = ''
        self._browser.get(f"https://{self._map_country[country]}indeed.com/jobs?q={query}"
            f"{'&fromage=14' * past_14_days}{'&jt='*bool(job_type) + job_type}{'&explvl='*bool(exp_lvl) + exp_lvl}"
            f"{bool(remote)*('&remotejob=' + remote_id)}{'&l='*bool(location) + location}"
            f"{'&radius='*bool(radius) + radius}")
        batch_jobs_applied_to = 0
        active_search = True
        while active_search:
            sleep(5)  # Waiting for page to load.
            self._main_window = self._browser.current_window_handle  # Jobs are applied to in a separate tab.
            for tag in BeautifulSoup(self._browser.page_source, 'lxml').find_all('div', {'class': 'job_seen_beacon'}):
                # Automation is limited to "Easy apply".
                if not tag.find('span', string=compile_regex('Easily apply')):
                    continue
                job_jk = tag.find('a')
                if job_jk:
                    job_jk = job_jk.get('data-jk')
                if not job_jk:
                    self._log('Failed to find data-jk value.')
                    continue
                if job_jk in self._cache:
                    self._log(f"Already applied to job: {job_jk}.")
                    continue
                title = self._get_value('Job Title', tag.find('span', {'id': f"jobTitle-{job_jk}"}))
                if enforce_query and ((query.lower() not in title.lower()) or (title.lower() not in query.lower())):
                    self._log(f"Title {title} does not match query {query}")
                    continue
                if self._find_word_in_negate_list(title, job_negate_list):
                    continue
                company = self._get_value('Company Name', tag.find('span', {'data-testid': 'company-name'}))
                if self._find_word_in_negate_list(company, company_negate_list):
                    continue
                salary = self._get_value('Salary', tag.find(string=compile_regex('^\$?[0-9]{1,3},?[0-9]{0,3}.?[0-9]{0,2}')))
                if enforce_salary and (not salary):
                    self._log(f"Salary is enforced. Skipping job {job_jk}.")
                    continue
                if min_salary and salary:
                    # Needs rewriting.
                    pass
                location = self._get_value('Location', tag.find('div', {'data-testid': 'text-location'}))
                job_url = f"https://www.indeed.com/viewjob?jk={job_jk}"
                self._cache_job(job_jk)
                if self._apply_to_job(job_url):
                    self.results['Title'].append(title)
                    self.results['Company'].append(company)
                    self.results['Location'].append(location)
                    self.results['Salary'].append(salary)
                    self.results['URL'].append(job_url)
                    batch_jobs_applied_to += 1
                    self.total_jobs_applied_to += 1
                    self._log(f"You've applied to {self.total_jobs_applied_to} job(s).")
                if batch_jobs_applied_to == number_of_jobs:
                    active_search = False
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

    def _select_answer(self, answer: str, selections: Set[str]) -> str:
        select_array = array(list(selections), dtype='str')
        select_array = char.replace(select_array, '\n', '')
        self._log(f"Selections found: {selections}.")
        answer = select_array[argmin(self._cosine_distance(select_array, answer))]
        self._log(f"Answer selected: {answer}.")
        return answer

    def _select_continue(self) -> bool:
        # The continue button is duplicated in the html source.
        for element in self._browser.find_elements(By.XPATH, '//button//span[text()[contains(.,"Continue")]]'):
            try:
                element.click()
                self._log('Selected continue.')
                return True
            except ElementNotInteractableException:
                pass
        self._log('Failed to continue.')
        return False
