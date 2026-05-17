from src.main import compile_file, main
import src.main as main_module

# Tests for compiler entry points and file-level behavior.
# These cases verify correct output generation, input handling, default paths,
# and proper exit codes for success and various failure modes.


def test_compile_file_generates_vm(tmp_path):
    # Test that compile_file generates the correct VM code for a simple program.
    source = tmp_path / "hello.f"
    output = tmp_path / "hello.vm"

    source.write_text(
        "PROGRAM HELLO\n" "PRINT *, 'Hello, World!'\n" "END\n",
        encoding="utf-8",
    )

    result = compile_file(source, output)

    assert result == output
    assert output.read_text(encoding="utf-8") == (
        'PUSHS "Hello, World!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )


def test_compile_file_accepts_input_without_final_newline(tmp_path):
    # Test that compile_file handles input files without a trailing newline.
    source = tmp_path / "hello.f"
    output = tmp_path / "hello.vm"

    source.write_text(
        "PROGRAM HELLO\n" "PRINT *, 'Hello, World!'\n" "END",
        encoding="utf-8",
    )

    result = compile_file(source, output)

    assert result == output
    assert output.read_text(encoding="utf-8") == (
        'PUSHS "Hello, World!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )


def test_main_returns_zero_and_writes_output_file(tmp_path, capsys):
    # Test that the CLI main() returns success and writes the generated VM file.
    # This also confirms the success message is printed to stdout.
    source = tmp_path / "hello.f"
    output = tmp_path / "hello.vm"

    source.write_text(
        "PROGRAM HELLO\n" "PRINT *, 'Hello, World!'\n" "END\n",
        encoding="utf-8",
    )

    exit_code = main([str(source), "-o", str(output)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "VM code generated in:" in captured.out
    assert output.read_text(encoding="utf-8") == (
        'PUSHS "Hello, World!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )


def test_main_returns_one_when_input_file_does_not_exist(tmp_path, capsys):
    # Test that main() returns a failure code when the source file is missing.
    # The error message should indicate that the input file was not found.
    missing_file = tmp_path / "missing.f"

    exit_code = main([str(missing_file)])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Compilation failed:" in captured.err
    assert "Input file not found" in captured.err


def test_compile_file_uses_default_output_directory(tmp_path, monkeypatch):
    source = tmp_path / "hello.f"

    source.write_text(
        "PROGRAM HELLO\n" "PRINT *, 'Hello, World!'\n" "END\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(main_module, "ROOT_DIR", tmp_path)

    result = compile_file(source)

    assert result == tmp_path / "output" / "hello.vm"
    assert result.read_text(encoding="utf-8") == (
        'PUSHS "Hello, World!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )


def test_main_returns_one_on_syntax_error(tmp_path, capsys):
    # Test that main() reports a syntax error and returns failure when the
    # Fortran source program is malformed.
    source = tmp_path / "bad.f"

    source.write_text(
        "PROGRAM BAD\n" "PRINT *, 'missing end'\n",
        encoding="utf-8",
    )

    exit_code = main([str(source)])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Compilation failed:" in captured.err


def test_compile_file_creates_output_parent_directories(tmp_path):
    source = tmp_path / "hello.f"
    output = tmp_path / "generated" / "vm" / "hello.vm"

    source.write_text(
        "PROGRAM HELLO\n" "PRINT *, 'Hello, World!'\n" "END\n",
        encoding="utf-8",
    )

    result = compile_file(source, output)

    assert result == output
    assert output.exists()
    assert output.read_text(encoding="utf-8") == (
        'PUSHS "Hello, World!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )
