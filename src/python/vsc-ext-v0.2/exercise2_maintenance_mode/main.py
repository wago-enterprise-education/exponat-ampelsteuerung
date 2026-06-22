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
T_POLL               = 100
# TODO: Zeit für den Wartungsmodus definieren


# ---------------------------------------------------------------------------
# Modi 
# ---------------------------------------------------------------------------

MODE_NORMAL = "normal"
MODE_MAINTENANCE = "maintenance"


# ---------------------------------------------------------------------------
# IO-Mapping
# ---------------------------------------------------------------------------

# TODO: Tastereingänge definieren
# S1_INPUT = x
# S2_INPUT = x

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


def read_requested_mode(current_pending_mode):
    """Liest die Taster S1/S2 und liefert den gewünschten Modus zurueck."""
    # TODO: Tastereingänge lesen und gewünschten Modus zurückliefern


def wait_with_poll(duration_ms):
    """Wartet in kurzen Schritten und beobachtet dabei die Taster."""
    global pending_mode

    remaining = duration_ms
    while remaining > 0:
        step = T_POLL if remaining > T_POLL else remaining
        CC100IO.delay(step)
        remaining -= step
        pending_mode = read_requested_mode(pending_mode)


def set_all_red():
    """Schaltet beide Richtungen auf Rot."""
    set_lights(
        main_red=True,  main_yellow=False, main_green=False,
        side_red=True,  side_yellow=False, side_green=False,
    )


def set_all_off():
    """Schaltet alle Lampen aus."""
    set_lights(
        main_red=False, main_yellow=False, main_green=False,
        side_red=False, side_yellow=False, side_green=False,
    )


def run_normal_cycle():
    """Fuehrt einen kompletten Zyklus des Normalbetriebs aus."""
    # Phase 1: alles Rot.
    set_all_red()
    wait_with_poll(T_ALL_RED)

    # Phase 2: Hauptstrasse Rot+Gelb, Nebenstrasse Rot.
    apply_state(MAIN_RED_YELLOW)
    wait_with_poll(T_RED_YELLOW)

    # Phase 3: Hauptstrasse Gruen, Nebenstrasse Rot.
    apply_state(MAIN_GREEN)
    wait_with_poll(T_GREEN)

    # Phase 4: Hauptstrasse Gelb, Nebenstrasse Rot.
    apply_state(MAIN_YELLOW)
    wait_with_poll(T_YELLOW)

    # Phase 5: alles Rot als sichere Zwischenphase.
    set_all_red()
    wait_with_poll(T_ALL_RED)

    # Phase 6: Nebenstrasse Rot+Gelb, Hauptstrasse Rot.
    apply_state(SIDE_RED_YELLOW)
    wait_with_poll(T_RED_YELLOW)

    # Phase 7: Nebenstrasse Gruen, Hauptstrasse Rot.
    apply_state(SIDE_GREEN)
    wait_with_poll(T_GREEN)

    # Phase 8: Nebenstrasse Gelb, Hauptstrasse Rot.
    apply_state(SIDE_YELLOW)
    wait_with_poll(T_YELLOW)

    # Phase 9: alles Rot am Zyklusende.
    set_all_red()
    wait_with_poll(T_ALL_RED)


def run_maintenance_step():
    """Laesst beide gelben LEDs blinken."""
    # Gelb an.
    set_lights(
        main_red=False, main_yellow=True,  main_green=False,
        side_red=False, side_yellow=True,  side_green=False,
    )
    wait_with_poll(...)

    # Gelb aus.
    set_all_off()
    wait_with_poll(...)


# ---------------------------------------------------------------------------
# Hauptschleife
# ---------------------------------------------------------------------------

def main():
    global pending_mode

    current_mode = MODE_MAINTENANCE
    pending_mode = MODE_MAINTENANCE

    set_all_off()

    while True:
        pending_mode = read_requested_mode(pending_mode)

        if current_mode == MODE_MAINTENANCE:
            run_maintenance_step()

            if pending_mode == MODE_NORMAL:
                set_all_red()
                wait_with_poll(T_ALL_RED)
                current_mode = MODE_NORMAL
                pending_mode = MODE_NORMAL

        else:
            run_normal_cycle()

            if pending_mode == MODE_MAINTENANCE:
                set_all_red()
                wait_with_poll(T_ALL_RED)
                current_mode = MODE_MAINTENANCE
                pending_mode = MODE_MAINTENANCE


if __name__ == "__main__":
    main()
