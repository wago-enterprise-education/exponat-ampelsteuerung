# Python - Ampelsteuerung

Python-Implementierungen der Ampelsteuerung für den WAGO CC100 Controller, mit interaktiven Demo und Lernübungen.

## 🚀 Quick Start

### Voraussetzungen

- Python 3.8+
- WAGO-Controller mit Ampel-Hardware
- VS Code mit [WAGO CC100 Extension v0.2.x](https://marketplace.visualstudio.com/items?itemName=WAGO-education.vscode-wago-cc100)

### Mit VS Code Extension

Das Projekt `vsc-ext-v0.2/` ist vollständig mit der WAGO CC100 Extension kompatibel:

1. Extension in VS Code installieren
2. Projekt öffnen: `vsc-ext-v0.2/`
3. Projekt über die Extension ausführen

## Projektstruktur

### `vsc-ext-v0.2/`

WAGO CC100 Extension kompatibles Projekt mit:

- **demo/** – Vollständige funktionierende Demo mit State Machine
  - [`main.py`](vsc-ext-v0.2/demo/main.py) – Hauptprogramm
  - [`trafficlight.py`](vsc-ext-v0.2/demo/trafficlight.py) – Ampel-Logik
  - [Statemachine.md](vsc-ext-v0.2/demo/Statemachine.md) – Dokumentation

- **exercise1_io_mapping/** – Übung: Ein-/Ausgänge konfigurieren
  - [README.md](vsc-ext-v0.2/exercise1_io_mapping/README.md) – Aufgabenbeschreibung

- **exercise2_maintenance_mode/** – Übung: Wartungsmodus implementieren
  - [README.md](vsc-ext-v0.2/exercise2_maintenance_mode/README.md) – Aufgabenbeschreibung

- **solutions/** – Lösungsbeispiele
  - [`solution1_io_mapping.py`](vsc-ext-v0.2/solutions/solution1_io_mapping.py)

  - [`solution2_maintenance_mode.py`](vsc-ext-v0.2/solutions/solution2_maintenance_mode.py)

- **controller/** – Controller-Konfigurationen (eine Datei pro Controller)
  - [`controller1.yaml`](vsc-ext-v0.2/controller/controller1.yaml) – CC100 Konfigurationsdatei

- **wago.yaml** – Projekt-Manifest
  - [`wago.yaml`](vsc-ext-v0.2/wago.yaml) – Projekt-Manifest

## Weitere Informationen

- [WAGO CC100 Extension](https://marketplace.visualstudio.com/items?itemName=WAGO-education.vscode-wago-cc100)
- [CC100 Python Bibliothek](https://github.com/wago-enterprise-education/wago_cc100_python)
