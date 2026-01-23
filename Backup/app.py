from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate/bin")
def generate_bin(
    x: int = Form(...),
    y: int = Form(...),
    z: int = Form(...),
):
    filename = f"bin_{uuid.uuid4().hex}.stl"
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Simulate STL generation
    time.sleep(2)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Simulated STL for bin with x={x}, y={y}, z={z}\n")

    return FileResponse(output_path, filename=filename, media_type="application/sla")


@app.post("/generate/baseplate")
def generate_baseplate(
    x: int = Form(...),
    y: int = Form(...),
):
    filename = f"baseplate_{uuid.uuid4().hex}.stl"
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Simulate STL generation
    time.sleep(2)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Simulated STL for baseplate with x={x}, y={y}\n")

    return FileResponse(output_path, filename=filename, media_type="application/sla")
