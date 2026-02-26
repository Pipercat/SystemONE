# SystemONE – Installation & Betrieb

Diese Anleitung ist auf **reproduzierbaren Local-Betrieb mit Docker Compose** ausgelegt. NAS oder Spezialhardware sind optional.

## 1) Voraussetzungen

| Bereich | Minimum | Empfehlung | Hinweise |
|---|---|---|---|
| Betriebssystem | Linux, macOS, Windows (WSL2) | Aktuelle LTS-Version | Docker muss stabil laufen |
| Docker Engine | 24.x | Neueste stabile Version | `docker --version` |
| Docker Compose | v2.x | Neueste stabile Version | `docker compose version` |
| RAM | 8 GB | 16 GB+ | LLM/Embedding profitieren stark |
| Speicher | 20 GB frei | 50 GB+ | Für Modelle + Dokumente |
| Offene Ports | 80, 5432, 6379, 6333, 8000, 11434 | nur intern freigeben | Reverse Proxy später bevorzugen |

## 2) Konfiguration (.env)

```bash
cp .env.example .env
```

Wichtige Variablen aus `.env.example`:

| Variable | Zweck | Beispiel |
|---|---|---|
| `SS_API_KEY` | API-Zugriffsschutz für SmartSortierer-Endpunkte | `replace-with-long-random-key` |
| `SS_SECRET_KEY` | Interne Signierung/Secrets | `replace-with-second-random-key` |
| `SS_STORAGE_ROOT` | Basisordner für Dokumentablage | `./data/storage` (lokal) |
| `POSTGRES_*` | Datenbank-Verbindung für API/Worker | `POSTGRES_DB=smartsortierer` |
| `REDIS_*` | Queue/Background-Jobs | `REDIS_HOST=redis` |
| `QDRANT_*` | Vektorsuche/RAG-Index | `QDRANT_COLLECTION=smartsortierer_docs` |
| `OLLAMA_*` | Lokale KI-Modelle (Chat + Embedding) | `OLLAMA_MODEL_CHAT=llama3.2:3b` |
| `HA_*` | Optionale Home Assistant Integration | `HA_ENABLED=false` |
| `N8N_*` | Optionale Automationsumgebung | `N8N_ENABLED=false` |

**Wichtig:** Keine echten Keys oder Tokens in Git committen.

## 3) Erster Start (Schritt für Schritt)

1. Repository klonen:
   ```bash
   git clone https://github.com/Pipercat/SystemONE.git
   cd SystemONE
   ```
2. Konfiguration vorbereiten:
   ```bash
   cp .env.example .env
   ```
3. Optional lokale Storage-Ordner anlegen:
   ```bash
   mkdir -p data/storage
   ```
4. Stack starten:
   ```bash
   cd infra
   docker compose up -d --build
   ```
5. Status prüfen:
   ```bash
   docker compose ps
   docker compose logs --tail=100
   ```
6. Oberfläche öffnen:
   - `http://localhost`
   - `http://localhost/api/docs`

## 4) Troubleshooting (typische Fehlerbilder)

### Problem: Port bereits belegt
**Symptom:** `bind: address already in use` in Docker-Logs.

**Lösung:**
- Belegten Port identifizieren (`ss -ltnp` oder Docker Desktop Port-Ansicht).
- Port-Mapping in `infra/docker-compose.yml` anpassen.
- Stack neu starten (`docker compose down && docker compose up -d`).

### Problem: Container ist `unhealthy`
**Symptom:** `docker compose ps` zeigt `unhealthy`.

**Lösung:**
- Logs des betroffenen Dienstes prüfen (`docker compose logs <service>`).
- Prüfen, ob abhängige Dienste laufen (z. B. API benötigt Postgres/Redis).
- Bei Modellproblemen: Ollama starten und Modelle nachziehen.

### Problem: Volumes/Storage fehlen
**Symptom:** Uploads schlagen fehl, Pfade nicht auffindbar.

**Lösung:**
- `SS_STORAGE_ROOT` auf existierenden Pfad setzen.
- Schreibrechte prüfen (`chown/chmod` je nach OS).
- Bei NAS-Pfaden zuerst mit lokalem Testpfad starten.

## 5) Update, Wartung, Backup (kurz & realistisch)

- **Update:**
  ```bash
  git pull
  cd infra
  docker compose pull
  docker compose up -d --build
  ```
- **Wartung:** regelmäßig alte Images/Volumes prüfen (`docker system df`).
- **Backup-Konzept:**
  - Muss gesichert werden: PostgreSQL-Daten, Qdrant-Daten, `SS_STORAGE_ROOT`, `.env`.
  - Praxisnah: tägliches Dateibackup + regelmäßiger Restore-Test in Testumgebung.

## 6) Sicherer Betrieb (Mini-Checkliste)

- Secrets nur in `.env` oder Secret-Store verwalten.
- Öffentliche Exposition nur über Reverse Proxy (TLS) statt Direktports.
- API-Keys regelmäßig rotieren.
- Logs zentral prüfen (Fehler, Zugriffe, ungewöhnliche Muster).
- Details: [docs/SECURITY.md](docs/SECURITY.md)
