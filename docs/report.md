

## Intermediate representation

After lexical and sytantic analysis, teh compiler constructs an intermediate representation of the program in the form of an abstract syntax tree(AST).

This representation allows separating the language recognition phase from the subquent compiler phases, namely semantic analysis and code generation for the virtual machine.

The 'ast_nodes.py' file defines the main nodes used in this representation. Among them are:

- 'Program' which represents the complete program.
- 'Declaration', which represents variable declarations.
- 'Assigment' that represents assigments.
- 'Print' and 'Read', which represent basic input/output operations.
- 'IF' which represents conditional structures.
- 'DO' that represents 'Do' loops with labels.
- 'GOTO' and 'Continue', which represent jumps and labels.
- 'BinaryOp' and 'UnaryOp', which represent arithmetic, relational and logical expressions.
- 'variable', 'Number', 'String' and 'Boolean', which represent basic values.
- 'ArrayAccess' and 'FunctionalCall' that are designed to support array access and function calls like 'MOD'.

This structure was defined in a modular way so that the parser only needs to construct AST objects, while subsequent phases work on this representation without directly depending on the original source code.