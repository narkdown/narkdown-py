# Notion2Github

[![PyPI version](https://badge.fury.io/py/notion2github.svg)](https://badge.fury.io/py/notion2github)

![image-0](https://raw.githubusercontent.com/younho9/notion2github/main/images/image-0.png)

A tool to use Notion as a [Github Flavored Markdown(aka GFM)](https://github.github.com/gfm/) editor.

[View in Notion](https://bit.ly/2ZRElQg)

---

> ⚠️ **_NOTE:_** [Notion2Github](https://github.com/younho9/notion2github) uses customized version of [notion-py](https://github.com/jamalex/notion-py) created by [Jamie Alexandre](https://github.com/jamalex). That repository seems to be abandoned.
> Also, this is based on the private Notion API. It can not gurantee it will stay stable. If you need to use in production, I recommend waiting for their official release.

---

## Features

- **Auto synchronization of Notion2Github by using Github Actions and crontab.**

- **Format documents by using Prettier.**

- **Import a Notion page and save it to the desired path.**

  Useful for simple markdown exporter.

- **Import Notion pages from database to the desired path.**

  Useful for CMS(Contents Manage System) of static pages such as blog or docs page.

  - Support import by status of content.

  - Support filter contents.

- **Import "Child page" in Notion page recursively. And import "Linked page" as a Notion page link.**

- **Support nested block. (e.g. bulleted, numbered, to-do, toggle)**

- **Support syntax highlighting in code block.**

## Usage

### Quickstart

> ⚠️ **_NOTE:_** the latest version of [notion2github](https://github.com/younho9/notion2github) requires Python 3.5 or greater.

1. Install dependencies

   `pip install notion2github`

1. Get `token_v2` cookie from a logged-in browser session on Notion.so.

   ![image-1](https://raw.githubusercontent.com/younho9/notion2github/main/images/image-1.png)

1. Add [`config.py`](https://github.com/younho9/notion2github/blob/main/config.py.example) in root directory

   ```python
   token=
   database_url=
   page1_url=
   page2_url=
   page3_url=
   page4_url=
   # ... and so on
   ```

1. Use it like an [`example.py`](https://github.com/younho9/notion2github/blob/main/example.py)

   ```python
   import sys
   from config import token, page1_url, page2_url, database_url
   from notion2github.exporter import NotionExporter

   if __name__ == "__main__":
       # Get project README.md
       NotionExporter(token, ".").get_notion_page(
           url=page1_url, create_page_directory=False
       )

       # Get directory README.md
       NotionExporter(token, "./docs").get_notion_page(
           url=page2_url, create_page_directory=False
       )

       # Get all contents from database
       NotionExporter(token).get_notion_pages_from_database(
           url=database_url,
           category_column_name="Category",
           status_column_name="",
           current_status="",
           next_status="",
           filters={},
       )
   ```

### Format Documents

- Create `package.json` file to your document directory.

  - Example

  ```json
  {
    "name": "notion2github-docs",
    "dependencies": {
      "prettier": "2.1.1"
    },
    "scripts": {
      "format": "prettier --write ."
    },
    "author": "younho9",
    "license": "MIT"
  }
  ```

- Install dependencies

  ```bash
  cd docs # your documents directory
  npm install
  ```

- Add prettier setting

  `.prettierrc` (example)

  ```json
  {
    "printWidth": 100,
    "tabWidth": 2,
    "singleQuote": true,
    "trailingComma": "all",
    "bracketSpacing": true,
    "semi": true,
    "useTabs": false,
    "arrowParens": "avoid",
    "endOfLine": "lf"
  }
  ```

- Using npm scripts

  ```bash
  cd docs # your documents directory
  npm run format
  ```

### Examples

- <details><summary>Click here.</summary>

  #### Example : Categorize content by "Select" property.

  - Create "Select" column and specify category by page.

    ![image-2](https://raw.githubusercontent.com/younho9/notion2github/main/images/image-2.png)

  - Pass `category_column_name` to parameter.

    ```python
    NotionExporter(token).get_notion_pages_from_database(
        url=database_url,
        category_column_name="Category"
    )
    ```

  #### Example : Get content by status.

  - Create "Select" column and specify status of page.

    ![image-3](https://raw.githubusercontent.com/younho9/notion2github/main/images/image-3.png)

  - Pass `status_column_name`, `current_status`, `next_status` to parameter.

    ```python
    NotionExporter(token).get_notion_pages_from_database(
        url=database_url,
        status_column_name="Status",
        current_status="✅ Completed",
        next_status="🖨 Published"
    )
    ```

  - After extract page, status will be changed.

    ![image-4](https://raw.githubusercontent.com/younho9/notion2github/main/images/image-4.png)

  #### Example : Apply filter

  - Pass key, value pair of filter list to `filters` parameter.

    ```python
    NotionExporter(token).get_notion_pages_from_database(
        url=database_url,
        filter={"Name" : "Basic Blocks"}
    )
    ```

  #### Example : Auto synchronization of Notion and Github

  - Register `token_v2` and `url` of page to synchronize in github's secret.

    ![image-5](https://github.com/younho9/notion2github/blob/main/images/image-5.png)

  - Allow python files to receive arguments.

    ```python
    # auto_sync.py

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
    ```

  - [Create github actions workflow file](https://github.com/younho9/notion2github/blob/main/.github/workflows/auto-sync.yml) to `.github/workflows`

  </details>

## Supported Blocks

[View supported blocks by type](https://bit.ly/32PzfpT)

| Block Type           | Supported  | Notes                                                                                           |
| -------------------- | ---------- | ----------------------------------------------------------------------------------------------- |
| Heading 1            | ✅ Yes     | [Converted to heading 2 in markdown.](https://bit.ly/3hEM8ak)                                   |
| Heading 2            | ✅ Yes     | [Converted to heading 3 in markdown.](https://bit.ly/3hEM8ak)                                   |
| Heading 3            | ✅ Yes     | [Converted to heading 4 in markdown.](https://bit.ly/3hEM8ak)                                   |
| Text                 | ✅ Yes     |                                                                                                 |
| Divider              | ✅ Yes     | Divider after the Heading 1 is not added.                                                       |
| Callout              | ✅ Yes     | Callout block will be exported as quote block with emoji.                                       |
| Quote                | ✅ Yes     |                                                                                                 |
| Bulleted list        | ✅ Yes     | Support nested block.                                                                           |
| Numbered list        | ✅ Yes     | Support nested block.                                                                           |
| To-do list           | ✅ Yes     | Support nested block.                                                                           |
| Toggle list          | ✅ Yes     | Support nested block.                                                                           |
| Code                 | ✅ Yes     | Support syntax highlighting.                                                                    |
| Image                | ✅ Yes     | Uploaded image will be downloaded to local. Linked image will be linked not be downloaded.      |
| Web bookmark         | ✅ Yes     | Same as link text.                                                                              |
| Page                 | ✅ Yes     | Import "Child page" in Notion page recursively. And import "Linked page" as a Notion page link. |
| Table (aka database) | ⚠️ Partial | ⚠️The sequence of columns is not guaranteed.                                                    |
| Video                | ❌ No      |                                                                                                 |
| Audio                | ❌ No      |                                                                                                 |
| File                 | ❌ No      |                                                                                                 |
| Embed other services | ❌ No      |                                                                                                 |
| Advanced             | ❌ No      |                                                                                                 |
| Layout in page       | ❌ No      |                                                                                                 |

### License

MIT © [younho9](https://github.com/younho9)
