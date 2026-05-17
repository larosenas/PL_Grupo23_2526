from src.ast_nodes import (
    Assignment,
    BinaryOp,
    Declaration,
    Number,
    Print,
    Read,
    String,
    Variable,
    Boolean,
    If,
    GOTO,
    Continue,
    Do,
    FunctionCall,
    ArrayAccess,
    UnaryOp,
)
from src.errors import CodeGenerationError


class CodeGenerator:
    """
    Generates VM bytecode from an AST for a Fortran-like language.
    Manages symbol allocation, type checking, and instruction emission.
    """

    def __init__(self):
        # Map variable names to their global memory slot indices.
        self.symbols = {}

        # Track declared variable types for printing and type-based code selection.
        self.types = {}

        self.array_sizes = {}

        # Next available index for global variable allocation.
        self.next_global_index = 0

        self.label_counter = 0

    def generate(self, program):
        """
        Generate VM code for the given program AST.
        Returns a string of newline-separated instructions.
        """
        # Reset generator state between compilations.
        self.symbols = {}

        # Reset declared type bookkeeping as well.
        self.types = {}

        self.array_sizes = {}

        self.next_global_index = 0

        self.label_counter = 0

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

        if isinstance(statement, Read):
            return self._read(statement)

        if isinstance(statement, If):
            return self._if(statement)

        if isinstance(statement, GOTO):
            return self._goto(statement)

        if isinstance(statement, Continue):
            return self._continue(statement)
        if isinstance(statement, Do):
            return self._do(statement)

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
        for declaration in declarations:
            var_type = declaration.var_type.upper()

            for name in declaration.names:
                key, size = self._parse_declared_variable(name)

                if key in self.symbols:
                    raise CodeGenerationError(f"Variable '{key}' already allocated")

                self.symbols[key] = self.next_global_index
                self.types[key] = var_type
                self.array_sizes[key] = size
                self.next_global_index += size

    def _assignment(self, statement):
        if isinstance(statement.target, Variable):
            variable_index = self._lookup(statement.target.name)

            code = []
            code.extend(self._expression(statement.expr))
            code.append(f"STOREG {variable_index}")

            return code

        if isinstance(statement.target, ArrayAccess):
            code = []
            code.extend(self._array_address(statement.target))
            code.extend(self._expression(statement.expr))
            code.append("STORE 0")
            return code

        raise CodeGenerationError(
            f"Unsupported assignment target: {type(statement.target).__name__}"
        )

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

        if isinstance(expression, Boolean):
            return [f"PUSHI {1 if expression.value else 0}"]

        if isinstance(expression, FunctionCall):
            return self._function_call(expression)

        if isinstance(expression, ArrayAccess):
            code = []
            code.extend(self._array_address(expression))
            code.append("LOAD 0")
            return code
        if isinstance(expression, UnaryOp):
            return self._unary_expression(expression)

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

        if isinstance(expression, Boolean):
            return "LOGICAL"

        if isinstance(expression, Variable):
            key = expression.name.upper()

            if key not in self.types:
                raise CodeGenerationError(f"Variable '{key}' has no declared type")

            return self.types[key]

        if isinstance(expression, BinaryOp):
            op = expression.op.upper()

            if op in {".NOT.", "NOT"} and expression.right is None:
                return "LOGICAL"

            if op in {
                ".EQ.",
                ".NE.",
                ".LT.",
                ".LE.",
                ".GT.",
                ".GE.",
                "EQ",
                "NE",
                "LT",
                "LE",
                "GT",
                "GE",
                ".AND.",
                ".OR.",
                "AND",
                "OR",
            }:
                return "LOGICAL"

            left_type = self._expression_type(expression.left)
            right_type = self._expression_type(expression.right)

            if left_type == "REAL" or right_type == "REAL":
                return "REAL"

            return "INTEGER"

        if isinstance(expression, FunctionCall):
            if expression.name.upper() == "MOD":
                return "INTEGER"

            raise CodeGenerationError(f"Unsupported function call '{expression.name}'")

        if isinstance(expression, ArrayAccess):
            key = expression.name.upper()

            if key not in self.types:
                raise CodeGenerationError(f"Array '{key}' has no declared type")

            return self.types[key]
        if isinstance(expression, UnaryOp):
            op = expression.op.upper()

            if op in {".NOT.", "NOT"}:
                return "LOGICAL"

            raise CodeGenerationError(f"Unsupported unary operator '{expression.op}'")

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
        # Generate code for binary operations, mapping operators to VM instructions.
        code = []

        # Evaluate the left operand first, as the operator will consume both from the stack.
        code.extend(self._expression(expression.left))

        # Handle unary NOT as a special case since it only has one operand on the left.
        op = expression.op.upper()

        if op in {".NOT.", "NOT"} and expression.right is None:
            code = []
            code.extend(self._expression(expression.left))
            code.append("NOT")
            return code

        # Evaluate the right operand after the left, as the operator will consume both from the stack.
        code.extend(self._expression(expression.right))

        # Map of operators to VM opcodes
        operation_map = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            ".EQ.": "EQUAL",
            "EQ": "EQUAL",
            ".LT.": "INF",
            "LT": "INF",
            ".LE.": "INFEQ",
            "LE": "INFEQ",
            ".GT.": "SUP",
            "GT": "SUP",
            ".GE.": "SUPEQ",
            "GE": "SUPEQ",
            ".AND.": "AND",
            "AND": "AND",
            ".OR.": "OR",
            "OR": "OR",
        }

        op = expression.op.upper()

        if op in ("NE", ".NE."):
            return code + ["EQUAL", "NOT"]

        if op not in operation_map:
            raise CodeGenerationError(f"Unsupported binary operator '{expression.op}'")

        code.append(operation_map[op])
        return code

    def _read(self, statement):
        code = []

        for target in statement.variables:
            if isinstance(target, Variable):
                variable_name = target.name.upper()
                variable_index = self._lookup(variable_name)

                if variable_name not in self.types:
                    raise CodeGenerationError(
                        f"Variable '{variable_name}' has no declared type"
                    )

                variable_type = self.types[variable_name]

                if variable_type == "INTEGER":
                    conversion = "ATOI"
                elif variable_type == "REAL":
                    conversion = "ATOF"
                else:
                    raise CodeGenerationError(
                        f"READ only supports INTEGER and REAL variables, got {variable_type}"
                    )

                code.append("READ")
                code.append(conversion)
                code.append(f"STOREG {variable_index}")

            elif isinstance(target, ArrayAccess):
                array_name = target.name.upper()

                if array_name not in self.types:
                    raise CodeGenerationError(
                        f"Array '{array_name}' has no declared type"
                    )

                variable_type = self.types[array_name]

                if variable_type == "INTEGER":
                    conversion = "ATOI"
                elif variable_type == "REAL":
                    conversion = "ATOF"
                else:
                    raise CodeGenerationError(
                        f"READ only supports INTEGER and REAL arrays, got {variable_type}"
                    )

                code.extend(self._array_address(target))
                code.append("READ")
                code.append(conversion)
                code.append("STORE 0")

            else:
                raise CodeGenerationError(
                    f"Unsupported READ target: {type(target).__name__}"
                )

        return code

    def _new_label(self, prefix):
        # Generate a unique label with the given prefix
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def _if(self, statement):
        else_label = self._new_label("ELSE")
        end_label = self._new_label("ENDIF")

        code = []

        # Evaluate the condition and jump to else if false
        code.extend(self._expression(statement.condition))
        code.append(f"JZ {else_label}")

        # Execute then body
        for inner_statement in statement.then_body:
            code.extend(self._statement(inner_statement))

        if statement.else_body:
            # Jump over else body after then
            code.append(f"JUMP {end_label}")
            code.append(f"{else_label}:")

            # Execute else body
            for inner_statement in statement.else_body:
                code.extend(self._statement(inner_statement))

            code.append(f"{end_label}:")
        else:
            code.append(f"{else_label}:")

        return code

    def _goto(self, statement):
        return [f"JUMP F{statement.label}"]

    def _continue(self, statement):
        if statement.label is None:
            return []

        return [f"F{statement.label}:"]

    def _do(self, statement):
        # Generate code for a DO loop: initialize variable, check bounds, execute body, increment, and repeat.
        variable_name = statement.variable
        variable_index = self._lookup(variable_name)

        start_label = self._new_label("DOSTART")
        end_label = self._new_label("DOEND")
        continue_label = f"F{statement.label}"

        code = []

        # Initialize loop variable: I = start
        code.extend(self._expression(statement.start))
        code.append(f"STOREG {variable_index}")

        # Start of the loop
        code.append(f"{start_label}:")

        # Check condition: I <= end
        code.append(f"PUSHG {variable_index}")
        code.extend(self._expression(statement.end))
        code.append("INFEQ")
        code.append(f"JZ {end_label}")

        # Body of the DO loop, removing the final CONTINUE if it matches the DO label
        body = list(statement.body)

        if (
            body
            and isinstance(body[-1], Continue)
            and body[-1].label == statement.label
        ):
            body = body[:-1]

        for inner_statement in body:
            code.extend(self._statement(inner_statement))

        # Fortran label at the end of the DO
        code.append(f"{continue_label}:")

        # I = I + 1
        code.append(f"PUSHG {variable_index}")
        code.append("PUSHI 1")
        code.append("ADD")
        code.append(f"STOREG {variable_index}")

        # Return to the start
        code.append(f"JUMP {start_label}")

        # Exit the loop
        code.append(f"{end_label}:")

        return code

    def _function_call(self, expression):
        name = expression.name.upper()

        if name == "MOD":
            if len(expression.arguments) != 2:
                raise CodeGenerationError("MOD requires exactly two arguments")

            code = []
            code.extend(self._expression(expression.arguments[0]))
            code.extend(self._expression(expression.arguments[1]))
            code.append("MOD")
            return code

        raise CodeGenerationError(f"Unsupported function call '{expression.name}'")

    def _parse_declared_variable(self, name):
        # Parse variable name and size from declaration, handling arrays like "ARRAY(5)".
        text = name.upper()

        if "(" in text and text.endswith(")"):
            array_name = text[: text.index("(")]
            size_text = text[text.index("(") + 1 : -1]
            return array_name, int(size_text)

        return text, 1

    def _array_address(self, expression):
        # Calculate the memory address for a 1-based Fortran array access with bounds checking.
        array_name = expression.name.upper()

        if array_name not in self.symbols:
            raise CodeGenerationError(f"Array '{array_name}' has no global address")

        if self.array_sizes.get(array_name, 1) == 1:
            raise CodeGenerationError(f"Variable '{array_name}' is not an array")

        base_index = self.symbols[array_name]
        size = self.array_sizes[array_name]

        code = []

        code.append("PUSHGP")

        if base_index != 0:
            code.append(f"PUSHI {base_index}")
            code.append("PADD")

        code.extend(self._expression(expression.index))

        # Fortran arrays are 1-based: NUMS(1) is the first position.
        code.append("PUSHI 1")
        code.append("SUB")

        # Bounds check: valid internal indexes are 0..size-1.
        code.append(f"CHECK 0, {size - 1}")

        code.append("PADD")

        return code

    def _unary_expression(self, expression):
        op = expression.op.upper()

        if op in {".NOT.", "NOT"}:
            code = []
            code.extend(self._expression(expression.operand))
            code.append("NOT")
            return code

        raise CodeGenerationError(f"Unsupported unary operator '{expression.op}'")
