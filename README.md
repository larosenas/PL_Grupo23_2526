# Fortran 77 Compiler

Compiler for a subset of Fortran 77 developed for the Processamento de Linguagens 2026 project.

The compiler is implemented in Python using PLY.

## Suported features

## Installation

This project requires Python and the dependencies listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Running the test suite

To run the full test suite:

```bash
python -m pytest -q
```

Current expected result:

```text
79 passed
```

## Compiling a Fortran source file

The compiler entry point is `src.main`.

To compile the default hello example:

```bash
python -m src.main examples/hello.f
```

This generates:

```text
output/hello.vm
```

To choose an explicit output path:

```bash
python -m src.main examples/hello.f -o output/hello.vm
```

Expected VM output for `examples/hello.f`:

```text
PUSHS "Hello, World!"
WRITES
WRITELN
STOP
```

## Supported subset

The current compiler implementation supports the following Fortran-like constructs:

- `PROGRAM ... END`
- `INTEGER`, `REAL` and `LOGICAL` declarations
- scalar assignments
- arithmetic expressions with `+`, `-`, `*` and `/`
- relational expressions with `.EQ.`, `.NE.`, `.LT.`, `.LE.`, `.GT.` and `.GE.`
- logical expressions with `.AND.`, `.OR.` and `.NOT.`
- boolean literals `.TRUE.` and `.FALSE.`
- `PRINT *, ...`
- `READ *, ...`
- `IF (...) THEN ... ELSE ... ENDIF`
- labelled `DO` loops
- `GOTO`
- labelled `CONTINUE`
- basic arrays such as `INTEGER NUMS(5)`
- intrinsic `MOD(...)`

## Example programs

The repository includes the following example programs:

```text
examples/hello.f
examples/factorial.f
examples/prime.f
examples/sum_array.f
examples/converter.f
```

`hello.f` is currently used as the full integration example compiled directly from a real `.f` source file.

The larger examples are covered by functional backend tests using manually built ASTs. This validates semantic analysis and VM code generation independently from parser limitations.

## Current limitations

User-defined `FUNCTION` and `SUBROUTINE` definitions are not currently implemented.

The intrinsic function `MOD` is supported because it is required by the assignment examples, but user-defined calls such as `CONVRT(NUM, BASE)` are rejected in a controlled way by the backend.

Some larger examples may not compile directly from `.f` yet if the parser does not produce the required AST structure. The backend is tested separately with manually constructed ASTs for those cases.

## Documentation

Program(name, declarations, statements)
Declaration(var_type, names) # names: ["X", "A(10)"]
Assignment(target, expr) # target: Variable | ArrayAccess
If(condition, then_body, else_body) # else_body puede ser None
Do(label, variable, start, end, body)
GOTO(label)
Continue(label)
Return()
BinaryOp(op, left, right) # right=None si es NOT o UMINUS
Number(value) # int o float
Variable(name)
ArrayAccess(name, index)
FunctionCall(name, arguments)
String(value)
Boolean(value)
