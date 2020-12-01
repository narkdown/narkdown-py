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


def validate_args(args):
    token_v2 = args.token_v2 or os.environ.get(TOKEN_NAME)
    url = args.url
    is_database = args.is_database

    if not token_v2:
        token_v2 = input("Enter notion token_v2: ")
    if not url:
        url = input("Enter notion url: ")
    if not is_database:
        is_database = input("Is this notion database page? (y/n): ") == "y"

    return token_v2, url, is_database


def get_config():
    config = load_json(CONFIG_FILENAME) if os.path.isfile(CONFIG_FILENAME) else {}
    export_config = config.get("export_config") or {}
    database_config = config.get("database_config") or {}

    return export_config, database_config


def main():
    token_v2, url, is_database = validate_args(parse_args())
    export_config, database_config = get_config()

    exporter = NotionExporter(token=token_v2, **export_config)

    if is_database:
        exporter.get_notion_pages_from_database(database_url=url, **database_config)
    else:
        exporter.get_notion_page(page_url=url)
