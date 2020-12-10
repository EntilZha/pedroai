from pedroai.result import Err, Ok


def test_init():
    assert Ok(1).ok() == Ok(1)._value
