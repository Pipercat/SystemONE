# SystemONE Issue Backlog

Diese Liste ist als Vorlage für GitHub Issues gedacht. Jeder Eintrag ist klein genug, um einzeln umgesetzt und geprüft zu werden.

## Phase 1 – baubarer Kern

### [INFRA] Docker-Grundstruktur lokal startbar machen
- Ziel: Der Stack soll ohne NAS-Pflicht mit lokalem Storage starten.
- Ergebnis: `.env.example` enthält einen lokalen Host-Pfad und `infra/docker-compose.yml` nutzt diesen Pfad.
- Akzeptanz: `cd infra && docker compose config` läuft ohne Fehler.

### [DASHBOARD] Startseite mit Modul-Karten stabilisieren
- Ziel: Nutzer sieht die wichtigsten SystemONE-Module sofort.
- Ergebnis: Karten für Dashboard, SmartSortierer, PEET und Infrastruktur.
- Akzeptanz: Die Startseite ist über NGINX erreichbar und enthält klare Statusbereiche.

### [SMARTSORTIERER] End-to-End-Testpfad dokumentieren
- Ziel: Upload, Queue, Worker, Embedding und Suche nachvollziehbar machen.
- Ergebnis: Dokumentierter Testablauf mit erwarteten Logs und Statusübergängen.
- Akzeptanz: Ein frischer Nutzer kann die Pipeline anhand der Anleitung prüfen.

### [PEET] lokale LLM-Anbindung definieren
- Ziel: PEET bekommt einen klaren MVP-API-Vertrag.
- Ergebnis: Endpunktentwurf für Chat, Kontext und Quellenangaben.
- Akzeptanz: Frontend und API können unabhängig gegen den Vertrag entwickelt werden.

### [SECURITY] Secret- und Zugriffsbasis härten
- Ziel: Keine echten Tokens im Repo und klare Freigaberegeln.
- Ergebnis: Checkliste für `.env`, API-Key-Rotation und Reverse-Proxy-Zugriff.
- Akzeptanz: Security-Doku nennt konkrete Mindestanforderungen für lokalen Betrieb.

## Phase 2 – nützliche Integrationen

### [HOMEASSISTANT] Read-only Connector planen
- Ziel: Home-Assistant-Status sicher anzeigen, ohne Geräte zu schalten.
- Ergebnis: Entitätenliste, Token-Regeln und erlaubte Domains.
- Akzeptanz: Schreibaktionen sind im ersten Schritt technisch deaktiviert.

### [BACKUPONE] Backupstrategie als erstes Skript planen
- Ziel: Wichtige Datenquellen reproduzierbar sichern.
- Ergebnis: Liste der Backupquellen und Restore-Checkliste.
- Akzeptanz: Mindestens PostgreSQL, Qdrant, Storage und `.env` sind abgedeckt.

### [MONITORING] Service-Health im Dashboard visualisieren
- Ziel: Nutzer erkennt, welche Container gesund sind.
- Ergebnis: Health-Status für API, Worker, Redis, Postgres, Qdrant und Ollama.
- Akzeptanz: Fehlerzustände werden sichtbar und mit Troubleshooting-Hinweisen verknüpft.
