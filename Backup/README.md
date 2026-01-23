# Gridfinity Local Generator

Lokales FastAPI-Projekt mit moderner Web-Oberfläche zum Erzeugen von Gridfinity Boxen und Baseplates.

## Projektstruktur

gridfinity-local/
 ├ app.py
 ├ templates/
 │   └ index.html
 ├ requirements.txt
 ├ .gitignore
 ├ README.md
 ├ venv/ (virtuelle Umgebung)
 ├ output/ (generierte STL-Dateien)

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

## Start

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Browser: [http://localhost:8000](http://localhost:8000)
