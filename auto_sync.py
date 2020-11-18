import sys
from narkdown.exporter import NotionExporter

if __name__ == "__main__":
    token = sys.argv[1]
    database_url = sys.argv[2]

    """
    Get contents from the database that is in the "✅ Completed" state,
    and update it to the "🖨 Published" state.
    """
    NotionExporter(
        token=token,
        docs_directory="./docs",
        create_page_directory=False,
        add_metadata=True,
    ).get_notion_pages_from_database(
        url=database_url,
        category_column_name="Category",
        tags_column_name="Tags",
        status_column_name="Status",
        current_status="✅ Completed",
        next_status="🖨 Published",
        filters={},
        add_date_to_filename=True,
    )
