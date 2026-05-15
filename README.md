# pytestgen-ai

Auto-generate pytest tests for Python functions using Groq AI.

## What it does

`pytestgen-ai` reads your Python files, extracts all public functions using AST parsing, sends each function to Groq AI, and writes a complete `test_<filename>.py` file with pytest test cases — including coverage report. Works best with pure functions and business logic.

```
your code → AST parsing → Groq AI → test file → coverage report
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

1. **AST parsing** — uses Python's built-in `ast` module to extract every public function from your file
2. **File type detection** — detects if the file uses DB, Selenium, or requests
3. **Groq AI** — sends each function's source code to Groq with engineered prompts
4. **Test file** — writes a complete `test_<filename>.py` ready to run with pytest
5. **Coverage** — automatically runs `pytest --cov` and displays the report

## Supported file types

| File type | Support |
|---|---|
| Pure functions | ✅ Full support |
| Input validation | ✅ Full support |
| Database (psycopg2, SQLAlchemy) | ⚠️ Partial — results may vary |
| Selenium | ❌ Skipped |
| requests / httpx | ❌ Skipped |

## REST API

`pytestgen-ai` also ships with a FastAPI endpoint:

```bash
uvicorn api:app --reload
```

Upload a `.py` file via `POST /generate` and get the generated test content back as JSON.

Interactive docs available at `http://127.0.0.1:8000/docs`.

## Tech stack

- [Typer](https://typer.tiangolo.com/) — CLI
- [Groq API](https://console.groq.com/) — AI test generation
- [Python AST](https://docs.python.org/3/library/ast.html) — function extraction
- [pytest-cov](https://pytest-cov.readthedocs.io/) — coverage reports
- [FastAPI](https://fastapi.tiangolo.com/) — REST API

## Limitations

- Works best with pure functions and business logic
- Functions with external dependencies (DB, API calls) may generate partial tests
- Generated tests should be reviewed before committing to production

## License

MIT
