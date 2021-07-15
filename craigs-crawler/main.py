from craigs_crawler import CraigsCrawler

craigs_crawler = CraigsCrawler()
craigs_crawler._scrape_states_and_regions()
print(craigs_crawler.united_states)
craigs_crawler.session.close()
