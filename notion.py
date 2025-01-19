import math
import os
import re

from notion_helpers import prepare_page_properties, create_page, create_database, create_block
from datetime import datetime
from datetime import timedelta

from dotenv import load_dotenv
from notion_client import Client

from predict_category import predict_lecture_category

SKIP_LECTURE_TIME = 20


def setup_notion() -> tuple[Client, str]:
    load_dotenv()

    token = os.getenv('NOTION_TOKEN')
    page_id = os.getenv('NOTION_PAGE_ID')

    if not token or not token.strip():
        raise ValueError("Notion token is empty or missing")
    if not page_id or not page_id.strip():
        raise ValueError("Page ID is empty or missing")

    client = Client(auth=token)
    create_block(client, page_id, "callout", "This database was generated automatically")

    return client, page_id


def planner_create_block(data: dict) -> None:
    client, page_id = setup_notion()
    db_id = create_database(client, page_id, data['title'])

    start_date, daily_minutes, days_factor, play_speed = get_user_input()
    current_date = start_date

    for section in data['sections']:
        section_time = math.ceil(section_total_minutes(section['time']) / play_speed)
        counter_parts = 1

        while section_time > 0:
            if section_time < SKIP_LECTURE_TIME:
                print(f"Remaining time [{section_time}] min. is less than {SKIP_LECTURE_TIME} minutes, skipping.")
                break

            time_for_page = min(daily_minutes, section_time)

            start_date_next = current_date
            end_date = start_date_next + timedelta(minutes=time_for_page)

            properties = prepare_page_properties({
                "title": f"{section['section_title']} p.{counter_parts}",
                "category": "study block",
                "duration": time_for_page,
                "section_title": section["section_title"],
                "start_date": start_date_next,
                "end_date": end_date
            })

            response = create_page(client, db_id, properties)
            print(f"Created database page with ID: {response['id']}")

            section_time -= time_for_page
            current_date = current_date + timedelta(days=days_factor)
            counter_parts += 1


def planner_create_separate(data: dict) -> None:
    client, page_id = setup_notion()
    db_id = create_database(client, page_id, data['title'])

    start_date, daily_minutes, days_factor, play_speed = get_user_input()
    current_date = start_date
    remaining_minutes = daily_minutes
    counter = 0

    for section in data['sections']:
        section_title = section['section_title']

        for lecture in section['lectures']:
            lecture_title = lecture['lecture_title']

            duration_min = math.ceil(get_lecture_duration(lecture['duration']) / play_speed)
            category = predict_lecture_category(lecture_title)

            # If lecture won't fit in current day's remaining time, move to the next day
            if duration_min > remaining_minutes:
                current_date = start_date + timedelta(days=(days_factor * counter))
                current_date = current_date.replace(
                    hour=start_date.hour,
                    minute=start_date.minute,
                    second=0,
                    microsecond=0
                )
                remaining_minutes = daily_minutes
                counter += 1

            lecture_end = current_date + timedelta(minutes=duration_min)

            properties = prepare_page_properties({
                "title": lecture_title,
                "category": category,
                "duration": duration_min,
                "section_title": section_title,
                "start_date": current_date,
                "end_date": lecture_end
            })

            response = create_page(client, db_id, properties)
            print(f"Created database page with ID: {response['id']}")

            remaining_minutes -= duration_min
            current_date = lecture_end

            if duration_min > remaining_minutes:
                current_date = start_date + timedelta(days=(days_factor * counter))
                current_date = current_date.replace(
                    hour=start_date.hour,
                    minute=start_date.minute,
                    second=0,
                    microsecond=0
                )
                remaining_minutes = daily_minutes
                counter += 1


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

    while True:
        try:
            days_factor = int(input("You want to study every i.e. 1 day, 2 days, etc.: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number of days i.e. 1, 2, 3, etc.")

    while True:
        play_speed = input('You usually play video at what speed (e.g., 0.75x, 1x, etc.). Enter only number: ').strip()
        if play_speed:
            play_speed = float(play_speed)
            break
        else:
            print("Please enter a valid number.")

    return start_date, daily_minutes, days_factor, play_speed


def reset_start_date(start_date: datetime, interval_days: int, minutes_per_day: float) -> tuple[datetime, float]:
    updated_date = start_date + timedelta(days=interval_days)
    updated_date = updated_date.replace(hour=start_date.hour, minute=start_date.minute, second=0, microsecond=0)
    return updated_date, minutes_per_day


def get_lecture_duration(duration_str: str) -> int:
    parts = list(map(int, duration_str.split(':')))
    if len(parts) == 2:
        return parts[0] + math.ceil(parts[1] / 60)
    elif len(parts) == 3:
        return parts[0] * 60 + parts[1] + math.ceil(parts[2] / 60)
    return 0


def section_total_minutes(duration_str: str) -> int:
    hours = int(re.search(r'(\d+)\s*hr', duration_str.lower()).group(1)) if 'hr' in duration_str else 0
    minutes = int(re.search(r'(\d+)\s*min', duration_str.lower()).group(1)) if 'min' in duration_str else 0
    return hours * 60 + minutes
