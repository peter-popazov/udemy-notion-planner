from notion_client import Client
from constatnts import *


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
                    "options": STATUS_OPTIONS
                }
            },
            "Type": {
                "select": {
                    "options": TYPE_OPTIONS
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


def prepare_page_properties(page_data: dict) -> dict:
    page = {
        "Lecture": {"title": [{"text": {"content": page_data["title"]}}]},
        "Type": {"select": {"name": page_data["category"]}},
        "Time": {"number": page_data["duration"]},
        "Section": {"select": {"name": page_data["section_title"]}},
        "Date": {"date": {"start": page_data["start_date"].isoformat(), "end": page_data["end_date"].isoformat()}}
    }

    return page


def create_block(client: Client, page_id: str, block_type: str, text: str) -> None:
    if block_type not in ALLOWED_BLOCK_TYPES:
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
