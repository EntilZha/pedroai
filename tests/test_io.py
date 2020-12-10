import types

from pedroai.io import read_jsonlines, write_jsonlines


def test_read_write_jsonlines(tmp_path):
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
