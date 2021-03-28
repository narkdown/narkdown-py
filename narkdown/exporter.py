import os
import sys
import requests
import re
from .notion.client import NotionClient
from .notion.settings import *
from .constants import *
from .utils import *


class NotionExporter:
    def __init__(
        self,
        token,
        docs_directory="./docs",
        recursive_export=True,
        create_page_directory=True,
        add_metadata=False,
        append_created_time=False,
        generate_slug=False,
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

        append_created_time : boolean, optional
            Whether or not to append created time to filename.
            Defaults to False

        generate_slug : boolean, optional
            Whether or not to generate and append slug to metatdata.
            Defaults to False
        """
        self.token = token
        self.client = NotionClient(token_v2=token)
        self.docs_directory = docs_directory.lower()
        self.recursive_export = recursive_export
        self.create_page_directory = create_page_directory
        self.add_metadata = add_metadata
        self.append_created_time = append_created_time
        self.generate_slug = generate_slug

    def get_notion_page(
        self,
        page_url,
        sub_path="",
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
        """
        # Setup variables
        page = self.client.get_block(page_url)
        parent_database = self.client.get_collection(page.parent.id)
        self.image_number = 0
        self.filename = get_filename(self.append_created_time, page, parent_database)
        dir_path = get_dir_path(self.create_page_directory, sub_path, self.filename)
        full_path = os.path.join(self.docs_directory, dir_path)
        filename = "index" if self.create_page_directory else self.filename
        metadata = self.get_metadata(page, parent_database, dir_path)

        # Write post
        post = append_metadata(self.add_metadata, metadata, page)
        post = post + self.parse_notion_blocks(page.children, dir_path, "")
        create_directory(full_path)
        write_post(post, full_path, filename)
        print(
            f'✅ Successfully exported page To "{full_path}/{filename}.md" From "{page.get_browseable_url()}"'
        )

    def get_notion_pages_from_database(
        self,
        database_url,
        category_column_name="",
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
                path = page.get_property(category_column_name)

            self.get_notion_page(
                page.get_browseable_url(),
                sub_path=path,
            )

            if next_status:
                page.set_property(status_column_name, next_status)

    def parse_notion_blocks(self, blocks, path, offset):
        """Parse Notion blocks

        Arguments
        ---------
        blocks : list
            Block list in Notion page to parse.

        path : str
            Path where "ChildPage blocks" or "Image blocks" will be stored.

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
                contents += f"## {block.title}"
            elif block.type == "sub_header":
                contents += f"### {block.title}"
            elif block.type == "sub_sub_header":
                contents += f"#### {block.title}"
            elif block.type == "code":
                contents += f"```{block.language.lower()}\n"
                contents += f"{offset}{offset.join(block.title.splitlines(True))}\n"
                contents += f"{offset}```"
            elif block.type == "callout":
                contents += f"> {block.icon} {block.title}"
            elif block.type == "quote":
                contents += f"> {block.title}"
            elif block.type == "divider":
                if blocks[index - 1].type == "header":
                    continue
                contents += "---"
            elif block.type == "bookmark":
                contents += f"[{block.title}]({block.link})"
            elif block.type == "page":
                if (
                    self.recursive_export
                    and self.client.get_block(block.id).parent == block.parent
                ):
                    filename = self.filename
                    parent_image_number = self.image_number

                    self.get_notion_page(block.get_browseable_url(), sub_path=path)

                    child_title = replace_filename(block.title)

                    if self.create_page_directory:
                        contents += f"[{block.title}]({child_title}/index.md)"
                    else:
                        contents += f"[{block.title}](./{child_title}.md)"

                    self.filename = filename
                    self.image_number = parent_image_number
                else:
                    contents += f"[{block.title}]({block.get_browseable_url()})"
            elif block.type == "image":
                image_path = self.get_image_path(path, block.source, "image")
                contents += (
                    f"![{self.filename}-image-{self.image_number}]({image_path})"
                )
                self.image_number += 1
            elif block.type == "bulleted_list":
                contents += f"- {block.title}"
            elif block.type == "numbered_list":
                contents += f"1. {block.title}"
            elif block.type == "to_do":
                contents += f"- [ ] {block.title}"
            elif block.type == "toggle":
                contents += f"- <details><summary>{block.title}</summary>"
            elif block.type == "text":
                if block.title:
                    contents += block.title
                else:
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
            else:
                contents += "\n\n"

            if block.children:
                if block.type == "page":
                    continue
                elif block.type == "toggle":
                    contents += self.parse_notion_blocks(
                        block.children, path, f"{offset}   "
                    )
                    contents += f"{offset}  </details>\n\n"
                else:
                    contents += self.parse_notion_blocks(
                        block.children, path, f"{offset}   "
                    )

        return contents

    def get_image_path(self, path, source, image_type):
        """Get image and return path of image file.

        Arguments
        ---------
        path : str
            Path where "Image" will be stored.

        source : str
            Image source to get.

        image_type : str
            Image type.
            ex) icon, cover, image

        Returns
        ---------
        image_path or source : str
            If image is uploaded, download it first and return path of image file.
            If image is linked, then return URL of image source.
        """
        if source.startswith("/"):
            create_directory(os.path.join(self.docs_directory, path, "images"))
            type = "".join(filter(lambda i: i in source, IMAGE_EXTS))
            image_path = f"./images/{self.filename}-{image_type}.{type}"

            try:
                r = requests.get(f"{NOTION_BASE_URL}{source}", allow_redirects=True)
                open(os.path.join(self.docs_directory, path, image_path), "wb").write(
                    r.content
                )
            except HTTPError as e:
                print(e.code)
            except URLError as e:
                print(e.reason)

            return image_path

        if source.startswith(S3_URL_PREFIX_ENCODED):
            create_directory(os.path.join(self.docs_directory, path, "images"))
            type = "".join(filter(lambda i: i in source, IMAGE_EXTS))
            image_path = (
                f"./images/{self.filename}-{image_type}-{self.image_number}.{type}"
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
        ordered_properties = get_ordered_properties(table)

        columns = list(
            map(
                lambda i: {"id": i["id"], "name": i["name"], "type": i["type"]},
                ordered_properties,
            )
        )

        contents = f"| {' | '.join(map(lambda i: i['name'], columns))} |\n"
        contents += f"{offset} | {' | '.join(map(lambda i: '---', columns))} |\n"

        for row in table.get_rows():
            contents += offset
            for column in columns:
                contents += "| "
                data = row.get_property(column["id"])
                if data is None or not data:
                    contents += "   "
                elif column["type"] == "date":
                    contents += ("" if data.start is None else str(data.start)) + (
                        "" if data.end is None else f" -> {data.end}"
                    )
                elif column["type"] == "person":
                    contents += ", ".join(map(lambda i: i.full_name, data))
                elif column["type"] == "file":
                    contents += ", ".join(map(lambda i: f"[link]({i})", data))
                elif column["type"] == "select":
                    contents += str([data])
                elif column["type"] == "multi_select":
                    contents += ", ".join(map(lambda i: f"[{i}]", data))
                elif column["type"] == "checkbox":
                    contents += "✅" if data else "⬜️"
                else:
                    contents += str(data)
                contents += " "
            contents += "|\n"

        return contents

    def get_metadata(self, page, database, path):
        if not self.add_metadata:
            return []

        metadata = []

        if page.icon:
            if page.icon.startswith("http"):
                metadata.append(f"icon: {self.get_image_path(path, page.icon, 'icon')}")
            else:
                metadata.append(f"icon: {page.icon}")
        if page.cover:
            metadata.append(f"cover: {self.get_image_path(path, page.cover, 'cover')}")
        if self.generate_slug:
            metadata.append(f"slug: '{replace_filename(page.title)}'")
        if database:
            ordered_properties = get_ordered_properties(database)
            prop_map = map(
                partial(property_to_str, page),
                ordered_properties,
            )
            props = list(filter(lambda s: len(s) != 0, prop_map))
            return metadata + props
        if page.title:
            metadata.append(f"title: '{page.title}'")

        return metadata


def create_directory(path):
    if not (os.path.isdir(path)):
        try:
            os.makedirs(path)
        except:
            pass


def write_post(post, path, title):
    with open(f"{path}/{title}.md", "w", encoding="utf-8") as f:
        f.write(post)
