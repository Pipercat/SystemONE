# SystemONE Modul-Steckbriefe

Die Steckbriefe beschreiben pro Modul Zweck, MVP-Umfang, Schnittstellen, Datenquellen, Container, Ports, Abhängigkeiten, Sicherheitsrisiken und nächste Aufgaben.

## Dashboard

| Punkt | Inhalt |
|---|---|
| Zweck | Zentrale Oberfläche für Status, Navigation, Modul-Karten und PEET-Zugriff. |
| MVP-Funktionen | Startseite, Modul-Karten, einfache Health-/Statusanzeige, PEET-Panel-Platzhalter. |
| Schnittstellen | HTTP über NGINX, später API-Endpunkte unter `/api/`. |
| Datenquellen | API-Health, Service-Status, statische Modulmetadaten. |
| Docker-Container | `frontend`, `nginx`. |
| Ports | extern `80` über `NGINX_PORT`, intern Frontend `80`. |
| Abhängigkeiten | NGINX, API für dynamische Daten. |
| Sicherheitsrisiken | versehentlich direkt veröffentlichte interne Statusdaten, fehlende Authentifizierung bei späteren Schreibaktionen. |
| Nächste Aufgaben | Modul-Karten finalisieren, Healthdaten anbinden, PEET-Panel mit API-Vertrag verbinden. |

## SmartSortierer

| Punkt | Inhalt |
|---|---|
| Zweck | Dokumente aufnehmen, verarbeiten, klassifizieren und für Suche/RAG nutzbar machen. |
| MVP-Funktionen | Upload-/Dokumenten-API, Queue, Worker-Pipeline, Storage-Pfad, PostgreSQL-Metadaten, Qdrant-Index. |
| Schnittstellen | REST API unter `/api/`, Redis Queue, PostgreSQL, Qdrant, Ollama. |
| Datenquellen | Uploads, Dokumentmetadaten, extrahierter Text, Embeddings. |
| Docker-Container | `api`, `worker`, `postgres`, `redis`, `qdrant`, `ollama`. |
| Ports | intern API `8000`, PostgreSQL `5432`, Redis `6379`, Qdrant `6333`, Ollama `11434`; extern bevorzugt nur NGINX. |
| Abhängigkeiten | Storage, Datenbank, Redis, Qdrant, Ollama-Modell. |
| Sicherheitsrisiken | sensible Dokumentinhalte, unsichere Uploads, schwache API-Keys, fehlerhafte Dateirechte. |
| Nächste Aufgaben | End-to-End-Test dokumentieren, Uploadgrenzen prüfen, Audit-/Fehlerstatus sichtbar machen. |

## PEET

| Punkt | Inhalt |
|---|---|
| Zweck | Lokaler Assistent für Fragen, Systemhinweise und spätere Automationen. |
| MVP-Funktionen | sichtbarer Chat-/Assistenzbereich, definierter API-Vertrag, RAG-Integrationsplan. |
| Schnittstellen | Dashboard UI, spätere API-Endpunkte, Ollama, Qdrant. |
| Datenquellen | Systemstatus, Dokumentwissen, Roadmap-/Projektwissen. |
| Docker-Container | zunächst über `frontend`, `api`, `ollama`, `qdrant`; später eigener `peet-core` möglich. |
| Ports | keine eigene externe Freigabe im MVP. |
| Abhängigkeiten | lokale LLMs, Vektorindex, klare Berechtigungsregeln. |
| Sicherheitsrisiken | unbeabsichtigte Offenlegung privater Daten, unkontrollierte Automationen, Prompt-Injection über Dokumente. |
| Nächste Aufgaben | Chat-Endpunkt skizzieren, Tool-/Berechtigungsmodell festlegen, Read-only-Modus als Standard definieren. |

## Home Assistant Connector

| Punkt | Inhalt |
|---|---|
| Zweck | Smart-Home-Status lesen und später freigegebene Aktionen ausführen. |
| MVP-Funktionen | nicht im MVP; nur Konfigurationsplatzhalter und Sicherheitsregeln. |
| Schnittstellen | Home-Assistant-REST/WebSocket-API. |
| Datenquellen | Entitäten, Gerätestatus, Szenen, Automationen. |
| Docker-Container | noch keiner; spätere Integration über API oder separaten Connector. |
| Ports | Home Assistant typischerweise `8123` im lokalen Netz. |
| Abhängigkeiten | `HA_URL`, Long-lived Token, Domain-Allowlist. |
| Sicherheitsrisiken | zu breite Geräteberechtigungen, ungeprüfte Schaltbefehle, Token-Leak. |
| Nächste Aufgaben | read-only MVP definieren, erlaubte Domains dokumentieren, Bestätigungsmodus beibehalten. |

## BackupONE

| Punkt | Inhalt |
|---|---|
| Zweck | Daten, Konfiguration und Wissensspeicher wiederherstellbar sichern. |
| MVP-Funktionen | nicht als Automationsskript im MVP; Backupumfang dokumentieren. |
| Schnittstellen | Dateisystem, Docker Volumes, PostgreSQL-Dumps, Qdrant-Snapshots. |
| Datenquellen | `.env`, Storage, PostgreSQL, Qdrant, Projektkonfiguration. |
| Docker-Container | noch keiner. |
| Ports | keine. |
| Abhängigkeiten | definierte Backupziele, Speicherplatz, Restore-Testumgebung. |
| Sicherheitsrisiken | unverschlüsselte Secrets in Backups, nicht getestete Restore-Prozesse. |
| Nächste Aufgaben | erstes Backupskript planen, Restore-Checkliste erstellen, Secret-Handling klären. |
