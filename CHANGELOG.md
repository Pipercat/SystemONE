# SystemONE - Changelog

## [Unreleased]

### Added - SmartSortierer Pro Integration (2026-01-23)

#### 🎉 Neue Features
- **SmartSortierer Pro** vollständig in SystemONE integriert
- Intelligentes Dokumenten-Management mit KI-Klassifikation
- Automatische Pipeline: Upload → Extract → Chunk → Embed → Classify
- Vector-Search mit Qdrant für RAG (Retrieval Augmented Generation)
- Background-Worker-System für asynchrone Verarbeitung
- API mit Security & Audit-Logging

#### 📁 Neue Struktur
```
services/smartsortierer/
├── api/              # FastAPI Backend
├── worker/           # Background Jobs
└── frontend/         # Angular UI (in Entwicklung)
```

#### 🐳 Docker Services
- `api` - SmartSortierer FastAPI Backend
- `worker` - Background Job Processing
- `postgres` - PostgreSQL Datenbank (11 Tabellen)
- `redis` - Job Queue
- `qdrant` - Vector Database
- `ollama` - LLM Engine (llama3.2:3b, nomic-embed-text)
- `nginx` - Reverse Proxy

#### 📚 Dokumentation
- Aktualisiertes [README.md](README.md) mit vollständiger Übersicht
- Neue [INSTALL.md](INSTALL.md) mit Schritt-für-Schritt Anleitung
- [services/smartsortierer/README.md](services/smartsortierer/README.md) für Details
- `.env.example` mit allen Konfigurationsoptionen

#### 🛠️ Technologien
- **Backend:** FastAPI mit Pydantic
- **Database:** PostgreSQL 16
- **Queue:** Redis 7
- **Vector-DB:** Qdrant
- **LLM:** Ollama (lokal)
- **Frontend:** Angular (geplant)

#### ✅ Implementierte Phasen (SmartSortierer)
- [x] Phase 0: Projektsetup
- [x] Phase 1: Docker Infrastructure
- [x] Phase 2: Storage & Security
- [x] Phase 3: Database Schema
- [x] Phase 4: Extract & Chunk
- [x] Phase 5: Embedding & Vector-Storage

#### 📋 Geplante Features
- [ ] Phase 6: Klassifikation & Review UI
- [ ] Phase 8: RAG-Chat Interface
- [ ] Phase 9: Home Assistant Integration
- [ ] Phase 10: Angular Frontend
- [ ] Dashboard Integration
- [ ] PEET (KI-Agent) Integration

#### 🔗 Integration Highlights
- Einheitliches Docker Stack
- Gemeinsame Datenbank-Infrastruktur
- Vorbereitet für PEET-Integration (RAG über alle Dokumente)
- Unified API unter `/api/*`
- Dark Design passend zu SystemONE

---

## Previous Versions

### Generator_3
- Gridfinity Generator mit Three.js Preview
- STL Export Funktionalität
- Parameter-basierte Box-Generierung

### Generator_2
- Zweite Iteration des Generators
- Verbessertes UI

### Generator_1
- Erste Version des Gridfinity Generators
- Basis-Funktionalität

---

**Legende:**
- 🎉 Major Feature
- 🐛 Bugfix
- 📚 Dokumentation
- 🔒 Security
- ⚡ Performance
- 🎨 Design
- 🐳 Docker/Infrastructure
