import board
import digitalio

# Simple buttons class to keep button checking
# routines concise and less repetative while being consise and not so repe...
class Buttons:
    UP = 0
    ENTER = 1
    DOWN = 2
    PINS = [board.SWITCH_1, board.BOOT0, board.SWITCH_2]  # Replace with your actual pins

    def __init__(self):
        self._buttons = []
        for pin in self.PINS:
            button = digitalio.DigitalInOut(pin)
            button.direction = digitalio.Direction.INPUT
            button.pull = digitalio.Pull.UP
            self._buttons.append(button)

    def pressed(self, button_type):
        return not self._buttons[button_type].value
