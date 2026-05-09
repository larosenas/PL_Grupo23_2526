import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.codegen import CodeGenerator
from src.errors import CompilerError
from src.parser import parse
from src.semantic import SemanticAnalyzer


def compile_file(input_path, output_path=None):
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    source_code = input_path.read_text(encoding="utf-8")

    if not source_code.endswith("\n"):
        source_code += "\n"

    ast = parse(source_code)

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    generator = CodeGenerator()
    vm_code = generator.generate(ast)

    if output_path is None:
        output_dir = ROOT_DIR / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{input_path.stem}.vm"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(vm_code, encoding="utf-8")

    return output_path


def main(argv=None):
    argument_parser = argparse.ArgumentParser(
        description="Compile a Fortran 77 subset program into VM code."
    )

    argument_parser.add_argument(
        "input",
        help="Path to the input .f file",
    )

    argument_parser.add_argument(
        "-o",
        "--output",
        help="Path to the output .vm file",
    )

    args = argument_parser.parse_args(argv)

    try:
        output_path = compile_file(args.input, args.output)
    except (SyntaxError, CompilerError, FileNotFoundError) as error:
        print(f"Compilation failed: {error}", file=sys.stderr)
        return 1

    print(f"VM code generated in: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
