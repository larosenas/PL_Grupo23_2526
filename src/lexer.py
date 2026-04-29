import ply.lex as lex

reserved = {
    "PROGRAM": "PROGRAM",
    "END": "END",
    "INTEGER": "INTEGER",
    "REAL": "REAL",
    "IF": "IF",
    "LOGICAL": "LOGICAL",
    "THEN": "THEN",
    "ELSE": "ELSE",
    "ENDIF": "ENDIF",
    "DO": "DO",
    "CONTINUE": "CONTINUE",
    "GOTO": "GOTO",
    "READ": "READ",
    "PRINT": "PRINT",
    "RETURN": "RETURN",
    "FUNCTION": "FUNCTION",
    "SUBROUTINE": "SUBROUTINE",
}





# List of token names

tokens = [
    "ID", "INT_NUMBER", "REAL_NUMBER", "STRING",
    "PLUS", "MINUS", "TIMES", "DIVIDE", "ASSIGN",
    "LPAREN", "RPAREN", "COMMA", "SEMICOLON",
    "EQ", "NE", "LT", "GT", "LE", "GE",
    "AND", "OR", "NOT", "TRUE", "FALSE",
] + list(reserved.values())

# Regular expression rules for simple tokens
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_ASSIGN = r":="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","
t_SEMICOLON = r";"

def t_EQ(t):
    r".EQ\."
    return t

def t_NE(t):
    r".NE\."
    return t

def t_LT(t):
    r".LT\."
    return t

def t_GT(t):
    r".GT\."
    return t

def t_LE(t):
    r".LE\."
    return t

def t_GE(t):
    r".GE\."
    return t

def t_AND(t):
    r".AND\."
    return t

def t_OR(t):
    r".OR\."
    return t

def t_NOT(t):
    r".NOT\."
    return t

def t_TRUE(t):
    r".TRUE\."
    t.value = True
    return t

def t_FALSE(t):
    r".FALSE\."
    t.value = False
    return t

def t_REAL_NUMBER(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t

def t_INT_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t        

def t_STRING(t):
    r"'[^']*'"
    t.value = t.value[1:-1]  # Remove the surrounding quotes
    return t

def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    upper_value = t.value.upper()
    t.type = reserved.get(upper_value, "ID")  
    t.value = upper_value
    return t

t_ignore = " \t\r"

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_comment(t):
    r"!.*"
    pass


def t_error(t):
    raise SyntaxError(
        f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}"
    )

lexer = lex.lex()

def tokenize(source_code):
    lexer.input(source_code)
    return list(lexer)



