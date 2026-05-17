from pathlib import Path

import pytest

from src.main import compile_file

ROOT_DIR = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT_DIR / "examples"


EXAMPLE_PROGRAMS = {
    "hello.f": "PROGRAM HELLO",
    "factorial.f": "PROGRAM FACTORIAL",
    "prime.f": "PROGRAM PRIME",
    "sum_array.f": "PROGRAM SUMARRAY",
    "converter.f": "PROGRAM CONVERTER",
}


@pytest.mark.parametrize("filename, program_header", EXAMPLE_PROGRAMS.items())
def test_example_file_exists_and_has_expected_program_header(filename, program_header):
    example_path = EXAMPLES_DIR / filename

    assert example_path.exists(), f"Missing example file: {filename}"

    source = example_path.read_text(encoding="utf-8")

    assert source.strip(), f"Example file is empty: {filename}"
    assert program_header in source


def test_hello_example_compiles_to_vm(tmp_path):
    source = EXAMPLES_DIR / "hello.f"
    output = tmp_path / "hello.vm"

    result = compile_file(source, output)

    assert result == output
    assert output.read_text(encoding="utf-8") == (
        'PUSHS "Hello, World!"\n' "WRITES\n" "WRITELN\n" "STOP\n"
    )


def test_factorial_example_contains_required_constructs():
    source = (EXAMPLES_DIR / "factorial.f").read_text(encoding="utf-8")

    assert "PROGRAM FACTORIAL" in source
    assert "INTEGER N, I, FAT" in source
    assert "PRINT *, 'Enter a positive integer:'" in source
    assert "READ *, N" in source
    assert "FAT = 1" in source
    assert "DO 10 I = 1, N" in source
    assert "FAT = FAT * I" in source
    assert "10 CONTINUE" in source
    assert "PRINT *, 'Factorial of ', N, ': ', FAT" in source


def test_prime_example_contains_required_constructs():
    source = (EXAMPLES_DIR / "prime.f").read_text(encoding="utf-8")

    assert "PROGRAM PRIME" in source
    assert "INTEGER NUM, I" in source
    assert "LOGICAL ISPRIM" in source
    assert "PRINT *, 'Enter a positive integer:'" in source
    assert "READ *, NUM" in source
    assert "ISPRIM = .TRUE." in source
    assert "I = 2" in source
    assert "20 IF (I .LE. (NUM/2) .AND. ISPRIM) THEN" in source
    assert "MOD(NUM, I)" in source
    assert "ISPRIM = .FALSE." in source
    assert "GOTO 20" in source
    assert "IF (ISPRIM) THEN" in source
    assert "PRINT *, NUM, ' is a prime number'" in source
    assert "PRINT *, NUM, ' is not a prime number'" in source


def test_sum_array_example_contains_required_constructs():
    source = (EXAMPLES_DIR / "sum_array.f").read_text(encoding="utf-8")

    assert "PROGRAM SUMARRAY" in source
    assert "INTEGER NUMS(5)" in source
    assert "INTEGER I, SOMA" in source
    assert "SOMA = 0" in source
    assert "PRINT *, 'Enter 5 integers:'" in source
    assert "DO 30 I = 1, 5" in source
    assert "READ *, NUMS(I)" in source
    assert "SOMA = SOMA + NUMS(I)" in source
    assert "30 CONTINUE" in source
    assert "PRINT *, 'The sum of the numbers is: ', SOMA" in source


def test_converter_example_documents_function_case():
    source = (EXAMPLES_DIR / "converter.f").read_text(encoding="utf-8")

    assert "PROGRAM CONVERTER" in source
    assert "INTEGER NUM, BASE, RESULT, CONVRT" in source
    assert "PRINT *, 'Enter a decimal integer:'" in source
    assert "READ *, NUM" in source
    assert "DO 10 BASE = 2, 9" in source
    assert "RESULT = CONVRT(NUM, BASE)" in source
    assert "PRINT *, 'BASE ', BASE, ': ', RESULT" in source
    assert "10 CONTINUE" in source
    assert "INTEGER FUNCTION CONVRT(N, B)" in source
    assert "REM = MOD(QUOT, B)" in source
    assert "CONVRT = VAL" in source
    assert "RETURN" in source
