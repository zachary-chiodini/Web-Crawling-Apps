import os
import atexit
import requests
from re import search
from bs4 import BeautifulSoup
from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from typing import Dict

DRIVER_PATH = 'gpu-crawler//driver'


class BestBuyCrawler:

    def __init__(self, bestbuy_form: Dict, logger):
        self._form = bestbuy_form
        self._log = logger
        self._browser = None
        self._session = None
        self._screenshot = 1

    def setup_crawler(self) -> None:
        self._log('Setting up Selenium headless browser ...')
        self._setup_selenium_browser()
        self._log('Setting up requests session ...')
        self._set_up_requests_session()
        return None

    def login_crawler(self) -> None:
        self._log('Logging into www.bestbuy.com ...')
        self._login()
        return None

    def search_gpus(self, page: int) -> str:
        response = self._session.get(
            url='https://www.bestbuy.com/site/searchpage.jsp',
            parms={'st': 'gpus', 'cp': page}
            )
        return response.text

    def scrape_page(self, html: str) -> None:
        if self._form['search by']['sku id']['checked']:
            sku_list = self._form['search by']['sku id']['ids']
            self._log('Searching by SKU IDs: {}'
                      .format(','.join(sku_list)))
            self._search_by_sku_id(html, sku_list)
        if self._form['search by']['price range']['checked']:
            mini = float(
                self._form['search by']['price range']['min'])
            maxi = float(
                self._form['search by']['price range']['max'])
            self._log('Searching by price range ${}-${}'
                      .format(mini, maxi))
            self._search_by_price_range(html, mini, maxi)
        if self._form['search by']['price per sku id']['checked']:
            sku_list = self._form['search by']\
                ['price per sku id']['ids']
            price_list = self._form['search by']\
                ['price per sku id']['prices']
            self._search_by_price_per_sku_id(
                html, sku_list, price_list)
        return None

    def close(self) -> None:
        if self._browser:
            self._browser.close()
        if self._session:
            self._session.close()
        self._browser = None
        self._session = None
        return None

    def _setup_selenium_browser(self) -> None:
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
            'executable_path':
                os.path.join(DRIVER_PATH, 'geckodriver.exe'),
            'service_log_path': 'NUL',
            'firefox_profile': my_profile,
            'options': my_options
            }
        self._browser = Firefox(**kwargs)
        atexit.register(self._browser.close)
        return None

    def _set_up_requests_session(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': 'Mozilla/5.0'})
        atexit.register(self._session.close)
        return None

    def _login(self) -> None:
        self._browser.get(
            'https://www.bestbuy.com/identity/global/signin')
        self._browser.find_element_by_xpath(
            '//input[ @type="email" ]'
            ).send_keys(self._form['login']['username'])
        self._browser.find_element_by_xpath(
            '//input[ @type="password" ]'
            ).send_keys(self._form['login']['password'])
        self._browser.find_element_by_xpath(
            '//input[ @type="password" ]'
            ).send_keys(Keys.RETURN)
        return None

    def _add_to_cart(self, sku_id: str) -> None:
        self._browser.get(
            url='https://api.bestbuy.com/click/-/{}/cart'
                .format(sku_id)
            )
        return None

    def _fast_checkout(self) -> None:
        self._browser.get(
            url='https://www.bestbuy.com/checkout/r/fast-track'
            )
        return None

    def _fill_in_credit_card_security_code(self) -> None:
        self._browser.find_element_by_xpath(
            '//input[ @id="credit-card-cvv" ]'
            ).send_keys(self._form['credit card']['security code'])
        return None

    def _place_order(self) -> None:
        self._browser.find_element_by_xpath(
            '//button[ @class="btn btn-lg btn-block btn-primary button__fast-track" ]'
            ).click()
        return None

    def _take_screenshot(self, sku_id: str) -> None:
        file_name = 'SKU{}ORDER{}'\
            .format(sku_id, self._screenshot)
        self._browser.get_screenshot_as_file(file_name)
        self._log('Screenshot {} taken ...'.format(file_name))
        self._screenshot += 1
        return None

    def _within_budget(self, sku_id: str, price: float) -> bool:
        total = float(self._form['settings']['spent']) \
                + price
        if float(self._form['settings']['budget']) <= total:
            self._log('SKU ID {} is within your budget'
                      .format(sku_id))
            self._log('SKU ID {} is queued to order.'
                      .format(sku_id))
            return True
        self._log('SKU ID {} is not within your budget'
                  .format(sku_id))
        return False

    @staticmethod
    def _get_price(sku_id: str, html: str) -> float:
        price_tag = BeautifulSoup(html, 'lxml').find(
            'div', {'data-viewtype': 'price',
                    'data-skuid': sku_id}
            ).get_text()
        price = search(
            pattern='(?<=\$).+?(?=[A-Za-z])',
            string=price_tag
            ).group().replace(',', '')
        return float(price)

    def _get_sku_id(self, bs4tag, pattern) -> str:
        sku_id = search(
            pattern=pattern,
            string=str(bs4tag)
            ).group()
        self._log('Retrieved SKU ID {}'.format(sku_id))
        return sku_id

    def _gpu_is_available(self, sku_id: str,
                          status: str) -> bool:
        self._log('SKU ID {} status:'.format(sku_id, status))
        return status == 'Add to Cart'

    def _purchase_gpu(self, sku_id: str) -> None:
        self._add_to_cart(sku_id)
        self._log('SKU ID {} added to cart ...'.format(sku_id))
        self._fast_checkout()
        self._log('SKU ID {} at checkout ...'.format(sku_id))
        self._fill_in_credit_card_security_code()
        self._place_order()
        self._log('SKU ID {} ordered ...'.format(sku_id))
        self._take_screenshot(sku_id)
        return None

    def _update_money_spent(self, price: float) -> None:
        self._form['settings']['spent'] = \
            float(self._form['settings']['spent']) \
            + price
        self._log('Spent ${}.'.format(
            self._form['settings']['spent']))
        return None

    @staticmethod
    def _get_add_to_cart_status(html: str, sku_id: str) -> str:
        add_to_cart_status = BeautifulSoup(html, 'lxml')\
            .find('button', {'data-sku-id': sku_id}).get_text()
        return add_to_cart_status

    def _within_price_range(self, sku_id: str, price: float,
                            mini: float, maxi: float) -> bool:
        if mini <= price <= maxi:
            self._log('SKU ID {} is within the price range ...'
                      .format(sku_id))
            return True
        self._log('SKU ID {} is not within the price range ...'
                  .format(sku_id))
        return False

    def _the_price_is_right(self, sku_id: str, price: float,
                            right_price: float) -> bool:
        if price <= right_price:
            self._log('SKU ID {} has the right price.'
                      .format(sku_id))
            return True
        self._log('SKU ID {} has the wrong price.'
                  .format(sku_id))
        return False

    def _search_by_sku_id(self, html: str, sku_list) -> None:
        for add_to_cart_button in BeautifulSoup(html, 'lxml')\
                .find('button', {'data-sku-id': sku_list}):
            sku_id = self._get_sku_id(
                add_to_cart_button, '(?<=data-sku-id=")[0-9]+')
            add_to_cart_status = add_to_cart_button.get_text()
            if self._gpu_is_available(sku_id, add_to_cart_status):
                price = self._get_price(sku_id, html)
                if self._within_budget(sku_id, price):
                    self._purchase_gpu(sku_id)
                    self._update_money_spent(price)
        return None

    def _search_by_price_range(self, html: str, mini, maxi) -> None:
        for price_div in BeautifulSoup(html, 'lxml')\
                .findAll('div', {'data-viewtype': 'price'}):
            text = price_div.get_text()
            if text:
                sku_id = self._get_sku_id(
                    price_div, '(?<=data-skuid=")[0-9]+')
                price = self._get_price(sku_id, html)
                if self._within_price_range(price, mini, maxi):
                    add_to_cart_status = \
                        self._get_add_to_cart_status(html, sku_id)
                    if self._gpu_is_available(
                            sku_id, add_to_cart_status):
                        if self._within_budget(sku_id, price):
                            self._purchase_gpu(sku_id)
                            self._update_money_spent(price)
        return None

    def _search_by_price_per_sku_id(
            self, html: str, sku_list, price_list) -> None:
        for add_to_cart_button in BeautifulSoup(html, 'lxml') \
                .find('button', {'data-sku-id': sku_list}):
            sku_id = self._get_sku_id(
                add_to_cart_button, '(?<=data-sku-id=")[0-9]+')
            price_index = price_list[sku_list.index(sku_id)]
            right_price = price_list[price_index]
            add_to_cart_status = add_to_cart_button.get_text()
            if self._gpu_is_available(sku_id, add_to_cart_status):
                price = self._get_price(sku_id, html)
                if self._the_price_is_right(
                        sku_id, price, right_price):
                    if self._within_budget(sku_id, price):
                        self._purchase_gpu(sku_id)
                        self._update_money_spent(price)
        return None
