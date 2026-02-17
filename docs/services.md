# SystemONE Services

## Microservice Thinking

Jeder Dienst ist ein eigenständiger Container mit:

- klarer Verantwortung
- eigener Konfiguration (ENV)
- eigenem Logging
- Healthcheck/Statusendpoint

## Kern-Services

### `systemone-api`
- Zentrale API für Dashboard und Module
- Authentifizierung, Routing, Geschäftslogik

### `systemone-worker`
- Asynchrone Jobs (z. B. Datei- und KI-Pipelines)
- Queue-basierte Verarbeitung

### `peet-core`
- Agent-Logik von PEET
- Kontextverarbeitung, Task-Vorschläge, Automationen

### `qdrant`
- Vektor-Datenbank für Embeddings
- RAG-Suche für Dokumente und Wissensbasis

### `redis`
- Queue/Cache/ephemere Zustände
- Broker für Worker-Prozesse

### `ollama`
- Lokale LLM- und Embedding-Inferenz
- Kernkomponente für AI-Funktionen ohne Cloud-Zwang

### `nginx`
- Reverse Proxy
- zentrale Entry-Points und Header-/Security-Policies

## PEET Memory-Struktur (Ziel)

```text
/data/peet-memory/
  |- logs/
  |- chats/
  |- tasks/
  |- knowledge/
```

## Service-Checkliste

Für jeden neuen Service:

1. Zweck in 1 Satz definieren.
2. ENV-Variablen dokumentieren.
3. Persistente Volumes benennen.
4. Healthcheck bereitstellen.
5. Logs über `docker compose logs -f <service>` verifizierbar machen.
