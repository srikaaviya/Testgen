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
    class_name: str | None = None       # None if standalone function, class name if method
    external_calls: list[str] = None    # list of external calls detected in function body

    def __post_init__(self):
        if self.external_calls is None:
            self.external_calls = []


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

    def _detect_external_calls(self, node) -> list[str]:
        calls = []
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            # detect calls like requests.get, psycopg2.connect, boto3.client
            if isinstance(child.func, ast.Attribute):
                try:
                    caller = child.func.value.id
                    method = child.func.attr
                    calls.append(f"{caller}.{method}")
                except AttributeError:
                    pass
            # detect simple calls like get_db_connection()
            elif isinstance(child.func, ast.Name):
                calls.append(child.func.id)
        # remove duplicates while preserving order
        seen = set()
        unique_calls = []
        for call in calls:
            if call not in seen:
                seen.add(call)
                unique_calls.append(call)
        return unique_calls

    def _process_function(self, node):
        # skip private and dunder functions
        if node.name.startswith("_"):
            return

        args = [arg.arg for arg in node.args.args if arg.arg != "self"]

        start = node.lineno - 1
        end = node.end_lineno
        raw_source = "\n".join(self.source_lines[start:end])
        source = textwrap.dedent(raw_source)  # indentation removal

        external_calls = self._detect_external_calls(node)

        self.functions.append(FunctionInfo(
            name=node.name,
            args=args,
            source=source,
            lineno=node.lineno,
            class_name=self.current_class,
            external_calls=external_calls,
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
    fns = extract_functions("samples/database.py")
    for f in fns:
        print(f"Name         : {f.name}")
        print(f"Args         : {f.args}")
        print(f"Class        : {f.class_name}")
        print(f"External calls: {f.external_calls}")
        print(f"Line         : {f.lineno}")
        print("-" * 40)

