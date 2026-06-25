# SystemONE MVP

Dieses Dokument begrenzt die erste baubare Version von SystemONE auf einen kleinen, testbaren Kern. Ziel ist nicht, alle Visionen gleichzeitig umzusetzen, sondern eine stabile Basis zu schaffen, die lokal gestartet, geprüft und später erweitert werden kann.

## MVP-Ziel

**SystemONE MVP = Dashboard + SmartSortierer-Grundfunktion + PEET-Grundpanel + Docker-Basis + lokale Datenablage.**

Der MVP gilt als erreicht, wenn ein Nutzer den Docker-Stack lokal starten kann, im Dashboard den Systemstatus sieht, ein Dokument in den SmartSortierer-Workflow geben kann und PEET als sichtbares Assistenzpanel mit klar definierten nächsten Integrationspunkten vorhanden ist.

## Muss-Funktionen

| Bereich | Muss im MVP enthalten sein | Abnahmekriterium |
|---|---|---|
| Docker-Basis | `infra/docker-compose.yml`, `.env.example`, Reverse Proxy, persistente Volumes | `docker compose config` ist valide und der Stack ist reproduzierbar startbar |
| Dashboard | Startseite mit Modul-Karten und Basisnavigation | Nutzer sieht Statusbereiche für Dashboard, SmartSortierer, PEET und Infrastruktur |
| SmartSortierer | API, Worker, Redis, PostgreSQL, Qdrant und Storage-Pfad | Upload-/Pipeline-Endpunkte sind dokumentiert und Services sind im Stack verbunden |
| PEET | sichtbares Chat-/Assistenzpanel als MVP-Platzhalter | UI zeigt PEET-Bereich und dokumentiert spätere API-Anbindung |
| Local-first Storage | lokale Standardablage plus optionaler NAS-Pfad | `.env.example` erlaubt lokalen Start ohne NAS-Zwang |
| Sicherheit | keine echten Secrets im Repo, Reverse Proxy als Einstiegspunkt | Secrets stehen nur als Platzhalter in `.env.example` |

## Nicht im MVP

Diese Punkte bleiben bewusst außerhalb der ersten baubaren Version:

- vollständige Home-Assistant-Steuerung mit echten Gerätebefehlen
- SafetyPi- und CamPi-Hardwareintegration
- produktionsreife Benutzerverwaltung/Rollenmodell
- automatisierte Backups mit Restore-Orchestrierung
- Exo-Cluster-Verteilung auf mehrere Geräte
- Voice Manager und physische LED-/Hardware-Dashboards

## Phase-1 Backlog

1. Docker-Konfiguration lokal ohne NAS-Abhängigkeit lauffähig machen.
2. Dashboard-Startseite mit klaren Modul-Karten stabilisieren.
3. SmartSortierer-End-to-End-Pfad dokumentieren: Upload, Queue, Worker, Embedding, Suche.
4. PEET-Panel als UI-Baustein sichtbar machen und API-Vertrag skizzieren.
5. Healthchecks und Troubleshooting in der Installationsdokumentation nachziehen.

## Phase-2 Backlog

1. Home-Assistant-Connector spezifizieren und zunächst read-only anbinden.
2. PEET mit RAG-Suche aus Qdrant verbinden.
3. BackupONE-Konzept als erstes Skript und Restore-Test beschreiben.
4. Monitoring-Ansicht für Service Health und Fehlerstatus ausbauen.
5. GitHub-Issues aus `docs/ISSUES.md` in echte Tickets übertragen.

## Definition of Done

Der MVP ist fertig, wenn:

- ein frischer Checkout mit `.env.example` vorbereitet werden kann,
- `docker compose config` im Ordner `infra/` ohne Fehler läuft,
- README, Installation und Roadmap auf den MVP verweisen,
- jedes Kernmodul einen Steckbrief besitzt,
- offene nächste Aufgaben als konkrete Issues formuliert sind.
