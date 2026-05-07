from src.ast_nodes import (
    Assignment,
    BinaryOp,
    Declaration,
    Number,
    Print,
    String,
    Variable,
)
from src.errors import CodeGenerationError


class CodeGenerator:
    def __init__(self):
        # Map variable names to their global memory slot indices.
        self.symbols = {}

        # Track declared variable types for printing and type-based code selection.
        self.types = {}

        # Next available index for global variable allocation.
        self.next_global_index = 0

    def generate(self, program):
        # Reset generator state between compilations.
        self.symbols = {}

        # Reset declared type bookkeeping as well.
        self.types = {}

        self.next_global_index = 0

        code = []

        # Reserve global variables in memory before emitting executable code.
        self._allocate_declarations(program.declarations)

        for _ in range(self.next_global_index):
            code.append("PUSHI 0")

        # Generate code for each top-level statement in program order.
        for statement in program.statements:
            code.extend(self._statement(statement))

        code.append("STOP")
        return "\n".join(code) + "\n"

    def _statement(self, statement):
        # Dispatch generation based on statement node type.
        if isinstance(statement, Print):
            return self._print(statement)

        if isinstance(statement, Assignment):
            return self._assignment(statement)

        raise CodeGenerationError(f"Unsupported statement: {type(statement).__name__}")

    def _print(self, statement):
        code = []

        # Emit code for each print argument, then append the correct write opcode.
        for value in statement.values:
            code.extend(self._expression(value))
            code.append(self._write_instruction(value))

        # Always terminate print output with a newline instruction.
        code.append("WRITELN")
        return code

    def _allocate_declarations(self, declarations):
        # Allocate memory slots for each declared variable and remember its type.
        for declaration in declarations:
            var_type = declaration.var_type.upper()

            for name in declaration.names:
                key = name.upper()

                if key in self.symbols:
                    raise CodeGenerationError(f"Variable '{key}' already allocated")

                self.symbols[key] = self.next_global_index
                self.types[key] = var_type
                self.next_global_index += 1

    def _assignment(self, statement):
        # Only scalar variable assignments are supported by this backend.
        if not isinstance(statement.target, Variable):
            raise CodeGenerationError(
                f"Unsupported assignment target: {type(statement.target).__name__}"
            )

        variable_index = self._lookup(statement.target.name)

        code = []
        code.extend(self._expression(statement.expr))
        code.append(f"STOREG {variable_index}")

        return code

    def _expression(self, expression):
        # Emit a literal value push for numeric and string constants.
        if isinstance(expression, Number):
            if isinstance(expression.value, float):
                return [f"PUSHF {expression.value}"]
            return [f"PUSHI {expression.value}"]

        if isinstance(expression, String):
            return [f'PUSHS "{expression.value}"']

        if isinstance(expression, Variable):
            variable_index = self._lookup(expression.name)
            return [f"PUSHG {variable_index}"]

        if isinstance(expression, BinaryOp):
            return self._binary_expression(expression)

        raise CodeGenerationError(
            f"Unsupported expression: {type(expression).__name__}"
        )

    def _expression_type(self, expression):
        # Determine the type of an expression for print formatting and type checks.
        if isinstance(expression, String):
            return "STRING"

        if isinstance(expression, Number):
            if isinstance(expression.value, float):
                return "REAL"
            return "INTEGER"

        if isinstance(expression, Variable):
            key = expression.name.upper()

            if key not in self.types:
                raise CodeGenerationError(f"Variable '{key}' has no declared type")

            return self.types[key]

        if isinstance(expression, BinaryOp):
            left_type = self._expression_type(expression.left)
            right_type = self._expression_type(expression.right)

            # Binary arithmetic promotes to REAL when either operand is REAL.
            if left_type == "REAL" or right_type == "REAL":
                return "REAL"

            return "INTEGER"

        raise CodeGenerationError(
            f"Cannot determine expression type: {type(expression).__name__}"
        )

    def _write_instruction(self, expression):
        # Choose the correct write opcode based on expression type.
        expression_type = self._expression_type(expression)

        if expression_type == "STRING":
            return "WRITES"

        if expression_type == "REAL":
            return "WRITEF"

        return "WRITEI"

    def _lookup(self, name):
        key = name.upper()

        if key not in self.symbols:
            raise CodeGenerationError(f"Variable '{key}' has no global address")

        return self.symbols[key]

    def _binary_expression(self, expression):
        code = []

        # Evaluate left and right operands before emitting the operator.
        code.extend(self._expression(expression.left))
        code.extend(self._expression(expression.right))

        operation_map = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
        }

        op = expression.op.upper()

        if op not in operation_map:
            raise CodeGenerationError(f"Unsupported binary operator '{expression.op}'")

        code.append(operation_map[op])
        return code
