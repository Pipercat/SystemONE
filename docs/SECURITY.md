# SystemONE Security

## Sicherheitsziele
- Minimaler Angriffsvektor pro Service.
- Nachvollziehbare Zugriffe (Audit/Logs).
- Geheimnisse sicher verwalten (keine Hardcoded Keys).
- Sicherer externer Zugriff über Reverse Proxy statt Direktfreigaben.

## Baseline-Standards
1. **Secrets-Management:** Keys nur über `.env`/Secret-Store.
2. **Netzwerkprinzip:** Nur notwendige Ports öffnen; extern bevorzugt über Proxy/TLS.
3. **Least Privilege:** Container und Tokens mit minimalen Rechten.
4. **Auditierbarkeit:** Requests, Fehler und sicherheitsrelevante Events protokollieren.
5. **Backup & Restore:** Regelmäßig sichern und Wiederherstellung testen.

## Kurzcheck für den Betrieb
- API-Keys gesetzt und regelmäßig rotiert.
- `.env` nicht versioniert.
- Reverse Proxy aktiv und gehärtet.
- Logging zentral verfügbar.
- Abhängigkeiten regelmäßig aktualisiert.

## Nächste Security-Schritte
- Header-Härtung und Rate-Limits systemweit vereinheitlichen.
- Rollen-/Zugriffskonzept für Admin vs. Read-Only Nutzer schärfen.
- Incident-Runbook ergänzen.

## Verknüpfte Dokumente
- [INSTALL](../INSTALL.md)
- [ROADMAP](ROADMAP.md)
- [ARCHITECTURE](ARCHITECTURE.md)
