import sys

from notion import planner_create_block, planner_create_separate
from udemy_scraper import scrape_udemy_course
from utils import get_user_data, get_data_dict, preview_course_structure, filter_sections, get_sections_to_remove


# Before starting a program, create .env file, provide NOTION_TOKEN and NOTION_PAGE_ID
def main() -> None:
    """
    Main entry point for the program. Handles user input, fetches data,
    processes course structure, and creates a Notion planner.
    """
    url, is_block = get_user_data()

    file_name = ""
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        file_name = sys.argv[1]

    try:
        data = get_data_dict(file_name) if file_name else scrape_udemy_course(url)
        if data is None:
            sys.exit("\nError occurred while fetching the data")

        preview_course_structure(data)
        sections_to_remove = get_sections_to_remove()
        data_filtered = filter_sections(data, sections_to_remove)

        if is_block:
            planner_create_separate(data_filtered)
        else:
            planner_create_block(data_filtered)

        print("The database has been created. Checkout your Notion page!")

    except ValueError as e:
        print(f"\nValueError occurred: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
