import os
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv
from pytestgen_ai.extractor import FunctionInfo

load_dotenv()

# AsyncGroq — async version of Groq client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(fn: FunctionInfo, module_name: str, file_type: str, class_inits: dict = None) -> str:
    base_rules = f"""- Use pytest only (no unittest)
- Use Python 3.12+ compatible syntax only
- Do NOT use backticks — use repr() instead
- Cover: normal case, edge cases, and any exceptions raised
- Each test function must be named test_<scenario>_{fn.name}
- Do NOT include any explanation or markdown — return only raw Python code
- Do NOT add any import statements
- Test functions must have NO parameters except pytest fixtures — if you use monkeypatch, declare it as a parameter: def test_something(monkeypatch):
- Every test function definition MUST have parentheses: def test_something():
- Do NOT define any classes inside the test file — use classes imported from the module directly
- Do NOT use non-ASCII characters in test values
- Before writing each assertion, trace through the function line by line with the test input to find the exact return value
- Only generate an exception test if the function explicitly raises an exception in its code
- Never assume a function raises TypeError or ValueError unless the function body contains raise TypeError or raise ValueError
- Never use repr() to compare objects — check attributes directly (e.g. assert node.data == 1, not assert repr(node) == repr(...))
- If you use unittest.mock.call in assertions, you must import it explicitly: from unittest.mock import MagicMock, call"""

    db_rules = f"""
- For mocking, use monkeypatch with MagicMock like this exact pattern:
    mock_obj = MagicMock()
    monkeypatch.setattr('{module_name}.function_name', lambda: mock_obj)
- monkeypatch.setattr string form takes exactly 2 args: ('module.attribute', value) — never 3 args
- To mock something defined in the source module use '{module_name}.attribute' (e.g. '{module_name}.SinglyLinkedListNode')
- To mock a Python builtin like print or open use 'builtins.print' or 'builtins.open' — never '{module_name}.print'
- Never mock builtins like range, len, isinstance — these are not patchable and should never appear in monkeypatch.setattr
- Never use monkeypatch.setattr(...).return_value — monkeypatch returns None, not a mock"""

    rules = base_rules + (db_rules if fn.external_calls else "")

    class_context = (
        f"This function is a method of the class `{fn.class_name}`. "
        f"Instantiate `{fn.class_name}()` before calling the method."
        if fn.class_name else
        "This is a standalone function — call it directly without instantiating any class."
    )

    # tell Groq exactly what external calls were detected so it knows what to mock
    if fn.external_calls:
        calls_list = ", ".join(fn.external_calls)
        mock_context = (
            f"This function makes the following external calls: {calls_list}. "
            f"Use monkeypatch to mock these in tests where needed."
        )
    else:
        mock_context = "This function has no external calls — no mocking needed."

    # show all class __init__ definitions to every function — not just methods.
    # standalone functions that receive class instances as input also need to
    # know the real attribute names (e.g. self.data, not self.val or self.node_data)
    if class_inits:
        shape_hint = "\nClasses available in this file and their exact attributes:\n"
        for cls_name, init_src in class_inits.items():
            shape_hint += f"\nClass `{cls_name}`:\n{init_src}\n"
        shape_hint += "\nUse ONLY these exact attribute names in assertions — never guess from parameter names."
    else:
        shape_hint = ""

    return f"""You are an expert Python testing engineer.

Generate pytest unit tests for the following Python function.

Context: {class_context}
Mocking: {mock_context}
{shape_hint}
Rules:
{rules}

Function:
{fn.source}
"""


async def generate_test(fn: FunctionInfo, module_name: str, file_type: str, class_inits: dict = None) -> str:
    prompt = build_prompt(fn, module_name, file_type, class_inits)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
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
                import_lines.append(f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(
                (f"{a.name} as {a.asname}" if a.asname else a.name) for a in node.names
            )
            import_lines.append(f"from {module} import {names}")

    return "\n".join(import_lines)


def get_class_names(filepath: str) -> list[str]:
    import ast
    from pathlib import Path

    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def get_class_inits(filepath: str) -> dict[str, str]:
    """Returns {class_name: __init__ source} for every class in the file."""
    import ast
    import textwrap
    from pathlib import Path

    source = Path(filepath).read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source)
    class_inits = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                    start = item.lineno - 1
                    end = item.end_lineno
                    raw = "\n".join(source_lines[start:end])
                    class_inits[node.name] = textwrap.dedent(raw)
                    break

    return class_inits


async def generate_all_tests(functions: list[FunctionInfo], filepath: str, file_type: str = "pure") -> str:
    from pathlib import Path
    module_name = Path(filepath).stem
    source_imports = get_source_imports(filepath)

    # only import standalone functions — class methods can't be imported directly
    standalone_names = [fn.name for fn in functions if fn.class_name is None]

    # also import any classes defined in the source file
    class_names = get_class_names(filepath)

    all_parts = standalone_names + class_names
    all_names = ", ".join(all_parts)

    has_external_calls = any(fn.external_calls for fn in functions)
    mock_import = "from unittest.mock import MagicMock, call\n" if has_external_calls else ""
    header = f"import pytest\n{mock_import}{source_imports}\nfrom {module_name} import {all_names}\n\n"

    class_inits = get_class_inits(filepath)

    # fire all Groq API calls simultaneously
    test_blocks = await asyncio.gather(
        *[generate_test(fn, module_name, file_type, class_inits) for fn in functions]
    )

    return header + "\n\n".join(test_blocks)


if __name__ == "__main__":
    from extractor import extract_functions  # only needed for manual test

    fns = extract_functions("samples/sample.py")
    result = asyncio.run(generate_all_tests(fns, "samples/sample.py"))
    print(result)
