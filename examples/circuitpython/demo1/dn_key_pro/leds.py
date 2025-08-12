import board
import neopixel

LED_BRIGHTNESS = 0.2

pixels = neopixel.NeoPixel(board.NEOPIXELS, 4, brightness=LED_BRIGHTNESS)
pixels.fill(0)
