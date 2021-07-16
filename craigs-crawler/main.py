from craigs_crawler import CraigsCrawler

# Nationwide search takes some time and may result in a connection error.
craigs_crawler = CraigsCrawler()
results = craigs_crawler.search_cars_and_trucks('Volvo S80 V8', enforce_substring='Volvo')
craigs_crawler.close()
print(results)
