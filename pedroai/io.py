import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, List, Union

import requests
import simdjson
from pydantic import BaseModel
from rich.console import Console

console = Console()


def shell(command: str):
    subprocess.run(command, shell=True, check=True)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def read_json(path: Union[str, Path]):
    """
    Read a json file from a string path
    """
    with open(path) as f:
        return simdjson.load(f)  # type: ignore


def write_json(path: Union[str, Path], obj: Any):
    """
    Write an object to a string path as json.
    If the object is a pydantic model, export it to json
    """
    if isinstance(obj, BaseModel):
        with open(path, "w") as f:
            f.write(obj.json())
    else:
        with open(path, "w") as f:
            json.dump(obj, f)


def _read_jsonlines_list(path: Union[str, Path]):
    """
    Read a jsonlines file into memory all at once
    """
    parser = simdjson.Parser()
    out = []
    with open(path) as f:
        for line in f:
            out.append(parser.parse(line, recursive=True))
    return out


def _read_jsonlines_lazy(path: Union[str, Path]):
    """
    Lazily return the contents of a jsonlines file
    """
    parser = simdjson.Parser()
    with open(path) as f:
        for line in f:
            yield parser.parse(line, recursive=True)


def read_jsonlines(path: Union[str, Path], lazy: bool = False):
    """
    Read a jsonlines file as a list/iterator of json objects
    """
    if lazy:
        return _read_jsonlines_lazy(path)
    else:
        return _read_jsonlines_list(path)


def write_jsonlines(path: Union[str, Path], elements: List[Any]):
    """
    Write a list of json serialiazable objects to the path given
    """
    with open(path, "w") as f:
        for e in elements:
            f.write(json.dumps(e))
            f.write("\n")


def download(remote_path, local_path):
    console.log(f"Downloading {remote_path} to {local_path}")
    response = requests.get(remote_path, stream=True)
    with open(local_path, "w") as f:
        for data in response.iter_content():
            f.write(data)


class requires_file:
    def __init__(self, path: Union[str, Path]):
        self._path = path

    def __call__(self, f):
        if os.path.exists(self._path):
            return f
        else:

            def nop(*args, **kwargs):  # pylint: disable=unused-argument
                console.log("File missing, skipping function: path=", self._path)

            return nop


class requires_files:
    def __init__(self, paths: List[Union[str, Path]]):
        self._paths = paths

    def __call__(self, f):
        missing_files = []
        for path in self._paths:
            if not os.path.exists(path):
                missing_files.append(path)

        if len(missing_files) > 0:

            def nop(*args, **kwargs):  # pylint: disable=unused-argument
                console.log("Files missing, skipping function: paths=", missing_files)

            return nop
        else:
            return f


def safe_file(path: Union[str, Path]) -> Union[str, Path]:
    """
    Ensure that the path to the file exists, then return the path.

    For example, if the path passed in is /home/entilzha/stuff/stuff/test.txt,
    this function will run the equivalent of mkdir -p /home/entilzha/stuff/stuff/
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path
