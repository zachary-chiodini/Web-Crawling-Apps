from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options


class IndeedCrawler:
    def __init__(self, email: str, password: str) -> None:
        self._email = email
        self._password = password
        self._browser = None

    def login(self) -> Response:
        response = self.session.post('https://secure.indeed.com/account/login')
