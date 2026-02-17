# SystemONE Security

## Sicherheitsziele

- Minimale Angriffsfläche
- Nachvollziehbarkeit durch Logging/Audit
- Sichere Secrets-Verwaltung
- Sichere Remote-Erreichbarkeit ohne offene Einzelports

## Bestehende Grundlagen

- SSH Hardening
- Fail2Ban
- Firewall-Regeln

## Security-Baseline für Services

1. **Secrets nur per ENV / Secret-Store**
   - keine API Keys im Code
   - `.env` nicht committen
2. **TLS über Cloudflare Tunnel/Proxy**
   - HTTPS erzwingen
3. **Least Privilege**
   - Container mit minimalen Rechten
   - nur notwendige Ports freigeben
4. **Audit Trail**
   - API-Aufrufe, Fehler, sicherheitsrelevante Events protokollieren
5. **Backups & Restore-Proben**
   - regelmäßige Backup-Jobs
   - dokumentierte Restore-Tests

## Mindest-Logging

- Request-ID / Correlation-ID
- Timestamp
- Nutzer/Token-Kontext (anonymisiert, falls nötig)
- Service-Name
- Aktion + Ergebnis (success/fail)

## Security-Roadmap

- [ ] Secrets-Management vereinheitlichen
- [ ] Endpunkt-Härtung (Rate Limits, Header Policies)
- [ ] Regelmäßige Dependency-Scans
- [ ] Audit-Views im Dashboard
- [ ] Incident-Runbook in `docs/` ergänzen
