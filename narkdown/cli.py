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
    parser.add_argument("-d", "--docs-directory")
    parser.add_argument("-fp", "--filter-prop")
    parser.add_argument("-fv", "--filter-value")
    parser.add_argument("-i", "--is-database", action="store_true", default=False)

    return parser.parse_args()


def validate_args(args):
    token_v2 = args.token_v2 or os.environ.get(TOKEN_NAME)
    url = args.url
    docs_directory = args.docs_directory
    filters = {}
    is_database = args.is_database

    if not token_v2:
        token_v2 = input("Enter notion token_v2: ")
    if not url:
        url = input("Enter notion url: ")
    if not docs_directory:
        docs_directory = inputWithDefault("Enter target directory?", "./docs")
    if not is_database:
        is_database = (
            inputWithDefault("Is this notion database page? (y/n)", "n") == "y"
        )
    if args.filter_prop and args.filter_value:
        filters.update({args.filter_prop: args.filter_value})

    return token_v2, url, docs_directory, filters, is_database


def get_config():
    config = load_json(CONFIG_FILENAME) if os.path.isfile(CONFIG_FILENAME) else {}
    export_config = config.get("export_config") or {}
    database_config = config.get("database_config") or {}

    return export_config, database_config


def main():
    token_v2, url, docs_directory, filters, is_database = validate_args(parse_args())
    export_config, database_config = get_config()

    export_config.update({"docs_directory": docs_directory})
    database_config.update({"filters": filters})

    exporter = NotionExporter(token=token_v2, **export_config)

    if is_database:
        exporter.get_notion_pages_from_database(database_url=url, **database_config)
    else:
        exporter.get_notion_page(page_url=url)
