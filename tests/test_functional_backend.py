import pytest
from src.ast_nodes import (
    Assignment,
    BinaryOp,
    Continue,
    Declaration,
    Do,
    Number,
    Print,
    Program,
    Read,
    String,
    Variable,
    ArrayAccess,
    Boolean,
    FunctionCall,
    GOTO,
    If,
)
from src.codegen import CodeGenerator
from src.semantic import SemanticAnalyzer
from src.errors import SemanticError


def analyze_and_generate(program):
    # Perform semantic analysis on the program and generate VM code.
    SemanticAnalyzer().analyze(program)
    return CodeGenerator().generate(program)


def assert_in_order(text, expected_lines):
    # Assert that the expected lines appear in the given text in the specified order.
    current_position = 0

    for expected in expected_lines:
        next_position = text.find(expected, current_position)

        assert next_position != -1, f"Expected line not found in order: {expected}"

        current_position = next_position + len(expected)


def test_backend_factorial_program():
    program = Program(
        name="FACTORIAL",
        declarations=[Declaration("INTEGER", ["N", "I", "FAT"])],
        statements=[
            Print([String("Enter a positive integer:")]),
            Read([Variable("N")]),
            Assignment(Variable("FAT"), Number(1)),
            Do(
                label=10,
                variable="I",
                start=Number(1),
                end=Variable("N"),
                body=[
                    Assignment(
                        Variable("FAT"),
                        BinaryOp("*", Variable("FAT"), Variable("I")),
                    ),
                    Continue(10),
                ],
            ),
            Print(
                [
                    String("Factorial of "),
                    Variable("N"),
                    String(": "),
                    Variable("FAT"),
                ]
            ),
        ],
    )

    code = analyze_and_generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        'PUSHS "Enter a positive integer:"\n'
        "WRITES\n"
        "WRITELN\n"
        "READ\n"
        "ATOI\n"
        "STOREG 0\n"
        "PUSHI 1\n"
        "STOREG 2\n"
        "PUSHI 1\n"
        "STOREG 1\n"
        "DO_START_1:\n"
        "PUSHG 1\n"
        "PUSHG 0\n"
        "INFEQ\n"
        "JZ DO_END_2\n"
        "PUSHG 2\n"
        "PUSHG 1\n"
        "MUL\n"
        "STOREG 2\n"
        "F_10:\n"
        "PUSHG 1\n"
        "PUSHI 1\n"
        "ADD\n"
        "STOREG 1\n"
        "JUMP DO_START_1\n"
        "DO_END_2:\n"
        'PUSHS "Factorial of "\n'
        "WRITES\n"
        "PUSHG 0\n"
        "WRITEI\n"
        'PUSHS ": "\n'
        "WRITES\n"
        "PUSHG 2\n"
        "WRITEI\n"
        "WRITELN\n"
        "STOP\n"
    )


def test_backend_sum_array_program():
    program = Program(
        name="SOMAARR",
        declarations=[
            Declaration("INTEGER", ["NUMS(5)"]),
            Declaration("INTEGER", ["I", "SOMA"]),
        ],
        statements=[
            Assignment(Variable("SOMA"), Number(0)),
            Print([String("Introduza 5 numeros inteiros:")]),
            Do(
                label=30,
                variable="I",
                start=Number(1),
                end=Number(5),
                body=[
                    Read([ArrayAccess("NUMS", Variable("I"))]),
                    Assignment(
                        Variable("SOMA"),
                        BinaryOp(
                            "+",
                            Variable("SOMA"),
                            ArrayAccess("NUMS", Variable("I")),
                        ),
                    ),
                    Continue(30),
                ],
            ),
            Print(
                [
                    String("A soma dos numeros e: "),
                    Variable("SOMA"),
                ]
            ),
        ],
    )

    code = analyze_and_generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "STOREG 6\n"
        'PUSHS "Introduza 5 numeros inteiros:"\n'
        "WRITES\n"
        "WRITELN\n"
        "PUSHI 1\n"
        "STOREG 5\n"
        "DO_START_1:\n"
        "PUSHG 5\n"
        "PUSHI 5\n"
        "INFEQ\n"
        "JZ DO_END_2\n"
        "PUSHGP\n"
        "PUSHG 5\n"
        "PUSHI 1\n"
        "SUB\n"
        "CHECK 0 4\n"
        "PADD\n"
        "READ\n"
        "ATOI\n"
        "STORE 0\n"
        "PUSHG 6\n"
        "PUSHGP\n"
        "PUSHG 5\n"
        "PUSHI 1\n"
        "SUB\n"
        "CHECK 0 4\n"
        "PADD\n"
        "LOAD 0\n"
        "ADD\n"
        "STOREG 6\n"
        "F_30:\n"
        "PUSHG 5\n"
        "PUSHI 1\n"
        "ADD\n"
        "STOREG 5\n"
        "JUMP DO_START_1\n"
        "DO_END_2:\n"
        'PUSHS "A soma dos numeros e: "\n'
        "WRITES\n"
        "PUSHG 6\n"
        "WRITEI\n"
        "WRITELN\n"
        "STOP\n"
    )


def test_backend_prime_program():
    program = Program(
        name="PRIMO",
        declarations=[
            Declaration("INTEGER", ["NUM", "I"]),
            Declaration("LOGICAL", ["ISPRIM"]),
        ],
        statements=[
            Print([String("Introduza um numero inteiro positivo:")]),
            Read([Variable("NUM")]),
            Assignment(Variable("ISPRIM"), Boolean(True)),
            Assignment(Variable("I"), Number(2)),
            # Equivalent backend representation of:
            # 20 IF (...) THEN
            Continue(20),
            If(
                condition=BinaryOp(
                    ".AND.",
                    BinaryOp(
                        ".LE.",
                        Variable("I"),
                        BinaryOp("/", Variable("NUM"), Number(2)),
                    ),
                    Variable("ISPRIM"),
                ),
                then_body=[
                    If(
                        condition=BinaryOp(
                            ".EQ.",
                            FunctionCall("MOD", [Variable("NUM"), Variable("I")]),
                            Number(0),
                        ),
                        then_body=[Assignment(Variable("ISPRIM"), Boolean(False))],
                    ),
                    Assignment(
                        Variable("I"),
                        BinaryOp("+", Variable("I"), Number(1)),
                    ),
                    GOTO(20),
                ],
            ),
            If(
                condition=Variable("ISPRIM"),
                then_body=[
                    Print(
                        [
                            Variable("NUM"),
                            String(" e um numero primo"),
                        ]
                    )
                ],
                else_body=[
                    Print(
                        [
                            Variable("NUM"),
                            String(" nao e um numero primo"),
                        ]
                    )
                ],
            ),
        ],
    )

    code = analyze_and_generate(program)

    assert_in_order(
        code,
        [
            'PUSHS "Introduza um numero inteiro positivo:"',
            "WRITES",
            "READ",
            "ATOI",
            "STOREG 0",
            "PUSHI 1",
            "STOREG 2",
            "PUSHI 2",
            "STOREG 1",
            "F_20:",
            "PUSHG 1",
            "PUSHG 0",
            "PUSHI 2",
            "DIV",
            "INFEQ",
            "PUSHG 2",
            "AND",
            "JZ ELSE_1",
            "PUSHG 0",
            "PUSHG 1",
            "MOD",
            "PUSHI 0",
            "EQUAL",
            "JZ ELSE_3",
            "PUSHI 0",
            "STOREG 2",
            "PUSHG 1",
            "PUSHI 1",
            "ADD",
            "STOREG 1",
            "JUMP F_20",
            "PUSHG 2",
            "JZ ELSE_5",
            "PUSHG 0",
            "WRITEI",
            'PUSHS " e um numero primo"',
            "WRITES",
            "JUMP ENDIF_6",
            "PUSHG 0",
            "WRITEI",
            'PUSHS " nao e um numero primo"',
            "WRITES",
            "STOP",
        ],
    )


def test_backend_converter_user_defined_function_is_not_supported_yet():
    program = Program(
        name="CONVERSOR",
        declarations=[Declaration("INTEGER", ["NUM", "BASE", "RESULT", "CONVRT"])],
        statements=[
            Print([String("INTRODUZA UM NUMERO DECIMAL INTEIRO:")]),
            Read([Variable("NUM")]),
            Do(
                label=10,
                variable="BASE",
                start=Number(2),
                end=Number(9),
                body=[
                    Assignment(
                        Variable("RESULT"),
                        FunctionCall(
                            "CONVRT",
                            [Variable("NUM"), Variable("BASE")],
                        ),
                    ),
                    Print(
                        [
                            String("BASE "),
                            Variable("BASE"),
                            String(": "),
                            Variable("RESULT"),
                        ]
                    ),
                    Continue(10),
                ],
            ),
        ],
    )

    with pytest.raises(SemanticError, match="Unsupported function call 'CONVRT'"):
        analyze_and_generate(program)
