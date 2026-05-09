import ast
from pathlib import Path

SELENIUM_IMPORTS = {"selenium"}
REQUESTS_IMPORTS = {"requests", "httpx", "aiohttp"}
DB_IMPORTS = {"psycopg2", "sqlite3", "sqlalchemy", "pymysql", "asyncpg"}


def detect_file_type(filepath: str) -> str:
    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])

    if imports & SELENIUM_IMPORTS:
        return "selenium"
    if imports & REQUESTS_IMPORTS:
        return "requests"
    if imports & DB_IMPORTS:
        return "db"
    return "pure"
