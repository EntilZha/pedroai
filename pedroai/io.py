from typing import List, Any
import sys
import json
import os
import requests


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def read_json(path: str):
    """
    Read a json file from a string path
    """
    with open(path) as f:
        return json.load(f)


def write_json(path: str, obj: Any):
    """
    Write an object to a string path as json
    """
    with open(path, "w") as f:
        json.dump(obj, f)


def _read_jsonlines_list(path: str):
    """
    Read a jsonlines file into memory all at once
    """
    out = []
    with open(path) as f:
        for line in f:
            out.append(json.loads(line))
    return out


def _read_jsonlines_lazy(path: str):
    """
    Lazily return the contents of a jsonlines file
    """
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def read_jsonlines(path: str, lazy: bool = False):
    """
    Read a jsonlines file as a list/iterator of json objects
    """
    if lazy:
        return _read_jsonlines_lazy(path)
    else:
        return _read_jsonlines_list(path)


def write_jsonlines(path: str, elements: List[Any]):
    """
    Write a list of json serialiazable objects to the path given
    """
    with open(path, "w") as f:
        for e in elements:
            f.write(json.dumps(e))
            f.write("\n")


def download(remote_path, local_path):
    eprint(f"Downloading {remote_path} to {local_path}")
    response = requests.get(remote_path, stream=True)
    with open(local_path, "w") as f:
        for data in response.iter_content():
            f.write(data)


class requires_file:
    def __init__(self, path):
        self._path = path

    def __call__(self, f):
        if os.path.exists(self._path):
            return f
        else:
            eprint(f"File missing, skipping function: {self._path}")

            def nop(*args, **kwargs):  # pylint: disable=unused-argument
                pass

            return nop


def safe_file(path: str) -> str:
    """
    Ensure that the path to the file exists, then return the path.
    
    For example, if the path passed in is /home/entilzha/stuff/stuff/test.txt,
    this function will run the equivalent of mkdir -p /home/entilzha/stuff/stuff/
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
