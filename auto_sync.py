import sys
from notion2github.exporter import NotionExporter

if __name__ == "__main__":
    token = sys.argv[1]
    database_url = sys.argv[2]

    """
    Get contents from the database that is in the "✅ Completed" state,
    and update it to the "🖨 Published" state.
    """
    NotionExporter(token).get_notion_pages_from_database(
        url=database_url,
        category_column_name="Category",
        status_column_name="Status",
        current_status="✅ Completed",
        next_status="🖨 Published",
        filters={},
    )
