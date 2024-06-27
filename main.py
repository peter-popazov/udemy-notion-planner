from udemy_scraper import scrape_udemy_course
from pprint import pprint

url = "https://www.udemy.com/course/introduction-to-fiber-optic-cabling"

data = scrape_udemy_course(url)
pprint(data)