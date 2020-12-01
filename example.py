import sys
import json
from narkdown.exporter import NotionExporter

if __name__ == "__main__":
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except:
        config = {}

    print(config)
    # token = config["TOKEN"]
    # readme_url = config["README_URL"]
    # database_url = config["DATABASE_URL"]

    # # Get project README.md
    # NotionExporter(
    #     token=token,
    #     docs_directory="./docs",
    #     recursive_export=False,
    #     create_page_directory=False,
    #     add_metadata=False,
    #     lower_pathname=False,
    #     lower_filename=False,
    #     line_break=False,
    # ).get_notion_page(page_url=readme_url)

    # # Get all contents from database
    # NotionExporter(
    #     token=token,
    #     docs_directory="./docs",
    #     recursive_export=True,
    #     create_page_directory=False,
    #     add_metadata=True,
    #     lower_pathname=True,
    #     lower_filename=True,
    #     line_break=False,
    # ).get_notion_pages_from_database(
    #     database_url=database_url,
    #     category_column_name="Category",
    #     tags_column_name="Tags",
    #     created_time_column_name="Created Time",
    #     status_column_name="Status",
    #     current_status="✅ Completed",
    #     next_status="🖨 Published",
    #     filters={},
    # )
