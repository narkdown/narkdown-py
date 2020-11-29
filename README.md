# Narkdown

[![PyPI version](https://badge.fury.io/py/narkdown.svg)](https://badge.fury.io/py/narkdown)

![Narkdown-image-0.png](https://raw.githubusercontent.com/younho9/narkdown/main/docs/images/readme-image-0.png)

A tool to use Notion as a Markdown editor.

---

> ⚠️ **_NOTE:_** Narkdown uses customized version of [notion-py](https://github.com/jamalex/notion-py) created by [Jamie Alexandre](https://github.com/jamalex). That repository seems to be abandoned.
> Also, this is based on the private Notion API. It can not gurantee it will stay stable. If you need to use in production, I recommend waiting for their official release.

---

## Features

- **Auto synchronization of Notion to Github by using Github Actions and crontab.**

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

> ⚠️ **_NOTE:_** the latest version of narkdown requires Python 3.5 or greater.

1. Install dependencies

   `pip install narkdown`

1. Get `token_v2` cookie from a logged-in browser session on Notion.so.

   ![Narkdown-image-1](https://raw.githubusercontent.com/younho9/narkdown/main/docs/images/readme-image-1.png)

1. Add [`config.json`](https://github.com/younho9/narkdown/blob/main/config.json.example) in root directory

   ```json
   {
       "TOKEN":
       "DATABASE_URL":
       "PAGE1_URL":
       "PAGE2_URL":
       "PAGE3_URL":
       "PAGE4_URL":
       // and so on ...
   }
   ```

1. Use it like an [`example.py`](https://github.com/younho9/narkdown/blob/main/example.py)

   ```python
   import sys
   import json
   from narkdown.exporter import NotionExporter

   if __name__ == "__main__":
       with open("config.json", "r") as f:
           config = json.load(f)

       token = config["TOKEN"]
       readme_url = config["README_URL"]
       docs_page_url = config["DOCS_PAGE_URL"]
       database_url = config["DATABASE_URL"]

       # Get project README.md
       NotionExporter(token, ".").get_notion_page(
           url=readme_url, create_page_directory=False
       )

       # Get directory README.md
       NotionExporter(token, "./docs").get_notion_page(
           url=docs_page_url, create_page_directory=False
       )

       # Get all contents from database
       NotionExporter(token).get_notion_pages_from_database(
           url=database_url,
           category_column_name="Category",
           status_column_name="Status",
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
    "name": "narkdown-docs",
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

    ![Narkdown-image-2](https://raw.githubusercontent.com/younho9/narkdown/main/docs/images/readme-image-2.png)

  - Pass `category_column_name` to parameter.

    ```python
    NotionExporter(token).get_notion_pages_from_database(
        url=database_url,
        category_column_name="Category"
    )
    ```

  #### Example : Get content by status.

  - Create "Select" column and specify status of page.

    ![Narkdown-image-3](https://raw.githubusercontent.com/younho9/narkdown/main/docs/images/readme-image-3.png)

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

    ![Narkdown-image-4](https://raw.githubusercontent.com/younho9/narkdown/main/docs/images/readme-image-4.png)

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

    ![Narkdown-image-5](https://raw.githubusercontent.com/younho9/narkdown/main/docs/images/readme-image-5.png)

  - Allow python files to receive arguments.

    ```python
    # auto_sync.py

    import sys
    from narkdown.exporter import NotionExporter

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

  - [Create github actions workflow file](https://github.com/younho9/narkdown/blob/main/.github/workflows/auto-sync.yml) to `.github/workflows`

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
| Table (aka database) | ⚠️ Partial | ⚠️ The sequence of columns is not guaranteed.                                                   |
| Video                | ❌ No      |                                                                                                 |
| Audio                | ❌ No      |                                                                                                 |
| File                 | ❌ No      |                                                                                                 |
| Embed other services | ❌ No      |                                                                                                 |
| Advanced             | ❌ No      |                                                                                                 |
| Layout in page       | ❌ No      |                                                                                                 |

### License

MIT © [younho9](https://github.com/younho9)
