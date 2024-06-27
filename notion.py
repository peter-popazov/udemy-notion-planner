import os
import math
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime, timedelta


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Initialize Notion client
    token = os.getenv('NOTION_TOKEN')
    page_id = os.getenv('NOTION_PAGE_ID')
    client = Client(auth=token)

    data = {
        'sections': [
            {
                'lectures': [
                    {'duration': '10:42', 'lecture_title': 'Lecture1'},
                    {'duration': '17:43', 'lecture_title': 'Lecture2'}
                ],
                'section_title': 'Intro'
            }
        ],
        'title': 'Introduction To Fiber Optic Cabling'
    }

    # Create the database
    db_id = create_database(client, page_id, data['title'])

    create_block(client, page_id, "callout", "This database was generated automatically")

    # Populate the database
    for section in data['sections']:
        section_title = section['section_title']
        for lecture in section['lectures']:
            lecture_title = lecture['lecture_title']
            duration_min = duration_to_minutes(lecture['duration'])

            start_date = datetime.now()
            end_date = start_date + timedelta(minutes=duration_min)
            properties = prepare_page_properties(section_title, lecture_title, duration_min, start_date, end_date)

            response = create_page(client, db_id, properties)
            print(f"Created page with ID: {response['id']}")


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


def create_page(client, database_id, properties):
    new_page = {
        "parent": {"database_id": database_id},
        "properties": properties
    }
    return client.pages.create(**new_page)


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


def duration_to_minutes(duration_str):
    parts = duration_str.split(':')
    if len(parts) == 2:
        return math.ceil(int(parts[0]) + int(parts[1]) / 60)
    elif len(parts) == 3:
        return math.ceil(int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60)


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


if __name__ == "__main__":
    main()
