## Range of the Project

The compiler implements a subset of Fortran 77 focused on the constructs required by the assignment: declarations, arithmetic, relational and logical expressions, `IF`, labelled `DO`, `GOTO`, `READ` and `PRINT`.

The compiler also supports arrays and the intrinsic `MOD` function. User-defined `FUNCTION` and `SUBROUTINE` constructs are partially represented at parser level, but they are not fully supported by the backend.


## Intermediate representation

After lexical and sytantic analysis, the compiler constructs an intermediate representation of the program in the form of an abstract syntax tree(AST).

This representation allows separating the language recognition phase from the subquent compiler phases, namely semantic analysis and code generation for the virtual machine.

The `ast_nodes.py` file defines the main nodes used in this representation. Among them are:

-`File` which represents the complete compilation unit, containing a `Program`and a list of subprograms.
- `Program` which represents the main program block.
- `Declaration`, which represents variable declarations.
- `Assignment` that represents assignments statements.
- `Print` and `Read`, which represent basic input/output operations.
- `If` which represents conditional , with optional `ELSE` branch.
- `DO` that represents `Do` loops with labels.
- `GOTO` and `Continue`, which represent jumps and labels.
- `Return` which represents the `RETURN` statement inside subprograms.
- `BinaryOp` and `UnaryOp`, which represent arithmetic, relational and logical expressions, it is also used for unary operations.
- `Variable`, `Number`, `String` and `Boolean`, which represent basic values.
- `ArrayAccess` and `FunctionCall` that represent array indexing and function calls respectively.

This structure was defined in a modular way so that the parser only needs to construct AST objects, while subsequent phases work on this representation without directly depending on the original source code.

## Lexical Analysis

Lexical analysis was implemented using the `ply.lex` library.

The lexer is responsible for transforming the Fortran source code into a sequence of tokens.
Tokens were defined for a language keywords, identifiers, integers and real numbers, string, arithmetic operators, relational operators, logical operators and special symbols.

Recognized keywords include, among others, 'PROGRAM', 'END', 'INTEGER', 'REAL', 'LOGICAL', 'IF', 'THEN', 'ELSE', 'ENDIF', 'DO', 'CONTINUE', 'GOTO', 'READ' and 'PRINT'.

Identifiers are normalized to uppercase in order to maintain compability with the traditional Fortran style, where the language is not case-sensitive in usual usage.

The lexer also recognizes Fortran-style relational and logical operators, such as '.EQ.', '.NE.', '.LT.', '.LE.', '.GT.', '.GE.', '.AND.', '.OR.', '.NOT.', '.TRUE.' and '.FALSE.'.

Newline characters are returned as 'NEWLINE' tokens. This decision simplifies the parser, because the grammar can explicitly distinguish the end of one statement from the beginning of the next one.

At this stage, the compiler adopts a free-form approach to writing source code, simplifying lexical analysis compared to the fixed-column format of the original Fortran 77.

## Syntactic Analysis

Syntactic analysis was implemented using the `ply.yacc` library.

The parser receives the sequence of tokens produced by the lexer and checks whether the input follows grammar supported by the compiler. If the program is syntactically valid, the parser builds the corresponding Abstract Syntax Tree.

The current parser supports the following constructs:

- Program structure using `PROGRAM <identifier>` and `END`;
- Variable declarations using `INTEGER`, `REAL` and `LOGICAL`, including array declarations such as `INTEGER NUMS (5)`;
- Assignments statements;
- Arithmetic expressions using `+`, `-`, `*` and `/`;
- Relational expressions using `.EQ.`, `.NE.`, `.LT.`, `.LE.`, `.GT.` and `.GE.`;
- Logical expressions using `.AND.`, `.OR.` and `.NOT.`;
- `PRINT *, ...` statements;
- `READ *, ...` statements;
- Conditional blocks using `IF (...) THEN ... ELSE... ENDIF`;
- Labelled `DO` loops;
- `GOTO` statements;
- Labelled `CONTINUE`statements.
- `FUNCTION`and `SUBROUTINE` definitions defined by the user with parameters.

Operator precedence was defined in the parser to avoid ambiguous parsing of expressions. Logical operators have lower precedence than relational operators, and arithmetic multiplication and division have higher precedence than addition and substraction.

Newline tokens are part of the grammar. This allows the parser to identify the end of declarations and statements clearly. Optional newlines are also accepted after the final `END`, so source files ending with a trailing newline can be parsed correctly.

The parser creates specific AST nodes depending on the recognized construct. For example, declarations generate `Declaration` nodes, assignments generate `Assignment` nodes, print statements generate `Print` nodes, conditional blocks generate `If` nodes, and labelled loops generate `Do` nodes.

### Label Handling

Fortran 77 allows statements to be prefixed by with a numeric label, which is used as a target for `GOTO` and `DO` statements. The parser handles labels by including them in the grammar rules for `continue`and `do`statements.

### Array declarations and access

Array declarations are handled at the id_list level. Each element in a declaration can be either a plain identifier or an identifier with a size. This allows mixed declarations like `INTEGER I, NUMS(5)` to be parsed correctly.
Array access and fucntion calls share the same syntactic form, so depending on the number of arguments, the parser clasifies them as a `ArrayAccess` node (one argument) or a `FunctionCall` (two or more). 
The semantic analyzer is responsible for resolving ambiguous single-argument cases.

### Subprograms

The top level grammar rule is file, which consists of a main program followed by an optional list of subprograms. This allows source files to contain both a main program and one or more `FUNCTION` or `SUBROUTINE`definitions.
Each `FUNCTION` definition includes a return type, a name, a parameter list, local declarations and a body ending with `RETURN` and `END`. Each `SUBROUTINE` definition has the same structure but without the return type.
The `parse()` function returns a file node containing the main program and the list of subprograms, processing them separately.


## Semantic Analysis

The semantic analyzer receives the AST generated by the parser and validates that the program is meaningful before VM code generation.

The implemented semantic checks include:

- construction of a symbol table for declared variables;
- detection of duplicated declarations;
- detection of variables used before declaration;
- support for `INTEGER`, `REAL` and `LOGICAL` types;
- assignment compatibility checks;
- validation of arithmetic, relational and logical expressions;
- validation of array declarations and indexed accesses;
- validation of `GOTO` targets;
- validation that `DO` loops end with the expected `CONTINUE` label;
- validation of the intrinsic `MOD` function;
- rejection of unsupported user-defined function calls.

### Symbol table

The symbol table stores each declared variable with its type and array information. Scalar variables and arrays are distinguished so that the semantic analyzer can reject invalid usages such as using an array without an index or indexing a scalar variable.

For example, `INTEGER NUMS(5)` is stored as an `INTEGER` array with size 5, while `INTEGER I` is stored as an `INTEGER` scalar.

### Type checking

The semantic analyzer checks assignment compatibility. Assigning an `INTEGER` expression to a `REAL` variable is accepted, but assigning a `REAL` expression to an `INTEGER` variable is rejected because it would lose information.

Logical expressions are also validated. For example, `.AND.`, `.OR.` and `.NOT.` require `LOGICAL` operands, while arithmetic operators require numeric operands.

### Label validation

Labels are collected before statement validation. This allows the analyzer to check that `GOTO` statements reference existing labels.

For `DO` loops, the analyzer also verifies that the last statement in the loop body is a `CONTINUE` statement with the same label as the `DO`. For example, `DO 10 ...` must end with `10 CONTINUE`.

## VM Code Generation

The code generator translates the validated AST into stack-based VM instructions.

Variables are allocated in global memory slots. Scalar variables use `PUSHG` and `STOREG`, while array accesses use address calculation with `PUSHGP`, `PADD`, `CHECK`, `LOAD` and `STORE`.

The generator currently supports:

- integer, real, string and logical literals;
- scalar variable access;
- assignments;
- arithmetic operators: `+`, `-`, `*`, `/`;
- relational operators: `.EQ.`, `.NE.`, `.LT.`, `.LE.`, `.GT.`, `.GE.`;
- logical operators: `.AND.`, `.OR.`, `.NOT.`;
- the intrinsic `MOD` function;
- `PRINT` and `READ`;
- `IF / ELSE`;
- `GOTO`;
- labelled `CONTINUE`;
- labelled `DO` loops;
- basic array access.

### Variable allocation

Declared variables are assigned consecutive global memory slots. For scalar variables, one slot is reserved. For arrays, several consecutive slots are reserved according to the declared size.

For example:

```fortran
INTEGER NUMS(5)
INTEGER I, SOMA
```

reserves five positions for `NUMS`, one position for `I`, and one position for `SOMA`.

### Expression generation

Expressions are generated using stack-based evaluation. For example:

```fortran
FAT = FAT * I
```

is translated conceptually as:

```text
PUSHG <slot_FAT>
PUSHG <slot_I>
MUL
STOREG <slot_FAT>
```

Relational and logical expressions also leave their result on the stack, allowing them to be used directly by conditional jumps.

### Input and output

`PRINT` statements generate the expression code followed by the correct output instruction depending on the expression type:

- `WRITES` for strings;
- `WRITEI` for integers and logical values;
- `WRITEF` for real values.

`READ` statements currently support `INTEGER` and `REAL` targets. The input is read as text and converted using `ATOI` or `ATOF` before being stored.

## Control Flow Generation

Conditional statements are translated using internal VM labels. An `IF / ELSE` statement generates a conditional jump with `JZ`, an optional jump to the end of the structure, and internal labels such as `ELSE1` and `ENDIF2`.

Fortran labels are represented separately using the `F` prefix. For example:

```fortran
20 CONTINUE
```

becomes:

```text
F20:
```

and:

```fortran
GOTO 20
```

becomes:

```text
JUMP F20
```

`DO` loops are translated as labelled loops. The control variable is initialized with the start expression, the loop condition checks whether the variable is less than or equal to the end expression, and the variable is incremented by one at the end of each iteration.

For example:

```fortran
DO 10 I = 1, N
FAT = FAT * I
10 CONTINUE
```

is translated into a structure equivalent to:

```text
PUSHI 1
STOREG <slot_I>
DOSTART1:
PUSHG <slot_I>
PUSHG <slot_N>
INFEQ
JZ DOEND2
...
F10:
PUSHG <slot_I>
PUSHI 1
ADD
STOREG <slot_I>
JUMP DOSTART1
DOEND2:
```

## Runtime and Execution Pipeline

The `main.py` module connects the compiler pipeline:

```text
source file
→ parser
→ semantic analyzer
→ VM code generator
→ output .vm file
```

The compiler can be executed with:

```bash
python -m src.main examples/hello.f
```

or with an explicit output path:

```bash
python -m src.main examples/hello.f -o output/hello.vm
```

The runtime normalizes input files that do not end with a final newline before passing them to the parser. This avoids parser errors caused by source files ending immediately after `END`.

If no output path is provided, the compiler writes the generated VM code to the `output/` directory using the same base name as the input file.

## Backend and Functional Tests

In addition to the lexer and parser tests already described above, the backend is tested at several levels.

The semantic tests verify both valid and invalid AST programs. They cover:

- valid declarations, assignments and print statements;
- variables used before declaration;
- duplicate declarations;
- incompatible assignments;
- invalid `IF` conditions;
- valid relational conditions;
- valid and invalid `GOTO` labels;
- valid and invalid `DO` loop labels;
- array index validation;
- logical `.NOT.` validation;
- invalid `MOD` argument types;
- invalid logical operands;
- invalid scalar/array usage;
- invalid `DO` control variables and bounds.

The code generation tests verify VM output for individual constructs. They cover:

- empty programs;
- string output;
- integer assignments;
- arithmetic expressions;
- printing variables;
- `READ`;
- boolean assignments;
- relational expressions;
- logical expressions;
- `IF / ELSE`;
- `GOTO` and `CONTINUE`;
- `DO` loops;
- `MOD`;
- array access and array reads;
- `.NOT.` expressions;
- controlled failures for unsupported or invalid code generation cases.

The functional backend tests build larger AST programs equivalent to the provided Fortran examples. These tests validate the backend flow:

```text
manual AST
→ semantic analyzer
→ VM code generator
```

The functional backend tests cover:

- factorial;
- sum of an integer array;
- prime number checking;
- unsupported user-defined function calls such as `CONVRT`.

The examples tests verify that the example source files exist, are not empty, contain the expected program headers and include the required constructs from the assignment. The `hello.f`, `factorial.f`, `prime.f`and `sum_array.f` examples can be compiled through the pipeline.

At the current stage, the complete project test suite passes successfully with:

```text
83 passed
```

## Example Programs

The repository includes example Fortran files in the `examples/` directory:

- `hello.f`;
- `factorial.f`;
- `prime.f`;
- `sum_array.f`;
- `converter.f`.

The `hello.f` example is currently the main integration example compiled directly from a `.f` source file through the full compiler pipeline.

The larger examples are also represented in backend functional tests using manually constructed ASTs. This isolates the backend from parser limitations and demonstrates that semantic analysis and VM generation work correctly when the parser provides a valid AST.

## Current Limitations


The compiler includes parser-level support for user-defined `FUNCTION` and `SUBROUTINE` definitions. However, full end-to-end support for user-defined subprograms is not implemented yet. The intrinsic `MOD` function is supported because it is required by the provided examples.

The converter example is therefore included as an example of a program using user-defined functions, but the backend currently rejects calls such as `CONVRT(NUM, BASE)` in a controlled way.

Some larger examples are validated through manually constructed ASTs in the backend tests. This isolates the backend from parser limitations and demonstrates that semantic analysis and VM generation work correctly when the parser provides a valid AST.

## Tests

The project includes tests using `pytest`.

The lexer tests verify that the source code is correctly transformed into tokens. They cover:

- program headers;
- integer declarations;
- print statements with strings;
- arithmetic expressions;
- relational operators;
- logical operators;
- string values without quotes;
- boolean values.

The parser tests verify that valid Fortran-like programs are correctly transformed into AST structures. They cover:

- a minimal `HELLO` program;
- variable declarations and assignments;
- `IF` statements;
- labelled `Do` loops;
- `GOTO` statements.
- Array declarations, verifying that the array name and size are stored correctly in the `Declaration` node.
- Functions calls with multiple arguments, verifying that they are parsed as `FunctionCall`nodes.
- User-defined `FUNCTION` and `SUBROUTINE` definitions.
- Multiple subprograms in the same source file.

All parser tests verify both the structure of the AST and the specific values of the relevant fields, such as labels, variable names and node types.

At the current stage, all available tests pass successfully:

```text
83 passed
```

## Execution Instructions

To install the required dependencies:

```bash
pip install -r requirements.txt
```
