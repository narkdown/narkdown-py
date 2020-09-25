import sys
import json
from notion2github.exporter import NotionExporter

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    token = config["TOKEN"]
    readme_url = config["README_URL"]
    docs_page_url = config["DOCS_PAGE_URL"]
    database_url = config["DATABASE_URL"]

    # Get project README.md
    NotionExporter(token, ".").get_notion_page(
        url=readme_url, create_page_directory=False
    )

    # Get directory README.md
    NotionExporter(token, "./docs").get_notion_page(
        url=docs_page_url, create_page_directory=False
    )

    # Get all contents from database
    NotionExporter(token).get_notion_pages_from_database(
        url=database_url,
        category_column_name="Category",
        status_column_name="Status",
        current_status="",
        next_status="",
        filters={},
    )
