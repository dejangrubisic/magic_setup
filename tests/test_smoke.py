from magic.smoke import smoke


def test_smoke_returns_ok():
    assert smoke() == "ok"
