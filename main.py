from udemy_scraper import scrape_udemy_course
from pprint import pprint

url = "https://www.udemy.com/course/datastructurescncpp"

data = scrape_udemy_course(url)
pprint(data)