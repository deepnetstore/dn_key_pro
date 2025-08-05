import time
import board
import pwmio
import displayio
from adafruit_st7789 import ST7789

import adafruit_imageload

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

from .periferals import spi

# Initialize display
BL_PWM_MIN = 65534
BL_PWM_MAX = 0

BL_PWM_ON = BL_PWM_MAX
BL_PWM_OFF = BL_PWM_MIN

tft_backlight = pwmio.PWMOut(board.TFT_BL, frequency=80)
tft_backlight.duty_cycle = BL_PWM_OFF

time.sleep(0.001)

# LOAD TFT STUFF FIRST!!!
# TFT Configuration
WIDTH = 320
HEIGHT = 172

tft_cs = board.TFT_CS
tft_dc = board.TFT_DC

while not spi.try_lock():
    pass

spi.configure(baudrate=40000000)  # how fast is too fast?
spi.unlock()

displayio.release_displays()
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(display_bus, rotation=270, width=WIDTH, height=HEIGHT, colstart=34)

print("Initializing DEEPNET Key Pro V0\n\n")

# main group to show on display
display_group = displayio.Group()

# show the splash image
image, palette = adafruit_imageload.load(
    "images/dn-hckr-crop.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
)
tile_grid = displayio.TileGrid(image, pixel_shader=palette, x=112)

display_group.append(tile_grid)

# set main group to display
display.root_group = display_group
time.sleep(0.1)

# screen fade in
for i in range(BL_PWM_MIN, BL_PWM_MAX, -655):
    tft_backlight.duty_cycle = i
    time.sleep(0.01)

for i in range(0, 24):
    tile_grid.x += 4
    time.sleep(0.0075)

time.sleep(0.1)