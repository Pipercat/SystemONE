# 🎨 SmartSorter UI Design Specification

**Version**: 1.0  
**Target**: Angular PWA Frontend (Phase 10)  
**Style**: Dark Tech Dashboard (Proxmox/Synology/GitHub Dark inspired)

---

## 1. Design-Philosophie

### Ziel
Modernes, technisches, ruhiges Dark-Dashboard  
→ Mischung aus Apple / Proxmox / GitHub / Enterprise-Dashboards

### Charakter
- ✅ Seriös
- ✅ Clean
- ✅ „High-Tech"
- ❌ Nicht verspielt
- ❌ Nicht bunt
- ✅ Fokus auf Daten

---

## 2. Farbpalette (Fix vorgegeben)

### 2.1 Hauptfarben
```css
--bg: #0b1220;        /* Haupt-Hintergrund */
--panel: #0f1a2b;     /* Panels */
--panel2: #0c1626;    /* Sidebar */
--card: #111f34;      /* Cards */
```

### 2.2 Textfarben
```css
--text: #e7f0ff;      /* Haupttext */
--muted: #8ea4c3;     /* Sekundärtext */
```

### 2.3 Akzentfarben
```css
--accent: #4da3ff;    /* Blau (Primary Actions) */
--accent2: #9b7bff;   /* Violett (Secondary) */
```

### 2.4 Statusfarben
```css
--good: #3ddc97;      /* Erfolg / Grün */
--warn: #ffcc66;      /* Warnung / Gelb */
--bad: #ff6b6b;       /* Fehler / Rot */
```

### 2.5 Linien / Rahmen
```css
--line: rgba(255,255,255,.08);  /* Subtile Trennlinien */
```

---

## 3. Formen & Rundungen

### 3.1 Standard-Radius
```css
--radius: 18px;   /* Standard für Panels */
--radius2: 24px;  /* Größere Cards */
```

### 3.2 Element-spezifische Rundungen

| Element | Radius | Verwendung |
|---------|--------|------------|
| Button | `16px` | Alle Buttons |
| Card | `24px` | KPI-Cards, Info-Cards |
| Panel | `24px` | Tables, Settings, Logs |
| Input | `16px` | Text-Inputs, Selects |
| Badge | `999px` | Pills (Status, Tags) |

**Regel**: Alles ist abgerundet, **keine harten Ecken**.

---

## 4. Schatten (Depth-System)

```css
--shadow: 0 10px 30px rgba(0,0,0,.35);
```

### Anwendung
- Jede **Card**
- Jedes **Panel**
- Jede **Floating-Komponente**
- Modals, Dropdowns

**Regel**: Keine flachen Flächen. Schatten erzeugen Tiefe.

---

## 5. Typografie

### 5.1 Schrift
```css
font-family:
  ui-sans-serif,
  system-ui,
  "Segoe UI",
  Roboto,
  "Helvetica Neue",
  Arial,
  sans-serif;
```

**Kein Custom-Font nötig.** System-Fonts für Performance.

### 5.2 Größen

| Element | Größe | Gewicht |
|---------|-------|---------|
| H1 | `14px` | `600` |
| H2 | `14px` | `600` |
| Body Text | `13–14px` | `400` |
| Meta / Small | `12px` | `400` |
| Badges | `11px` | `500` |

**Regel**: Kompakt, professionell. Keine riesigen Headlines.

---

## 6. Layout-System

### 6.1 Grid Structure

```
┌─────────────┬──────────────────────────────┐
│   Sidebar   │        Main Content         │
│   280px     │           1fr               │
│             │                              │
│   Nav       │  ┌──────────┬──────────┐   │
│   Items     │  │  Card 1  │  Card 2  │   │
│             │  └──────────┴──────────┘   │
│             │  ┌────────────────────┐     │
│             │  │   Table Panel      │     │
│             │  └────────────────────┘     │
└─────────────┴──────────────────────────────┘
```

**CSS:**
```css
.layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 0;
  height: 100vh;
}

.content {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 16px;
  padding: 22px;
}
```

### 6.2 Spacing-Regeln

| Typ | Wert | Verwendung |
|-----|------|------------|
| Card Gap | `12px` | Zwischen Cards in einer Reihe |
| Panel Gap | `16px` | Zwischen Panels vertikal |
| Content Padding | `14–18px` | Innerhalb Cards/Panels |
| Section Gap | `22px` | Zwischen großen Bereichen |

**Regel**: Alles ist „luftig", nicht gedrängt.

---

## 7. UI-Komponenten-Design

### 7.1 Cards (KPIs)

**Eigenschaften:**
- Verlauf: oben hell → unten dunkel
- Shadow
- Große Zahl + kleines Label
- Optional: Sparkline Animation

**CSS:**
```css
.card {
  background: linear-gradient(180deg, 
    rgba(255,255,255,.05), 
    rgba(255,255,255,.02)
  );
  border-radius: var(--radius2);
  padding: 18px;
  box-shadow: var(--shadow);
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}
```

**Beispiel:**
```
┌──────────────────────┐
│  Documents           │
│  1,234               │  ← Große Zahl
│  ▁▃▅▇ (Sparkline)   │
└──────────────────────┘
```

### 7.2 Panels (Tables, Logs, Settings)

**Eigenschaften:**
- Border 1px semi-transparent
- Shadow
- Header + Content Trennung

**CSS:**
```css
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.panel-header {
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-content {
  padding: 18px;
}
```

### 7.3 Buttons

**Primary Button:**
```css
.btn-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: white;
  padding: 10px 18px;
  border-radius: 16px;
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: filter 0.15s ease;
}

.btn-primary:hover {
  filter: brightness(1.1);
}
```

**Secondary Button:**
```css
.btn-secondary {
  background: rgba(255,255,255,.08);
  color: var(--text);
  padding: 10px 18px;
  border-radius: 16px;
  border: 1px solid var(--line);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-secondary:hover {
  background: rgba(255,255,255,.12);
}
```

**Regel**: Kein Flat-Design. Immer Gradient oder Glas-Effekt.

### 7.4 Badges / Chips

**CSS:**
```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.5;
}

.badge-success {
  background: rgba(61, 220, 151, 0.15);
  color: var(--good);
  border: 1px solid rgba(61, 220, 151, 0.3);
}

.badge-warning {
  background: rgba(255, 204, 102, 0.15);
  color: var(--warn);
  border: 1px solid rgba(255, 204, 102, 0.3);
}

.badge-error {
  background: rgba(255, 107, 107, 0.15);
  color: var(--bad);
  border: 1px solid rgba(255, 107, 107, 0.3);
}
```

**Verwendung:**
- Dokument-Status (INGESTED, ANALYZED, etc.)
- Filter-Chips
- Tags

### 7.5 Switches (iOS-Style)

**CSS:**
```css
.switch {
  position: relative;
  width: 44px;
  height: 24px;
  background: rgba(255,255,255,.12);
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.switch.active {
  background: var(--accent);
}

.switch-handle {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s ease;
}

.switch.active .switch-handle {
  transform: translateX(20px);
}
```

### 7.6 Inputs

**CSS:**
```css
.input {
  background: rgba(255,255,255,.05);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 10px 14px;
  color: var(--text);
  font-size: 13px;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.input:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(255,255,255,.08);
}

.input::placeholder {
  color: var(--muted);
}
```

---

## 8. Animationen

### 8.1 Pflichtanimationen

| Typ | Zweck | Dauer | Easing |
|-----|-------|-------|--------|
| **Shine** | Logo-Effekt | 2s | ease-in-out |
| **Sweep** | Sparklines | 1.5s | ease |
| **Hover** | Buttons, Cards | 0.15s | ease |
| **Toast** | Notifications | 0.25s | ease |
| **Load-Pulse** | Pipeline Status | 1s | ease-in-out |

**Regel**: Keine harten Transitions. Alles soft.

### 8.2 Standard-Transition
```css
transition: 0.15s–0.25s ease;
```

### 8.3 Shine Effect (Logo)
```css
@keyframes shine {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.logo {
  animation: shine 2s ease-in-out infinite;
}
```

### 8.4 Sparkline Sweep
```css
@keyframes sweep {
  from { stroke-dashoffset: 100; }
  to { stroke-dashoffset: 0; }
}

.sparkline {
  stroke-dasharray: 100;
  animation: sweep 1.5s ease forwards;
}
```

---

## 9. Interaktionsdesign

### 9.1 Feedback-Prinzip

**Jede Aktion erzeugt:**
1. **Toast-Notification** (oben rechts)
2. **Log-Eintrag** (in Activity-Log)
3. **Visuelle Änderung** (Status-Update)

**Niemals „stumm".**

### 9.2 Toast Notifications

**CSS:**
```css
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,.5);
  animation: slideIn 0.25s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

### 9.3 Hotkeys

**Pflicht:**
- `Ctrl/Cmd + K` → Global Search

**Optional (erweiterbar):**
- `Ctrl/Cmd + S` → Save
- `Escape` → Close Modal
- `Enter` → Submit Form

---

## 10. Responsive-Regeln

### 10.1 Breakpoints

```css
/* Desktop (default) */
@media (min-width: 1100px) {
  .layout {
    grid-template-columns: 280px 1fr;
  }
}

/* Tablet/Small Laptop */
@media (max-width: 1099px) {
  .layout {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    display: none; /* Hamburger-Menu */
  }
  
  .content {
    grid-template-columns: 1fr; /* Single Column */
    padding: 16px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .content {
    padding: 12px;
    gap: 12px;
  }
  
  .card {
    padding: 14px;
  }
}
```

---

## 11. Design-Gebote (WICHTIG)

### ❌ Der Agent darf NICHT:
- Weißes UI bauen
- Material Design verwenden
- Bootstrap-Theme nutzen
- Eckige Boxen bauen
- Knallige Farben (außer Status)
- Flat-Design ohne Schatten

### ✅ Er MUSS:
- Dark Tech Look umsetzen
- Alles abrunden (min. 16px)
- Glas-Effekt / Gradients verwenden
- Schatten auf Cards/Panels
- Blau/Violett-Akzente nutzen
- Kompakte Typo (13-14px)
- Luftige Abstände

---

## 12. Zieloptik (Referenzen)

### Inspiration (Stil-Vergleich):
- ✅ **Proxmox VE**: Dark Dashboard, kompakte Daten
- ✅ **Synology DSM**: Abgerundete Cards, Glas-Effekte
- ✅ **Portainer**: Clean Dark UI, Tech-Look
- ✅ **GitHub Dark**: Professionell, nicht verspielt
- ✅ **Apple Dev Tools**: Sauber, minimalistisch

### NICHT:
- ❌ AdminLTE
- ❌ Bootstrap Standard-Themes
- ❌ Material Design Light
- ❌ Bunte Consumer-Apps

---

## 13. Komponenten-Übersicht

### Priorität: Phase 10 Implementation

| Komponente | Priorität | Datei | Beschreibung |
|------------|-----------|-------|--------------|
| **Layout** | P0 | `app.component` | Sidebar + Main Grid |
| **Sidebar** | P0 | `sidebar.component` | Navigation |
| **Dashboard** | P0 | `dashboard.component` | KPI-Cards + Activity |
| **Card** | P0 | `card.component` | Wiederverwendbar |
| **Panel** | P0 | `panel.component` | Tables, Logs |
| **Button** | P0 | `button.component` | Primary, Secondary |
| **Badge** | P1 | `badge.component` | Status-Pills |
| **Toast** | P1 | `toast.service` | Notifications |
| **Input** | P1 | `input.component` | Forms |
| **Switch** | P2 | `switch.component` | Toggles |
| **Modal** | P2 | `modal.component` | Dialogs |
| **Sparkline** | P2 | `sparkline.component` | Mini-Charts |

---

## 14. CSS-Variablen (globals.css)

```css
:root {
  /* Farben */
  --bg: #0b1220;
  --panel: #0f1a2b;
  --panel2: #0c1626;
  --card: #111f34;
  --text: #e7f0ff;
  --muted: #8ea4c3;
  --accent: #4da3ff;
  --accent2: #9b7bff;
  --good: #3ddc97;
  --warn: #ffcc66;
  --bad: #ff6b6b;
  --line: rgba(255,255,255,.08);
  
  /* Formen */
  --radius: 18px;
  --radius2: 24px;
  --shadow: 0 10px 30px rgba(0,0,0,.35);
  
  /* Layout */
  --sidebar-width: 280px;
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 22px;
  
  /* Typografie */
  --font-size-xs: 11px;
  --font-size-sm: 12px;
  --font-size-base: 13px;
  --font-size-lg: 14px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: var(--font-size-base);
  color: var(--text);
  background: var(--bg);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}
```

---

## 15. Fazit

**Mit dieser Spec hat der Agent:**
- ✅ **Farben** (exakte HEX-Werte)
- ✅ **Formen** (Radien, Schatten)
- ✅ **Abstände** (Spacing-System)
- ✅ **Typografie** (Größen, Gewichte)
- ✅ **Effekte** (Animationen, Hover)
- ✅ **Interaktion** (Feedback, Hotkeys)
- ✅ **Design-Regeln** (Gebote & Verbote)

= **Komplette UI-DNA** für Phase 10 (Angular Frontend)

---

*Version: 1.0*  
*Erstellt: 2026-01-22*  
*Für: SmartSortierer Pro - Phase 10 Implementation*
