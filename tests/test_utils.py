def test_safe_call_returns_default_on_error(caplog):
    from monitor.utils import safe_call

    @safe_call(default=-1.0)
    def boom():
        raise RuntimeError("x")

    with caplog.at_level("ERROR"):
        assert boom() == -1.0

    assert any(
        "Błąd podczas wykonywania" in record.getMessage()
        for record in caplog.records
    )
