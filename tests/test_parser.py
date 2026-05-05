from src.parser import parse
from src.ast_nodes import *


def test_parse_hello():
    src = "PROGRAM HELLO\nPRINT *, 'Ola Mundo!'\nEND\n"
    tree = parse(src)
    assert isinstance(tree, Program)
    assert tree.name == "HELLO"
    assert len(tree.statements) == 1
    assert isinstance(tree.statements[0], Print)

def test_parse_assignment():
    src = "PROGRAM T\nINTEGER X\nX = 5\nEND\n"
    tree = parse(src)
    assert isinstance(tree.statements[0], Assigment)

def test_parse_if():
    src = "PROGRAM T\nIF (A .GT. 0) THEN\nPRINT *, 'pos'\nENDIF\nEND\n"
    tree = parse(src)
    assert isinstance(tree.statements[0], If)

def test_parse_do():
    ...

def test_parse_goto():
    ...