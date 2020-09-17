import sys
from .config import token, page_url, database_url
from .notion2github import Notion2Github

if __name__ == "__main__":
    Notion2Github(token).get_notion_page(page_url)
