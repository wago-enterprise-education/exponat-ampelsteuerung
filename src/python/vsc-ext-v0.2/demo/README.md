# Ampelanlage

## Kurzbeschreibung Exponat

Der vor Dir stehende Aufbau zeigt die Logik einer Ampelsteuerung mit Haupt- und Nebenstraße. Die Ampel ist ausschließlich über definierte Zeitintervalle gesteuert, es gibt keine Sensoren oder andere Eingaben, die den Ablauf beeinflussen können.

Es gibt zwei Modi: Normalbetrieb und Wartungsmodus.

## Normalbetrieb

Nach dem Start mit Schalter `S1` läuft die Anlage in einem festen Zyklus mit definierten Rot-, Rot-Gelb-, Grün- und Gelbphasen.
Der folgende Zustandsautomat beschreibt die Logik des Normalbetriebs der Ampelsteuerung:

```mermaid
stateDiagram-v2
    [*] --> AllRot1: S1 gedrückt
    
    AllRot1: Hauptstraße: 🔴<br/>Nebenstraße: 🔴
    AllRot1 --> HauptRotGelb: 1200ms
    
    HauptRotGelb: Hauptstraße: 🔴🟡<br/>Nebenstraße: 🔴
    HauptRotGelb --> HauptGrün: 1200ms
    
    HauptGrün: Hauptstraße: 🟢<br/>Nebenstraße: 🔴
    HauptGrün --> HauptGelb: 8500ms
    
    HauptGelb: Hauptstraße: 🟡<br/>Nebenstraße: 🔴
    HauptGelb --> AllRot2: 1800ms
    
    AllRot2: Hauptstraße: 🔴<br/>Nebenstraße: 🔴
    AllRot2 --> NebenRotGelb: 1200ms
    
    NebenRotGelb: Hauptstraße: 🔴<br/>Nebenstraße: 🔴🟡
    NebenRotGelb --> NebenGrün: 1200ms
    
    NebenGrün: Hauptstraße: 🔴<br/>Nebenstraße: 🟢
    NebenGrün --> NebenGelb: 8500ms
    
    NebenGelb: Hauptstraße: 🔴<br/>Nebenstraße: 🟡
    NebenGelb --> AllRot1: 1800ms
```

### Zeiten der Phasen

- Rot Phasen: 1200ms
- Rot+Gelb Phasen: 1200ms
- Grün Phasen: 8500ms
- Gelb Phasen: 1800ms

## Wartungsmodus

Der Wartungsmodus wird durch das Drücken von Schalter `S2` aktiviert. In diesem Modus blinkt die Ampel dauerhaft gelb, um Wartungsarbeiten sicher durchführen zu können.

```mermaid
stateDiagram-v2
    [*] --> Wartungsmodus_GelbAn: `S2` gedrückt
    
    Wartungsmodus_GelbAn: Hauptstraße: 🟡<br/>Nebenstraße: 🟡
    Wartungsmodus_Aus: Hauptstraße: ⚫<br/>Nebenstraße: ⚫
    
    Wartungsmodus_GelbAn --> Wartungsmodus_Aus: 500ms
    Wartungsmodus_Aus --> Wartungsmodus_GelbAn: 500ms
       
```

### Blinkverhalten

- Gelb An: 500ms
- Gelb Aus: 500ms

## Übergang zwischen Modi

Der Übergang zwischen Normalbetrieb und Wartungsmodus erfolgt durch das Drücken der entsprechenden Schalter. Der Modus-Wunsch wird zwar sofort registriert, aber der eigentliche Wechsel erfolgt erst nach Abschluss des aktuellen Zyklus (Normalbetrieb) oder Wartungsschritts (Wartungsmodus). Beim Wechsel wird eine sichere Rot-Phase (1200ms) eingeleitet, um einen konfliktfreien Übergang zu gewährleisten.

```mermaid
stateDiagram-v2
    [*] --> Normalbetrieb
    
    Normalbetrieb: Normalbetrieb<br/>(Zyklus läuft)
    Wartungsmodus: Wartungsmodus<br/>(Blinken 🟡)
    AllRed_N2M: Hauptstraße: 🔴<br/>Nebenstraße: 🔴
    AllRed_M2N: Hauptstraße: 🔴<br/>Nebenstraße: 🔴
    
    Normalbetrieb --> AllRed_N2M: `S2` gedrückt<br/>(Zyklus-Ende)
    AllRed_N2M --> Wartungsmodus: 1200ms
    
    Wartungsmodus --> AllRed_M2N: `S1` gedrückt
    AllRed_M2N --> Normalbetrieb: 1200ms
```
