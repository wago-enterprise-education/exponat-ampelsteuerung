"""Traffic light controller for WAGO CC100 - single traffic light instance."""

import CC100IO


class TrafficLight:
    """Single traffic light with configurable IO pins for all colors."""

    def __init__(self, name, red_io_type, red_io, yellow_io_type, yellow_io,
                 green_io_type, green_io, ao_off=0, ao_on=9999):
        """Initialize a single traffic light.

        Args:
            name: Name of the traffic light (e.g., "main", "side")
            red_io_type: "DO" or "AO" for red lamp
            red_io: Output number for red lamp
            yellow_io_type: "DO" or "AO" for yellow lamp
            yellow_io: Output number for yellow lamp
            green_io_type: "DO" or "AO" for green lamp
            green_io: Output number for green lamp
            ao_off: AO command level for OFF state (mV), configured in main
            ao_on: AO command level for ON state (mV), configured in main
        """
        self.name = name
        self.red_io_type = red_io_type
        self.red_io = red_io
        self.yellow_io_type = yellow_io_type
        self.yellow_io = yellow_io
        self.green_io_type = green_io_type
        self.green_io = green_io
        self.AO_OFF = ao_off
        self.AO_ON = ao_on

    def _write_output(self, io_type, io_number, state):
        """Write to DO or AO output."""
        if io_type == "DO":
            CC100IO.digitalWrite(io_number, state)
        else:  # AO
            CC100IO.analogWrite(io_number, self.AO_ON if state else self.AO_OFF)

    def set_red(self, state):
        """Set red lamp on/off."""
        self._write_output(self.red_io_type, self.red_io, state)

    def set_yellow(self, state):
        """Set yellow lamp on/off."""
        self._write_output(self.yellow_io_type, self.yellow_io, state)

    def set_green(self, state):
        """Set green lamp on/off."""
        self._write_output(self.green_io_type, self.green_io, state)

    def set_all(self, red_state, yellow_state, green_state):
        """Set all three lamps at once."""
        self.set_red(red_state)
        self.set_yellow(yellow_state)
        self.set_green(green_state)

    def set_red_only(self):
        """Set only red lamp on, others off."""
        self.set_all(red_state=True, yellow_state=False, green_state=False)

    def set_off(self):
        """Switch all lamps off."""
        self.set_all(red_state=False, yellow_state=False, green_state=False)

    def set_red_yellow(self):
        """Set red and yellow on, green off."""
        self.set_all(red_state=True, yellow_state=True, green_state=False)

    def set_green_only(self):
        """Set only green lamp on, others off."""
        self.set_all(red_state=False, yellow_state=False, green_state=True)

    def set_yellow_only(self):
        """Set only yellow lamp on, others off."""
        self.set_all(red_state=False, yellow_state=True, green_state=False)
