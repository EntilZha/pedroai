import types
from pathlib import Path

from pydantic import BaseModel

from pedroai.io import read_jsonlines, write_json, write_jsonlines


class JsonTest(BaseModel):
    text: str


def test_read_write_jsonlines(tmp_path: Path):
    elements = [
        {"id": "hello"},
        {"id": "world"},
    ]
    write_jsonlines(tmp_path / "elements.jsonl", elements)
    parsed_elements = read_jsonlines(tmp_path / "elements.jsonl")
    assert elements == parsed_elements

    assert isinstance(parsed_elements, list)
    lazy_elements = read_jsonlines(tmp_path / "elements.jsonl", lazy=True)
    assert isinstance(lazy_elements, types.GeneratorType)


def test_pydantic_write_json(tmp_path):
    obj = JsonTest(text="testing")
    write_json(tmp_path / "pydantic_test.json", obj)

    parsed_obj = JsonTest.parse_file(tmp_path / "pydantic_test.json")
    assert obj.text == parsed_obj.text
