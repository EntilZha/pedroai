from pedroai.result import Ok, Err


def test_init():
    assert Ok(1).ok() == Ok(1)._value
