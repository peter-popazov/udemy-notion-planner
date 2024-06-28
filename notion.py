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

    if token is None or page_id is None:
        raise ValueError

    client = Client(auth=token)

    # Create callout block
    create_block(client, page_id, "callout", "This database was generated automatically")

    # Create the database
    db_id = create_database(client, page_id, data['title'])

    # Populate the database
    start_date = get_date()

    # Prompt the user for the days factor
    while True:
        try:
            days_factor = int(input("You want to study every i.e. 1 day, 2 days, etc.: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number of days i.e. 1, 2, 3, etc.")

    for section in data['sections']:
        section_title = section['section_title']
        for lecture in section['lectures']:
            lecture_title = lecture['lecture_title']
            duration_min = duration_to_minutes(lecture['duration'])

            if duration_min is None:
                duration_min = 0

            end_date = start_date + timedelta(minutes=duration_min)
            properties = prepare_page_properties(section_title, lecture_title, duration_min, start_date, end_date)

            response = create_page(client, db_id, properties)
            print(f"Created database page with ID: {response['id']}")

            # Increment start_date by one day for the next iteration
            start_date += timedelta(days=days_factor)


# Get start date from the user
def get_date():
    print("When do you want start learning?")
    date_input = input("Enter a date (YYYY-MM-DD): ")
    time_input = input("Enter a time (HH:MM): ")

    datetime_input = f"{date_input} {time_input}:00"
    try:
        parsed_datetime = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")
        return parsed_datetime
    except ValueError as e:
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
def prepare_page_properties(section_title, lecture_title, duration, start_date, end_date):
    return {
        "Lecture": {
            "title": [
                {
                    "text": {
                        "content": lecture_title
                    }
                }
            ]
        },
        "Section": {
            "select": {
                "name": section_title
            }
        },
        "Time": {
            "number": duration
        },
        "Date": {
            "date": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    }


# from MM:SS or HH:MM:SS to minutes
def duration_to_minutes(duration_str):
    parts = duration_str.split(':')
    if len(parts) == 2:
        return math.ceil(int(parts[0]) + int(parts[1]) / 60)
    elif len(parts) == 3:
        return math.ceil(int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60)


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
            {
                "object": "block",
                "type": block_type,
                block_type: {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": text}
                        }
                    ]
                }
            }
        ]
    }
    return client.blocks.children.append(block_id=page_id, **new_block)
