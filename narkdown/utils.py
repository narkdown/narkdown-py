import os
import re
import json
from functools import partial
from .constants import *


def convert(s):
    a = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")
    return a.sub(r"_\1", s).lower()


def convertArray(a):
    newArr = []
    for i in a:
        if isinstance(i, list):
            newArr.append(convertArray(i))
        elif isinstance(i, dict):
            newArr.append(convertJSON(i))
        else:
            newArr.append(i)
    return newArr


def convertJSON(j):
    out = {}
    for k in j:
        newK = convert(k)
        if isinstance(j[k], dict):
            out[newK] = convertJSON(j[k])
        elif isinstance(j[k], list):
            out[newK] = convertArray(j[k])
        else:
            out[newK] = j[k]
    return out


def load_json(filename):
    with open(filename, "r") as f:
        return convertJSON(json.load(f))


def str_to_json(s):
    return json.loads(s.replace("'", '"'))


def inputWithDefault(message, default):
    value = input(f"{message} (default: {default}): ")

    if not value.strip():
        return default
    else:
        return value


def replace_filename(filename):
    return strip_dash(remove_dup_dash(remove_slash(remove_special(filename)))).lower()


def replace_path(pathname):
    return strip_dash(remove_dup_dash(remove_special(pathname))).lower()


def remove_dup_dash(string):
    return re.sub("--+", "-", string)


def remove_special(string):
    return re.sub(
        r"[\~\`\;\:\'\"\!\@\#\$\%\^\&\*\(\)\-\_\+\=\<\>\{\}\[\]\,\. ]", "-", string
    )


def remove_slash(string):
    return re.sub(r"[\/]", "-", string)


def strip_dash(string):
    if len(string) == 0:
        return string

    striped = string

    if striped[-1] == "-":
        striped = striped[:-1]
    if striped[0] == "-":
        striped = striped[1:]

    return striped


def property_to_str(page, prop):
    prop_type = prop["type"]
    prop_slug = prop["slug"]
    prop_value = page.get_property(prop_slug)

    if not prop_value:
        return ""

    if prop_type == "title":
        return f"{prop_slug}: '{prop_value}'"
    if prop_type in ["created_time", "last_edited_time"]:
        return f"{prop_slug}: {prop_value.strftime('%Y-%m-%d')}"
    if prop_type in ["created_by", "last_edited_by"]:
        return f"{prop_slug}: {prop_value.full_name}"
    if prop_type == "date":
        if not prop_value:
            return ""
        if prop_value.end:
            return f"{prop_slug}: {prop_value.start} - {prop_value.end}"
        return f"{prop_slug}: {prop_value.start}"
    if prop_type == "file":
        if len(prop_value) == 1:
            return f'{prop_slug}: "{prop_value[0]}"'
        else:
            return f"{prop_slug}: {prop_value}"
    else:
        return f"{prop_slug}: {prop_value}"


def get_created_time(page, database):
    if not database:
        return ""

    created_times = list(
        filter(lambda p: p["type"] == "created_time", database.get_schema_properties())
    )

    if len(created_times) == 0:
        return ""

    prop_slug = created_times[0]["slug"]

    return page.get_property(prop_slug).strftime("%Y-%m-%d")


def get_filename(append_created_time, page, database):
    created_time = get_created_time(page, database)
    title = replace_filename(page.title)

    if not created_time:
        return title
    if not append_created_time:
        return title

    return f"{created_time}-{title}"


def get_dir_path(create_page_directory, sub_path, filename):
    replaced_sub_path = replace_path(sub_path)

    if create_page_directory:
        return os.path.join(replaced_sub_path, filename)
    else:
        return os.path.join(replaced_sub_path)


def append_metadata(add_metadata, metadata, page):
    metadata_str = ""

    if add_metadata and len(metadata):
        metadata_str += "---\n"
        metadata_str += "\n".join(metadata)
        metadata_str += "\n---\n\n"
        return metadata_str
    else:
        return f"# {page.title}\n\n"


def get_ordered_properties(database):
    cv = database._get_a_collection_view()
    tp = filter(
        lambda tp_item: tp_item["visible"] == True, cv.get("format.table_properties")
    )
    sp = database.get_schema_properties()

    properties = []

    for tp_item in tp:
        properties += list(
            filter(lambda sp_item: sp_item["id"] == tp_item["property"], sp)
        )

    return properties
