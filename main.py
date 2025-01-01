import sys

from udemy_scraper import scrape_udemy_course
from notion import planer_create_separate
from notion import planner_create_block


# Before starting a program, create .env file, provide NOTION_TOKEN and NOTION_PAGE_ID
def main() -> None:
    url, is_block = get_user_data()

    try:
        data = scrape_udemy_course(url)
        if data is None:
            sys.exit("\nError occurred while fetching the data")

        preview_course_structure(data)
        sections_to_remove = get_sections_to_remove()
        data_filtered = filter_sections(data, sections_to_remove)

        if is_block:
            planer_create_separate(data_filtered)
        else:
            planner_create_block(data_filtered)

        print("The database has been created. Checkout your notion page!")

    except ValueError as e:
        print(f"\nValueError occurred: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


def get_user_data() -> tuple[str, bool]:
    url = input("Enter URL of Udemy Course: ")

    is_block = ""
    while is_block not in ["yes", "no"]:
        is_block = input("Do you want a separate page for the lecture? yes/no [no]: ").strip().lower() or "no"

    is_block = True if "yes" in is_block else False
    return url, is_block


def preview_course_structure(data: dict) -> None:
    print("\nPreview of the course structure:")
    for section in data['sections']:
        print(f"- {section['section_title']} ({len(section['lectures'])} lectures) - {section['time']}")


def get_sections_to_remove() -> list:
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


def filter_sections(data: dict, sections_to_remove: list) -> dict:
    data['sections'] = [section for section in data['sections'] if section['section_title'] not in sections_to_remove]
    return data


if __name__ == "__main__":
    main()
