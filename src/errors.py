# Custom exception classes for the compiler.
# This module defines specific error types for different compilation phases,
# allowing for precise error handling and reporting.


class CompilerError(Exception):
    """Base class for compiler-specific errors."""


class SemanticError(CompilerError):
    """Raised when the AST is syntactically valid but semantically incorrect."""


class CodeGenerationError(CompilerError):
    """Raised when VM code cannot be generated from a valid AST."""
