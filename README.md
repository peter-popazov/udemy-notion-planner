# Notion Planner Automation

## Description

This Python program automates the creation of a study planner in Notion. It reads user inputs for study start date,
daily study hours, and the interval of study days. It then organizes lecture sections and lectures into a Notion
database, automatically scheduling each lecture while ensuring that the daily study hours are not exceeded.

## Prerequisites

- Python 3.x
- Notion API Token
- `dotenv` for environment variable management
- `notion-client` for interacting with the Notion API
- `selenium` for interacting with web application
- `beautifulsoup` for parsing the page

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/peter-popazov/udemy-notion-planner
    cd udemy-notion-planner
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add your Notion API token and page ID:

    ```env
    NOTION_TOKEN=your_notion_token
    NOTION_PAGE_ID=your_notion_page_id
    ```
   
4. Provide url of the Udemy course in the main.py

   ```
   url=https://www.udemy.com/course/course-name
   ```
   
## Usage

1. Follow Notion Docs on how to get Internal Integration Secret and Give your integration page permissions
   
   ```
   https://developers.notion.com/docs/create-a-notion-integration#getting-started
   ```

2. Obtain _NOTION_PAGE_ID_.

   ```
   By pressing CTRL+L in the created page from / to ? is your NOTION_PAGE_ID
   ```

3. Provide both Internal Integration Secret (_NOTION_TOKEN_) and _NOTION_PAGE_ID_ in .env file

4. Run the script:

   ```bash
   python main.py
   ```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.