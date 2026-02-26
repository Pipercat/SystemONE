# Contributing

Danke für Beiträge zu SystemONE.

## Branching
- `main`: stabiler Stand.
- Feature-Arbeit in eigenen Branches, z. B. `docs/readme-refresh` oder `feat/worker-retry`.

## Commit-Standard
- Kleine, nachvollziehbare Commits.
- Präfix empfohlen: `docs:`, `feat:`, `fix:`, `chore:`.
- Beispiel: `docs: align roadmap phases with architecture`

## Doku-Standards
- Begriffskonsistenz: **SystemONE**, **PEET**, **SmartSortierer**.
- Kurze Abschnitte, Tabellen/Bullets statt Fließtext.
- Dokumente gegenseitig verlinken (README, INSTALL, ROADMAP, ARCHITECTURE, SECURITY).

## Sicherheit
- Keine Secrets, Tokens oder private Hostpfade committen.
- `.env` bleibt lokal; nur `.env.example` versionieren.

## Ideen festhalten
- Wenn möglich als GitHub Issue mit Template: *Problem → Vorschlag → Nutzen → Aufwand*.
- Falls Issues nicht genutzt werden: Eintrag in `docs/IDEAS.md` und bei Reife in `docs/ROADMAP.md` übernehmen.
