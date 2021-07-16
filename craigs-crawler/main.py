from craigs_crawler import CraigsCrawler

craigs_crawler = CraigsCrawler()  # Nationwide search takes some time.
results = craigs_crawler.search_cars_and_trucks('Volvo S80 V8')
craigs_crawler.close()
print(results)
