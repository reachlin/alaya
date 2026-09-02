"""Loading credentials from a file, without taking on a dependency to do it."""
import pytest

from alaya.env import find_env, load_env


def test_it_loads_key_values(tmp_path, monkeypatch):
    monkeypatch.delenv("ALAYA_TEST_KEY", raising=False)
    path = tmp_path / ".env"
    path.write_text("ALAYA_TEST_KEY=abc123\n")
    load_env(path)
    import os
    assert os.environ["ALAYA_TEST_KEY"] == "abc123"


def test_an_existing_variable_wins(tmp_path, monkeypatch):
    """What the shell already says is authoritative — a file cannot override it."""
    monkeypatch.setenv("ALAYA_TEST_KEY", "from-shell")
    path = tmp_path / ".env"
    path.write_text("ALAYA_TEST_KEY=from-file\n")
    load_env(path)
    import os
    assert os.environ["ALAYA_TEST_KEY"] == "from-shell"


def test_comments_blanks_and_quotes(tmp_path, monkeypatch):
    monkeypatch.delenv("ALAYA_QUOTED", raising=False)
    path = tmp_path / ".env"
    path.write_text('\n# a comment\n\nALAYA_QUOTED="spaced value"\nnot-a-pair\n')
    load_env(path)
    import os
    assert os.environ["ALAYA_QUOTED"] == "spaced value"


def test_an_empty_value_is_not_a_key(tmp_path, monkeypatch):
    """Placeholder lines are common and must not mask a real shell variable."""
    monkeypatch.setenv("ALAYA_TEST_KEY", "real")
    path = tmp_path / ".env"
    path.write_text("ALAYA_TEST_KEY=\n")
    load_env(path)
    import os
    assert os.environ["ALAYA_TEST_KEY"] == "real"


def test_a_missing_file_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_env(tmp_path / "nope.env")


def test_a_missing_file_is_tolerated_when_not_asked_for_explicitly(tmp_path):
    assert load_env(tmp_path / "nope.env", required=False) is False


def test_find_env_prefers_the_working_directory(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("X=1\n")
    monkeypatch.chdir(tmp_path)
    assert find_env() == tmp_path / ".env"


def test_find_env_returns_nothing_when_there_is_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert find_env(extra=()) is None
