# Fortran 77 Compiler

Compiler for a subset of Fortran 77 developed for the Processamento de Linguagens 2026 project.

The compiler is implemented in Python using PLY.

## Suported features

## Installation


## Documentation
Program(name, declarations, statements)
Declaration(var_type, names)          # names: ["X", "A(10)"]
Assignment(target, expr)              # target: Variable | ArrayAccess
If(condition, then_body, else_body)   # else_body puede ser None
Do(label, variable, start, end, body)
GOTO(label)
Continue(label)
Return()
BinaryOp(op, left, right)            # right=None si es NOT o UMINUS
Number(value)                         # int o float
Variable(name)
ArrayAccess(name, index)
FunctionCall(name, arguments)
String(value)
Boolean(value)
