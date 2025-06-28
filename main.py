# main.py
from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import google.generativeai as genai
import base64

# === 1. Configure Gemini ===
genai.configure(api_key="AIzaSyC_RYuYakQgffMn6rCqfOHYel1mCQCeZII")
model = genai.GenerativeModel('gemini-1.5-flash')

# === 2. Initialize FastAPI app ===
app = FastAPI()

# === 3. Enable CORS for frontend ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-nextjs-domain.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 4. Simple in-memory job store ===
job_store = {}

# === 5. Root route ===
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Document Processing API!"}

# === 6. Upload endpoint ===
@app.post("/upload")
async def upload(file: UploadFile, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    content = await file.read()
    mime_type = file.content_type
    print(f"[UPLOAD] Received file: {file.filename} | MIME: {mime_type}")

    # Background task runs Gemini + stores result
    background_tasks.add_task(process_document, job_id, content, mime_type)

    return {"jobId": job_id}

# === 7. Result polling endpoint ===
@app.get("/result")
async def result(jobId: str):
    job = job_store.get(jobId)

    if not job:
        return {"status": "processing"}
    return {"status": "done", **job}

# === 8. Background processor ===
async def process_document(job_id: str, file_bytes: bytes, mime_type: str):
    try:
        base64_file = base64.b64encode(file_bytes).decode("utf-8")

        prompt = "Extract all text from this insurance document and return it as plain text."

        resp =  model.generate_content([
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64_file
                        }
                    }
                ]
            }
        ])

        text = resp.text
        job_store[job_id] = {"message": text}
        print(f"[PROCESS] Text extraction complete for job: {job_id}")

    except Exception as e:
        print(f"[ERROR] Gemini processing failed: {e}")
        job_store[job_id] = {"error": "Failed to process file"}








# //below is new code #

import re
from typing import Dict

# … your existing imports and setup above …

def parse_policy_text(raw_text: str) -> Dict[str,str]:
    data = {}
    entries = raw_text.strip().split("||")
    for entry in entries:
        if ":" in entry:
            key, value = entry.split(":", 1)
            data[key.strip()] = value.strip()
    return data

def generate_insurance_summary(full_text: str) -> str:
    prompt = f"""
You are an insurance assistant.

Given the text of an insurance document below, write a friendly and short summary (3–5 lines max) for the user. Mention details like:

- Type of policy
- Policy duration
- Insurance company (if mentioned)
- Vehicle make/model (if found)
- Premium (if available)

Do **not** hardcode field names. Just summarize what’s clearly present.

Insurance Document:
\"\"\"
{full_text}
\"\"\"
Summary:
"""
    resp = model.generate_content(prompt)
    return resp.text.strip()

@app.get("/extract")
async def extract(jobId: str):
    job = job_store.get(jobId)
    if not job or "message" not in job:
        return {"status": "processing"}
    raw = job["message"]
    # build and call the key‑info prompt
    prompt = f"""
From the following insurance document text, extract and return the key information as a plain text list in this exact format:

<key>: <value>||

Make sure every entry ends with '||' and don't explain anything — just return the list.

Document Text:
{raw}
"""
    resp = model.generate_content(prompt)
    raw_keys = resp.text
    fields = parse_policy_text(raw_keys)
    # store back into job_store
    job_store[jobId]["fields"] = fields
    return {"status": "done", "fields": fields}

@app.get("/summary")
async def summary(jobId: str):
    job = job_store.get(jobId)
    if not job or "message" not in job:
        return {"status": "processing"}
    full_text = job["message"]
    summary = generate_insurance_summary(full_text)
    # store back into job_store
    job_store[jobId]["summary"] = summary
    return {"status": "done", "summary": summary}
