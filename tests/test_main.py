from src.main import compile_file


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
