from udemy_scraper import scrape_udemy_course
from notion import planer_create


def main():
    # Before starting a program, create .env file, provide NOTION_TOKEN and NOTION_PAGE_ID
    url = "https://www.udemy.com/course/introduction-to-fiber-optic-cabling"

    try:
        data = scrape_udemy_course(url)
    except ValueError:
        print("Create .env file and provide these variables: NOTION_TOKEN, NOTION_PAGE_ID")

    if data is None:
        print("Error occurred while fetching the data")
        return

    planer_create(data)
    print("The database has been created. Checkout your notion page!")


if __name__ == "__main__":
    main()
