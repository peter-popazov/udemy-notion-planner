import os
import math
import re
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime, timedelta

SKIP_LECTURE_TIME = 20


def setup_notion() -> tuple[Client, str]:
    load_dotenv()

    token = os.getenv('NOTION_TOKEN')
    page_id = os.getenv('NOTION_PAGE_ID')

    if not token or not page_id:
        raise ValueError("Missing Notion token or page ID")

    client = Client(auth=token)
    create_block(client, page_id, "callout", "This database was generated automatically")

    return client, page_id


def planner_create_block(data: dict) -> None:
    client, page_id = setup_notion()
    db_id = create_database(client, page_id, data['title'])

    user_inputs = get_user_input()
    start_date = user_inputs['start_date']
    daily_minutes = user_inputs['daily_minutes']
    days_factor = user_inputs['days_factor']
    play_speed = user_inputs['play_speed']

    current_date = start_date

    for section in data['sections']:
        section_time = round(section_total_minutes(section['time']) / play_speed)
        counter_parts = 1

        while section_time > 0:
            if section_time < SKIP_LECTURE_TIME:
                print(f"Remaining time [{section_time}] min. is less than {SKIP_LECTURE_TIME} minutes, skipping.")
                break

            time_for_page = min(daily_minutes, section_time)

            start_date_next = current_date
            end_date = start_date_next + timedelta(minutes=time_for_page)

            properties = prepare_page_properties(
                section['section_title'],
                f"{section['section_title']} p.{counter_parts}",
                time_for_page,
                start_date_next,
                end_date,
                ""
            )
            response = create_page(client, db_id, properties)
            print(f"Created database page with ID: {response['id']}")

            section_time -= time_for_page
            current_date = current_date + timedelta(days=days_factor)
            counter_parts += 1


def planer_create(data: dict) -> None:
    client, page_id = setup_notion()
    db_id = create_database(client, page_id, data['title'])

    user_inputs = get_user_input()
    start_date = initial_start_date = user_inputs['start_date']
    daily_minutes = user_inputs['daily_minutes']
    days_factor = user_inputs['days_factor']
    play_speed = user_inputs['play_speed']
    daily_minutes_remaining = daily_minutes

    for section in data['sections']:
        for lecture in section['lectures']:
            lecture_title = lecture['lecture_title']
            duration_min = lecture_duration(lecture['duration']) // play_speed
            lec_type = determine_lecture_type(lecture_title)

            if duration_min > daily_minutes_remaining:
                start_date, daily_minutes_remaining = reset_start_date(initial_start_date, days_factor, daily_minutes)

            end_date = start_date + timedelta(minutes=duration_min)
            daily_minutes_remaining -= duration_min

            if daily_minutes_remaining < 0:
                start_date, daily_minutes_remaining = reset_start_date(
                    initial_start_date, days_factor, daily_minutes - duration_min
                )

            properties = prepare_page_properties(
                section['section_title'], lecture_title, duration_min, start_date, end_date, lec_type
            )
            response = create_page(client, db_id, properties)
            print(f"Created database page with ID: {response['id']}")
            start_date = end_date


def get_user_input():
    # Start date and time input
    print("\nWhen do you want to start learning?")

    while True:
        try:
            date_input = input("Enter a date (YYYY-MM-DD): ")
            time_input = input("Enter a time (HH:MM): ")
            start_date = datetime.strptime(f"{date_input} {time_input}:00", "%Y-%m-%d %H:%M:%S")
            break
        except ValueError:
            print("\nInvalid date or time format. Please try again.")

    # Daily hours input
    while True:
        try:
            daily_hours = float(input("How many hours a day do you want to study?: "))
            if 0 < daily_hours < 24:
                daily_minutes = int(daily_hours * 60)
                break
            else:
                print("Please enter a number between 0 and 24.")
        except ValueError:
            print("Invalid input. Please enter a valid number of hours.")

    # Days factor input
    while True:
        try:
            days_factor = int(input("You want to study every i.e. 1 day, 2 days, etc.: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number of days i.e. 1, 2, 3, etc.")

    # Video play speed input
    while True:
        play_speed = input('You usually play video at which speed (e.g., 0.75x, 1x, etc.). Enter only number: ').strip()
        if play_speed:
            play_speed = float(play_speed)
            break
        else:
            print("Please enter a valid number.")

    return {'start_date': start_date, 'daily_minutes': daily_minutes, 'days_factor': days_factor,
            'play_speed': play_speed}


def reset_start_date(initial_start_date: datetime, days_factor: int, daily_minutes: int) -> tuple[datetime, int]:
    start_date = initial_start_date + timedelta(days=days_factor)
    start_date = start_date.replace(
        hour=initial_start_date.hour, minute=initial_start_date.minute, second=0, microsecond=0
    )
    return start_date, daily_minutes


def determine_lecture_type(lecture_title: str) -> str:
    lecture_types = ["quiz", "practice", "challenge", "assignment"]
    for lec_type in lecture_types:
        if lec_type in lecture_title.lower():
            return lec_type
    return "Lecture"


def lecture_duration(duration_str: str) -> int:
    parts = list(map(int, duration_str.split(':')))
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 60 + parts[1] + math.ceil(parts[2] / 60)
    return 0


def section_total_minutes(duration_str: str) -> int:
    hours = int(re.search(r'(\d+)\s*hr', duration_str.lower()).group(1)) if 'hr' in duration_str else 0
    minutes = int(re.search(r'(\d+)\s*min', duration_str.lower()).group(1)) if 'min' in duration_str else 0
    return hours * 60 + minutes


# Notion related functions

def create_database(client: Client, page_id: str, title: str, is_inline: bool = True) -> str:
    db = {
        "parent": {"type": "page_id", "page_id": page_id},
        "is_inline": is_inline,
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": {
            "Done": {"checkbox": {}},
            "Lecture": {"title": {}},
            "Section": {"select": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Comfortable", "color": "green"},
                        {"name": "OK", "color": "blue"},
                        {"name": "Need more Info", "color": "red"},
                        {"name": "Skipped", "color": "yellow"}
                    ]
                }
            },
            "Type": {
                "select": {
                    "options": [
                        {"name": "Lecture", "color": "yellow"},
                        {"name": "Practice", "color": "blue"},
                        {"name": "Assignment", "color": "green"},
                        {"name": "Quiz", "color": "orange"},
                        {"name": "Challenge", "color": "red"}
                    ]
                }
            },
            "Time": {"number": {}},
            "Date": {"date": {}},
        }
    }

    response = client.databases.create(**db)
    return response["id"]


def create_page(client: Client, database_id: str, properties: dict) -> dict:
    new_page = {"parent": {"database_id": database_id}, "properties": properties}
    return client.pages.create(**new_page)


def prepare_page_properties(section_title: str, lecture_title: str, duration: int, start_date: datetime,
                            end_date: datetime, lec_type: str) -> dict:
    page = {
        "Lecture": {"title": [{"text": {"content": lecture_title}}]},
        "Time": {"number": duration},
        "Section": {"select": {"name": section_title}},
        "Date": {"date": {"start": start_date.isoformat(), "end": end_date.isoformat()}}
    }
    if lec_type:
        page["Type"] = {"select": {"name": lec_type}}

    return page


def create_block(client: Client, page_id: str, block_type: str, text: str) -> None:
    block_type_allowed = [
        "paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item",
        "numbered_list_item", "to_do", "toggle", "code", "quote", "callout", "embed",
        "bookmark", "image", "video", "pdf", "file", "audio", "table", "table_row", "divider",
        "breadcrumb", "table_of_contents", "link_to_page", "synced_block", "template", "column",
        "column_list", "ai_block"
    ]
    if block_type not in block_type_allowed:
        raise ValueError("Invalid block type specified.")

    new_block = {
        "children": [
            {
                "object": "block",
                "type": block_type,
                block_type: {"rich_text": [{"type": "text", "text": {"content": text}}]}
            }
        ]
    }
    client.blocks.children.append(block_id=page_id, **new_block)
