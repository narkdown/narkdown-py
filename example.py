import os
from narkdown.exporter import NotionExporter

if __name__ == "__main__":
    token = "YOUR_NOTION_TOKEN"
    page_url = "NOTION_PAGE_URL"
    database_url = "NOTION_DATABASE_URL"

    notion_exporter = NotionExporter(token)
    notion_exporter.get_notion_page(page_url)
    notion_exporter.get_notion_pages_from_database(database_url)
