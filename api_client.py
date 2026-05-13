import requests
import sys
from pathlib import Path


API_URL = "http://127.0.0.1:8000/generate"


def generate_tests_via_api(filepath: str):
    path = Path(filepath)

    # step 1 — send the .py file to the API
    print(f"Sending {path.name} to testgen API...")
    with open(path, "rb") as f:
        response = requests.post(API_URL, files={"file": f})

    # step 2 — check if API returned an error
    if response.status_code != 200:
        print(f"Error: {response.json()['detail']}")
        return

    # step 3 — extract the result from the response
    result = response.json()
    print(f"  File type   : {result['file_type']}")
    print(f"  Functions   : {result['function_count']}")
    print(f"  Output file : {result['filename']}")

    # step 4 — save the generated test content to a file
    output_path = path.parent / result["filename"]
    output_path.write_text(result["test_content"], encoding="utf-8")

    print(f"  Tests saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python api_client.py <path_to_file.py>")
        sys.exit(1)

    generate_tests_via_api(sys.argv[1])
