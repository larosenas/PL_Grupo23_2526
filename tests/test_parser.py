from src.parser import parse
from src.ast_nodes import *


def test_parse_hello():
    # Test parsing a simple hello world program.

    src = "PROGRAM HELLO\nPRINT *, 'Hello World!'\nEND\n"

    tree = parse(src)

    assert isinstance(tree.program, Program)
    assert tree.program.name == "HELLO"
    assert len(tree.program.statements) == 1
    assert isinstance(tree.program.statements[0], Print)

def test_parse_assignment():
    # Test parsing an assignment statement.

    src = "PROGRAM T\nINTEGER X\nX = 5\nEND\n"

    tree = parse(src)
    assert isinstance(tree.program.statements[0], Assignment)

def test_parse_if():
    # Test parsing an if statement with a condition.

    src = "PROGRAM T\nIF (A .GT. 0) THEN\nPRINT *, 'pos'\nENDIF\nEND\n"

    tree = parse(src)
    assert isinstance(tree.program.statements[0], If)

def test_parse_do():
    #test parsing a do statement with a loop variable and a label 

    src = "PROGRAM T\n" "INTEGER I\n" "DO 10 I = 1, 5\n" "PRINT *, I\n" "10 CONTINUE\n" "END\n"

    tree = parse(src)

    assert isinstance(tree.program.statements[0], Do)
    assert tree.program.statements[0].label == 10
    assert tree.program.statements[0].variable == "I"
    assert isinstance(tree.program.statements[0].body[-1], Continue)
    assert tree.program.statements[0].label == 10


def test_parse_goto():
    #test parsing a goto and a continue statement with the same label

    src = "PROGRAM T\n" "GOTO 20\n" "20 CONTINUE\n" "END\n"
    
    tree = parse(src)

    assert isinstance(tree.program.statements[0], GOTO)
    assert tree.program.statements[0].label == 20   
    assert isinstance(tree.program.statements[1], Continue)
    assert tree.program.statements[1].label == 20

def test_parse_array_access_in_read() :
    #test parsing an array access in a read   

    src = "PROGRAM T\nINTEGER NUMS\nINTEGER I\nREAD *, NUMS(I)\nEND\n"

    tree = parse(src)

    read_stmt = tree.program.statements[0]
    assert isinstance(read_stmt.variables[0], ArrayAccess)
    assert read_stmt.variables[0].name == "NUMS"

def test_parse_array_declaration():
    #test parsing an array declaration

    src = "PROGRAM T\n" "INTEGER NUMS(5)\n" "END\n"

    tree = parse(src)

    assert len(tree.program.declarations) == 1
    assert tree.program.declarations[0].var_type == "INTEGER"
    assert tree.program.declarations[0].names == ["NUMS(5)"]

def test_parse_array_access_in_expression():
    #test parsing an array access in an expression

    src = "PROGRAM T\nINTEGER NUMS\nINTEGER I\nINTEGER SOMA\nSOMA = SOMA + NUMS(I)\nEND\n"

    tree = parse(src)

    assignment = tree.program.statements[0]
    assert isinstance(assignment.expr.right, ArrayAccess)
    assert assignment.expr.right.name == "NUMS"

def test_parse_function_call():
    #test parsing a function call

    src = "PROGRAM T\nINTEGER NUM\nINTEGER I\nIF (MOD(NUM, I) .EQ. 0) THEN\nPRINT *, 'divisible'\nENDIF\nEND\n"

    tree = parse(src)

    if_stmt = tree.program.statements[0]
    assert isinstance(if_stmt.condition.left, FunctionCall)
    assert if_stmt.condition.left.name == "MOD"

def test_parse_function():
    #test parsing a function definition with parameters and a return type

    src = "PROGRAM T\n INTEGER RESULT\n RESULT = CONVRT(5, 2)\n END\n INTEGER FUNCTION CONVRT(N, B)\n INTEGER N, B\n CONVRT = N + B\n RETURN\n END\n"

    tree = parse(src)

    
    assert isinstance(tree.program, Program)
    assert len(tree.subprograms) == 1
    func = tree.subprograms[0]
    assert isinstance(func, Function)
    assert func.name == "CONVRT"
    assert func.return_type == "INTEGER"
    assert func.params == ["N", "B"]


def test_parse_subroutine():
    #test parsing a subroutine definition with parameters

    src = "PROGRAM T\n INTEGER A\n A = 1\n END\n SUBROUTINE MYSUB(X, Y)\n INTEGER X, Y\n X = X + Y\n RETURN\n END\n"
    
    tree = parse(src)

    assert isinstance(tree.program, Program)
    assert len(tree.subprograms) == 1
    sub = tree.subprograms[0]
    assert isinstance(sub, Subroutine)
    assert sub.name == "MYSUB"
    assert sub.params == ["X", "Y"]


def test_parse_multiple_subprograms():
    #test parding multiple subprograms (functions and subroutines) in the same program

    src =  "PROGRAM T\n INTEGER A\n END\n INTEGER FUNCTION FOO(X)\n INTEGER X\n FOO = X\n RETURN\n END\n SUBROUTINE BAR(Y)\n INTEGER Y\n Y = 0\n RETURN\n END\n"

    tree = parse(src)

    assert len(tree.subprograms) == 2
    assert isinstance(tree.subprograms[0], Function)
    assert isinstance(tree.subprograms[1], Subroutine)