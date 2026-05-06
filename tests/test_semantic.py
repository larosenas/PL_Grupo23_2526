# Semantic Analysis Test Suite
# This module contains comprehensive tests for the semantic analyzer component.
# Tests cover variable declaration, type checking, control flow validation,
# and error detection for a Fortran-inspired programming language.

# Import pytest framework for testing and assertion utilities
import pytest

# Import AST node classes representing the abstract syntax tree elements
from src.ast_nodes import (
    ArrayAccess,
    Assignment,
    BinaryOp,
    Boolean,
    Continue,
    Declaration,
    Do,
    GOTO,
    If,
    Number,
    Print,
    Program,
    Read,
    String,
    Variable,
)
# Import custom exception class for semantic analysis errors
from src.errors import SemanticError
# Import the semantic analyzer that performs type checking and validation
from src.semantic import SemanticAnalyzer


# Test Infrastructure
# ===================

# Helper function that creates a SemanticAnalyzer instance and analyzes a program
def analyze(program):
    """Analyze a program and return its symbol table, or raise SemanticError if invalid."""
    return SemanticAnalyzer().analyze(program)


# Variable Declaration Tests
# ==========================

# Test: Valid program with variable declaration, assignment, and print statement
# This test verifies that a basic program with INTEGER variable declaration,
# assignment of a numeric value, and print statement is semantically correct
def test_valid_program_with_declaration_assignment_and_print():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[
            Assignment(Variable("A"), Number(3)),
            Print([Variable("A")]),
        ],
    )

    # Analyze the program for semantic validity
    table = analyze(program)

    # Verify that variable A is correctly stored as INTEGER type in symbol table
    assert table.lookup("A").var_type == "INTEGER"


# Test: Variable used before declaration should fail
# This test verifies that semantic analysis detects when a variable (B) is used
# without being declared first, which is a semantic error
def test_variable_used_before_declaration_fails():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[
            Assignment(
                Variable("B"),  # B is used but never declared
                BinaryOp("+", Variable("A"), Number(1)),
            )
        ],
    )

    # Expect a SemanticError containing the variable name "B"
    with pytest.raises(SemanticError, match="B"):
        analyze(program)


# Test: Duplicate variable declaration should fail
# This test verifies that the semantic analyzer rejects attempts to declare
# the same variable twice with different types
def test_duplicate_declaration_fails():
    program = Program(
        name="TEST",
        declarations=[
            Declaration("INTEGER", ["A"]),  # First declaration
            Declaration("REAL", ["A"]),     # Duplicate with different type
        ],
        statements=[],
    )

    # Expect a SemanticError with message about variable already being declared
    with pytest.raises(SemanticError, match="already declared"):
        analyze(program)


# Type Checking Tests
# ===================

# Test: Type incompatibility in assignment should fail
# This test verifies that semantic analysis detects incompatible type assignments,
# such as assigning a BOOLEAN value to an INTEGER variable
def test_incompatible_assignment_fails():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[Assignment(Variable("A"), Boolean(True))],  # BOOLEAN to INTEGER
    )

    # Expect a SemanticError about incompatible type assignment
    with pytest.raises(SemanticError, match="Cannot assign"):
        analyze(program)


# Control Flow Tests
# ==================

# Test: IF condition must be logical/boolean type
# This test verifies that semantic analysis requires IF statements to have
# boolean conditions, not arbitrary integer or other types
def test_if_condition_must_be_logical():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[
            If(
                condition=Variable("A"),  # INTEGER condition - should fail
                then_body=[Print([String("bad")])],
            )
        ],
    )

    # Expect a SemanticError about IF condition requiring logical type
    with pytest.raises(SemanticError, match="IF condition"):
        analyze(program)


# Test: Valid IF statement with relational condition
# This test verifies that IF statements work correctly when the condition
# is a relational expression (comparison) that produces a boolean result
def test_valid_if_with_relational_condition():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["A"])],
        statements=[
            If(
                condition=BinaryOp(".GT.", Variable("A"), Number(0)),  # Relational condition
                then_body=[Print([Variable("A")])],
                else_body=[Print([Number(0)])],
            )
        ],
    )

    # This should not raise an error - the program is semantically valid
    analyze(program)


# Label and GOTO Tests
# ====================

# Test: GOTO to undefined label should fail
# This test verifies that semantic analysis detects references to labels
# that do not exist in the program
def test_goto_to_undefined_label_fails():
    program = Program(
        name="TEST",
        declarations=[],
        statements=[GOTO(20)],  # Label 20 doesn't exist
    )

    # Expect a SemanticError about undefined label target
    with pytest.raises(SemanticError, match="undefined label"):
        analyze(program)


# Test: GOTO to existing CONTINUE label is valid
# This test verifies that GOTO statements are semantically valid when they
# reference an existing label defined by a CONTINUE statement
def test_goto_to_existing_continue_label_is_valid():
    program = Program(
        name="TEST",
        declarations=[],
        statements=[
            GOTO(20),      # Jump to label 20
            Continue(20),  # Label 20 defined here
        ],
    )

    # This should not raise an error - label 20 is defined by Continue statement
    analyze(program)


# DO Loop Tests
# =============

# Test: DO loop must finish with matching CONTINUE label
# This test verifies that semantic analysis ensures DO loops have a matching
# CONTINUE statement at the end with the same label number
def test_do_must_finish_with_matching_continue_label():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["I"])],
        statements=[
            Do(
                label=10,           # DO loop with label 10
                variable="I",       # Note: corrected from 'varibale' to 'variable'
                start=Number(1),
                end=Number(5),
                body=[Continue(20)], # CONTINUE with wrong label 20
            )
        ],
    )

    # Expect a SemanticError because DO label 10 doesn't match CONTINUE label 20
    with pytest.raises(SemanticError, match="CONTINUE label 10"):
        analyze(program)


# Test: Valid DO loop with proper structure
# This test verifies that a properly structured DO loop is semantically valid:
# - Loop variable I is declared as INTEGER
# - DO loop has label 10 and iterates from 1 to 5
# - Loop body contains matching CONTINUE(10) statement
# - Factorial calculation inside the loop is type-correct
def test_valid_do_loop():
    program = Program(
        name="TEST",
        declarations=[Declaration("INTEGER", ["I", "FAT"])],
        statements=[
            Assignment(Variable("FAT"), Number(1)),  # Initialize factorial to 1
            Do(
                label=10,
                variable="I",       # Note: corrected from 'varibale' to 'variable'
                start=Number(1),    # Loop from 1 to 5
                end=Number(5),
                body=[
                    Assignment(                      # FAT = FAT * I
                        Variable("FAT"),
                        BinaryOp("*", Variable("FAT"), Variable("I")),
                    ),
                    Continue(10),   # Matching CONTINUE label
                ],
            ),
        ],
    )

    # This should not raise an error - the DO loop is properly structured
    analyze(program)


# Array Tests
# ===========

# Test: Array access requires integer index type
# This test verifies that semantic analysis enforces type checking on array indices,
# ensuring that array subscripts must be INTEGER type, not REAL or other types
def test_array_access_requires_integer_index():
    program = Program(
        name="TEST",
        declarations=[
            Declaration("INTEGER", ["NUMS(5)"]),  # Array of 5 integers
            Declaration("REAL", ["I"]),           # REAL index variable
        ],
        statements=[Read([ArrayAccess("NUMS", Variable("I"))])],  # REAL index
    )

    # Expect a SemanticError because array index I is REAL instead of INTEGER
    with pytest.raises(SemanticError, match="Array index"):
        analyze(program)