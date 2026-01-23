# SmartSortierer Pro - SystemONE Integration

SmartSortierer ist ein intelligentes Dokumenten-Management-System mit KI-Integration für automatische Klassifikation und Archivierung. Es ist vollständig in SystemONE integriert und läuft als Teil des Gesamtsystems.

## Übersicht

SmartSortierer Pro verarbeitet Dokumente automatisch:
- **Upload** → Automatische Duplikat-Erkennung (SHA256)
- **Extract** → Text- und Metadaten-Extraktion
- **Chunk** → Intelligente Textaufteilung
- **Embed** → Vector-Embeddings für RAG
- **Classify** → KI-basierte Kategorisierung
- **Archive** → Strukturierte Ablage

## Architektur

```
smartsortierer/
├── api/              # FastAPI Backend mit REST API
├── worker/           # Background Jobs (Redis Queue)
└── frontend/         # Angular UI (in Entwicklung)
```

## Services

### API Service
- FastAPI mit automatischer Dokumentation (`/api/docs`)
- Security: API-Key Authentifizierung
- Audit-Logging für alle kritischen Aktionen
- PostgreSQL für Metadaten
- Qdrant für Vector-Suche

### Worker Service
- Verarbeitet Jobs aus Redis Queue
- Handler für: Extract, Chunk, Embed, Classify
- Ollama Integration für LLM-Features
- Automatische Fehlerbehandlung

### Frontend (in Entwicklung)
- Angular-basierte UI
- Datei-Upload & Verwaltung
- RAG-Chat Interface
- Admin-Dashboard

## Storage-Struktur

```
/storage/
├── 00_inbox/        # Neuer Upload
├── 01_ingested/     # Verarbeitet (SHA256-Namen)
├── 02_staging/      # Zwischenspeicher
├── 03_sorted/       # Fertig kategorisiert
├── 04_archive/      # Archivierte Dateien
└── 99_errors/       # Fehlerhafte Dateien
```

## Integration mit SystemONE

SmartSortierer ist als **Files/NAS-Modul** in SystemONE integriert:

- Gemeinsame PostgreSQL-Datenbank
- Gemeinsamer Redis für Queue-Management
- Gemeinsamer Qdrant für Vector-Storage
- Zugriff über SystemONE Dashboard
- Integration mit PEET (KI-Agent) für Chat über Dokumente

## Entwicklung

Siehe [Hauptdokumentation](../../README.md) für Docker-Setup und Deployment.

## Status

- ✅ Phase 0-5: Core-Funktionen (Upload, Extract, Chunk, Embed)
- 🚧 Phase 6: Klassifikation & Review
- 📋 Phase 8: RAG-Chat
- 📋 Phase 9: Home Assistant Integration
- 📋 Phase 10: Angular Frontend

Details: siehe [smartsortierer-pro/STATUS.md](../../../smartsortierer-pro/STATUS.md)
