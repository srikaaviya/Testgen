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
    class_name: str | None = None   # None if standalone function, class name if method


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, source_lines: list[str]):
        self.source_lines = source_lines
        self.functions = []
        self.current_class = None   # tracks which class we're currently inside

    def visit_ClassDef(self, node: ast.ClassDef):
        # entering a class — save the class name
        previous_class = self.current_class
        self.current_class = node.name

        # visit all children inside this class
        self.generic_visit(node)

        # exiting the class — restore previous context
        self.current_class = previous_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._process_function(node)
        self.generic_visit(node)  # visit nested functions if any

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._process_function(node)
        self.generic_visit(node)

    def _process_function(self, node):
        # skip private and dunder functions
        if node.name.startswith("_"):
            return

        args = [arg.arg for arg in node.args.args if arg.arg != "self"]

        start = node.lineno - 1
        end = node.end_lineno
        raw_source = "\n".join(self.source_lines[start:end])
        source = textwrap.dedent(raw_source)  # indentation removal

        self.functions.append(FunctionInfo(
            name=node.name,
            args=args,
            source=source,
            lineno=node.lineno,
            class_name=self.current_class,  # None if standalone, class name if method
        ))


def extract_functions(filepath: str) -> list[FunctionInfo]:
    path = Path(filepath)
    source_code = path.read_text(encoding="utf-8")
    tree = ast.parse(source_code)
    source_lines = source_code.splitlines()

    visitor = FunctionVisitor(source_lines)
    visitor.visit(tree)

    return visitor.functions

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

