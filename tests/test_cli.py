import json
import time
import pytest
from speculative_decoding_demo.cli import main


def test_run_completes_on_fixture(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    start = time.perf_counter()
    assert main(["fixtures", "--out", "demo"]) == 0
    assert main(["run", "--input", "demo"]) == 0
    assert main(["report", "--format", "md"]) == 0
    assert time.perf_counter() - start < 5
    assert "synthetic fixture records" in capsys.readouterr().out


def test_empty_input_renders_without_traceback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["run", "--input", "."]) == 0
    assert json.loads((tmp_path / ".sdd-results.json").read_text())["totals"]["tokens"] == 0
    assert main(["report"]) == 0


def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path / "bad.jsonl").write_text("# header\n{broken\n")
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "ParseError" in error and "bad.jsonl" in error and "line 2" in error


def test_determinism_byte_identical(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main(["fixtures", "--out", "demo"])
    main(["run", "--input", "demo"])
    first = (tmp_path / ".sdd-results.json").read_bytes()
    main(["run", "--input", "demo"])
    assert first == (tmp_path / ".sdd-results.json").read_bytes()
    main(["report", "--out", "a.md"])
    main(["report", "--out", "b.md"])
    assert (tmp_path / "a.md").read_bytes() == (tmp_path / "b.md").read_bytes()


def test_cli_smoke_all_subcommands(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main(["fixtures", "--out", "demo"])
    for command in ("run", "decode", "compare"):
        assert main([command, "--input", "demo"]) == 0
    assert main(["report", "--format", "json"]) == 0
    for command in ("fixtures", "run", "report", "decode", "compare"):
        with pytest.raises(SystemExit) as exit:
            main([command, "--help"])
        assert exit.value.code == 0


def test_missing_input_and_atomic_write_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["run", "--input", "missing"]) == 2
    assert "MissingInput" in capsys.readouterr().err
    main(["run", "--input", "."])
    assert main(["report", "--out", "missing/report.md"]) == 2
    assert not (tmp_path / "missing").exists()


def test_schema_error_names_file_line_and_field(tmp_path, capsys):
    (tmp_path / "bad.jsonl").write_text('{"id":"x"}\n')
    assert main(["run", "--input", str(tmp_path)]) == 2
    assert "line 1" in capsys.readouterr().err


def test_failed_replace_preserves_existing_and_cleans_temp(tmp_path, monkeypatch):
    import speculative_decoding_demo.cli as cli
    destination = tmp_path / "report.md"
    destination.write_text("prior")
    def fail(*args):
        raise OSError("blocked replacement")
    monkeypatch.setattr(cli.os, "replace", fail)
    with pytest.raises(OSError):
        cli.atomic_write(destination, "new")
    assert destination.read_text() == "prior"
    assert list(tmp_path.iterdir()) == [destination]


def test_unsupported_format_is_named(tmp_path, capsys):
    (tmp_path / "bad.csv").write_text("broken")
    assert main(["run", "--input", str(tmp_path)]) == 2
    assert "unsupported format" in capsys.readouterr().err
