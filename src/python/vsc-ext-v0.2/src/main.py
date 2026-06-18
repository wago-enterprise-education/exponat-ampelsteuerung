"""Main entry point for the traffic light application.

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
from trafficlight import TrafficLight


def main():
	"""Main control loop orchestrating both traffic lights."""

	# AO command levels for AO-driven lights (mV).
	AO_OFF = 0
	AO_ON = 9999

	# Create main street traffic light (all on DO).
	main_light = TrafficLight(
		name="main",
		red_io_type="DO",
		red_io=1,
		yellow_io_type="DO",
		yellow_io=2,
		green_io_type="DO",
		green_io=3
	)

	# Create side street traffic light (red on DO, yellow and green on AO).
	side_light = TrafficLight(
		name="side",
		red_io_type="DO",
		red_io=4,
		yellow_io_type="AO",
		yellow_io=1,
		green_io_type="AO",
		green_io=2,
		ao_off=AO_OFF,
		ao_on=AO_ON
	)

	# Mode and timing configuration.
	S1_INPUT = 1
	S2_INPUT = 2
	MODE_NORMAL = "normal"
	MODE_MAINTENANCE = "maintenance"

	T_RED_YELLOW_MS = 1200
	T_GREEN_MS = 8500
	T_YELLOW_MS = 1800
	T_ALL_RED_MS = 1200
	T_MAINTENANCE_BLINK_MS = 500
	T_HANDOVER_ALL_RED_MS = 1200
	T_POLL_MS = 100

	# Internal state.
	current_mode = MODE_MAINTENANCE
	pending_mode = MODE_MAINTENANCE

	def read_requested_mode(current_pending_mode):
		"""Read S1/S2 buttons and update requested mode."""
		if CC100IO.digitalRead(S2_INPUT):
			return MODE_MAINTENANCE
		if CC100IO.digitalRead(S1_INPUT):
			return MODE_NORMAL
		return current_pending_mode

	def wait_with_poll(duration_ms):
		"""Wait in short slices while collecting mode requests."""
		nonlocal pending_mode
		remaining = duration_ms
		while remaining > 0:
			step = T_POLL_MS if remaining > T_POLL_MS else remaining
			CC100IO.delay(step)
			remaining -= step
			pending_mode = read_requested_mode(pending_mode)

	def set_all_red():
		"""Set both traffic lights to red only."""
		main_light.set_red_only()
		side_light.set_red_only()

	def set_all_off():
		"""Switch all lamps off."""
		main_light.set_off()
		side_light.set_off()

	def run_normal_cycle():
		"""Run one full normal traffic light cycle."""
		# Phase 1: all red before main street.
		set_all_red()
		wait_with_poll(T_ALL_RED_MS)

		# Phase 2: main red+yellow, side red.
		main_light.set_red_yellow()
		side_light.set_red_only()
		wait_with_poll(T_RED_YELLOW_MS)

		# Phase 3: main green, side red.
		main_light.set_green_only()
		side_light.set_red_only()
		wait_with_poll(T_GREEN_MS)

		# Phase 4: main yellow, side red.
		main_light.set_yellow_only()
		side_light.set_red_only()
		wait_with_poll(T_YELLOW_MS)

		# Phase 5: all red clearance.
		set_all_red()
		wait_with_poll(T_ALL_RED_MS)

		# Phase 6: side red+yellow, main red.
		main_light.set_red_only()
		side_light.set_red_yellow()
		wait_with_poll(T_RED_YELLOW_MS)

		# Phase 7: side green, main red.
		main_light.set_red_only()
		side_light.set_green_only()
		wait_with_poll(T_GREEN_MS)

		# Phase 8: side yellow, main red.
		main_light.set_red_only()
		side_light.set_yellow_only()
		wait_with_poll(T_YELLOW_MS)

		# Phase 9: all red cycle end marker.
		set_all_red()
		wait_with_poll(T_ALL_RED_MS)

	def run_maintenance_step():
		"""Run one maintenance blink step for both traffic lights."""
		# Yellow ON for both.
		main_light.set_yellow_only()
		side_light.set_yellow_only()
		wait_with_poll(T_MAINTENANCE_BLINK_MS)

		# Yellow OFF for both.
		set_all_off()
		wait_with_poll(T_MAINTENANCE_BLINK_MS)

	# Main control loop.
	set_all_off()

	while True:
		pending_mode = read_requested_mode(pending_mode)

		if current_mode == MODE_MAINTENANCE:
			run_maintenance_step()

			if pending_mode == MODE_NORMAL:
				set_all_red()
				wait_with_poll(T_HANDOVER_ALL_RED_MS)
				current_mode = MODE_NORMAL
				pending_mode = MODE_NORMAL

		else:
			run_normal_cycle()

			if pending_mode == MODE_MAINTENANCE:
				set_all_red()
				wait_with_poll(T_HANDOVER_ALL_RED_MS)
				current_mode = MODE_MAINTENANCE
				pending_mode = MODE_MAINTENANCE


if __name__ == "__main__":
	main()
