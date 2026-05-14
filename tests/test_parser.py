import src
from src.parser import parse
from src.ast_nodes import *


def test_parse_hello():
    # Test parsing a simple hello world program.
    src = "PROGRAM HELLO\nPRINT *, 'Hello World!'\nEND\n"
    tree = parse(src)
    assert isinstance(tree, Program)
    assert tree.name == "HELLO"
    assert len(tree.statements) == 1
    assert isinstance(tree.statements[0], Print)

def test_parse_assignment():
    # Test parsing an assignment statement.
    src = "PROGRAM T\nINTEGER X\nX = 5\nEND\n"
    tree = parse(src)
    assert isinstance(tree.statements[0], Assignment)

def test_parse_if():
    # Test parsing an if statement with a condition.
    src = "PROGRAM T\nIF (A .GT. 0) THEN\nPRINT *, 'pos'\nENDIF\nEND\n"
    tree = parse(src)
    assert isinstance(tree.statements[0], If)

def test_parse_do():
    ...

def test_parse_goto():
    ...


def test_parse_array_access_in_read() :
    #test parsing an array access in a read   
    src = "PROGRAM T\nINTEGER NUMS\nINTEGER I\nREAD *, NUMS(I)\nEND\n"
    tree = parse(src)
    read_stmt = tree.statements[0]
    assert isinstance(read_stmt.variables[0], ArrayAccess)
    assert read_stmt.variables[0].name == "NUMS"

def test_parse_array_access_in_expression():
    #test parsing an array access in an expression
    src = "PROGRAM T\nINTEGER NUMS\nINTEGER I\nINTEGER SOMA\nSOMA = SOMA + NUMS(I)\nEND\n"
    tree = parse(src)

    assignment = tree.statements[0]
    assert isinstance(assignment.expr.right, ArrayAccess)
    assert assignment.expr.right.name == "NUMS"

def test_parse_function_call():
    #test parsing a function call
    src = "PROGRAM T\nINTEGER NUM\nINTEGER I\nIF (MOD(NUM, I) .EQ. 0) THEN\nPRINT *, 'divisible'\nENDIF\nEND\n"
    tree = parse(src)

    if_stmt = tree.statements[0]
    assert isinstance(if_stmt.condition.left, FunctionCall)
    assert if_stmt.condition.left.name == "MOD"