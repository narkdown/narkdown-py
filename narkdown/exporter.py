import os
import sys
import requests
import re
from notion.client import NotionClient
from notion.settings import *
from .constants import *


class NotionExporter:
    def __init__(
        self,
        token,
        docs_directory="./docs",
        recursive_export=True,
        create_page_directory=True,
        add_metadata=False,
        lower_pathname=False,
        lower_filename=False,
        line_break=False,
    ):
        """Initialization of Notion Exporter

        Arguments
        ---------
        token : str
            The "token_v2" cookie from a logged-in browser session on Notion.so.

        docs_directory : str, optional
            Directory in which the Notion page to extract will be stored.

            Defaults to "./docs".
            e.g.
                "." : root directory.
                "./docs" : create "docs" folder in root directory.

        recursive_export : bool, optional
            Whether or not to recursively export child page.
            Defaults to True.

        create_page_directory : bool, optional
            Whether or not to create subdirectory with page title.
            Defaults to True.

        add_metadata : boolean, optional
            Whether or not to add metadata to content.
            Defaults to False

        lower_pathname : boolean, optional
            Whether or not to make pathname to lowercase.
            Defaults to False

        lower_filename : boolean, optional
            Whether or not to make filename to uppercase.
            Defaults to False

        line_break : boolean, optional
            Whether or not to convert empty blocks of notion to line break tag(<br />).
            Defaults to False
        """
        self.token = token
        self.client = NotionClient(token_v2=token)
        self.docs_directory = docs_directory
        self.recursive_export = recursive_export
        self.create_page_directory = create_page_directory
        self.add_metadata = add_metadata
        self.lower_pathname = lower_pathname
        self.lower_filename = lower_filename
        self.line_break = line_break

    def get_notion_page(
        self,
        page_url,
        sub_path="",
        created_time="",
        tags=[],
    ):
        """Get single Notion page to path

        Arguments
        ---------
        page_url : str
            URL of the Notion page to extract.

        sub_path : str, optional
            Specify where you want to save the file. If you pass parameter,
            then will be created directory under "docs_directory".
            Defaults to empty string.

        created_time : str, optional
            Specify date string before the filename.
            Defaults to empty string.

        tags : list, optional
            Add tag meta data to contents.
            Defaults to empty list.
        """
        page = self.client.get_block(page_url)

        path_set = [sub_path]
        if self.create_page_directory:
            path_set.append(page.title)

        sub_path = os.path.join(*path_set).replace(" ", "-")
        full_path = os.path.join(self.docs_directory, sub_path).replace(" ", "-")

        if self.lower_pathname:
            self.docs_directory = self.docs_directory.lower()
            sub_path = sub_path.lower()
            full_path = full_path.lower()

        create_directory(full_path)

        self.filename = ""

        if created_time:
            self.filename += created_time + "-"

        self.filename += re.sub(
            "--+", "-", re.sub(r"[\(\)\{\}\[\]\,\.\/ ]", "-", page.title)
        )

        if self.filename[-1] == "-":
            self.filename = self.filename[:-1]
        if self.filename[0] == "-":
            self.filename = self.filename[1:]

        if self.lower_filename:
            self.filename = self.filename.lower()

        self.image_number = 0

        post = ""

        if self.add_metadata:
            post = "---\n"
            post += "id: " + self.filename + "\n"
            post += "title: '" + page.title + "'\n"
            if tags:
                post += "tags: " + str(tags) + "\n"
            post += "---\n\n"
        else:
            post = "# " + page.title + "\n\n"

        post = post + self.parse_notion_blocks(
            page.children, sub_path, created_time, ""
        )

        write_post(post, full_path, self.filename)

        if len(sub_path) != 0:
            full_path += "/"

        print(
            '✅ Successfully exported page To "{0}.md" From "{1}"'.format(
                full_path + self.filename, page.get_browseable_url()
            )
        )

    def get_notion_pages_from_database(
        self,
        database_url,
        category_column_name="",
        tags_column_name="",
        created_time_column_name="",
        status_column_name="",
        current_status="",
        next_status="",
        filters={},
    ):
        """Get Notion pages from database to "docs_directory"

        Arguments
        ---------
        database_url : str
            URL of the Notion database to extract.

        category_column_name : str, optional
            In Notion database, content can be classified by category by select property.
            When you create the select property in the Notion database and pass the name of the column, folders are created by category.
            Defaults to empty string.

        tags_column_name : str, optional
            In the Notion database, you can tag content with "Multi Select" property.
            If you create a "Multi Select" property in the Notion database and pass the name of the column,
            then meta data will be insterted to contents. (should set add_metadata to True.)
            Defaults to empty string.

        created_time_column_name : str, optional
            In the Notion database, you can manage created time of content with "Created Time" property.
            If you create a "Created Time" property in the Notion database and pass the name of the column,
            you can add created time to filename. (e.g. 2020-12-02-some-title.md)
            Defaults to empty string.

        status_column_name : str, optional
            In the Notion database, you can manage the status of content with "Select" property.
            If you create a "Select" property in the Notion database and pass the name of the column,
            you can import contents in a specific state or change the status of the content. (should be used with the current_status or next_status option.)
            Defaults to empty string.

        current_status : str, optional
            Import only the content that corresponds to current_status value. ( status_column_name must be set.)
            Defaults to empty string.

        next_status : str, optional
            Changes content status to next_status value after import. ( status_column_name must be set.)
            Defaults to empty string.

        filters : dict, optional
            Key, value pair of filter list to apply to the Notion database.
            Defaults to empty dict.
        """
        collection = self.client.get_block(database_url).collection

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
            path = ""
            if category_column_name and page.get_property(category_column_name):
                path = page.get_property(category_column_name).replace(" ", "-")
                path = re.sub("--+", "-", re.sub(r"[\(\)\{\}\[\]\,\.\/ ]", "-", path))

            tags = []
            if tags_column_name and page.get_property(tags_column_name):
                tags = page.get_property(tags_column_name)

            created_time = ""
            if created_time_column_name and page.get_property(created_time_column_name):
                created_time = page.get_property(created_time_column_name).strftime(
                    "%Y-%m-%d"
                )

            self.get_notion_page(
                page.get_browseable_url(),
                sub_path=path,
                tags=tags,
                created_time=created_time,
            )

            if next_status:
                page.set_property(status_column_name, next_status)

    def parse_notion_blocks(self, blocks, path, created_time, offset):
        """Parse Notion blocks

        Arguments
        ---------
        blocks : list
            Block list in Notion page to parse.

        path : str
            Path where "ChildPage blocks" or "Image blocks" will be stored.

        created_time : str
            Specify created time string before the filename.

        offset : str
            Parameter to support indentation of blocks.

        Returns
        ---------
        contents : str
            Markdown contents
        """
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
                contents += "```" + block.language.lower() + "\n"
                contents += offset
                contents += offset.join(block.title.splitlines(True)) + "\n"
                contents += offset + "```"
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
                if (
                    self.recursive_export
                    and self.client.get_block(block.id).parent == block.parent
                ):
                    filename = self.filename
                    parent_image_number = self.image_number

                    self.get_notion_page(
                        block.get_browseable_url(),
                        sub_path=path,
                        created_time=created_time,
                    )
                    contents += "[{0}]({1}/{1}.md)".format(
                        block.title, block.title.replace(" ", "-")
                    )
                    self.filename = filename
                    self.image_number = parent_image_number
                else:
                    contents += (
                        "[" + block.title + "](" + block.get_browseable_url() + ")"
                    )
            elif block.type == "image":
                image_path = self.get_image_path(path, block.source)
                contents += "![{0}-image-{1}]({2})".format(
                    self.filename, str(self.image_number), image_path
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
                if block.title:
                    contents += block.title
                elif self.line_break:
                    contents += "<br />"
            elif block.type == "collection_view":
                if block.collection:
                    contents += self.parse_notion_collection(block.collection, offset)
                else:
                    block.remove()

            if block.type == "collection_view":
                contents += "\n"
            elif block.type != "text":
                contents += "\n\n"
            elif block.title:
                contents += "\n\n"
            elif self.line_break:
                contents += "\n\n"

            if block.children:
                if block.type == "page":
                    continue
                elif block.type == "toggle":
                    contents += self.parse_notion_blocks(
                        block.children, path, created_time, offset + "   "
                    )
                    contents += offset + "  </details>\n\n"
                else:
                    contents += self.parse_notion_blocks(
                        block.children, path, created_time, offset + "   "
                    )

        return contents

    def get_image_path(self, path, source):
        """Get image and return path of image file.

        Arguments
        ---------
        path : str
            Path where "Image" will be stored.

        source : str
            Image source to get.

        Returns
        ---------
        image_path or source : str
            If image is uploaded, download it first and return path of image file.
            If image is linked, then return URL of image source.
        """
        if source.startswith(S3_URL_PREFIX_ENCODED):
            create_directory(os.path.join(self.docs_directory, path, "images"))

            type = "".join(filter(lambda i: i in source, IMAGE_TYPES))
            image_path = "images/{0}-image-{1}.{2}".format(
                self.filename, self.image_number, type
            )

            try:
                r = requests.get(source, allow_redirects=True)
                open(os.path.join(self.docs_directory, path, image_path), "wb").write(
                    r.content
                )
            except HTTPError as e:
                print(e.code)
            except URLError as e:
                print(e.reason)

            return image_path

        return source

    def parse_notion_collection(self, table, offset):
        """Parse Notion collection(aka table or database)

        Arguments
        ---------
        table : <class 'notion.collection.Collection'>
            Notion table block.

        offset : str
            Parameter to support indentation of blocks.

        Returns
        ---------
        contents : str
            Markdown contents
        """

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


def write_post(post, path, title):
    file = open(path + "/" + title + ".md", "w")
    file.write(post)
