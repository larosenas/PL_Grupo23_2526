from src.ast_nodes import (
    Program,
    Print,
    Read,
    String,
    Assignment,
    Declaration,
    Number,
    Variable,
    BinaryOp,
    Boolean,
    If,
    GOTO,
    Continue,
    Do,
    FunctionCall,
    ArrayAccess,
    UnaryOp,
)
from src.codegen import CodeGenerator

# Code generation unit tests for the simple VM backend.
# These tests ensure that AST nodes are translated into the expected instruction stream.


def test_codegen_print_string():
    program = Program(
        name="HELLO",
        declarations=[],
        statements=[Print([String("Hello, World!")])],
    )

    code = CodeGenerator().generate(program)

    assert code == ('PUSHS "Hello, World!"\n' "WRITES\n" "WRITELN\n" "STOP\n")


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


def test_codegen_read_integer_variable():
    # Test reading an integer value into a variable from input.
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["N"])],
        statements=[Read([Variable("N")])],
    )

    code = CodeGenerator().generate(program)

    assert code == ("PUSHI 0\n" "READ\n" "ATOI\n" "STOREG 0\n" "STOP\n")


def test_codegen_boolean_assignment():
    # Test assigning a boolean value to a logical variable.
    program = Program(
        name="TEST",
        declarations=[Declaration("LOGICAL", ["FLAG"])],
        statements=[Assignment(Variable("FLAG"), Boolean(True))],
    )

    code = CodeGenerator().generate(program)

    assert code == ("PUSHI 0\n" "PUSHI 1\n" "STOREG 0\n" "STOP\n")


def test_codegen_relational_expression():
    # Test evaluating a relational expression (greater than) and assigning to a boolean variable.
    program = Program(
        name="TEST",
        declarations=[
            Declaration("INTEGER", ["A"]),
            Declaration("LOGICAL", ["FLAG"]),
        ],
        statements=[
            Assignment(Variable("A"), Number(3)),
            Assignment(
                Variable("FLAG"),
                BinaryOp(".GT.", Variable("A"), Number(0)),
            ),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 3\n"
        "STOREG 0\n"
        "PUSHG 0\n"
        "PUSHI 0\n"
        "SUP\n"
        "STOREG 1\n"
        "STOP\n"
    )


def test_codegen_logical_and_expression():
    # Test evaluating a logical AND operation between two boolean variables.
    program = Program(
        name="TEST",
        declarations=[Declaration("LOGICAL", ["A", "B", "C"])],
        statements=[
            Assignment(Variable("A"), Boolean(True)),
            Assignment(Variable("B"), Boolean(False)),
            Assignment(
                Variable("C"),
                BinaryOp(".AND.", Variable("A"), Variable("B")),
            ),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 1\n"
        "STOREG 0\n"
        "PUSHI 0\n"
        "STOREG 1\n"
        "PUSHG 0\n"
        "PUSHG 1\n"
        "AND\n"
        "STOREG 2\n"
        "STOP\n"
    )


def test_codegen_if_else():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[
            If(
                condition=BinaryOp(".GT.", Variable("A"), Number(0)),
                then_body=[Print([Variable("A")])],
                else_body=[Print([Number(0)])],
            )
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHG 0\n"
        "PUSHI 0\n"
        "SUP\n"
        "JZ ELSE_1\n"
        "PUSHG 0\n"
        "WRITEI\n"
        "WRITELN\n"
        "JUMP ENDIF_2\n"
        "ELSE_1:\n"
        "PUSHI 0\n"
        "WRITEI\n"
        "WRITELN\n"
        "ENDIF_2:\n"
        "STOP\n"
    )


def test_codegen_goto_and_continue():
    # Test generating code for GOTO and CONTINUE statements with labels.
    program = Program(
        name="TEST",
        declarations=[],
        statements=[
            GOTO(20),
            Continue(20),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == ("JUMP F_20\n" "F_20:\n" "STOP\n")


def test_codegen_do_loop():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["I", "FAT"])],
        statements=[
            Assignment(Variable("FAT"), Number(1)),
            Do(
                label=10,
                variable="I",
                start=Number(1),
                end=Number(5),
                body=[
                    Assignment(
                        Variable("FAT"),
                        BinaryOp("*", Variable("FAT"), Variable("I")),
                    ),
                    Continue(10),
                ],
            ),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 1\n"
        "STOREG 1\n"
        "PUSHI 1\n"
        "STOREG 0\n"
        "DO_START_1:\n"
        "PUSHG 0\n"
        "PUSHI 5\n"
        "INFEQ\n"
        "JZ DO_END_2\n"
        "PUSHG 1\n"
        "PUSHG 0\n"
        "MUL\n"
        "STOREG 1\n"
        "F_10:\n"
        "PUSHG 0\n"
        "PUSHI 1\n"
        "ADD\n"
        "STOREG 0\n"
        "JUMP DO_START_1\n"
        "DO_END_2:\n"
        "STOP\n"
    )


def test_codegen_mod_function_call():
    # Test calling the MOD function and assigning the result to a variable.
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[
            Assignment(
                Variable("A"),
                FunctionCall("MOD", [Number(10), Number(3)]),
            )
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == ("PUSHI 0\n" "PUSHI 10\n" "PUSHI 3\n" "MOD\n" "STOREG 0\n" "STOP\n")


def test_codegen_array_read_and_access():
    # Test reading into an array element and accessing it in an expression.
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["NUMS(5)", "I", "SOMA"])],
        statements=[
            Read([ArrayAccess("NUMS", Variable("I"))]),
            Assignment(
                Variable("SOMA"),
                BinaryOp(
                    "+",
                    Variable("SOMA"),
                    ArrayAccess("NUMS", Variable("I")),
                ),
            ),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 0\n"
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
        "STOP\n"
    )


def test_codegen_logical_not_expression():
    program = Program(
        name="TEST",
        declarations=[Declaration("LOGICAL", ["FLAG", "RESULT"])],
        statements=[
            Assignment(Variable("FLAG"), Boolean(True)),
            Assignment(
                Variable("RESULT"),
                UnaryOp(".NOT.", Variable("FLAG")),
            ),
        ],
    )

    code = CodeGenerator().generate(program)

    assert code == (
        "PUSHI 0\n"
        "PUSHI 0\n"
        "PUSHI 1\n"
        "STOREG 0\n"
        "PUSHG 0\n"
        "NOT\n"
        "STOREG 1\n"
        "STOP\n"
    )
