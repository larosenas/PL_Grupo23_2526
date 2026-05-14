

## Intermediate representation

After lexical and sytantic analysis, teh compiler constructs an intermediate representation of the program in the form of an abstract syntax tree(AST).

This representation allows separating the language recognition phase from the subquent compiler phases, namely semantic analysis and code generation for the virtual machine.

The 'ast_nodes.py' file defines the main nodes used in this representation. Among them are:

- 'Program' which represents the complete program.
- 'Declaration', which represents variable declarations.
- 'Assignment' that represents assignments statements.
- 'Print' and 'Read', which represent basic input/output operations.
- 'If' which represents conditional structures.
- 'DO' that represents 'Do' loops with labels.
- 'GOTO' and 'Continue', which represent jumps and labels.
- 'BinaryOp' and 'UnaryOp', which represent arithmetic, relational and logical expressions.
- 'Variable', 'Number', 'String' and 'Boolean', which represent basic values.
- 'ArrayAccess' and 'FunctionCall' that are designed to support array access and function calls like 'MOD'.

This structure was defined in a modular way so that the parser only needs to construct AST objects, while subsequent phases work on this representation without directly depending on the original source code.


## Lexical Analysis

Lexical analysis was implemented using the 'ply.lex' library.

The lexer is responsible for transforming the Fortran source code into a sequence of tokens.
Tokens were defined for a language keywords, identifiers, integers and real numbers, string, arithmetic operators, relational operators, logical operators and special symbols.

Recognized keywords include, among others, 'PROGRAM', 'END', 'INTEGER', 'REAL', 'LOGICAL', 'IF', 'THEN', 'ELSE', 'ENDIF', 'DO', 'CONTINUE', 'GOTO', 'READ' and 'PRINT'.

Identifiers are normalized to uppercase in order to maintain compability with the traditional Fortran style, where the language is not case-sensitive in usual usage.

The lexer also recognizes Fortran-style relational and logical operators, such as '.EQ.', '.NE.', '.LT.', '.LE.', '.GT.', '.GE.', '.AND.', '.OR.', '.NOT.', '.TRUE.' and '.FALSE.'.

Newline characters are returned as 'NEWLINE' tokens. This decision simplifies the parser, because the grammar can explicitly distinguish the end of one statement from the beginning of the next one.

At this stage, the compiler adopts a free-form approach to writing source code, simplifying lexical analysis compared to the fixed-column format of the original Fortran 77.


## Syntactic Analysis

Syntactic analysis was implemented using the `ply.yacc`library.

The parser receives the sequence of tokens produced by the lexer and checks whether the input follows grammar supported by the compiler. If the program is syntactically valid, the parser builds the corresponding Abstract Syntax Tree.

The current parser supports the following constructs:

- Program structure using `PROGRAM <identifier>` and `END`;
- Variable declarations using `INTEGER`, `REAL` and `LOGICAL`;
- Assignments statements;
- Arithmetic expressions using  `+`, `-`, `*` and `/`;
- Relational expressions using `.EQ.`, `.NE.`, `.LT.`, `.LE.`, `.GT.` and `.GE.`;
- Logical expressions using `.AND.`, `.OR.` and `.NOT.`;
- `PRINT *, ...` statements;
- `READ *, ...` statements;
- Conditional blocks using `IF (...) THEN ... ELSE... ENDIF`;
- Labelled `DO` loops;
- `GOTO` statements;
- Labelled `CONTINUE`statements.

Operator precedence was defined in the parser to avoid ambiguous parsing of expressions. Logical operators have lower precedence than relational operators, and arithmetic multiplication and division have higher precedence than addition and substraction.

Newline tokens are part of the grammar. This allows the parser to identify the end of declarations and statements clearly. Optional newlines are also accepted after the final `END`, so source files ending with a trailing newline can be parsed correctly.

The parser creates specific AST nodes depending on the recognized construct. For example, declarations generate `Declaration` nodes, assignments generate `Assignment` nodes, print statements generate `Print` nodes, conditional blocks generate `If` nodes, and labelled loops generate `Do` nodes.


## Tests

The project includes tests using 'pytest'.


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

- a minimal 'HELLO' program;
- variable declarations and assignments;
- 'IF' statements;
- labelled 'Do' loops;
- 'GOTO' statements.

At the current stage, all available tests pass successfully:

```text
24 passed
```





## Execution Instructions --ESTO IGUAL EN EL README

To install the required dependencies:

```bash
pip install -r requirements.txt
```




