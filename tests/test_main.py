from src.main import compile_file


def test_compile_file_generates_vm(tmp_path):
    source = tmp_path / "hello.f"
    output = tmp_path / "hello.vm"

    source.write_text(
        "PROGRAM HELLO\n" "PRINT *, 'Ola, Mundo!'\n" "END\n",
        encoding="utf-8",
    )

    result = compile_file(source, output)

    assert result == output
    assert output.read_text(encoding="utf-8") == (
        'PUSHS "Ola, Mundo!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )


def test_compile_file_accepts_input_without_final_newline(tmp_path):
    source = tmp_path / "hello.f"
    output = tmp_path / "hello.vm"

    source.write_text(
        "PROGRAM HELLO\n" "PRINT *, 'Ola, Mundo!'\n" "END",
        encoding="utf-8",
    )

    result = compile_file(source, output)

    assert result == output
    assert output.read_text(encoding="utf-8") == (
        'PUSHS "Ola, Mundo!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )
