import sys

from udemy_scraper import scrape_udemy_course
from notion import planer_create
from notion import planner_create_block


# Before starting a program, create .env file, provide NOTION_TOKEN and NOTION_PAGE_ID
def main():
    # Provide the url
    url = input("Enter URL of Udemy Course: ")

    is_block = ""

    while is_block not in ["yes", "no"]:
        is_block = input("Do you want a separate page for the lecture? yes/no: ").strip().lower()

    try:
        data = scrape_udemy_course(url, get_sections_to_remove())

        if data is None:
            print("\nError occurred while fetching the data")
            return

        if "yes" in is_block:
            planer_create(data)
        else:
            planner_create_block(data)

        print("The database has been created. Checkout your notion page!")

    except ValueError:
        print("\nSomething went wrong")


def get_sections_to_remove():
    print("\nEnter the title of each section you want to remove, one at a time.")
    print("Type 'done' when you are finished.")
    sections_to_remove = []

    while True:
        user_input = input("Enter a section title to remove: ").strip()
        if user_input.lower() == 'done':
            break
        elif user_input:
            sections_to_remove.append(user_input)

    return sections_to_remove


if __name__ == "__main__":
    main()
