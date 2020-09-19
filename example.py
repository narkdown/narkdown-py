import sys
from config import token, page_url, database_url
from notion2github.exporter import NotionExporter

if __name__ == "__main__":
    # Get project README.md
    NotionExporter(token, ".").get_notion_page(
        url=page_url, create_page_directory=False
    )

    # Get directory README.md
    NotionExporter(token, "./docs").get_notion_page(
        url=page_url, create_page_directory=False
    )

    # Get all contents from database
    NotionExporter(token).get_notion_pages_from_database(
        url=database_url,
        category_column_name="Category",
        status_column_name="",
        current_status="",
        next_status="",
        filters={},
    )
