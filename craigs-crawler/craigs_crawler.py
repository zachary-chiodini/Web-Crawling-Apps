from re import search
from typing import Dict, Optional, Set

from bs4 import BeautifulSoup
from requests import Session, Response


class CraigsCrawler:

    def __init__(
            self,
            state_set: Set[str] = set(),
            state_and_regions_dict: Dict[str, Set[str]] = {}
            ) -> None:
        self.state_set = {text.lower().strip() for text in state_set}
        self.state_and_cities_dict = {
            state.lower().strip():
                [region.lower().strip() for region
                 in state_and_regions_dict[state]]
            for state in state_and_regions_dict
            }
        self.united_states = {}
        self.session = Session()

    def _scrape_states_and_regions(self) -> Response:
        response = self.session.get('https://www.craigslist.org/about/sites#US')
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
                if self.state_set or self.state_and_cities_dict:
                    if state in self.state_set or state in self.state_and_cities_dict:
                        united_states[state] = {}
                    else:
                        continue
                else:
                    united_states[state] = {}
                for region in BeautifulSoup(str(list_), 'lxml').findAll('a'):
                    if self.state_and_cities_dict:
                        region_text = region.get_text().lower()
                        if region_text in self.state_and_cities_dict[state]:
                            url = search('".+"', str(region)).group().strip('"')
                            united_states[state][region_text] = url
                        else:
                            continue
                    else:
                        url = search('".+"', str(region)).group().strip('"')
                        united_states[state][region.get_text().lower()] = url
        self.united_states = united_states
        return response
