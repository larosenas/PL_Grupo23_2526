import ply.yacc as yacc
from src.lexer import tokens
from src.ast_nodes import *

#operators precedence
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),
)

def p_program(p):
    """program: PROGRAM ID NEWLINE declarations statements END"""
    p[0]= Program(name=p[2], declarations=p[4], statements=p[5])

def p_declarations(p):
    """declarations: declarations declaration
                    | empty"""
    ...

def p_declaration(p):
    """declaration : type id_list NEWLINE"""
    ...

def p_type(p):
    """type : INTEGER
            | REAL
            | LOGICAL"""
    p[0] = p[1]

def p_statement_assign(p):
    """statement : ID ASSIGN expression NEWLINE"""
    p[0] = Assignment(target=Variable(p[1]), expr=p[3])

def p_statement_print(p):
    """statement : PRINT TIMES COMMA expr_list NEWLINE"""
    p[0] = Print(values=p[4])

def p_statement_read(p):
    """statement : READ TIMES COMMA id_list NEWLINE"""
    p[0] = Read(variables=[Variable(v) for v in p[4]])

def p_statement_if(p):
    """statement : IF LPAREN expression RPAREN THEN NEWLINE statements ENDIF NEWLINE
                 | IF LPAREN expression RPAREN THEN NEWLINE statements ELSE NEWLINE statements ENDIF NEWLINE"""
    ...

def p_statement_do(p):
    """statement : INT_NUMBER DO INT_NUMBER ID ASSIGN expression COMMA expression NEWLINE statements"""
    ...

def p_statement_goto(p):
    """statement : GOTO INT_NUMBER NEWLINE"""
    p[0] = GOTO(label=p[2])

def p_statement_continue(p):
    """statement : INT_NUMBER CONTINUE NEWLINE"""
    p[0] = Continue(label=p[1])


#Expressions with precedence
def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression AND expression
                  | expression OR expression"""
    p[0] = BinaryOp(op=p[2], left=p[1], right=p[3])

def p_expression_not(p):
    """expression : NOT expression"""
    p[0] = BinaryOp(op='NOT', left=p[2], right=None)

def p_expression_number(p):
    """expression : INT_NUMBER
                  | REAL_NUMBER"""
    p[0] = Number(value=p[1])

def p_expression_variable(p):
    """expression : ID"""
    p[0] = Variable(name=p[1])

def p_expression_string(p):
    """expression : STRING"""
    p[0] = String(value=p[1])

def p_expression_bool(p):
    """expression : TRUE
                  | FALSE"""
    p[0] = Boolean(value=p[1])

def p_expression_paren(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_empty(p):
    """empty :"""
    p[0] = []

def p_error(p):
    raise SyntaxError(f"Syntax error at token '{p.value}', line {p.lineno}")

parser = yacc.yacc()

def parse(source_code):
    from src.lexer import lexer
    lexer.lineno = 1
    return parser.parse(source_code, lexer=lexer)

