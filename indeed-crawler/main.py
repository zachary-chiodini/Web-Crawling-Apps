from os import path
from re import search

from bs4 import BeautifulSoup
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

DRIVER_PATH = 'driver'

my_options = Options()
my_profile = FirefoxProfile()
settings = [
    '-headless', '-disable-gpu',
    '-ignore-certificate-errors',
    '-disable-extensions', '-no-sandbox',
    '-disable-dev-shm-usage'
    ]
for argument in settings:
    my_options.add_argument(argument)
my_profile.set_preference('permissions.default.image', 2)
kwargs = {
    'executable_path': path.join(DRIVER_PATH, 'geckodriver.exe'),
    'service_log_path': 'NUL',
    # 'firefox_profile': my_profile,
    # 'options': my_options
    }
browser = Firefox(**kwargs)
browser.get('https://secure.indeed.com/account/login')
browser.find_element_by_xpath(
    '//input[@type="email"]'
    ).send_keys('zachary.chiodini@outlook.com')
browser.find_element_by_xpath(
    '//input[@type="password"]'
    ).send_keys('12Bryant$$')
browser.find_element_by_xpath(
    '//input[ @type="password" ]'
    ).send_keys(Keys.RETURN)
try:
    WebDriverWait(browser, 10).until(
        lambda driver: driver.current_url == 'https://secure.indeed.com/settings?hl=en'
        )
except TimeoutException as e:
    # Captcha or 2-Step Verification
    WebDriverWait(browser, 600).until(
        lambda driver: driver.current_url == 'https://secure.indeed.com/settings?hl=en'
        )

browser.get('https://www.indeed.com/jobs?q={query}&fromage={days}&start={start}'
            .format(query='data', days=14, start=1))

x = 'Please list 2-3 dates and time ranges that you could do an interview.'

main_window = browser.current_window_handle
mobtk = search('(?<=data-mobtk=").+?(?=")', browser.page_source).group()

for tag in BeautifulSoup(browser.page_source, 'lxml').findAll('a', {'data-mobtk': mobtk}):
    job_jk = search('(?<=data-jk=").+?(?=")', str(tag)).group()
    result_content = BeautifulSoup(str(tag), 'lxml').find('td', {'class': 'resultContent'})
    job_title = BeautifulSoup(str(result_content), 'lxml')\
        .find('h2', {'class': 'jobTitle jobTitle-color-purple jobTitle-newJob'})
    company_name = BeautifulSoup(str(result_content), 'lxml')\
        .find('span', {'class': 'companyName'})
    location = BeautifulSoup(str(result_content), 'lxml')\
        .find('div', {'class': 'companyLocation'})
    salary = BeautifulSoup(str(result_content), 'lxml')\
        .find('span', {'class': 'salary-snippet'})
    quick_apply = BeautifulSoup(str(tag), 'lxml')\
        .find('span', {'class': 'ialbl iaTextBlack'})
    print(job_jk)
    if job_title:
        print(job_title.get_text())
    if company_name:
        print(company_name.get_text())
    if location:
        print(location.get_text())
    if salary:
        print(salary.get_text())
    if quick_apply:
        print(quick_apply.get_text())
    if quick_apply:
        job_url = 'https://www.indeed.com/viewjob?jk={}'.format(job_jk)
        browser.execute_script('window.open()')
        tab = browser.window_handles[-1]
        browser.switch_to.window(tab)
        browser.get(job_url)
        WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//*[@id="indeedApplyButton"]')
                )
            )
        browser.find_element_by_xpath('//*[@id="indeedApplyButton"]').click()
        while True:
            try:
                WebDriverWait(browser, 10).until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH, '//button//span[text()="Continue"]')
                        )
                    )
                browser.find_element_by_xpath('//button//span[text()="Continue"]').click()
            except TimeoutException:
                break
        WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button//span[text()="Review your application"]')
                )
            )
        browser.find_element_by_xpath('//button//span[text()="Review your application"]').click()
        WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button//span[text()="Submit your application"]')
            )
        )
        browser.find_element_by_xpath('//button//span[text()="Submit your application"]').click()
        WebDriverWait(browser, 10).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//button//span[text()="Return to job search"]')
            )
        )
        browser.find_element_by_xpath('//button//span[text()="Return to job search"]').click()
        browser.close()
        break
