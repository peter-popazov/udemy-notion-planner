from dotenv import load_dotenv
from notion_client import Client
from pprint import pprint
import os


def main():
    # Load environment variables from .env file
    load_dotenv()

    notion_token = os.getenv('NOTION_TOKEN')
    notion_page_id = os.getenv('NOTION_PAGE_ID')

    client = Client(auth=notion_token)

    create_block(client, notion_page_id, "callout", "Udemy Course")
    create_database(client, notion_page_id, "SAMPLE DB", )

    page_response = client.pages.retrieve(notion_page_id)
    pprint(page_response)


def create_block(client, page_id, block_type, text):
    client.blocks.children.append(
        **{"block_id": page_id,
           "children": [
               {
                   "object": "block",
                   "type": block_type,
                   block_type: {
                       "rich_text": [{
                           "type": "text",
                           "text": {
                               "content": text
                           }
                       }]
                   }
               }
           ]}
    )


def write_to_database(client, db_id, content):
    client.pages.create(
        **{
            "parent": {
                "database_id": db_id
            },
            "properties": {
                "Name": {'title': [{"text": {"content": "hello"}}]},
                "Tags": {"select": {"name": "hi!"}}
            }
        }
    )


def create_database(client, page_id, title, is_inline=True):
    client.databases.create(
        **{
            "parent": {
                "type": "page_id",
                "page_id": page_id
            },
            "is_inline": is_inline,
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ],
            "properties": {
                "Lecture Title": {
                    "title": {}
                },
                "Status": {
                    "select": {
                        "options": [
                            {
                                "name": "Comfortable",
                                "color": "green"
                            },
                            {
                                "name": "OK",
                                "color": "blue"
                            },
                            {
                                "name": "Need More Info",
                                "color": "red"
                            },
                            {
                                "name": "Skipped",
                                "color": "yellow"
                            }
                        ]
                    }
                },
                "Time": {
                    "number": {}
                },
                "Date": {
                    "date": {}
                },
                "?": {
                    "checkbox": {}
                }
            }
        }
    )


if __name__ == "__main__":
    main()
