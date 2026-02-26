# SystemONE Architecture

## Zielbild
SystemONE verfolgt ein **local-first**, **privacy-orientiertes** und **modulares** Architekturziel. Jeder Service hat eine klare Aufgabe, ist austauschbar und über definierte Schnittstellen angebunden.

## Komponentenübersicht

| Komponente | Rolle |
|---|---|
| UI / Dashboard | Bedienung, Statusansicht, PEET-Interaktion |
| API (FastAPI) | Zentrale Schnittstelle für Uploads, Metadaten, Steuerung |
| Worker | Asynchrone Verarbeitung (Extract, Chunk, Embed, Klassifikation) |
| PostgreSQL | Strukturierte Fach- und Prozessdaten |
| Redis | Queue für Background-Jobs |
| Qdrant | Vektorindex für semantische Suche (RAG) |
| Ollama | Lokale LLMs und Embeddings |
| Reverse Proxy (NGINX) | Entry Point, Routing, Zugriffshärtung |

## Datenflüsse in Textform
1. Nutzer lädt Dokument über UI/API hoch.
2. API speichert Datei in `SS_STORAGE_ROOT` und legt Metadaten in PostgreSQL an.
3. API sendet Job in Redis Queue.
4. Worker holt Job, führt OCR/Parsing und Chunking aus.
5. Worker erzeugt Embeddings über Ollama.
6. Embeddings + Referenzen werden in Qdrant gespeichert.
7. Suchanfragen laufen über API (keyword + semantisch) und liefern Ergebnis an UI/PEET zurück.

## Wie Services kommunizieren
- **UI ↔ API:** HTTP/JSON-Endpunkte.
- **API ↔ Worker:** Entkoppelt über Redis-Queue und Statusdatenbank.
- **API/Worker ↔ DB:** Persistenz von Dokument-, Job- und Auditdaten in PostgreSQL.
- **Worker ↔ Qdrant:** Schreiben/Lesen von Vektor-Daten für RAG.
- **API/Worker ↔ Ollama:** Lokale Modellaufrufe für Klassifikation/Embeddings.
- **API ↔ UI:** Rückgabe von Dokumentstatus, Suche, Health und PEET-Antworten.

## Warum diese Technik (kurz)
- **FastAPI:** Schnell für saubere, dokumentierte REST-APIs.
- **Redis:** Einfaches, robustes Queue-Muster für asynchrone Jobs.
- **PostgreSQL:** Verlässliche relationale Basis für Status und Fachdaten.
- **Qdrant:** Speziell für performante Vektorsuche geeignet.
- **Ollama:** Lokale KI-Ausführung ohne Cloud-Zwang.
- **Docker Compose:** Reproduzierbare Umgebung für Entwicklung und Abnahme.
- **NGINX:** Klarer Entry Point mit Security- und Routing-Kontrolle.

## Future Architecture (Exo-Idee)
- **Exo-node (Mac mini):** UI, leichte Assistenz-Tasks, Dashboard-nahe Dienste.
- **Server (Intel Mini-PC):** Schwere Services (Worker, Qdrant, Ollama, Datenbanken).
- **Nutzen:** Bessere Lastverteilung, klare Rollen, schrittweise Skalierung ohne Komplettumbau.

## Verknüpfte Dokumente
- [README](../README.md)
- [INSTALL](../INSTALL.md)
- [ROADMAP](ROADMAP.md)
- [GLOSSARY](GLOSSARY.md)
- [SECURITY](SECURITY.md)
