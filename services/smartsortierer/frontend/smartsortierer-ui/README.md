# SmartSortierer UI

Das ist die Angular-basierte Web-Oberfläche für SmartSortierer. Hier können Dokumente hochgeladen und verwaltet werden.

## Setup

Die Dependencies sind bereits installiert. Um die App lokal zu entwickeln:

```bash
npm start
```

Die App lädt dann auf `http://localhost:4200`.

## Build

Für Production:

```bash
npm run build
```

Die fertigen Dateien landen in `dist/`.

## Tests

Unit-Tests mit Vitest:

```bash
npm test
```

## Struktur

- `src/app/pages/` - Verschiedene Seiten (upload, documents, review, rules)
- `src/app/components/` - Wiederverwendbare UI-Komponenten
- `src/app/services/` - API-Kommunikation
- `src/app/app.routes.ts` - Routing-Konfiguration

Die App nutzt Angular 21 mit standalone components.

```bash
ng e2e
```

Angular CLI does not come with an end-to-end testing framework by default. You can choose one that suits your needs.

## Additional Resources

For more information on using the Angular CLI, including detailed command references, visit the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.
