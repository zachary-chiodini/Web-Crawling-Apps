# Craigs-Crawler
This is used to search craigslist statewide or nationwide.
The default is a nationwide search. 
Currently, the CraigsCrawler class can only search for cars and trucks.
The nationwide search may take up to 20 or so minutes. 
A progress bar will keep you updated.

```python
import json

from craigs_crawler import CraigsCrawler

# Nationwide search takes some time.
# This may result in a connection error.
craigs_crawler = CraigsCrawler()
results = craigs_crawler.search_cars_and_trucks(
    query='Volvo S80 V8',
    )
craigs_crawler.close()
print(json.loads(results, indent=4, default=str))
```
The data in the results is a dictionary that contains the state, region, 
result header, price, date, URL and image for each result.

To refine the search, the optional parameter "enforce_substrings" can be used.
Each substring in this list must exist within the header of each search result.

```python
import json

from craigs_crawler import CraigsCrawler

# Nationwide search takes some time.
# This may result in a connection error.
craigs_crawler = CraigsCrawler()
results = craigs_crawler.search_cars_and_trucks(
    query='Volvo S80 V8',
    enforce_substrings=['Volvo', 'S80', 'V8']
    )
craigs_crawler.close()
print(json.loads(results, indent=4, default=str))
```

The search can be narrowed down to statewide, using the optional parameter "state_set."

```python
import json

from craigs_crawler import CraigsCrawler

craigs_crawler = CraigsCrawler(
    state_set={'North Carolina', 'South Carolina', 'Virginia'}
    )
results = craigs_crawler.search_cars_and_trucks(
    query='Volvo S80 V8',
    enforce_substrings=['Volvo', 'S80', 'V8']
    )
craigs_crawler.close()
print(json.loads(results, indent=4, default=str))
```

Furthermore, the search can be narrowed down to city and state,
using the optional parameter "states_and_region_dict."
Note that the region you choose must exist on the craigslist website 
https://www.craigslist.org/about/sites#US. 
Additionally, Puerto Rico cannot be chosen, because the Puerto Rico craigslist is not in English.

```python
import json

from craigs_crawler import CraigsCrawler

craigs_crawler = CraigsCrawler(
    state_and_regions_dict={'Texas': 'El Paso', 'California': 'Los Angeles'}
    )
results = craigs_crawler.search_cars_and_trucks(
    query='Volvo S80 V8',
    enforce_substrings=['Volvo', 'S80', 'V8']
    )
craigs_crawler.close()
print(json.loads(results, indent=4, default=str))
```
Both of these search criteria can be used at the same time.
```python
import json

from craigs_crawler import CraigsCrawler

craigs_crawler = CraigsCrawler(
    state_set={'North Carolina', 'South Carolina', 'Virginia'},
    state_and_regions_dict={'Texas': 'El Paso', 'California': 'Los Angeles'}
    )
results = craigs_crawler.search_cars_and_trucks(
    query='Volvo S80 V8',
    enforce_substrings=['Volvo', 'S80', 'V8']
    )
craigs_crawler.close()
print(json.loads(results, indent=4, default=str))
```
See "main.py" to change the search parameters.
Run "main.py" to begin searching.