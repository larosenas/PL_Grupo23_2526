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