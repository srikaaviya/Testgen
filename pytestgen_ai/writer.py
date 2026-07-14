from pathlib import Path


def write_tests(source_filepath: str, test_content: str, output_dir: str = None) -> str:
    source_path = Path(source_filepath)
    output_filename = f"test_{source_path.stem}.py"

    if output_dir:
        output_folder = Path(output_dir)
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / output_filename
    else:
        output_path = source_path.parent / output_filename

# source_path.stem —.stem strips the extension. So sample.py → sample.
# Then we prefix test_ → test_sample.py
# source_path.parent — puts the output file in the same folder as the original file.
# So if you run it on src/auth.py, it writes src/test_auth.py.

    output_path.write_text(test_content, encoding="utf-8")

    return str(output_path)


if __name__ == "__main__":
    from extractor import extract_functions
    from generator import generate_all_tests

    fns = extract_functions("samples/sample.py")
    test_content = generate_all_tests(fns)
    output = write_tests("samples/sample.py", test_content)
    print(f"Tests written to: {output}")
