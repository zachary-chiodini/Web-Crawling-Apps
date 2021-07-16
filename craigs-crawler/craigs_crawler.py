from io import BytesIO
from PIL import Image
from re import search
from tqdm import tqdm
from typing import Dict, List, Optional, Set

from bs4 import BeautifulSoup
from requests import Response, Session
from requests.exceptions import HTTPError


class CraigsException(HTTPError):
    def __init__(self, response: Response) -> None:
        super().__init__('Get response to URL {url} failed with code {code}'
                         .format(url=response.url, code=response.status_code))
        self.code = response.status_code
        self.headers = response.headers


class CraigsCrawler:
    def __init__(
            self,
            state_set: Set[str] = set(),
            state_and_regions_dict: Dict[str, Set[str]] = {}
            ) -> None:
        self.united_states = {}
        self.session = Session()
        self._state_set = {text.lower().strip() for text in state_set}
        self._state_and_cities_dict = {
            state.lower().strip():
                [region.lower().strip() for region
                 in state_and_regions_dict[state]]
            for state in state_and_regions_dict
            }

    def _craigs_validate_get(self, url: str) -> Response:
        response = self.session.get(url)
        if response.status_code != 200:
            raise CraigsException(response)
        return response

    def _scrape_states_and_regions(self) -> None:
        response = self._craigs_validate_get(
            'https://www.craigslist.org/about/sites#US')
        soup = BeautifulSoup(response.text, 'lxml')
        united_states = {}
        for i in range(1, 5):
            # United States data is in the first occurrence of box_1-box_4.
            united_states_box = str(soup.find('div', {'class': 'box box_{}'.format(i)}))
            for state, list_ in zip(
                    BeautifulSoup(united_states_box, 'lxml').findAll('h4'),
                    BeautifulSoup(united_states_box, 'lxml').findAll('ul')
                    ):
                state = state.get_text().lower()
                if self._state_set or self._state_and_cities_dict:
                    if state in self._state_set or state in self._state_and_cities_dict:
                        united_states[state] = {}
                    else:
                        continue
                else:
                    united_states[state] = {}
                for region in BeautifulSoup(str(list_), 'lxml').findAll('a'):
                    if self._state_and_cities_dict:
                        region_text = region.get_text().lower()
                        if region_text in self._state_and_cities_dict[state]:
                            url = search('(?<=").+(?=")', str(region)).group().strip('"')
                            united_states[state][region_text] = url
                        else:
                            continue
                    else:
                        url = search('(?<=").+(?=")', str(region)).group()
                        united_states[state][region.get_text().lower()] = url
        self.united_states = united_states
        return None

    def search_cars_and_trucks(
            self, query: str,
            enforce_substrings: Optional[List[str]] = None
            ) -> Dict:
        prev_result_urls = set()  # Used to prevent duplicates
        search_results = {}
        self._scrape_states_and_regions()
        if 'territories' in self.united_states:
            if 'puerto rico' in self.united_states['territories']:
                # Puerto Rico craigslist is not in English.
                del self.united_states['territories']['puerto rico']
        num_loops = sum(len(self.united_states[state])
                        for state in self.united_states)
        with tqdm(total=num_loops) as progress_bar:
            for state in self.united_states:
                search_results[state] = {}
                for region, url in self.united_states[state].items():
                    search_results[state][region] = {}
                    response = self._craigs_validate_get(url)
                    cars_and_trucks_path = search(
                            '(?<=href=").+?(?=")',
                            str(BeautifulSoup(response.text, 'lxml').select('a:contains("cars+trucks")'))
                            ).group()
                    domain = search('.+(.org)', url).group()
                    encoded_query = query.replace(' ', '%20')
                    search_url = '{}/{}?query={}'.format(
                        domain, cars_and_trucks_path.strip('/'), encoded_query)
                    response = self._craigs_validate_get(search_url)
                    for result in BeautifulSoup(response.text, 'lxml') \
                            .findAll('div', {'class': 'result-info'}):
                        result_heading = BeautifulSoup(str(result), 'lxml') \
                            .find('h3', {'class': 'result-heading'})
                        heading = result_heading.get_text()
                        if enforce_substrings:
                            substring_not_found = False
                            for substring in enforce_substrings:
                                if substring.lower() not in heading.lower():
                                    substring_not_found = True
                                    break
                            if substring_not_found:
                                continue
                        result_url = search('(?<=href=").+?(?=")', str(result_heading)).group()
                        if result_url in prev_result_urls:
                            continue
                        result_date = search(
                            '(?<=datetime=").+?(?=")',
                            str(BeautifulSoup(str(result), 'lxml').find('time'))
                            ).group()
                        result_price = BeautifulSoup(str(result), 'lxml') \
                            .find('span', {'class': 'result-price'}).get_text()
                        response = self._craigs_validate_get(result_url)
                        image_url = search(
                            '(?<=content=").+?(?=")',
                            str(BeautifulSoup(response.text, 'lxml')
                                .find('meta', {'property': 'og:image'}))
                            )
                        if image_url:
                            response = self._craigs_validate_get(image_url.group())
                            result_image = Image.open(BytesIO(response.content))
                        else:
                            result_image = None
                        search_results[state][region][heading] = {
                            'price': result_price,
                            'date': result_date,
                            'url': result_url,
                            'image': result_image
                            }
                        prev_result_urls.add(result_url)
                    if not search_results[state][region]:
                        del search_results[state][region]
                    progress_bar.update(1)
                if not search_results[state]:
                    del search_results[state]
        return search_results

    def close(self) -> None:
        self.session.close()
        return
