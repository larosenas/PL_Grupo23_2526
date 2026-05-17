from src.lexer import tokenize

def token_types(source):
    # Extract the token types from the tokenized source code.
    return [token.type for token in tokenize(source)]

def token_values(source):
    # Extract the token values from the tokenized source code.
    return [token.value for token in tokenize(source)]

def test_program_header_tokens():
    assert token_types("PROGRAM HELLO") == ["PROGRAM","ID"]

def test_integer_declaration_tokens():
    assert token_types("INTEGER A, B") == [
        "INTEGER",
        "ID",
        "COMMA",
        "ID",
    ]

def test_print_string_tokens():
    assert token_types("PRINT *, 'Hello, World!'") == [
        "PRINT",
        "TIMES",
        "COMMA",
        "STRING",
    ]

def test_arithmetic_expression_tokens():
    assert token_types("A = 3 + 2 * B") == [
        "ID",
        "ASSIGN",
        "INT_NUMBER",
        "PLUS",
        "INT_NUMBER",
        "TIMES",
        "ID",
    ]

def test_relational_operator_tokens():
    assert token_types("A .LE. B") == ["ID", "LE", "ID"]


def test_logical_operator_tokens():
    assert token_types("A .AND. .TRUE.") == ["ID", "AND", "TRUE"]


def test_string_value_without_quotes():
    assert token_values("'Hello, World!'") == ["Hello, World!"]


def test_boolean_values():
    assert token_values(".TRUE. .FALSE.") == [True, False]