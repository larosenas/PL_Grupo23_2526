# Semantic Analyzer for Fortran-like Language
# This module performs semantic analysis including type checking, variable declaration validation,
# and control flow verification for a Fortran-inspired programming language.

# Import necessary modules for data structures, regular expressions, and type hints
from dataclasses import dataclass
import re
from typing import Any, Dict, Iterable, Optional, Set

# Import AST node classes for semantic analysis
from src.ast_nodes import (
    ArrayAccess,
    Assignment,
    BinaryOp,
    Boolean,
    Continue,
    Declaration,
    Do,
    FuntionalCall,
    GOTO,
    If,
    Number,
    Print,
    Program,
    Read,
    Return,
    String,
    Variable,
    UnaryOp,
)

# Import custom error class for semantic errors
from src.errors import SemanticError

# Define string constants for data types to ensure consistency
INTEGER = "INTEGER"
REAL = "REAL"
LOGICAL = "LOGICAL"
STRING = "STRING"

# Set of numeric types for validation (used in arithmetic operations)
NUMERIC_TYPES = {INTEGER, REAL}
# Set of valid types for variables (excludes STRING as it's not assignable)
VALID_TYPES = {INTEGER, REAL, LOGICAL}


# Define a frozen dataclass to represent a symbol in the symbol table
@dataclass(frozen=True)
class Symbol:
    name: str
    var_type: str
    is_array: bool = False
    size: Optional[int] = None


# Class to manage the symbol table for variables
class SymbolTable:
    def __init__(self) -> None:
        # Initialize an empty dictionary to store symbols
        self._symbols: Dict[str, Symbol] = {}

    def declare(
        self,
        name: str,
        var_type: str,
        *,
        is_array: bool = False,
        size: Optional[int] = None,
    ) -> None:
        # Convert name and type to uppercase for consistency
        name = name.upper()
        var_type = var_type.upper()

        # Check if the type is valid
        if var_type not in VALID_TYPES:
            raise SemanticError(f"Unsupported type '{var_type}' for variable '{name}'")

        # Check if the variable is already declared
        if name in self._symbols:
            raise SemanticError(f"Variable '{name}' already declared")

        # For arrays, ensure size is positive
        if is_array and (size is None or size <= 0):
            raise SemanticError(f"Array '{name}' must have a positive size")

        # Add the symbol to the table
        self._symbols[name] = Symbol(name, var_type, is_array, size)

    def lookup(self, name: str) -> Symbol:
        # Convert name to uppercase
        name = name.upper()
        # Raise error if not found
        if name not in self._symbols:
            raise SemanticError(f"Variable '{name}' used before declaration")
        # Return the symbol
        return self._symbols[name]

    def contains(self, name: str) -> bool:
        # Check if the symbol exists
        return name.upper() in self._symbols

    def as_dict(self) -> Dict[str, Symbol]:
        # Return a copy of the symbols dictionary
        return dict(self._symbols)


# Main class for semantic analysis
class SemanticAnalyzer:
    def __init__(self) -> None:
        # Initialize symbol table and labels set
        self.symbol_table = SymbolTable()
        # Track all numeric labels found in the program to validate GOTO and DO targets
        self.labels: Set[int] = set()

    def analyze(self, program: Program) -> SymbolTable:
        # Reset symbol table and labels for a new analysis
        self.symbol_table = SymbolTable()
        self.labels = set()

        # Declare all variables from declarations
        self._declare_variables(program.declarations)
        # Collect all labels from statements
        self._collect_labels(program.statements)
        # Analyze all statements
        self._analyze_statements(program.statements)

        # Return the populated symbol table
        return self.symbol_table

    def _declare_variables(self, declarations: Iterable[Declaration]) -> None:
        # Iterate through each declaration
        for declaration in declarations:
            var_type = declaration.var_type.upper()
            for declared in declaration.names:
                # Parse the declared variable to get name, is_array, size
                name, is_array, size = self._parse_declared_variable(declared)
                # Declare the variable in the symbol table
                self.symbol_table.declare(
                    name,
                    var_type,
                    is_array=is_array,
                    size=size,
                )

    def _parse_declared_variable(
        self, declared: Any
    ) -> tuple[str, bool, Optional[int]]:
        # Handle string format for declarations
        if isinstance(declared, str):
            text = declared.strip().upper()
            match = re.fullmatch(r"([A-Z][A-Z0-9_]*)\((\d+)\)", text)
            if match:
                return match.group(1), True, int(match.group(2))
            return text, False, None

        # Handle tuple format
        if isinstance(declared, tuple) and len(declared) == 2:
            name, size = declared
            return str(name).upper(), True, int(size)

        # Handle dict format
        if isinstance(declared, dict):
            name = str(declared["name"]).upper()
            size = declared.get("size")
            return name, size is not None, int(size) if size is not None else None

        # Raise error for invalid format
        raise SemanticError(f"Invalid declaration format: {declared!r}")

    def _collect_labels(self, statements: Iterable[Any]) -> None:
        # Iterate through statements to collect labels
        for statement in statements:
            # Add label from Continue statements, which may act as loop terminators
            if isinstance(statement, Continue) and statement.label is not None:
                self._add_label(statement.label)

            # Handle labelled statements and nested statement wrappers
            # The parser may represent a labelled statement as an object with a label and inner statement
            labelled_statement = getattr(statement, "statement", None)
            label = getattr(statement, "label", None)
            if labelled_statement is not None and label is not None:
                self._add_label(label)
                self._collect_labels([labelled_statement])

            # Recursively collect labels from If bodies
            if isinstance(statement, If):
                self._collect_labels(statement.then_body)
                if statement.else_body:
                    self._collect_labels(statement.else_body)

            # Recursively collect labels from Do bodies
            if isinstance(statement, Do):
                self._collect_labels(statement.body)

    def _add_label(self, label: int) -> None:
        # Check for duplicate labels
        if label in self.labels:
            raise SemanticError(f"Label '{label}' declared more than once")
        # Add label to the set
        self.labels.add(label)

    def _analyze_statements(self, statements: Iterable[Any]) -> None:
        # Analyze each statement in the list
        for statement in statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, statement: Any) -> None:
        # Dispatch to appropriate analysis method based on statement type
        # This method acts as a central hub for statement analysis, routing each
        # statement to its specific validation logic

        # Handle labelled statements by analyzing the inner statement
        # This allows label wrappers to be transparent for semantic validation
        labelled_statement = getattr(statement, "statement", None)
        if labelled_statement is not None:
            self._analyze_statement(labelled_statement)
            return

        # Analyze different types of statements with appropriate validation
        if isinstance(statement, Assignment):
            self._analyze_assignment(statement)

        elif isinstance(statement, Print):
            # Print statements can contain various expression types
            for value in statement.values:
                self._expression_type(value)

        elif isinstance(statement, Read):
            # Read statements assign values to variables, so check assignability
            for variable in statement.variables:
                self._analyze_assignable(variable)

        elif isinstance(statement, If):
            self._analyze_if_statement(statement)

        elif isinstance(statement, Do):
            self._analyze_do(statement)

        elif isinstance(statement, GOTO):
            self._validate_goto_label(statement)

        elif isinstance(statement, Continue):
            # Continue statements are valid as long as their labels exist
            # (already checked during label collection)
            return

        elif isinstance(statement, Return):
            # Return statements don't require additional validation in this language
            return

        else:
            # If we encounter an unknown statement type, it's a language implementation error
            raise SemanticError(
                f"Unsupported statement node: {type(statement).__name__}"
            )

    def _analyze_if_statement(self, statement: If) -> None:
        """Analyze an IF statement ensuring the condition is logical and both branches are valid."""
        condition_type = self._expression_type(statement.condition)
        if condition_type != LOGICAL:
            raise SemanticError("IF condition must be LOGICAL")

        # Analyze the 'then' branch
        self._analyze_statements(statement.then_body)

        # Analyze the optional 'else' branch
        if statement.else_body:
            self._analyze_statements(statement.else_body)

    def _validate_goto_label(self, statement: GOTO) -> None:
        """Validate that a GOTO statement references an existing label."""
        if statement.label not in self.labels:
            raise SemanticError(f"GOTO references undefined label '{statement.label}'")

    def _analyze_assignment(self, statement: Assignment) -> None:
        # Get types of target and expression
        target_type = self._analyze_assignable(statement.target)
        expression_type = self._expression_type(statement.expr)

        # Check if assignment is valid
        if not self._can_assign(target_type, expression_type):
            raise SemanticError(
                f"Cannot assign expression of type {expression_type} "
                f"to target of type {target_type}"
            )

    def _analyze_assignable(self, target: Any) -> str:
        # Handle variable targets
        if isinstance(target, Variable):
            symbol = self.symbol_table.lookup(target.name)

            if symbol.is_array:
                raise SemanticError(f"Array '{symbol.name}' requires an index")

            return symbol.var_type

        # Handle array access targets
        if isinstance(target, ArrayAccess):
            symbol = self.symbol_table.lookup(target.name)

            if not symbol.is_array:
                raise SemanticError(f"Variable '{symbol.name}' is not an array")

            index_type = self._expression_type(target.index)

            if index_type != INTEGER:
                raise SemanticError(f"Array index for '{symbol.name}' must be INTEGER")

            return symbol.var_type

        # Raise error for invalid targets
        raise SemanticError(f"Invalid assignment target: {type(target).__name__}")

    def _analyze_do(self, statement: Do) -> None:
        # Get the loop variable name, tolerating parser output with the misspelled attribute name
        loop_variable_name = getattr(statement, "variable", None) or getattr(
            statement, "varibale", None
        )

        if loop_variable_name is None:
            raise SemanticError("DO loop has no control variable")

        # Lookup the loop variable symbol
        loop_symbol = self.symbol_table.lookup(loop_variable_name)

        if loop_symbol.var_type != INTEGER or loop_symbol.is_array:
            raise SemanticError("DO control variable must be an INTEGER scalar")

        # Check types of start and end expressions
        start_type = self._expression_type(statement.start)
        end_type = self._expression_type(statement.end)

        if start_type != INTEGER or end_type != INTEGER:
            raise SemanticError("DO start and end expressions must be INTEGER")

        # Check if body is not empty
        if not statement.body:
            raise SemanticError(f"DO {statement.label} has an empty body")

        # Check if last statement is the correct continue
        last_statement = statement.body[-1]

        if (
            not isinstance(last_statement, Continue)
            or last_statement.label != statement.label
        ):
            raise SemanticError(
                f"DO {statement.label} must finish with CONTINUE label {statement.label}"
            )

        # Analyze the body statements
        self._analyze_statements(statement.body)

    def _expression_type(self, expression: Any) -> str:
        """
        Determine the data type of an expression through recursive analysis.

        This method traverses the expression tree and returns the resulting type,
        performing type checking along the way. It's the core of the type system.
        """
        # Handle literal values - these have inherent types
        if isinstance(expression, Number):
            # Numbers are REAL if they contain decimals, INTEGER otherwise
            return REAL if isinstance(expression.value, float) else INTEGER

        if isinstance(expression, String):
            return STRING

        if isinstance(expression, Boolean):
            return LOGICAL

        # Handle variable references - look up in symbol table
        if isinstance(expression, Variable):
            symbol = self.symbol_table.lookup(expression.name)

            if symbol.is_array:
                raise SemanticError(f"Array '{symbol.name}' requires an index")

            return symbol.var_type

        # Handle array element access
        if isinstance(expression, ArrayAccess):
            symbol = self.symbol_table.lookup(expression.name)

            if not symbol.is_array:
                raise SemanticError(f"Variable '{symbol.name}' is not an array")

            # Array indices must be integers
            index_type = self._expression_type(expression.index)

            if index_type != INTEGER:
                raise SemanticError(f"Array index for '{symbol.name}' must be INTEGER")

            return symbol.var_type

        # Handle binary operations (arithmetic, relational, logical)
        if isinstance(expression, BinaryOp):
            return self._binary_expression_type(expression)

        # Handle function calls
        if isinstance(expression, FuntionalCall):
            return self._function_call_type(expression)

        # Handle unary operations (e.g., negation, logical NOT)
        if isinstance(expression, UnaryOp):
            return self._unary_expression_type(expression)

        # If we reach here, the expression type is not supported
        raise SemanticError(f"Unsupported expression node: {type(expression).__name__}")

    def _unary_expression_type(self, expression: UnaryOp) -> str:
        op = expression.op.upper()
        operand_type = self._expression_type(expression.operand)

        if op == "-":
            if operand_type not in NUMERIC_TYPES:
                raise SemanticError("Unary '-' operator requires a numeric operand")
            return operand_type  # Result type is the same as operand type

        if op in {".NOT.", "NOT"}:
            if operand_type != LOGICAL:
                raise SemanticError("Unary NOT operator requires a LOGICAL operand")
            return LOGICAL

        raise SemanticError(f"Unsupported unary operator '{expression.op}'")

    def _binary_expression_type(self, expression: BinaryOp) -> str:
        """
        Determine the result type of a binary operation based on operator and operand types.

        Different operators have different type requirements and produce different result types:
        - Arithmetic: numeric operands -> numeric result
        - Relational: comparable operands -> logical result
        - Logical: logical operands -> logical result
        """
        # Get operator and operand types
        op = expression.op.upper()
        left_type = self._expression_type(expression.left)
        right_type = self._expression_type(expression.right)

        # Arithmetic operators (+, -, *, /) require numeric operands
        if op in {"+", "-", "*", "/"}:
            self._require_numeric(left_type, right_type, op)
            # Result is REAL if either operand is REAL, otherwise INTEGER
            return REAL if REAL in {left_type, right_type} else INTEGER

        # MOD operator requires integer operands and produces integer result
        if op == "MOD":
            if left_type != INTEGER or right_type != INTEGER:
                raise SemanticError("MOD operands must be INTEGER")
            return INTEGER

        # Relational operators compare values and produce logical results
        if op in {
            ".EQ.",
            ".NE.",
            ".LT.",
            ".LE.",
            ".GT.",
            ".GE.",  # Fortran-style
            "EQ",
            "NE",
            "LT",
            "LE",
            "GT",
            "GE",  # Alternative style
        }:
            # Numeric types can be compared with all relational operators
            if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                return LOGICAL

            # Equality operators work on any matching types
            if op in {".EQ.", ".NE.", "EQ", "NE"} and left_type == right_type:
                return LOGICAL

            raise SemanticError(
                f"Invalid operands for relational operator '{expression.op}'"
            )

        # Logical operators require logical operands and produce logical results
        if op in {".AND.", ".OR.", "AND", "OR"}:
            if left_type != LOGICAL or right_type != LOGICAL:
                raise SemanticError(
                    f"Logical operator '{expression.op}' requires LOGICAL operands"
                )
            return LOGICAL

        # If we reach here, the operator is not supported
        raise SemanticError(f"Unsupported binary operator '{expression.op}'")

    def _function_call_type(self, expression: FuntionalCall) -> str:
        # Get function name and arguments
        name = expression.name.upper()
        arguments = expression.arguments

        # Handle MOD function call semantics
        if name == "MOD":
            if len(arguments) != 2:
                raise SemanticError("MOD requires exactly two arguments")

            first_type = self._expression_type(arguments[0])
            second_type = self._expression_type(arguments[1])

            if first_type != INTEGER or second_type != INTEGER:
                raise SemanticError("MOD arguments must be INTEGER")

            return INTEGER

        # Unsupported functions are rejected by the semantic analyzer
        # This is the extension point for future built-in function support
        raise SemanticError(f"Unsupported function call '{expression.name}'")

    def _require_numeric(self, left_type: str, right_type: str, operator: str) -> None:
        # Check if both operands are numeric
        if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
            raise SemanticError(f"Operator '{operator}' requires numeric operands")

    def _can_assign(self, target_type: str, expression_type: str) -> bool:
        """
        Determine if an expression of one type can be assigned to a variable of another type.

        Assignment rules:
        - Same types are always compatible
        - INTEGER can be assigned to REAL (widening conversion)
        - Other conversions are not allowed
        """
        if target_type == expression_type:
            return True

        # Allow assignment of INTEGER to REAL (automatic widening)
        if target_type == REAL and expression_type == INTEGER:
            return True

        return False
