import ast
import inspect
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FunctionInfo:
    name: str
    args: list[str]
    source: str
    lineno: int


def extract_functions(filepath: str) -> list[FunctionInfo]:
    path = Path(filepath)
    source_code = path.read_text(encoding="utf-8")
    tree = ast.parse(source_code)
    source_lines = source_code.splitlines()

    functions = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue

        args = [arg.arg for arg in node.args.args if arg.arg != "self"]

        start = node.lineno - 1
        end = node.end_lineno
        raw_source = "\n".join(source_lines[start:end])
        source = textwrap.dedent(raw_source) #intendation removal

        functions.append(FunctionInfo(
            name=node.name,
            args=args,
            source=source,
            lineno=node.lineno,
        ))

    return functions

# Why @dataclass instead of a plain dict?
# gives better readability and easy access like fn.name instead of fn["name"].

if __name__ == "__main__": #written to manually test this file.
    fns = extract_functions("samples/sample.py")
    for f in fns:
        print(f"Name: {f.name}")
        print(f"Args: {f.args}")
        print(f"Line: {f.lineno}")
        print(f"Source:\n{f.source}")
        print("-" * 40)

