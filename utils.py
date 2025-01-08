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
    print("\nEnter the title of each section you want to remove, one at a time. Copy only section title!")
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


def get_data_dict(file_name: str) -> dict:
    import json

    with open(file_name, "r") as file:
        data = json.load(file)

    return data
