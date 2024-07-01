from udemy_scraper import scrape_udemy_course
from notion import planer_create


# Before starting a program, create .env file, provide NOTION_TOKEN and NOTION_PAGE_ID
def main():
    # Provide the url
    url = ""

    try:
        data = scrape_udemy_course(url)

        if data is None:
            print("Error occurred while fetching the data")
            return

        planer_create(data)
        print("The database has been created. Checkout your notion page!")

    except ValueError:
        print("Create .env file and provide these variables: NOTION_TOKEN, NOTION_PAGE_ID")


if __name__ == "__main__":
    main()
