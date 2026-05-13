import ply.yacc as yacc
from src.lexer import tokens, lexer
from src.ast_nodes import *

# operators precedence
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("left", "EQ", "NE", "LT", "LE", "GT", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "UMINUS")
)

# program structure


def p_program(p):
    """program : PROGRAM ID NEWLINE declarations statement_list END newlines_opt"""
    p[0] = Program(name=p[2], declarations=p[4], statements=p[5])


def p_declarations_empty(p):
    """declarations : empty"""
    p[0] = []


def p_declaration_list(p):
    """declarations : declarations declaration"""
    p[0] = p[1] + [p[2]]


def p_declaration(p):
    """declaration : type id_list NEWLINE"""
    p[0] = Declaration(var_type=p[1], names=p[2])


def p_type(p):
    """type : INTEGER
    | REAL
    | LOGICAL"""
    p[0] = p[1]


# Lists


def p_id_list_single(p):
    """id_list : ID"""
    p[0] = [p[1]]


def p_id_list_multiple(p):
    """id_list : id_list COMMA ID"""
    p[0] = p[1] + [p[3]]


def p_expr_list_single(p):
    """expr_list : expression"""
    p[0] = [p[1]]


def p_expr_list_multiple(p):
    """expr_list : expr_list COMMA expression"""
    p[0] = p[1] + [p[3]]

def p_decl_list_single(p):
    """decl_list : declaration"""
    p[0] = [p[1]]

def p_decl_list_multiple(p):
    """decl_list : decl_list COMMA declaration"""
    p[0] = p[1] + [p[3]]


# Statements


def p_statement_list_empty(p):
    """statement_list : empty"""
    p[0] = []


def p_statement_list_multiple(p):
    """statement_list : statement_list statement"""
    p[0] = p[1] + [p[2]]


def p_statement(p):
    """
    statement : assignment
              | print_statement
              | read_statement
              | if_statement
              | do_statement
              | goto_statement
              | continue_statement
    """
    p[0] = p[1]


def p_assignment(p):
    """assignment : ID ASSIGN expression NEWLINE"""
    p[0] = Assignment(target=Variable(p[1]), expr=p[3])


def p_print_statement(p):
    """print_statement : PRINT TIMES COMMA expr_list NEWLINE"""
    p[0] = Print(values=p[4])


def p_read_statement(p):
    """read_statement : READ TIMES COMMA expr_list NEWLINE"""
    p[0] = Read(variables= p[4])


def p_if_statement(p):
    """if_statement : IF LPAREN expression RPAREN THEN NEWLINE statement_list ENDIF NEWLINE
    | IF LPAREN expression RPAREN THEN NEWLINE statement_list ELSE NEWLINE statement_list ENDIF NEWLINE
    """
    p[0] = If(condition=p[3], then_body=p[7], else_body=p[10] if len(p) == 13 else None)

def p_do_statement(p):
    """do_statement : INT_NUMBER DO INT_NUMBER ID ASSIGN expression COMMA expression NEWLINE statement_list"""
    p[0] = Do(label=p[2], variable=p[3], start=p[5], end=p[7], body=p[10])


def p_goto_statement(p):
    """goto_statement : GOTO INT_NUMBER NEWLINE"""
    p[0] = GOTO(label=p[2])


def p_continue_statement(p):
    """continue_statement : INT_NUMBER CONTINUE NEWLINE"""
    p[0] = Continue(label=p[1])


# Expressions with precedence
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
    #modelate NOT as a binary operator with right = None so that FunctionCall is free to use it as a unary operator
    p[0] = BinaryOp(op="NOT", left=p[2], right=None)

def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS"""
    p[0] = BinaryOp(op="UMINUS", left=p[2], right=None)


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


def p_expr_true(p):
    """expression : TRUE"""
    p[0] = Boolean(value=True)
 
def p_expr_false(p):
    """expression : FALSE"""
    p[0] = Boolean(value=False)

def p_expression_paren(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_empty(p):
    """empty :"""
    p[0] = []


#Acess to the array/ function call
def p_expr_call_or_array(p):
    """expression : ID LPAREN expr_list RPAREN"""
    #If there is only one argument and it is an integer, 
    # we let the semantic analysis decide if it is an array access 
    # or a function call, otherwise we model it as a function call
    if len(p[3]) == 1:
        p[0] = ArrayAccess(
            name=p[1],
            index=p[3][0],
        )
    else:
        p[0] = FunctionCall(
            name=p[1],
            arguments=p[3],
        )

#Newline rules 
 
def p_newlines(p):
    """newlines : NEWLINE
                | newlines NEWLINE"""
    pass  # solo necesitamos que existan, no su valor
 
def p_newlines_opt(p):
    """newlines_opt : newlines
                    | empty"""
    pass




# Error handling


def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at token '{p.value}', line {p.lineno}")
    raise SyntaxError("Syntax error end of input")


#Construct the parser

parser = yacc.yacc(debug=False, write_tables=False)


def parse(source_code: str):

    if not source_code.endswith("\n"):
        source_code += "\n"

    #Reset line number for each new parse
    lexer.lineno = 1
    return parser.parse(source_code, lexer=lexer)
