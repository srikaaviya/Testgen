import os
from groq import Groq
from dotenv import load_dotenv
from extractor import FunctionInfo

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(fn: FunctionInfo, module_name: str, file_type: str) -> str:
    base_rules = f"""- Use pytest only (no unittest)
- Use Python 3.12+ compatible syntax only
- Do NOT use backticks — use repr() instead
- Cover: normal case, edge cases, and any exceptions raised
- Each test function must be named test_<scenario>_{fn.name}
- Do NOT include any explanation or markdown — return only raw Python code
- Do NOT add any import statements
- Test functions must have NO parameters at all — hardcode all values inside the function body
- Do NOT use non-ASCII characters in test values"""

    db_rules = f"""
- For mocking, use monkeypatch with MagicMock like this exact pattern:
    mock_conn = MagicMock()
    monkeypatch.setattr('{module_name}.get_db_connection', lambda: mock_conn)
- monkeypatch.setattr string form takes exactly 2 args: ('module.attribute', value) — never 3 args
- Never use monkeypatch.setattr(...).return_value — monkeypatch returns None, not a mock"""

    rules = base_rules + (db_rules if file_type == "db" else "")

    return f"""You are an expert Python testing engineer.

Generate pytest unit tests for the following Python function.

Rules:
{rules}

Function:
{fn.source}
"""


def generate_test(fn: FunctionInfo, module_name: str, file_type: str) -> str:
    prompt = build_prompt(fn, module_name, file_type)

    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [{"role": "user", "content": prompt}],
        temperature = 0.2,
    )

    return response.choices[0].message.content.strip()


def get_source_imports(filepath: str) -> str:
    import ast
    from pathlib import Path

    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source)
    import_lines = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                import_lines.append(f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(
                (f"{a.name} as {a.asname}" if a.asname else a.name) for a in node.names
            )
            import_lines.append(f"from {module} import {names}")

    return "\n".join(import_lines)


def generate_all_tests(functions: list[FunctionInfo], filepath: str, file_type: str = "pure") -> str:
    from pathlib import Path
    module_name = Path(filepath).stem
    function_names = ", ".join(fn.name for fn in functions)
    source_imports = get_source_imports(filepath)

    mock_import = "from unittest.mock import MagicMock\n" if file_type == "db" else ""
    header = f"import pytest\n{mock_import}{source_imports}\nfrom {module_name} import {function_names}\n\n"

    test_blocks = []
    for fn in functions:
        test_blocks.append(generate_test(fn, module_name, file_type))
    return header + "\n\n".join(test_blocks)


if __name__ == "__main__":
    from extractor import extract_functions     #only needed for manual test

    fns = extract_functions("samples/sample.py")
    result = generate_all_tests(fns, "samples/sample.py")
    print(result)
