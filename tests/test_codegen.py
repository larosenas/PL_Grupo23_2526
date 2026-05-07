from src.ast_nodes import (
    Program,
    Print,
    String,
    Assignment,
    Declaration,
    Number,
    Variable,
    BinaryOp,
)
from src.codegen import CodeGenerator

# Code generation unit tests for the simple VM backend.
# These tests ensure that AST nodes are translated into the expected instruction stream.


def test_codegen_print_string():
    program = Program(
        name="HELLO",
        declarations=[],
        statements=[Print([String("Ola, Mundo!")])],
    )

    code = CodeGenerator().generate(program)

    assert code == ('PUSHS "Ola, Mundo!"\n' "WRITES\n" "WRITELN\n" "STOP\n")


def test_codegen_empty_program():
    # Verify that an empty program still emits the program termination opcode.
    program = Program(
        name="TEST",
        declarations=[],
        statements=[],
    )

    code = CodeGenerator().generate(program)

    assert code == "STOP\n"


def test_codegen_integer_assignment():
    # Check that an integer variable declaration and assignment generate storage code.
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[Assignment(Variable("A"), Number(3))],
    )

    code = CodeGenerator().generate(program)

    assert code == ("PUSHI 0\n" "PUSHI 3\n" "STOREG 0\n" "STOP\n")


def test_codegen_arithmetic_expression_with_variable():
    # Ensure arithmetic expressions involving variables produce evaluation and operator opcodes.
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A", "B"])],
        statements=[
            Assignment(Variable("A"), Number(2)),
            Assignment(
                Variable("B"),
                BinaryOp("*", Variable("A"), Number(5)),
            ),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 2\n"
        "STOREG 0\n"
        "PUSHG 0\n"
        "PUSHI 5\n"
        "MUL\n"
        "STOREG 1\n"
        "STOP\n"
    )


def test_codegen_print_variable():
    # Test printing a string prefix followed by a variable value.
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[
            Assignment(Variable("A"), Number(3)),
            Print([String("Resultado: "), Variable("A")]),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 3\n"
        "STOREG 0\n"
        'PUSHS "Resultado: "\n'
        "WRITES\n"
        "PUSHG 0\n"
        "WRITEI\n"
        "WRITELN\n"
        "STOP\n"
    )
