from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import tempfile
import os

from extractor import extract_functions
from generator import generate_all_tests
from detector import detect_file_type

app = FastAPI(
    title="testgen API",
    description="Auto-generate pytest tests for any Python file using Groq AI",
    version="0.1.0"
)


# what we send back to the user after generating tests
class GenerateResponse(BaseModel):
    filename: str        # test_auth.py
    test_content: str    # full generated test code as string
    file_type: str       # pure / db
    function_count: int  # how many functions were found


@app.post("/generate", response_model=GenerateResponse)
async def generate(file: UploadFile = File(...)):  # user uploads a .py file
    # async def + await means: While waiting for the file to finish uploading,
    # let the server handle other incoming requests — don't block and sit idle.

    # step 1 — make sure it's a python file
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are supported")

    # step 2 — read the uploaded file content (returns bytes, so decode to string)
    content = await file.read()

    # step 3 — write content to a temp file on disk
    # extractor and detector need a real file path to work with
    with tempfile.NamedTemporaryFile(
        suffix=".py",
        delete=False,   # don't delete yet — we need it in the try block below
        mode="w",
        encoding="utf-8"
    ) as tmp:
        tmp.write(content.decode("utf-8"))
        tmp_path = tmp.name  # save the temp file path

    try:
        # step 4 — detect file type (pure, db, selenium, requests)
        file_type = detect_file_type(tmp_path)

        # step 5 — skip unsupported file types
        if file_type in {"selenium", "requests"}:
            raise HTTPException(
                status_code=400,
                detail=f"{file_type} files are not supported"
            )

        # step 6 — extract all public functions from the file
        functions = extract_functions(tmp_path)

        if not functions:
            raise HTTPException(
                status_code=400,
                detail="No public functions found in the file"
            )

        # step 7 — generate test code using Groq
        test_content = generate_all_tests(functions, tmp_path, file_type)

    finally:
        os.remove(tmp_path)  # always delete temp file even if an error occurs

    # step 8 — return the result
    return GenerateResponse(
        filename=f"test_{file.filename}",
        test_content=test_content,
        file_type=file_type,
        function_count=len(functions)
    )


@app.get("/health")
def health():
    # simple check to confirm the API is running
    return {"status": "ok"}
