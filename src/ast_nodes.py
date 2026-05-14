from dataclasses import dataclass
from typing import List, Optional, Union

## Base classes
# -----------------------


class ASTnode:
    """
    Base class for all AST nodes.
    It is useful for type checking and for keeping the AST structure clear.
    """

    pass


class Statement(ASTnode):
    """
    Base class for executable statements.
    Ex: IF,DO,PRINT,...
    """

    pass


class Expression(ASTnode):
    """
    Base class for exceptions
    """

    pass


## Program structure
# ---------------------


@dataclass
class Program(ASTnode):
    """
    Represents a complete Fortran program.
    """

    name: str
    declarations: List["Declaration"]
    statements: List[Statement]


@dataclass
class Declaration(ASTnode):
    """
    Represents a variable declaration
    """

    var_type: str
    names: List[str]


## Statements
# ------------------


@dataclass
class Assignment(Statement):
    """
    Represents and assignment
    """

    target: Expression  # no como str para poder soportar arrays
    expr: Expression


@dataclass
class Print(Statement):
    """
    Reprensents a print statement
    """

    values: List[Expression]


@dataclass
class Read(Statement):
    """
    Reprensents a read statement
    """

    variables: List[Expression]


@dataclass
class If(Statement):
    """
    Reprensents a if,then,else,endif block
    """

    condition: Expression
    then_body: List[Statement]
    else_body: Optional[List[Statement]] = None


@dataclass
class Do(Statement):
    """
    Reprensents a do loop with a label
    """

    label: int
    variable: str
    start: Expression
    end: Expression
    body: List[Statement]


@dataclass
class GOTO(Statement):
    """
    Reprensents a GOTO statement
    """

    label: int


@dataclass
class Continue(Statement):
    """
    Reprensents a labelled CONTINUE statement
    """

    label: Optional[int] = None


@dataclass
class Return(Statement):
    """
    Reprensents a RETURN statement
    """

    pass


## Expressions
# ----------------


@dataclass
class BinaryOp(Expression):
    """
    Reprensents a binary operation
    """

    op: str
    left: Expression
    right: Expression


@dataclass
class UnaryOp(Expression):
    """
    Represents a unary operation.
    Example: .NOT. FLAG
    """

    op: str
    operand: Expression


@dataclass
class Number(Expression):
    """
    Reprensents an integer or a real number
    """

    value: Union[int, float]


@dataclass
class String(Expression):
    """
    Reprensents a string
    """

    value: str


@dataclass
class Boolean(Expression):
    """
    Reprensents a logical value
    """

    value: bool


@dataclass
class Variable(Expression):
    """
    Reprensents a variable usage
    """

    name: str


@dataclass
class ArrayAccess(Expression):
    """
    Reprensents access to an array position
    """

    name: str
    index: Expression


@dataclass
class FunctionCall(Expression):
    """
    Reprensents a function call
    """

    name: str
    arguments: List[Expression]
