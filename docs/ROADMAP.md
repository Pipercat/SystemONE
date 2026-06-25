# SystemONE Roadmap

Diese Roadmap ist die **bewertungsreife Planungsansicht** (Status + Nutzen + Aufwand). Brainstorming-Ideen stehen optional in `docs/IDEAS.md`.

## Phasenmodell
- **P0 – stabil:** Kernstack zuverlässig und nachvollziehbar betreiben.
- **P1 – nützlich:** Funktionen mit direktem Alltagsnutzen liefern.
- **P2 – nice:** UX, Integrationen und Produktreife erhöhen.
- **P3 – vision:** Erweiterungen mit Forschungs-/Prototyp-Charakter.

## Priorisierte Roadmap

| Phase | Idee | Beschreibung | Nutzen | Aufwand | Abhängigkeiten | Status |
|---|---|---|---|---|---|---|
| P0 | SmartSortierer-Pipeline | Dokumente ingest → OCR/Parsing → Embeddings → Qdrant → Suche | Kern-Mehrwert für Dokumentwissen | M | API, Worker, Qdrant, Ollama | In progress |
| P0 | Worker-Service | Queue/Redis-basierte Background-Jobs mit Status-Tracking und Logs | Stabilität und Nachvollziehbarkeit | M | Redis, DB, API-Endpunkte | Done |
| P0 | Security-Basics | Secrets/Rotation, Reverse Proxy, Zugriffskonzepte, Audit/Hardening | Sichere Demo- und Betriebsbasis | M | NGINX/Proxy, Logging, Rollenmodell | In progress |
| P1 | PEET Chat-Panel | KI-Assistent im Dashboard mit Chat | Schnellere Bedienung und Hilfestellung | M | UI, API, Ollama | Planned |
| P1 | PEET-Folder Kontext | Eigener Bereich mit dynamischen Kontextinfos (Status, Prioritäten, Hinweise) | Bessere Orientierung im System | M | PEET, Event-/Statusdaten | Planned |
| P1 | RAG-Wissensdatenbank | Qdrant als Vektor-DB + lokale LLMs via Ollama | Präzise Suche über eigene Dokumente | M | Pipeline, Embeddings, Retrieval API | In progress |
| P1 | Home Assistant Integration | Gerätebefehle, Status und einfache Automationen | Direkter Smart-Home-Mehrwert | M | HA-API, Auth, Freigaberegeln | Planned |
| P2 | Interaktive Dashboard-Visualisierungen | HTML/CSS/JS-Visuals für Architekturmap und Systemstatus | Bessere Übersicht für Nutzer/Prüfer | S | Frontend-Komponenten, Healthdaten | Planned |
| P2 | UI-Design Standard | SmartSortierer Dark + konsistente Design Tokens | Einheitliches, professionelles Erscheinungsbild | S | UI-Styleguide, Komponentenpflege | Planned |
| P2 | Memory System | Langfristiges Speichern strukturierter Infos (privacy/local-first) | Nachhaltige Assistenz und Verlauf | L | Datenmodell, Policies, PEET | Planned |
| P3 | Exo-Cluster Architektur | Mac mini als exo-node (UI/light) + Intel Mini-PC als Server (heavy) | Skalierung ohne Cloud-Zwang | L | Netzwerkdesign, Deploymentprofile | Planned |
| P3 | LED-Matrix / Physical Dashboard | Physische Statusanzeige (optional) | Lern- und Demoeffekt | M | API/Events, Hardware-Schnittstelle | Vision |

## Nächste 5 Schritte (Mini-Backlog)
1. MVP-Scope anhand von `docs/MVP.md` als erste baubare Version abschließen.
2. End-to-End Testpfad für SmartSortierer dokumentieren und stabilisieren.
3. PEET Chat-Panel als MVP im Dashboard sichtbar machen.
4. Security-Baseline vereinheitlichen (Key-Rotation + Reverse-Proxy-Standard).
5. Architekturstatus im Dashboard visualisieren (Service Health + Datenfluss).

## Verknüpfte Dokumente
- [README](../README.md)
- [INSTALL](../INSTALL.md)
- [MVP](MVP.md)
- [ARCHITECTURE](ARCHITECTURE.md)
- [MODULE_STECKBRIEFE](MODULE_STECKBRIEFE.md)
- [ISSUES](ISSUES.md)
- [SECURITY](SECURITY.md)
- [CHANGELOG](../CHANGELOG.md)
