from pedroai.io import read_jsonlines, write_jsonlines


def test_read_write_jsonlines(tmp_path):
    elements = [
        {"id": "hello"},
        {"id": "world"},
    ]
    write_jsonlines(tmp_path / "elements.jsonl", elements)
    parsed_elements = read_jsonlines(tmp_path / "elements.jsonl")
    assert elements == parsed_elements
