<p align="right">
  <img src="Generator_3/logo/logo_groß.png" alt="SystemONE Logo" width="120"/>
</p>

# SystemONE

**SystemONE** ist ein **lokales Smart-System-Dashboard** im **Digital-Dark Design**:  
eine zentrale Oberfläche, die **Smart Home (Home Assistant)**, **NAS/Files**, **KI-Agent (PEET)** und Tools wie **3D Creator / Gridfinity Generator** in **einem** System bündelt.

---

## Highlights

- **Digital-Dark Dashboard UI** (dark, modern, klar strukturiert)
- **SystemONE Logo oben rechts** (fix im Header integriert)
- **PEET Agent**: Chat + Automationen + Wissenssuche über Dokumente
- **Home Assistant Steuerung**: Geräte, Szenen, Sensoren (inkl. KI-triggerbar)
- **NAS / File Hub**: Zugriff, Suche, Sortierung (SmartSortier-Logik möglich)
- **3D Bereich**: 3D-Objekte live ansehen & verwalten (Creator-Workflow)
- **Gridfinity Generator**: Parameter → Vorschau → Export → Presets
- **Docker-first**: modulare Services, sauber getrennte Komponenten

---

## Module

### 1) Dashboard (Frontend)
- Startseite mit **Karten / Panels**
- Navigation zu: **Chat**, **SmartHome**, **NAS**, **3D**, **Generator**, **Settings**
- Fokus: schnelle Übersicht + klare Interaktion (ohne UI-Overkill)
- **Top-Header mit SystemONE Logo oben rechts (fix)**

### 2) PEET (KI-Agent)
- Chat UI (Kontext + Verlauf)
- Dokumentenfragen (RAG / Vektorsuche optional)
- Aktionen ausführen (z. B. Licht schalten, Datei sortieren, Preset speichern)

### 3) SmartHome (Home Assistant)
- Geräte-Listen, Räume, Favoriten
- Sensor-Status, Automations-Trigger
- API-Anbindung (REST/WebSocket – je nach Setup)

### 4) NAS / Files
- Browse / Search
- Upload / Download (optional)
- SmartSortier-Workflows: erkennen → klassifizieren → umbenennen → ablegen

### 5) 3D / Creator
- Live Preview von 3D-Objekten (Browser/Three.js oder Desktop)
- Bibliothek / Projekte / Export
- Optional: Slicer-Integration / Direktdruck-Workflow (später)

### 6) Gridfinity Generator
- Parameter UI (Units, Wall, Raster, etc.)
- Vorschau/Preview
- STL Export
- Presets (localStorage / DB)

---

## Architektur (Kurz)

**Frontend** → **API** → (SmartHome / NAS / KI / Generator)

- Frontend: Angular (oder Web UI)
- API: FastAPI / Node / Gateway (je nach Build)
- KI: Ollama / lokale Modelle + optional Vector DB (z. B. Qdrant)
- Daten: Postgres (optional), Redis (optional), Filesystem/NAS

---

## Design-Standard (Digital-Dark)

- Dunkler Hintergrund, **runde Cards**, klare Kontraste
- Wenige Akzentfarben (z. B. Blau/Orange je nach Theme)
- **Links Navigation**, **Center Content**, optional **Right Panel**
- Icons sparsam (nur wo funktional notwendig)
- Fokus auf **Lesbarkeit + klare Hierarchie**
- **Fixer Header mit SystemONE Logo oben rechts**

---

## Repository Struktur (Empfehlung)

```txt
SystemONE/
  frontend/            # UI (Angular / Web)
  api/                 # Backend API (FastAPI/Node)
  services/
    peet/              # Agent / RAG / Tools
    smarthome/         # HA Adapter / Clients
    files/             # NAS + SmartSortier
    gridfinity/        # Generator + Presets
    creator3d/         # 3D Viewer/Renderer
  infra/
    docker-compose.yml # gesamter Stack
    nginx/             # optional Reverse Proxy
  docs/                # Doku, Screens, Entscheidungen


⸻

Getting Started

Wird ergänzt, sobald docker-compose.yml + erste Module im Repo sind.

	1.	Repository klonen
	2.	infra/docker-compose.yml starten
	3.	Frontend öffnen (Nginx/Dev-Server)
	4.	Home Assistant / NAS / PEET verbinden

⸻

Roadmap
	•	Basis Dashboard + Navigation (Digital-Dark)
	•	Header inkl. SystemONE Logo oben rechts
	•	PEET Chat (lokal) + Tool-Calls
	•	Home Assistant Anbindung + Geräte-UI
	•	NAS Hub + Suche
	•	Gridfinity Generator V1 (Preview + STL Export)
	•	3D Live Preview + Objektbibliothek
	•	Presets + Profile Auswahl beim Start

⸻

License

TBD (z. B. MIT / Private)

⸻

Credits

Built by Pipercat.

---