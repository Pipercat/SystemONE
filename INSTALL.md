# SystemONE - Installationsanleitung

## Schnellstart

### 1. Voraussetzungen prüfen

```bash
docker --version    # Min. 20.x
docker compose version  # Min. 2.x
free -h            # Min. 8GB RAM empfohlen
df -h              # Min. 20GB freier Speicher
```

### 2. Repository klonen

```bash
git clone https://github.com/Pipercat/SystemONE.git
cd SystemONE
```

### 3. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
nano .env
```

**Wichtige Einstellungen in .env:**

```bash
# === API Security ===
SS_API_KEY=your-secure-api-key-here-change-me

# === Storage ===
STORAGE_PATH=/path/to/your/storage  # Absoluter Pfad!

# === PostgreSQL ===
POSTGRES_PASSWORD=change-this-password
POSTGRES_USER=ssuser
POSTGRES_DB=smartsortierer

# === Ollama ===
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3.2:3b

# === Qdrant ===
QDRANT_API_KEY=change-this-qdrant-key
```

### 4. Docker Stack starten

```bash
cd infra
docker compose up -d --build
```

**Dienste werden gestartet:**
- `nginx` - Reverse Proxy (Port 80)
- `api` - FastAPI Backend
- `worker` - Background Jobs
- `postgres` - Datenbank
- `redis` - Queue
- `qdrant` - Vector-DB
- `ollama` - LLM Engine

### 5. Ollama Modelle installieren

```bash
# LLM für Klassifikation & Chat
docker compose exec ollama ollama pull llama3.2:3b

# Embedding Model für Vector-Search
docker compose exec ollama ollama pull nomic-embed-text
```

⏱️ **Hinweis:** Das erste Pullen kann 5-15 Minuten dauern (je nach Internetverbindung)

### 6. System testen

**Services überprüfen:**
```bash
docker compose ps
```

Alle Services sollten Status `running` haben.

**API Test:**
```bash
curl -H "x-ss-api-key: your-secure-api-key-here-change-me" \
  http://localhost/api/health
```

Erwartete Antwort: `{"status": "ok"}`

**Web-Interfaces öffnen:**
- Dashboard: http://localhost
- API Dokumentation: http://localhost/api/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

### 7. Ersten Upload testen

```bash
# Test-PDF erstellen (oder eigene Datei verwenden)
echo "Test Dokument" > test.txt

# Upload
curl -X POST \
  -F "file=@test.txt" \
  -H "x-ss-api-key: your-secure-api-key-here-change-me" \
  http://localhost/api/files/upload?path=00_inbox

# Verarbeitung triggern
curl -X POST \
  -H "x-ss-api-key: your-secure-api-key-here-change-me" \
  -H "Content-Type: application/json" \
  -d '{"inbox_path":"00_inbox/test.txt"}' \
  http://localhost/api/docs/ingest

# Status prüfen (nach ~10 Sekunden)
curl -H "x-ss-api-key: your-secure-api-key-here-change-me" \
  http://localhost/api/docs/list
```

## Storage-Struktur

Nach dem ersten Start wird folgende Ordnerstruktur angelegt:

```
$STORAGE_PATH/
├── 00_inbox/        # Neue Uploads
├── 01_ingested/     # Verarbeitete Dateien (SHA256 Namen)
├── 02_staging/      # Zwischenspeicher
├── 03_sorted/       # Kategorisierte Dokumente
├── 04_archive/      # Archivierte Dateien
└── 99_errors/       # Fehlerhafte Dateien
```

## Troubleshooting

### Container startet nicht

```bash
# Logs anschauen
docker compose logs -f api
docker compose logs -f worker

# Service neu starten
docker compose restart api
```

### Ollama Modell fehlt

```bash
# Verfügbare Modelle prüfen
docker compose exec ollama ollama list

# Modell neu laden
docker compose exec ollama ollama pull llama3.2:3b
```

### PostgreSQL Verbindungsfehler

```bash
# Datenbank-Status prüfen
docker compose exec postgres pg_isready -U ssuser

# Datenbank-Shell öffnen
docker compose exec postgres psql -U ssuser -d smartsortierer

# Tabellen anzeigen
\dt
```

### Qdrant Verbindungsfehler

```bash
# Qdrant Status prüfen
curl http://localhost:6333/collections

# Qdrant neu starten
docker compose restart qdrant
```

### Speicherplatz voll

```bash
# Docker Ressourcen aufräumen
docker system prune -a --volumes

# Alte Images entfernen
docker image prune -a
```

## Wartung

### Backup erstellen

```bash
# PostgreSQL Backup
docker compose exec postgres pg_dump -U ssuser smartsortierer > backup.sql

# Storage Backup
tar -czf storage_backup.tar.gz $STORAGE_PATH
```

### Updates einspielen

```bash
cd SystemONE
git pull

cd infra
docker compose down
docker compose up -d --build
```

### Logs rotieren

```bash
# Logs ansehen
docker compose logs --tail=100 api

# Alte Logs löschen
docker compose down
docker system prune --volumes
docker compose up -d
```

## Sicherheit

⚠️ **Vor Produktiveinsatz:**

1. ✅ Alle Passwörter in `.env` ändern
2. ✅ Starke API-Keys verwenden (min. 32 Zeichen)
3. ✅ HTTPS mit Let's Encrypt einrichten (Nginx Konfiguration anpassen)
4. ✅ Firewall konfigurieren (nur Port 80/443 öffnen)
5. ✅ Regelmäßige Backups einrichten
6. ✅ Audit-Logs regelmäßig prüfen

## Weiterführende Dokumentation

- [SmartSortierer Details](services/smartsortierer/README.md)
- [API Dokumentation](http://localhost/api/docs) (nach Start)
- [Docker Compose Referenz](infra/docker-compose.yml)

## Support

Bei Problemen:
1. Logs prüfen: `docker compose logs -f`
2. Container-Status: `docker compose ps`
3. Issues auf GitHub: https://github.com/Pipercat/SystemONE/issues
