# SystemONE

SystemONE ist ein local-first Dashboard für Smart Home, Dokumentenautomatisierung und KI-Unterstützung mit **PEET** als Assistent. Es bündelt mehrere Services in einem Docker-Stack, damit der gesamte Workflow nachvollziehbar, modular und datenschutzfreundlich lokal betrieben werden kann.

**Aktueller Stand:** SmartSortierer-Backend mit API/Worker ist aufgebaut, die Dokumentenpipeline läuft serverseitig, Dashboard- und Integrationsmodule sind in Arbeit.

**Warum Ausbildungsprojekt?** SystemONE verbindet Softwareentwicklung, DevOps, IT-Sicherheit, KI-Grundlagen und Dokumentation in einem realitätsnahen End-to-End-Projekt.

## Quickstart (2 Minuten)
```bash
git clone https://github.com/Pipercat/SystemONE.git
cd SystemONE
cp .env.example .env
cd infra && docker compose up -d --build
```
Danach erreichbar unter:
- Dashboard / Reverse Proxy: `http://localhost`
- API-Dokumentation: `http://localhost/api/docs`

## Module / Services

| Komponente | Zweck | Status | Doku |
|---|---|---|---|
| Dashboard (Frontend) | Zentrale Oberfläche für Status, Navigation und PEET-Panel | In progress | [Architektur](docs/ARCHITECTURE.md) |
| SmartSortierer API | Upload, Metadaten, Security, Dokumenten-Endpunkte | Done | [Services](docs/services.md) |
| SmartSortierer Worker | Background-Jobs (Extract, Chunk, Embed, Klassifikation) | Done | [Architektur](docs/ARCHITECTURE.md) |
| PostgreSQL | Strukturierte Fachdaten und Job-Status | Done | [INSTALL](INSTALL.md) |
| Redis Queue | Job-Queue und asynchrone Verarbeitung | Done | [INSTALL](INSTALL.md) |
| Qdrant | Vektorindex für RAG und semantische Suche | Done | [ROADMAP](docs/ROADMAP.md) |
| Ollama (lokale LLMs) | Chat- und Embedding-Modelle lokal ausführen | In progress | [Architektur](docs/ARCHITECTURE.md) |
| Home Assistant Connector | Geräte, Szenen, Automationen aus Smart Home | Planned | [ROADMAP](docs/ROADMAP.md) |
| Exo-Cluster Setup | Verteiltes Setup (exo-node + Server) | Planned | [ROADMAP](docs/ROADMAP.md) |

## Architektur in 90 Sekunden
- **API-first:** Alle Kernfunktionen werden über klar definierte Endpunkte bereitgestellt.
- **Asynchroner Datenfluss:** Uploads laufen über Queue/Worker, damit UI und API reaktionsfähig bleiben.
- **RAG-Basis lokal:** Dokumente werden geparst, eingebettet und in Qdrant suchbar gemacht.
- **PEET als Assistenzschicht:** PEET nutzt strukturierte Daten + Vektorwissen für Hilfen im Dashboard.
- **Security-Baseline:** Secrets über `.env`, Reverse Proxy, minimierte Port-Freigaben.
- **Modular statt Monolith:** Services können einzeln erweitert oder ersetzt werden.

➡️ Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Screenshots / Mockups
Aktuell sind nur technische Mockups vorhanden. Finale UI-Screenshots folgen nach Dashboard-Stabilisierung.

- Platzhalter-Ordner: [docs/assets/](docs/assets/README.md)
- Beispiel-Mockup außerhalb der Doku: `SystemONE_MockUp.html`

## Projektstruktur (relevant für Bewertung)
```text
SystemONE/
├── README.md
├── INSTALL.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── GLOSSARY.md
│   ├── SECURITY.md
│   └── assets/
├── infra/
└── services/smartsortierer/
```

## Was ich gelernt habe (Ausbildungsbezug)
- Anforderungen in technische Module zu übersetzen (Planung vor Implementierung).
- APIs so zu strukturieren, dass Frontend und Worker sauber getrennt arbeiten.
- Hintergrundjobs mit Queue-Prinzip robuster zu gestalten als synchrone Verarbeitung.
- Datenmodellierung für Dokumenten-Workflows (Status, Metadaten, Audit).
- Lokale KI-Komponenten (Ollama + Qdrant) sinnvoll in einen Service-Stack einzubetten.
- Sicherheit nicht als Add-on, sondern als Baseline (Secrets, Logging, Zugriffskonzepte) zu behandeln.
- Docker Compose als reproduzierbare Entwicklungs- und Demo-Umgebung einzusetzen.
- Dokumentation so aufzubauen, dass auch fachfremde Prüfer den Stand schnell verstehen.
- Roadmaps in Phasen zu denken (stabil → nützlich → visionär), statt nur Feature-Listen zu pflegen.
- Technische Entscheidungen nachvollziehbar zu begründen (Trade-offs und Abhängigkeiten).

## Weiterführende Links
- [INSTALL](INSTALL.md)
- [ROADMAP](docs/ROADMAP.md)
- [SECURITY](docs/SECURITY.md)
- [ARCHITECTURE](docs/ARCHITECTURE.md)
- [CONTRIBUTING](CONTRIBUTING.md)
- [CHANGELOG](CHANGELOG.md)

## Lizenz
Dieses Projekt ist derzeit **proprietär (All rights reserved)**. Details siehe [LICENSE](LICENSE).
