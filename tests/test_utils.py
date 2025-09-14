def test_safe_call_returns_default_on_error(capsys):
    from monitor.utils import safe_call

    @safe_call
    def boom():
        raise RuntimeError("x")

    assert boom() == -1.0
    out = capsys.readouterr().out
    assert "Błąd podczas wykonywania" in out

