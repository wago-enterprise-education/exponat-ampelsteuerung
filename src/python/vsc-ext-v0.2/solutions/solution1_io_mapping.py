"""Ampelsteuerung mit Zustandsautomat (match/case) fuer den WAGO CC100.

IO-Belegung:
  DO1 - Hauptstrasse: Rot
  DO2 - Hauptstrasse: Gelb
  DO3 - Hauptstrasse: Gruen
  DO4 - Nebenstrasse: Rot
  DO5 - Nebenstrasse: Gelb
  DO6 - Nebenstrasse: Gruen
"""

import CC100IO


# ---------------------------------------------------------------------------
# Zustandsnamen
# ---------------------------------------------------------------------------

ALL_RED         = "ALL_RED"
MAIN_RED_YELLOW = "MAIN_RED_YELLOW"
MAIN_GREEN      = "MAIN_GREEN"
MAIN_YELLOW     = "MAIN_YELLOW"
SIDE_RED_YELLOW = "SIDE_RED_YELLOW"
SIDE_GREEN      = "SIDE_GREEN"
SIDE_YELLOW     = "SIDE_YELLOW"


# ---------------------------------------------------------------------------
# Zeitdauern (Millisekunden)
# ---------------------------------------------------------------------------

T_ALL_RED    = 1800
T_RED_YELLOW = 1200
T_GREEN      = 8500
T_YELLOW     = 1800


# ---------------------------------------------------------------------------
# IO-Mapping
# ---------------------------------------------------------------------------

MAIN_RED_PIN_DO    = 1
MAIN_YELLOW_PIN_DO = 2
MAIN_GREEN_PIN_DO  = 3
SIDE_RED_PIN_DO    = 4
SIDE_YELLOW_PIN_AO = 1
SIDE_GREEN_PIN_AO  = 2

# AO command levels for AO-driven lights (mV).
AO_OFF = 0
AO_ON = 9999


# ---------------------------------------------------------------------------
# IO-Ausgabe
# ---------------------------------------------------------------------------

def set_lights(main_red, main_yellow, main_green,
               side_red, side_yellow, side_green):
    """Setzt alle sechs Lampen gleichzeitig."""
    CC100IO.digitalWrite(MAIN_RED_PIN_DO, main_red)
    CC100IO.digitalWrite(MAIN_YELLOW_PIN_DO, main_yellow)
    CC100IO.digitalWrite(MAIN_GREEN_PIN_DO, main_green)
    CC100IO.digitalWrite(SIDE_RED_PIN_DO, side_red)
    CC100IO.analogWrite(SIDE_YELLOW_PIN_AO, AO_ON if side_yellow else AO_OFF)
    CC100IO.analogWrite(SIDE_GREEN_PIN_AO, AO_ON if side_green else AO_OFF)


# ---------------------------------------------------------------------------
# Zustandsautomat
# ---------------------------------------------------------------------------

def apply_state(state):
    """Setzt die Lampen gemaess dem aktuellen Zustand."""
    match state:
        case "ALL_RED":
            set_lights(
                main_red=True,  main_yellow=False, main_green=False,
                side_red=True,  side_yellow=False, side_green=False,
            )
        case "MAIN_RED_YELLOW":
            set_lights(
                main_red=True,  main_yellow=True,  main_green=False,
                side_red=True,  side_yellow=False, side_green=False,
            )
        case "MAIN_GREEN":
            set_lights(
                main_red=False, main_yellow=False, main_green=True,
                side_red=True,  side_yellow=False, side_green=False,
            )
        case "MAIN_YELLOW":
            set_lights(
                main_red=False, main_yellow=True,  main_green=False,
                side_red=True,  side_yellow=False, side_green=False,
            )
        case "SIDE_RED_YELLOW":
            set_lights(
                main_red=True,  main_yellow=False, main_green=False,
                side_red=True,  side_yellow=True,  side_green=False,
            )
        case "SIDE_GREEN":
            set_lights(
                main_red=True,  main_yellow=False, main_green=False,
                side_red=False, side_yellow=False, side_green=True,
            )
        case "SIDE_YELLOW":
            set_lights(
                main_red=True,  main_yellow=False, main_green=False,
                side_red=False, side_yellow=True,  side_green=False,
            )


def duration_for_state(state):
    """Gibt die Verweildauer (ms) fuer den aktuellen Zustand zurueck."""
    match state:
        case "ALL_RED":
            return T_ALL_RED
        case "MAIN_RED_YELLOW" | "SIDE_RED_YELLOW":
            return T_RED_YELLOW
        case "MAIN_GREEN" | "SIDE_GREEN":
            return T_GREEN
        case "MAIN_YELLOW" | "SIDE_YELLOW":
            return T_YELLOW


def next_state(state, go_side):
    """Gibt den Folgezustand und das aktualisierte go_side-Flag zurueck."""
    match state:
        case "ALL_RED":
            if go_side:
                return SIDE_RED_YELLOW, False
            else:
                return MAIN_RED_YELLOW, True
        case "MAIN_RED_YELLOW":
            return MAIN_GREEN, go_side
        case "MAIN_GREEN":
            return MAIN_YELLOW, go_side
        case "MAIN_YELLOW":
            return ALL_RED, go_side
        case "SIDE_RED_YELLOW":
            return SIDE_GREEN, go_side
        case "SIDE_GREEN":
            return SIDE_YELLOW, go_side
        case "SIDE_YELLOW":
            return ALL_RED, go_side


# ---------------------------------------------------------------------------
# Hauptschleife
# ---------------------------------------------------------------------------

def main():
    state   = ALL_RED
    go_side = False   # Wechselt nach jedem ALL_RED zwischen Haupt- und Nebenstrasse

    while True:
        apply_state(state)
        CC100IO.delay(duration_for_state(state))
        state, go_side = next_state(state, go_side)


if __name__ == "__main__":
    main()
