import sys
import json
from narkdown.exporter import NotionExporter

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    token = config["TOKEN"]
    readme_url = config["README_URL"]
    docs_page_url = config["DOCS_PAGE_URL"]
    database_url = config["DATABASE_URL"]

    # Get project README.md
    NotionExporter(
        token=token,
        docs_directory=".",
        create_page_directory=False,
        add_metadata=False,
    ).get_notion_page(url=readme_url)

    # Get directory README.md
    NotionExporter(
        token=token,
        docs_directory="./docs",
        create_page_directory=False,
        add_metadata=False,
    ).get_notion_page(url=docs_page_url)

    # Get all contents from database
    NotionExporter(
        token=token,
        docs_directory="./docs",
        create_page_directory=False,
        add_metadata=True,
        lower_pathname=True,
        lower_filename=True,
    ).get_notion_pages_from_database(
        url=database_url,
        category_column_name="Category",
        tags_column_name="Tags",
        created_time_column_name="Created Time",
        status_column_name="Status",
        current_status="",
        next_status="",
        filters={},
    )
