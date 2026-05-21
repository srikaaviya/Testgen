# pytestgen-ai

Auto-generate pytest tests for Python functions using Groq AI.

## What it does

`pytestgen-ai` reads your Python files, extracts all public functions using AST parsing, sends each function to Groq AI in parallel, and writes a complete `test_<filename>.py` file with pytest test cases — including a coverage report.

```
your code → AST parsing → Groq AI (parallel) → test file → coverage report
```

## Installation

```bash
pip install pytestgen-ai
```

Set your Groq API key (get one free at [console.groq.com](https://console.groq.com)):

```bash
export GROQ_API_KEY=your_key_here
```

Or create a `.env` file in your project:

```
GROQ_API_KEY=your_key_here
```

## Usage

**Single file:**
```bash
pytestgen-ai auth.py
```

**Entire folder:**
```bash
pytestgen-ai --folder src/
```

**Custom output directory:**
```bash
pytestgen-ai auth.py --output tests/
pytestgen-ai --folder src/ --output tests/
```

## Example

Given `auth.py`:
```python
def login(username, password):
    if not username or not password:
        raise ValueError("Username and password required")
    if username == "admin" and password == "secret":
        return True
    return False
```

Running:
```bash
pytestgen-ai auth.py
```

Output:
```
Processing: auth.py
  Found 2 function(s): ['login', 'is_strong_password']
  Tests written to: test_auth.py
  Running coverage...

  Name      Stmts   Miss  Cover   Missing
  ----------------------------------------
  auth.py      14      0   100%
  ----------------------------------------
  ✅ All tests passed.
```

Generated `test_auth.py`:
```python
import pytest
from auth import login

def test_normal_case_login():
    assert login("admin", "secret") == True

def test_empty_username_login():
    with pytest.raises(ValueError):
        login("", "secret")

def test_invalid_credentials_login():
    assert login("user", "wrong") == False
```

## How it works

1. **AST parsing** — uses Python's built-in `ast` module to extract every public function and class from your file
2. **External call detection** — automatically detects DB calls, requests, and other external dependencies that need mocking
3. **File type detection** — detects if the file uses DB, Selenium, or requests
4. **Groq AI (parallel)** — sends all functions to Groq simultaneously using async, so large files generate faster
5. **Test file** — writes a complete `test_<filename>.py` ready to run with pytest
6. **Coverage** — automatically runs `pytest --cov` and displays the report

## Supported file types

| File type | Support |
|---|---|
| Pure functions | ✅ Full support |
| Input validation | ✅ Full support |
| Class methods | ✅ Supported — class is imported, methods called via instance |
| Database (psycopg2, SQLAlchemy) | ⚠️ Partial — external calls mocked automatically |
| requests / httpx | ⚠️ Partial — external calls mocked automatically |
| Selenium | ❌ Skipped — browser automation not supported |

## REST API

`pytestgen-ai` also ships with a FastAPI endpoint. Install with the optional API dependencies:

```bash
pip install pytestgen-ai[api]
```

Then run:

```bash
uvicorn api:app --reload
```

Upload a `.py` file via `POST /generate` and get the generated test content back as JSON.

Interactive docs available at `http://127.0.0.1:8000/docs`.

## Tech stack

- [Typer](https://typer.tiangolo.com/) — CLI
- [Groq API](https://console.groq.com/) — AI test generation (llama-3.3-70b-versatile)
- [Python AST](https://docs.python.org/3/library/ast.html) — function extraction and external call detection
- [pytest-cov](https://pytest-cov.readthedocs.io/) — coverage reports
- [FastAPI](https://fastapi.tiangolo.com/) — REST API

## Limitations

- Works best with **pure utility functions and business logic**
- **Algorithm-heavy code** (linked lists, trees, monotonic stacks) may have incorrect expected values in assertions — the AI traces complex pointer logic imperfectly
- **Duplicate return values** across functions in the same file may cause test confusion
- Generated tests should always be **reviewed before committing to production**
- Requires a Groq API key (free tier available)

## License

MIT
