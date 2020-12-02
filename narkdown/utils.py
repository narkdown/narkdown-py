import re
import json


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
