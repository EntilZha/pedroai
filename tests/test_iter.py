from pedroai.iter import group_by


def test_group_by():
    items = [1, 2, 3, 4, 5, 6]
    grouped = group_by(lambda x: x % 2 == 0, items)
    assert [1, 3, 5] == sorted(grouped[False])
    assert [2, 4, 6] == sorted(grouped[True])
