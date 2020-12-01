import os
import argparse
import json

from narkdown.exporter import NotionExporter
from .utils import *
from .constants import *


def parse_args():
    parser = argparse.ArgumentParser(description="Get contents from notion.")
    parser.add_argument("-t", "--token-v2")
    parser.add_argument("-u", "--url")
    parser.add_argument("-d", "--is-database", action="store_true", default=False)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    config = load_json(CONFIG_FILENAME) if os.path.isfile(CONFIG_FILENAME) else {}
    config = {}
    export_config = config.get("export_config") or {}
    database_config = config.get("database_config") or {}

    args.token_v2 = os.environ.get(TOKEN_NAME)

    if not args.token_v2:
        args.token_v2 = input("Enter notion token_v2: ")
    if not args.url:
        args.url = input("Enter notion url: ")
    if not args.is_database:
        args.is_database = input("Is this notion database page? (y/n): ") == "y"

    exporter = NotionExporter(token=args.token_v2, **export_config)

    if args.is_database:
        exporter.get_notion_pages_from_database(
            database_url=args.url, **database_config
        )
    else:
        exporter.get_notion_page(page_url=args.url)
