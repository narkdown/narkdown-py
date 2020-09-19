import os
import sys
import requests
from .config import token, page_url, database_url
from .constants import *
from .notion.client import NotionClient


class Notion2Github:
    def __init__(
        self,
        token,
        docs_directory="./docs",
    ):
        self.token = token
        self.client = NotionClient(token_v2=token)
        self.docs_directory = docs_directory
        self.image_number = 0

    def get_notion_page(self, url, path="", create_page_directory=True):
        page = self.client.get_block(url)

        if not path:
            path = self.docs_directory

        if create_page_directory:
            path = os.path.join(path, page.title)
        else:
            path = os.path.join(path)

        create_directory(os.path.join(path, "images"))

        post = "# " + page.title + "\n\n"
        post = post + self.parse_notion_contents(page.children, path, "")

        write_post(post, path)

        print(
            '✅ Successfully exported page To "{0}" From "{1}"'.format(
                path, page.get_browseable_url()
            )
        )

    def get_notion_pages_from_database(
        self,
        url,
        category_column_name="",
        status_column_name="",
        current_status="",
        next_status="",
        filters={},
    ):

        collection = self.client.get_block(url).collection

        if status_column_name:
            try:
                status_options = list(
                    map(
                        lambda i: i["value"],
                        collection.get_schema_property(status_column_name)["options"],
                    )
                )
            except AttributeError:
                print('Status column should be "Select" property.')

        if current_status and current_status not in status_options:
            print('"{0}" is not in status list.'.format(current_status))
            return
        if next_status and next_status not in status_options:
            print('"{0}" is not in status list.'.format(next_status))
            return

        pages = collection.get_rows()

        if current_status:
            pages = list(
                filter(
                    lambda page: page.get_property(status_column_name)
                    == current_status,
                    pages,
                )
            )

        for key, value in filters.items():
            pages = list(filter(lambda page: page.get_property(key) == value, pages))

        for page in pages:
            path_set = (
                [
                    self.docs_directory,
                    page.get_property(category_column_name),
                    page.title,
                ]
                if category_column_name and page.get_property(category_column_name)
                else [self.docs_directory, page.title]
            )

            path = os.path.join(*path_set)
            create_directory(os.path.join(path, "images"))

            post = "# " + page.title + "\n\n"
            post = post + self.parse_notion_contents(page.children, path, "")

            write_post(post, path)

            if next_status:
                page.set_property(status_column_name, next_status)

            print(
                '✅ Successfully exported page To "{0}" From "{1}"'.format(
                    path, page.get_browseable_url()
                )
            )

    def parse_notion_contents(self, blocks, path, offset):
        contents = ""

        for index, block in enumerate(blocks):
            contents += offset
            if block.type == "header":
                contents += "## " + block.title
            elif block.type == "sub_header":
                contents += "### " + block.title
            elif block.type == "sub_sub_header":
                contents += "#### " + block.title
            elif block.type == "code":
                contents += (
                    "```" + block.language.lower() + "\n" + block.title + "\n```"
                )
            elif block.type == "callout":
                contents += "> " + block.icon + " " + block.title
            elif block.type == "quote":
                contents += "> " + block.title
            elif block.type == "divider":
                if blocks[index - 1].type == "header":
                    continue
                contents += "---"
            elif block.type == "bookmark":
                contents += "[" + block.title + "](" + block.link + ")"
            elif block.type == "page":
                if self.client.get_block(block.id).parent == block.parent:
                    self.get_notion_page(block.get_browseable_url(), path=path)
                    contents += (
                        "["
                        + block.title
                        + "]("
                        + block.title.replace(" ", "%20")
                        + "/README.md)"
                    )
                else:
                    contents += (
                        "[" + block.title + "](" + block.get_browseable_url() + ")"
                    )
            elif block.type == "image":
                image_path = self.get_image_path(path, block.source)
                contents += (
                    "![image-" + str(self.image_number) + "](" + image_path + ")"
                )
                self.image_number += 1
            elif block.type == "bulleted_list":
                contents += "- " + block.title
            elif block.type == "numbered_list":
                contents += "1. " + block.title
            elif block.type == "to_do":
                contents += "- [ ] " + block.title
            elif block.type == "toggle":
                contents += "- <details><summary>" + block.title + "</summary>"
            elif block.type == "text":
                contents += block.title
            elif block.type == "collection_view":
                contents += self.parse_notion_collection(block.collection, offset)

            contents += "\n\n"

            if block.children:
                if block.type == "page":
                    continue
                elif block.type == "toggle":
                    contents += self.parse_notion_contents(
                        block.children, path, offset + "\t"
                    )
                    contents += offset + "  </details>\n\n"
                else:
                    contents += self.parse_notion_contents(
                        block.children, path, offset + "\t"
                    )

        return contents

    def get_image_path(self, path, source):
        if source.startswith(S3_URL_PREFIX_ENCODED):
            type = "".join(filter(lambda i: i in source, IMAGE_TYPES))
            image_path = "images/image-{0}.{1}".format(self.image_number, type)

            try:
                r = requests.get(source, allow_redirects=True)
                open(os.path.join(path, image_path), "wb").write(r.content)
            except HTTPError as e:
                print(e.code)
            except URLError as e:
                print(e.reason)

            return image_path

        return source

    def parse_notion_collection(self, table, offset):
        columns = list(
            map(
                lambda i: {"id": i["id"], "name": i["name"], "type": i["type"]},
                table.get_schema_properties(),
            )
        )

        contents = "| " + " | ".join(map(lambda i: i["name"], columns)) + " |\n"
        contents += offset + "| " + " | ".join(map(lambda i: "---", columns)) + " |\n"

        for row in table.get_rows():
            contents += offset
            for column in columns:
                contents += "| "
                data = row.get_property(column["id"])
                if data is None or not data:
                    contents += "   "
                elif column["type"] == "date":
                    contents += ("" if data.start is None else str(data.start)) + (
                        "" if data.end is None else " -> " + str(data.end)
                    )
                elif column["type"] == "person":
                    contents += ", ".join(map(lambda i: i.full_name, data))
                elif column["type"] == "file":
                    contents += ", ".join(map(lambda i: "[link](" + i + ")", data))
                elif column["type"] == "select":
                    contents += str([data])
                elif column["type"] == "multi_select":
                    contents += ", ".join(map(lambda i: "[" + i + "]", data))
                elif column["type"] == "checkbox":
                    contents += "✅" if data else "⬜️"
                else:
                    contents += str(data)
                contents += " "
            contents += "|\n"

        return contents


def create_directory(path):
    if not (os.path.isdir(path)):
        try:
            os.makedirs(path)
        except:
            pass


def write_post(post, path):
    file = open(path + "/README.md", "w")
    file.write(post)
