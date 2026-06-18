"""Traffic light controller for WAGO CC100.

Modes:
- Normal mode: deterministic timed cycle for main and side street traffic lights.
- Maintenance mode: both yellow lights blink cyclically.

Mode selection buttons:
- S1 (DI1): request normal mode
- S2 (DI2): request maintenance mode

Safety behavior:
- Startup mode is maintenance mode.
- Mode switches are not immediate.
- Any switch is applied only at a cycle boundary and after an all-red handover.
"""

import CC100IO


# Digital inputs for mode selection.
S1_INPUT = 1
S2_INPUT = 2

# Main street outputs (all via DO).
MAIN_RED_DO = 1
MAIN_YELLOW_DO = 2
MAIN_GREEN_DO = 3

# Side street outputs.
SIDE_RED_DO = 4
SIDE_YELLOW_AO = 1
SIDE_GREEN_AO = 2

# Analog command levels for AO-driven lights (mV command value).
# 0 means OFF, a high value means ON.
AO_OFF = 0
AO_ON = 9999

# Timing constants (milliseconds). Full normal cycle is below 30 seconds.
T_RED_YELLOW_MS = 1200
T_GREEN_MS = 8500
T_YELLOW_MS = 1800
T_ALL_RED_MS = 1200
T_MAINTENANCE_BLINK_MS = 500
T_HANDOVER_ALL_RED_MS = 1200
T_POLL_MS = 100

MODE_NORMAL = "normal"
MODE_MAINTENANCE = "maintenance"


def _read_requested_mode(current_pending_mode):
	"""Read S1/S2 and update requested mode.

	Maintenance has priority if both buttons are pressed at once.
	If no button is pressed, keep the previous pending request.
	"""
	if CC100IO.digitalRead(S2_INPUT):
		return MODE_MAINTENANCE
	if CC100IO.digitalRead(S1_INPUT):
		return MODE_NORMAL
	return current_pending_mode


def _set_main(red_on, yellow_on, green_on):
	"""Set all three lamps of the main street traffic light."""
	CC100IO.digitalWrite(MAIN_RED_DO, red_on)
	CC100IO.digitalWrite(MAIN_YELLOW_DO, yellow_on)
	CC100IO.digitalWrite(MAIN_GREEN_DO, green_on)


def _set_side(red_on, yellow_on, green_on):
	"""Set all three lamps of the side street traffic light."""
	CC100IO.digitalWrite(SIDE_RED_DO, red_on)
	CC100IO.analogWrite(SIDE_YELLOW_AO, AO_ON if yellow_on else AO_OFF)
	CC100IO.analogWrite(SIDE_GREEN_AO, AO_ON if green_on else AO_OFF)


def _set_all_red():
	"""Set both directions to red and switch all yellow/green lamps off."""
	_set_main(red_on=True, yellow_on=False, green_on=False)
	_set_side(red_on=True, yellow_on=False, green_on=False)


def _set_all_off():
	"""Switch all lamps off (used for a clean startup state)."""
	_set_main(red_on=False, yellow_on=False, green_on=False)
	_set_side(red_on=False, yellow_on=False, green_on=False)


def _wait_with_poll(duration_ms, pending_mode):
	"""Wait in short slices while collecting mode requests.

	This keeps the mode request responsive without violating the rule that
	mode changes only happen at safe transition points.
	"""
	remaining = duration_ms
	while remaining > 0:
		step = T_POLL_MS if remaining > T_POLL_MS else remaining
		CC100IO.delay(step)
		remaining -= step
		pending_mode = _read_requested_mode(pending_mode)
	return pending_mode


def _run_normal_cycle(pending_mode):
	"""Run exactly one full traffic light cycle in normal mode."""

	# Phase 1: all red before giving way to main street.
	_set_all_red()
	pending_mode = _wait_with_poll(T_ALL_RED_MS, pending_mode)

	# Phase 2: main red+yellow, side red.
	_set_main(red_on=True, yellow_on=True, green_on=False)
	_set_side(red_on=True, yellow_on=False, green_on=False)
	pending_mode = _wait_with_poll(T_RED_YELLOW_MS, pending_mode)

	# Phase 3: main green, side red.
	_set_main(red_on=False, yellow_on=False, green_on=True)
	_set_side(red_on=True, yellow_on=False, green_on=False)
	pending_mode = _wait_with_poll(T_GREEN_MS, pending_mode)

	# Phase 4: main yellow, side red.
	_set_main(red_on=False, yellow_on=True, green_on=False)
	_set_side(red_on=True, yellow_on=False, green_on=False)
	pending_mode = _wait_with_poll(T_YELLOW_MS, pending_mode)

	# Phase 5: all red clearance.
	_set_all_red()
	pending_mode = _wait_with_poll(T_ALL_RED_MS, pending_mode)

	# Phase 6: side red+yellow, main red.
	_set_main(red_on=True, yellow_on=False, green_on=False)
	_set_side(red_on=True, yellow_on=True, green_on=False)
	pending_mode = _wait_with_poll(T_RED_YELLOW_MS, pending_mode)

	# Phase 7: side green, main red.
	_set_main(red_on=True, yellow_on=False, green_on=False)
	_set_side(red_on=False, yellow_on=False, green_on=True)
	pending_mode = _wait_with_poll(T_GREEN_MS, pending_mode)

	# Phase 8: side yellow, main red.
	_set_main(red_on=True, yellow_on=False, green_on=False)
	_set_side(red_on=False, yellow_on=True, green_on=False)
	pending_mode = _wait_with_poll(T_YELLOW_MS, pending_mode)

	# Phase 9: all red cycle end marker.
	_set_all_red()
	pending_mode = _wait_with_poll(T_ALL_RED_MS, pending_mode)

	return pending_mode


def _run_maintenance_step(pending_mode):
	"""Run one maintenance blink step (yellow ON + yellow OFF)."""

	# Yellow ON for both directions, red and green OFF.
	_set_main(red_on=False, yellow_on=True, green_on=False)
	_set_side(red_on=False, yellow_on=True, green_on=False)
	pending_mode = _wait_with_poll(T_MAINTENANCE_BLINK_MS, pending_mode)

	# Yellow OFF for both directions.
	_set_main(red_on=False, yellow_on=False, green_on=False)
	_set_side(red_on=False, yellow_on=False, green_on=False)
	pending_mode = _wait_with_poll(T_MAINTENANCE_BLINK_MS, pending_mode)

	return pending_mode


def main():
	"""Main loop for the traffic light application."""
	current_mode = MODE_MAINTENANCE
	pending_mode = MODE_MAINTENANCE

	_set_all_off()

	while True:
		pending_mode = _read_requested_mode(pending_mode)

		if current_mode == MODE_MAINTENANCE:
			pending_mode = _run_maintenance_step(pending_mode)

			if pending_mode == MODE_NORMAL:
				_set_all_red()
				pending_mode = _wait_with_poll(T_HANDOVER_ALL_RED_MS, pending_mode)
				current_mode = MODE_NORMAL
				pending_mode = MODE_NORMAL

		else:
			pending_mode = _run_normal_cycle(pending_mode)

			if pending_mode == MODE_MAINTENANCE:
				_set_all_red()
				pending_mode = _wait_with_poll(T_HANDOVER_ALL_RED_MS, pending_mode)
				current_mode = MODE_MAINTENANCE
				pending_mode = MODE_MAINTENANCE


if __name__ == "__main__":
	main()
