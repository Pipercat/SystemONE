# SystemONE Architektur

## Denkmodell: System statt Einzelprojekt

SystemONE wird als **lokales Ökosystem** aufgebaut. Fokus ist nicht nur Anwendungscode, sondern das Zusammenspiel aus:

1. **Infrastruktur** (Docker, Netzwerk, Reverse Proxy)
2. **Daten** (NAS, Qdrant, Logs, Persistenz)
3. **Intelligenz** (PEET, Ollama, RAG)
4. **Interface** (Dashboard, Module, Statusanzeigen)
5. **Automation** (Tasks, Workflows, Smart Home)

## Layered Architecture

```text
[Interface Layer]
  Dashboard / Module UIs / Control Panels

[Application Layer]
  API / Worker / PEET Logic / Integrationen

[Intelligence Layer]
  Ollama / Embeddings / RAG / Agent Memory

[Data Layer]
  PostgreSQL / Redis / Qdrant / NAS Filesystem

[Infrastructure Layer]
  Docker Compose / NGINX / Cloudflare Tunnel / Host OS
```

## Hauptprinzipien

- **Single Responsibility pro Service**: Jeder Container hat eine klar abgegrenzte Aufgabe.
- **API-first**: Module kommunizieren über definierte Schnittstellen.
- **Local-first AI**: Modelle und Vektor-Suche laufen primär lokal.
- **Observability by default**: Logs, Healthchecks und Status-Endpoints sind Pflicht.
- **Secure-by-default**: API Keys, TLS-Terminierung, minimale Port-Exposition.

## Service-Topologie (Zielbild)

```text
Internet
  |
Cloudflare Tunnel
  |
NGINX Reverse Proxy
  |
+-- systemone-dashboard
+-- systemone-api
+-- systemone-worker
+-- peet-core
+-- qdrant
+-- redis
+-- ollama
+-- home-assistant-connector
```

## Decision Log (leichtgewichtig)

Für Architekturentscheidungen wird pro Entscheidung ein kurzer Eintrag gepflegt:

- **Kontext**: Warum ist die Entscheidung nötig?
- **Entscheidung**: Was wird konkret umgesetzt?
- **Konsequenzen**: Vorteile, Nachteile, Risiken.
- **Status**: proposed / accepted / deprecated.

Empfohlenes Format: `docs/adr/ADR-XXXX-<titel>.md`.
