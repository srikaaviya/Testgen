# pytestgen-ai — Full Project Documentation

---

## What the project does

A CLI tool that auto-generates pytest unit tests for any Python file using Groq AI and Python's AST module.

```
your code → AST parsing → Groq AI (parallel) → test file → coverage report
```

**Install:** `pip install pytestgen-ai`
**PyPI:** https://pypi.org/project/pytestgen-ai/0.1.0/

---

## Project structure

```
Testgen/
├── pytestgen_ai/
│   ├── __init__.py
│   ├── cli.py          — Typer CLI entry point
│   ├── extractor.py    — AST parsing, FunctionInfo dataclass, external call detection
│   ├── generator.py    — Groq API calls, prompt engineering, async generation
│   ├── detector.py     — detects file type: pure / db / requests / selenium
│   ├── writer.py       — writes test file, handles --output flag
│   ├── coverage_run.py — runs pytest --cov via subprocess
│   ├── api.py          — FastAPI POST /generate endpoint
│   └── api_client.py   — sends .py file to API
├── samples/            — test input files and generated test files
├── pyproject.toml
└── README.md
```

---

## How it works — step by step

1. Read the Python file
2. Use Python's `ast` module to extract every public function — name, args, full source, class context, external calls
3. Extract `__init__` source for every class (shape hints)
4. Detect file type (pure / db / requests / selenium)
5. Build structured prompts per function — includes source, class shape, detected external calls
6. Send all functions to Groq AI in parallel via `asyncio.gather`
7. Write `test_<filename>.py` with auto-generated header (imports, mocks)
8. Run `pytest --cov` and print coverage report

---

## Files explained

### extractor.py

Core AST parsing. Uses `ast.NodeVisitor` to walk the syntax tree.

**FunctionInfo dataclass:**
```python
@dataclass
class FunctionInfo:
    name: str
    args: list[str]
    source: str
    lineno: int
    class_name: str | None = None    # None if standalone, class name if method
    external_calls: list[str] = None # real external calls detected in function body
```

**FunctionVisitor:**
- `visit_ClassDef` — tracks which class we're inside using `self.current_class`
- `visit_FunctionDef` / `visit_AsyncFunctionDef` — calls `_process_function`
- `_process_function` — skips private/dunder functions (`_` prefix), extracts args and source
- `_detect_external_calls` — walks AST for function calls, filters out builtins and stdlib

**External call detection — how it works:**
- Collects all imported names from the file first (`import requests` → `requests` in imported_names)
- For `caller.method` calls: only flags if `caller` is in imported_names (not a local variable)
- For simple name calls: only flags if name is in imported_names and not in BUILTIN_NAMES or STDLIB_NAMES

**BUILTIN_NAMES** — print, range, len, int, str, float, list, dict, set, etc.
**STDLIB_NAMES** — defaultdict, deque, Counter, OrderedDict, datetime, Path, json, etc.

**Why this matters:** Without this filter, `stack.append()` and `defaultdict()` were flagged as external calls, causing Groq to try mocking local variables — which always fails.

**extract_functions:**
```python
def extract_functions(filepath):
    # 1. parse AST
    # 2. collect all imported names
    # 3. run FunctionVisitor
    # returns list[FunctionInfo]
```

---

### generator.py

**build_prompt(fn, module_name, file_type, class_inits):**

Constructs the prompt sent to Groq. Includes:
- `class_context` — tells Groq if function is a method (instantiate the class first) or standalone
- `mock_context` — lists detected external calls so Groq knows what to mock
- `shape_hint` — shows all class `__init__` source so Groq uses correct attribute names
- `base_rules` — 15+ explicit rules constraining Groq's output
- `db_rules` — added only when external calls exist

**Key prompt rules:**
- Use pytest only, no unittest
- No backticks, use repr() instead
- No parameters except pytest fixtures (def test_something(monkeypatch):)
- Never use repr() to compare objects — check attributes directly
- Only generate exception tests if function explicitly raises
- monkeypatch.setattr takes exactly 2 args: ('module_name.attribute', value)
- To mock builtins use 'builtins.print', not 'module.print'
- Never mock builtins like range, len, isinstance
- Never use monkeypatch.setattr(...).return_value

**Shape hints — why they exist:**
```python
class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data   # attribute is .data, not .node_data
```
Groq sees `node_data` as the parameter and guesses that's the attribute name too. Wrong.
Fix: extract `__init__` source and pass it explicitly in the prompt.
Now shown to ALL functions (not just methods) — standalone functions that receive class instances also need to know attribute names.

**get_class_inits(filepath):**
Scans AST for every class, finds `__init__`, extracts its source code.
Returns `{class_name: init_source}`.

**generate_all_tests:**
```python
async def generate_all_tests(functions, filepath, file_type):
    # build header with imports
    # get class_inits
    # fire all Groq calls simultaneously with asyncio.gather
    # return header + all test blocks joined
```

**Header auto-generation:**
- Always includes `import pytest`
- Adds `from unittest.mock import MagicMock, call` if any function has external calls
- Adds all imports from the source file
- Imports standalone functions + class names (NOT methods)

**Why class methods are not in the import line:**
```python
# wrong — insert_node is a method, can't be imported directly
from hr_linkedlist import insert_node, SinglyLinkedList

# correct — import only the class, call method via instance
from hr_linkedlist import SinglyLinkedList
linked_list = SinglyLinkedList()
linked_list.insert_node(5)
```

---

### detector.py

Reads import statements and classifies the file:
- `selenium` → skip entirely
- `requests` / `httpx` / `aiohttp` → warn, generate with mocking
- `psycopg2` / `sqlite3` / `sqlalchemy` etc. → warn, generate with mocking
- anything else → pure

---

### cli.py

Typer CLI. Two modes:
- `testgen auth.py` — single file (Typer Argument)
- `testgen --folder src/` — folder (Typer Option, uses rglob)
- `testgen auth.py --output tests/` — custom output directory

`run_for_file()` — orchestrates: detect → extract → generate → write → coverage

---

### coverage_run.py

```python
subprocess.run([sys.executable, "-m", "pytest", test_filepath,
    f"--cov={module_name}", "--cov-report=term-missing", "-q"])
```

`--cov` takes the module name (stem), not the full file path.

---

### api.py

FastAPI endpoint:
- `POST /generate` — accepts `UploadFile`, writes to tempfile, runs full pipeline, returns JSON
- `GET /health` — returns `{"status": "ok"}`

Response: `{filename, test_content, file_type, function_count}`

Install API dependencies: `pip install pytestgen-ai[api]`

---

## All fixes made during development

### Fix 1 — NameError: functions not imported in test file
Groq generated tests without importing the functions being tested.
**Fix:** Auto-generate import header in `generate_all_tests()`:
```python
from {module_name} import {function_names}
```

### Fix 2 — Python backtick syntax error
Groq used backticks which Python 3.12+ doesn't support.
**Fix:** Added rule "Do NOT use backticks — use repr() instead"

### Fix 3 — mocker fixture error
Groq used `mocker` from pytest-mock (not installed). 
**Fix:** Added rule "Use only monkeypatch, never mocker"

### Fix 4 — Wrong monkeypatch 3-arg form
Groq called `monkeypatch.setattr(module, 'attr', value)` with 3 args.
**Fix:** Added rule "monkeypatch.setattr string form takes exactly 2 args"

### Fix 5 — coverage.py naming conflict
File named `coverage.py` conflicted with the coverage package.
**Fix:** Renamed to `coverage_run.py`

### Fix 6 — No data to report in coverage
`--cov` was given the full file path instead of module name.
**Fix:** Use `Path(source_filepath).stem` for `--cov`

### Fix 7 — Missing () in test function definitions
Groq wrote `def test_something:` without parentheses.
**Fix:** Added rule "Every test function definition MUST have parentheses"

### Fix 8 — Classes defined inside test files
Groq redefined classes inside test files instead of importing them.
**Fix:** Added rule "Do NOT define any classes inside the test file"

### Fix 9 — Wrong exception assumptions
Groq assumed functions raise TypeError/ValueError without checking.
**Fix:** Added rule "Only generate exception test if function explicitly raises"

### Fix 10 — ImportError for class methods
Groq put method names in the import line: `from hr_linkedlist import insert_node`.
**Fix:** Filter functions by `class_name is None` — only standalone functions go in import line.

### Fix 11 — Wrong attribute names (node_data vs data)
Groq guessed attribute names from constructor parameter names.
**Fix:** Extract `__init__` source for all classes, pass as shape hints in prompt.

### Fix 12 — Wrong monkeypatch path (hr_linkedlist.print)
After making module path rule too strict, Groq wrote `hr_linkedlist.print` for builtins.
**Fix:** Added rule distinguishing builtins (`builtins.print`) from module attributes.

### Fix 13 — range detected as external call
`range` was flagged as an external call, Groq tried to mock it.
**Fix:** Added `range` to BUILTIN_NAMES filter in extractor.py.

### Fix 14 — call not imported in test header
Groq used `call(...)` in assertions but didn't import it.
**Fix:** Auto-include `call` in mock import: `from unittest.mock import MagicMock, call`

### Fix 15 — monkeypatch used without fixture parameter
Conflict between "no parameters" rule and needing monkeypatch.
**Fix:** Updated rule to "no parameters EXCEPT pytest fixtures like monkeypatch"

### Fix 16 — Local variables flagged as external calls
`stack.append`, `res.append` were flagged — they're local variables.
**Fix:** Cross-reference detected calls against imported names — only flag if caller was actually imported.

### Fix 17 — stdlib flagged as external calls
`defaultdict` from collections was flagged, Groq tried to mock it.
**Fix:** Added STDLIB_NAMES filter and also cross-check against imports.

### Fix 18 — Build failure (hatchling can't find package)
All source files were in root directory, not a named package directory.
**Fix:** Created `pytestgen_ai/` directory, moved all files in, added `__init__.py`, updated pyproject.toml.

---

## Known limitations

- **Algorithm-heavy code** — linked list traversal, monotonic stacks, pointer manipulation produce wrong expected values. LLMs can't reliably trace complex logic step by step.
- **Duplicate values** — functions that map duplicate values to the same dict key cause wrong assertions.
- **Generated tests should be reviewed** before committing to production.

---

## What works well

- Pure utility functions (math, string operations)
- Input validation
- Business logic
- Class-based code with clear `__init__` attributes
- DB files (psycopg2, SQLAlchemy) — mocking works correctly

---

## Behavioral round content

**What the project is:**
A CLI tool that takes any Python file, extracts all public functions using Python's AST module, sends each function to Groq AI to generate pytest test cases, writes the test file, and automatically runs a coverage report.

**Why I built it:**
Writing tests is something most developers skip because it's tedious. I wanted to automate that — not just by asking an LLM to write tests, but by actually reading the code structure programmatically and generating tests that are aware of the real function signatures, class hierarchy, and external dependencies.

**How I built it — in phases:**

Phase 1 — Core extraction: Used `ast.NodeVisitor` to walk the syntax tree and extract every public function. Stored in a `FunctionInfo` dataclass. Tracked class context so methods know which class they belong to.

Phase 2 — Groq integration: Sent each function's source to Groq with engineered prompts. Fixed issues iteratively — missing imports, wrong syntax, wrong mocking style. Ended up with 15+ prompt rules refined through repeated test runs.

Phase 3 — Handling real-world files: Tested on DB files, class methods, algorithmic code. Each type exposed a new problem. DB files needed mocking — built dynamic external call detection via AST. Class methods can't be imported directly — fixed the import header. Wrong attribute names in assertions — extracted `__init__` source and passed it as context.

Phase 4 — Performance: Switched from sequential to async parallel Groq calls using `AsyncGroq` and `asyncio.gather`.

Phase 5 — External call detection refinement: Detector was too broad — flagged local variable method calls and stdlib. Fixed by cross-referencing against the file's import statements and filtering known stdlib names.

Phase 6 — Packaging and publishing: Structured as a proper Python package, configured pyproject.toml with hatchling, made FastAPI optional, published to PyPI.

**Key decisions:**
- AST over regex — AST gives you the actual syntax tree, guaranteed correct
- Groq over OpenAI — free tier, fast inference
- monkeypatch over pytest-mock — built into pytest, no extra dependency
- asyncio.gather over sequential — N functions = N API calls, parallel is faster
- Prompt rules over post-processing — constrain Groq's output at the source

**What didn't work:**
- Algorithm-heavy code produces wrong expected values — LLMs can't trace pointer logic reliably
- Overly prescriptive monkeypatch rule caused regression — Groq applied it to builtins too
- Prompt rule for attribute names helped but wasn't 100% — real fix was passing `__init__` source

**Answer to "why not just ask Claude/Gemini":**
Asking an LLM directly means manually copy-pasting each function, describing the context, specifying what to mock, and creating the test file yourself. For one function that's fine. For a file with 10 functions or a folder with 20 files, that's a lot of manual work. This tool automates the entire pipeline — reads the file, understands the structure, builds the right context, and writes the test file. One command. The prompt is also engineered once and applied consistently to every function.

---

## Concept explanations

### mocker vs monkeypatch
- `mocker` — fixture from `pytest-mock` (third-party, needs `pip install pytest-mock`)
- `monkeypatch` — built into pytest, no extra install
- Both temporarily replace something during a test and restore it after
- We use monkeypatch to avoid adding an extra dependency

### How monkeypatch works
```python
def test_fetch_user(monkeypatch):
    mock = MagicMock()
    mock.json.return_value = {"name": "Alice"}
    monkeypatch.setattr('requests.get', mock)  # replace requests.get with mock
    result = fetch_user("http://example.com")
    assert result == {"name": "Alice"}
# after test ends, requests.get is restored automatically
```

### Why class methods can't be imported directly
`insert_node` is a method — it lives inside `SinglyLinkedList`. It doesn't exist independently.
```python
# wrong
from hr_linkedlist import insert_node  # ImportError

# correct
from hr_linkedlist import SinglyLinkedList
ll = SinglyLinkedList()
ll.insert_node(5)
```

### Wrong attribute names — the fix
```python
class SinglyLinkedListNode:
    def __init__(self, node_data):
        self.data = node_data  # real attribute is .data
```
Groq sees `node_data` (parameter) and writes `node.node_data` (wrong).
Fix: pass `__init__` source in prompt → Groq sees `self.data` → writes `node.data` (correct).

### External call detection
AST walks the function body, collects all function calls, cross-references against imports.
- `stack.append` — `stack` not in imports → local variable → skip
- `requests.get` — `requests` in imports → real external call → flag for mocking
- `defaultdict` — in STDLIB_NAMES → skip

---

## pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pytestgen-ai"
version = "0.1.0"
description = "Auto-generate pytest tests for Python functions using Groq AI"
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["typer", "groq", "python-dotenv", "pytest", "pytest-cov"]

[project.optional-dependencies]
api = ["fastapi", "uvicorn", "python-multipart"]

[project.scripts]
testgen = "pytestgen_ai.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["pytestgen_ai"]
```

---

## Publishing steps

```bash
pip install build twine
python -m build          # creates dist/ with .tar.gz and .whl
twine upload dist/*      # username: __token__, password: PyPI API token
```
