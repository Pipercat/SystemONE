# Gridfinity Browser-Generator (Browser-only)

Diese kleine Web-App erzeugt Gridfinity-Boxen (`Bin`) und `Baseplate`-Modelle komplett im Browser mit Three.js und ermöglicht den direkten STL-Export.

Voraussetzungen
- Moderner Browser (Chrome, Edge, Firefox)

Schnellstart
1. Lokale Dateien öffnen: Doppelklick `index.html` (manche Browser blockieren lokale Module).
2. Empfohlen: Starte einen einfachen Server im Ordner und öffne `http://localhost:8000`:

```powershell
# Windows / PowerShell
python -m http.server 8000
# dann öffnen: http://localhost:8000
```

Benutzung
- Wähle "Box" oder "Baseplate", stelle X/Y/(Z) Werte ein und klicke "Vorschau aktualisieren".
- Klicke "STL herunterladen" um die aktuelle Vorschau als STL-Datei zu speichern.

Nächste Schritte
- Feinere Geometrie (Innenwände, Snap-Features) hinzufügen.
- Integration mit Web-OpenSCAD für parametrisiertere Exporte.
- Presets und Druckfreundliche Exportoptionen.

Lizenz: MIT (frei nutzbar)
