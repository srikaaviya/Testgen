import subprocess
import sys
from pathlib import Path


def run_coverage(test_filepath: str, source_filepath: str) -> None:
    module_name = Path(source_filepath).stem  # samples/auth.py → auth

    result = subprocess.run( #runs a terminal command from inside Python
        [
            sys.executable, "-m", "pytest", #This ensures it uses the correct .venv
            test_filepath,
            f"--cov={module_name}",
            "--cov-report=term-missing",
            "-q"
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr
    print(output)

    if result.returncode == 0:
        print("  ✅ All tests passed.")
    else:
        print("  ⚠️  Some tests failed. Check output above.")
