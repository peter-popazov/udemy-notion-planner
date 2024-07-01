import os
import math
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime, timedelta


def planer_create(data):
    # Load environment variables from .env file
    load_dotenv()

    # Initialize Notion client
    token = os.getenv('NOTION_TOKEN')
    page_id = os.getenv('NOTION_PAGE_ID')

    if not token or not page_id:
        raise ValueError("Missing Notion token or page ID")

    client = Client(auth=token)

    # Create callout block
    create_block(client, page_id, "callout", "This database was generated automatically")

    # Create the database
    db_id = create_database(client, page_id, data['title'])

    initial_start_date = get_date()
    while not initial_start_date:
        initial_start_date = get_date()
    start_date = initial_start_date

    # Store the initial start time
    initial_start_time = initial_start_date.time()

    # Get user inputs
    days_factor = get_days_factor()
    daily_minutes = get_daily_minutes()
    daily_minutes_remaining = daily_minutes

    for section in data['sections']:
        section_title = section['section_title']
        for lecture in section['lectures']:
            lecture_title = lecture['lecture_title']
            duration_min = duration_to_minutes(lecture['duration'])

            # Determine the lecture type
            lec_type = determine_lecture_type(lecture_title)

            # Handle cases where duration parsing fails
            if duration_min is None:
                duration_min = 0

            # Check if the lecture fits within the daily limit
            if duration_min > daily_minutes_remaining:
                # Move to the next study day at the specified start time
                start_date += timedelta(days=days_factor)
                start_date = start_date.replace(hour=initial_start_time.hour, minute=initial_start_time.minute,
                                                second=0, microsecond=0)
                daily_minutes_remaining = daily_minutes

            end_date = start_date + timedelta(minutes=duration_min)

            # Decrease the remaining minutes for the day
            daily_minutes_remaining -= duration_min

            # Check if the lecture exceeds the day limit and move to the next day if necessary
            if daily_minutes_remaining < 0:
                # Move to the next study day at the specified start time
                start_date += timedelta(days=days_factor)
                start_date = start_date.replace(hour=initial_start_time.hour, minute=initial_start_time.minute,
                                                second=0, microsecond=0)
                daily_minutes_remaining = daily_minutes - duration_min  # Start the new day with the current lecture

            properties = prepare_page_properties(section_title, lecture_title, duration_min, start_date, end_date, lec_type)

            response = create_page(client, db_id, properties)
            print(f"Created database page with ID: {response['id']}")

            # Update start_date to end_date for the next lecture
            start_date = end_date


def get_days_factor():
    while True:
        try:
            days_factor = int(input("You want to study every i.e. 1 day, 2 days, etc.: "))
            return days_factor
        except ValueError:
            print("Invalid input. Please enter a valid number of days i.e. 1, 2, 3, etc.")


def get_daily_minutes():
    while True:
        try:
            daily_hours = float(input("How many hours a day do you want to study?: "))
            daily_minutes = int(daily_hours * 60)
            return daily_minutes
        except ValueError:
            print("Invalid input. Please enter a valid number of hours.")


# Determine the type of lecture based on title
def determine_lecture_type(lecture_title):
    if "Quiz" in lecture_title:
        return "Quiz"
    elif "Practice" in lecture_title or "practice" in lecture_title:
        return "Practice"
    elif "Challenge" in lecture_title or "challenge" in lecture_title:
        return "Challenge"
    elif "Assignment" in lecture_title or "assignment" in lecture_title:
        return "Assignment"
    else:
        return "Lecture"


# Get start date from the user
def get_date():
    print("When do you want start learning?")
    date_input = input("Enter a date (YYYY-MM-DD): ")
    time_input = input("Enter a time (HH:MM): ")

    datetime_input = f"{date_input} {time_input}:00"
    try:
        parsed_datetime = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")
        return parsed_datetime
    except ValueError:
        print("Invalid date or time format. Please try again.")
        return None


# Created database with specified columns, return id of the created db
def create_database(client, page_id, title, is_inline=True):
    db = {
        "parent": {"type": "page_id", "page_id": page_id},
        "is_inline": is_inline,
        "title": [
            {
                "type": "text", "text": {"content": title}
            }
        ],
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


# creates a page in a database
def create_page(client, database_id, properties):
    new_page = {
        "parent": {"database_id": database_id},
        "properties": properties
    }
    return client.pages.create(**new_page)


# prepares data to be filled in a database
def prepare_page_properties(section_title, lecture_title, duration, start_date, end_date, lec_type):
    return {
        "Lecture": {"title": [{"text": {"content": lecture_title}}]},
        "Section": {"select": {"name": section_title}},
        "Type": {"select": {"name": lec_type}},
        "Time": {"number": duration},
        "Date": {"date": {"start": start_date.isoformat(), "end": end_date.isoformat()}}
    }


# from MM:SS or HH:MM:SS to minutes
def duration_to_minutes(duration_str):
    parts = duration_str.split(':')
    if len(parts) == 2:
        return math.ceil(int(parts[0]) + int(parts[1]) / 60)
    elif len(parts) == 3:
        return math.ceil(int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60)
    else:
        return None


# created a block in a page
def create_block(client, page_id, block_type, text):
    if block_type not in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item",
                          "numbered_list_item", "to_do", "toggle", "code", "quote", "callout", "embed", "bookmark",
                          "image", "video", "pdf", "file", "audio", "table", "table_row", "divider", "breadcrumb",
                          "table_of_contents", "link_to_page", "synced_block", "template", "column", "column_list",
                          "ai_block"]:
        raise ValueError("Invalid block type specified.")

    new_block = {
        "children": [
            {"object": "block", "type": block_type,
             block_type: {"rich_text": [{"type": "text", "text": {"content": text}}]}}]}
    return client.blocks.children.append(block_id=page_id, **new_block)
