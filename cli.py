import typer
import asyncio
from pathlib import Path
from extractor import extract_functions
from generator import generate_all_tests
from writer import write_tests
from detector import detect_file_type
from coverage_run import run_coverage

SKIP_TYPES = {"selenium"}  # requests is now handled via dynamic mocking detection

app = typer.Typer()

@app.command()
def main(
    file: str = typer.Argument(None, help="Path to a single Python file"),
    folder: str = typer.Option(None, "--folder", "-d", help="Path to a folder of Python files"),
    output: str = typer.Option(None, "--output", "-o", help="Directory to save generated test files"),
):
# typer.option --> we need to definitely mention --folder to folder
# typer.argument --> either mention file name or --file filename, if both file and folder were Arguments,
# Typer wouldn't know which is which. thats why folder is optional

    if not file and not folder:
        typer.echo("Error: provide a file path or --folder")
        raise typer.Exit(code=1)

    if file:
        run_for_file(file, output)

    if folder:
        folder_path = Path(folder)
        py_files = list(folder_path.rglob("*.py")) #recursive glob

        if not py_files:
            typer.echo(f"No Python files found in {folder}")
            raise typer.Exit(code=1)

        for py_file in py_files:
            run_for_file(str(py_file), output)


def run_for_file(filepath: str, output_dir: str = None):
    typer.echo(f"Processing: {filepath}")

    file_type = detect_file_type(filepath)

    if file_type in SKIP_TYPES:
        typer.echo(f"  Skipping — {file_type} files are not supported.")
        return

    if file_type in {"db", "requests"}:
        typer.echo(f"  Warning — {file_type} file detected. External calls will be mocked automatically.")

    fns = extract_functions(filepath)

    if not fns:
        typer.echo(f"  No public functions found.")
        return

    typer.echo(f"  Found {len(fns)} function(s): {[f.name for f in fns]}")

    test_content = asyncio.run(generate_all_tests(fns, filepath, file_type))
    output_path = write_tests(filepath, test_content, output_dir)

    typer.echo(f"  Tests written to: {output_path}")

    typer.echo(f"  Running coverage...")
    run_coverage(output_path, filepath)


if __name__ == "__main__":
    app()
