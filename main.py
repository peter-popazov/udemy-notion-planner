from udemy_scraper import scrape_udemy_course
from notion import planer_create


# Before starting a program, create .env file, provide NOTION_TOKEN and NOTION_PAGE_ID
def main():
    # Provide the url
    url = input("Enter URL of Udemy Course: ")

    try:
        data = scrape_udemy_course(url, get_sections_to_remove())

        if data is None:
            print("Error occurred while fetching the data")
            return

        planer_create(data)
        print("The database has been created. Checkout your notion page!")

    except ValueError:
        print("Create .env file and provide these variables: NOTION_TOKEN, NOTION_PAGE_ID")


def get_sections_to_remove():
    sections_to_remove = []
    print("Enter the titles of sections you want to remove, one at a time.")
    print("Type 'done' when you are finished.")

    while True:
        section = input("Enter section title to remove: ").strip()
        if section.lower() == 'done':
            break
        sections_to_remove.append(section)

    return sections_to_remove


if __name__ == "__main__":
    main()
