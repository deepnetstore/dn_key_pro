'''
DN Duck.

This code uses a modified Adafruit Ducky Script circuitpython code.
It has been adapted to report the 'percentage' complete of the Ducky script running.
It will report back an Integer value from 0-100; 100 being the completed value.
This value is fed into the Progressbar to be drawn just before running the ducky scripts 
HID command.
'''

import os
import time
import board
import busio
import pwmio
import storage
import array
import adafruit_sdcard
import digitalio
import displayio
import terminalio
import sys
import supervisor
import adafruit_max1704x
import neopixel

import max3421e
import usb

from adafruit_display_text import label
from adafruit_st7789 import ST7789

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

from dn_duck.dn_duck import Ducky

from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)

# import asyncio  # having problems
# import sdcardio  # didn't seem to work.. 


pixels = neopixel.NeoPixel(board.NEOPIXELS, 4)
pixels.fill(0)

# LOAD TFT STUFF FIRST!!!
# TFT Configuration
WIDTH = 320
HEIGHT = 172

# Initialize display
BL_PWM_MIN = 65534
BL_PWM_MAX = 0

BL_PWM_ON = BL_PWM_MAX
BL_PWM_OFF = BL_PWM_MIN

tft_backlight = pwmio.PWMOut(board.TFT_BL, frequency=80)
tft_backlight.duty_cycle = BL_PWM_OFF

spi = board.SPI()
tft_cs = board.TFT_CS
tft_dc = board.TFT_DC

while not spi.try_lock():
    pass
spi.configure(baudrate=40000000)
spi.unlock()

displayio.release_displays()
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(display_bus, rotation=270, width=WIDTH, height=HEIGHT, colstart=34)

print("Initializing DEEPNET Key Pro V0\n")

# screen fade in
for i in range(BL_PWM_MIN, BL_PWM_MAX, -655):
    tft_backlight.duty_cycle = i
    time.sleep(0.01)

print("")

cs = board.USB_SS
irq = board.USB_INT

max3421e = max3421e.Max3421E(spi, chip_select=cs, irq=irq)

device = None
vid = None
pid = None

# max3421e test
def test_max3421e():
    global device, vid, pid
    print("Finding devices:")
    time.sleep(0.5)
    for device in usb.core.find(find_all=True):
        print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
        if device == None:
            return None
        vid = device.idVendor
        pid = device.idProduct
        device = usb.core.find(idVendor=vid, idProduct=pid)
        time.sleep(0.1)
        device.set_configuration()
        print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
        # Test to see if the kernel is using the device and detach it.
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        return device
    return None

# uncomment to Run the test function
# device = test_max3421e()

i2c_ok = False

try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    max17 = adafruit_max1704x.MAX17048(i2c)

    print(
        "Found MAX1704x with chip version",
        hex(max17.chip_version),
        "and id",
        hex(max17.chip_id),
    )
    i2c_ok = True
except:
    print('no i2c setup, try later, check pull ups..')


# Quick starting allows an instant 'auto-calibration' of the battery. However, its a bad idea
# to do this right when the battery is first plugged in or if there's a lot of load on the battery
# so uncomment only if you're sure you want to 'reset' the chips charge calculator.
# print("Quick starting")
# max17.quick_start = True

def print_battery_levels():   
    if i2c_ok:
        print(f"Battery voltage: {max17.cell_voltage:.2f} Volts")
        print(f"Battery state  : {max17.cell_percent:.1f} %")


bat_counter = 0  # only update the battery every so often
bat_counter_max = 0xffff
def update_battery_levels():
    global bat_counter
    if bat_counter > bat_counter_max:
        print_battery_levels()
        bat_counter = 0
    bat_counter += 1

# spi bus used by SD Card, stored globably
spi_0 = None

# location in SD card to load scripts from
DUCKY_DIR = "/DUCKY_SCRIPTS/"

sd_card_init_success = False

print("Trying SD CARD setup")
# Initialize SD Card
try:
    spi_0 = busio.SPI(board.D5, MISO=board.D4, MOSI=board.D8)
    while not spi_0.try_lock():
        pass
    spi_0.configure(baudrate=2400000)
    spi_0.unlock()
    # spi_0 = busio.SPI(board.SD_CLK, MISO=board.SD_D0, MOSI=board.SD_DI)
    # sdcard = sdcardio.SDCard(spi_0, board.D7, baudrate=2000000)
    cs = digitalio.DigitalInOut(board.SD_CS)
    sdcard = adafruit_sdcard.SDCard(spi_0, cs)
    vfs = storage.VfsFat(sdcard)
    time.sleep(0.25)
    storage.mount(vfs, "/")
    time.sleep(0.75)
    print("SD Card Mounted")
    sd_card_init_success = True
except OSError as e:
    print(f"SD Card Error: {e}")


def print_directory(path, tabs=0):
    for file in os.listdir(path):
        if file == "?" or file[0] == ".":
            continue
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " bytes"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<32} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

if sd_card_init_success:
    print_directory("/")

print("continuing setup.")

# location helpers for drawing text locations
MENU_START_X = 16
MENU_START_Y = 32
MENU_ITEM_HEIGHT = 20


# empty objects in the group to show
def clear_group():
    global display_group
    while len(display_group) > 0:
        display_group.pop()


# update the current_view variable
def set_current_view(new_view):
    global current_menu
    current_menu = new_view


# storage class for passing as argument in Menu building
class ArgStore:
    def __init__(self, _data):
        self.data = _data



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


# Items have a text to display, a function to call and an argument to pass
# The action function will be called passing in the user_data as an agument
# when enter button has been pressed over a Menu choice
class MenuItem:
    def __init__(self, text, action, user_data=None):
        self.text = text
        self.action = action
        self.user_data = user_data

    def execute(self):
        self.action(self.user_data)


# Base class for basic Menu drawing and updating
# to be inherited by other classes to share common calls
# to change view, set a global 'current_view' and update
# that variable to the desired Menu class to display.
# clearing of old group will be required before 
# reloading the next view 
class MenuBase:
    def __init__(self, title, items, n_items=5):
        self.title = title
        self.items = items
        self.N_ITEMS = n_items      # set number of items shown on display space
        self.view_start = 0         # Index of the first item visible in the view
        self.selected_index = 0
        self.pressed = False
        if i2c_ok:
            self.battery_label = label.Label(terminalio.FONT, text=f"BAT:{max17.cell_percent:.1f}%", color=0xA999BE, x=180, y=16, scale=2)

    def draw(self, group):
        '''
        this is a dummy function that needs to be overridden by 
        a user's customer menu sub class. 
        See DuckyMenu below for example
        '''
        print("MUST BE IMPLEMENTED/OVERRIDDEN BY A SUBCLASS")
        
    def _adjust_view(self):
        """Adjusts the view_start to keep the selected item visible."""
        if self.selected_index < self.view_start:
            self.view_start = self.selected_index
        elif self.selected_index >= self.view_start + 5: # 5 is the max items on screen
            self.view_start = self.selected_index - 4

    def buttons_released(self, buttons):
        return not buttons.pressed(Buttons.UP) and not buttons.pressed(Buttons.DOWN) and not buttons.pressed(Buttons.ENTER)

    def handle_input(self, buttons, display_group):
        if i2c_ok:
            update_battery_levels()
            self.battery_label.text = f"BAT:{max17.cell_percent:.1f}%"

        if self.pressed and self.buttons_released(buttons):
            time.sleep(0.01)
            self.pressed = False

        elif buttons.pressed(Buttons.UP) and not self.pressed:
            self.pressed = True
            self.selected_index = (self.selected_index - 1) % len(self.items)
            # print("button up:", Buttons.UP, self.selected_index)
            self._adjust_view()  # Adjust view after changing selection
            self.draw(display_group)
            time.sleep(0.01)

        elif buttons.pressed(Buttons.DOWN) and not self.pressed:
            self.pressed = True
            self.selected_index = (self.selected_index + 1) % len(self.items)
            # print("button down:", Buttons.DOWN, self.selected_index)
            self._adjust_view()  # Adjust view after changing selection
            self.draw(display_group)
            time.sleep(0.01)

        elif buttons.pressed(Buttons.ENTER) and not self.pressed:
            self.pressed = True
            self.items[self.selected_index].execute()
            # print("button enter:", Buttons.ENTER, self.selected_index)
            time.sleep(0.01)


    def draw_items(self, group, *, offset_x=0, offset_y=0):
        if i2c_ok:
            group.append(self.battery_label)
        for i in range(min(self.N_ITEMS, len(self.items))):    # only draw N items at a time
            item_index = self.view_start + i        # update item index to show
            if item_index < len(self.items):        # note: view_start is adjusted on user input
                color = 0xFF00FF if item_index == self.selected_index else 0xF0F0F0
                text_area = label.Label(terminalio.FONT, text=self.items[item_index].text, color=color, x=MENU_START_X + offset_x, y=MENU_START_Y + i * MENU_ITEM_HEIGHT, scale=2)
                group.append(text_area)


# Class to implement the Main menu, 
# this inherits from the menu base class
class Menu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=0x00F000, x=8, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group)


# Class to implement the Ducky sctip menu, 
# this inherits from the menu base class
class DuckyMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=0x00F000, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


# Class for implementing USB Host device
class USBHostMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=0x00F000, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


class SettingsMenu(MenuBase):
    def draw(self, group):
        print("drawing settings")
        

# function calls to load when MenuItems are selected.
def load_new_menu(user_data=None):
    print("Loading New Menu")
    print("user_data:", user_data)
    clear_group()
    data = f" {user_data}" if user_data != None else ""
    text_area = label.Label(terminalio.FONT, text=f"New Menu Loaded{data}", color=0xF0F0F0, x=10, y=10, scale=2)
    display_group.append(text_area)
    time.sleep(0.01)
    main_menu.draw(display_group)


def start_kbd_read_task(device, text_area):
    usb_host_running = True
    while usb_host_running:
        try:
            available = supervisor.runtime.serial_bytes_available
            if available:
                c = sys.stdin.read(available)
                b = ord(bytes(c.encode()))
                if b == 0x08:  # backspace
                    text_area.text = text_area.text[:-int(len(c))]
                elif b == 0x1B: # escape
                    usb_host_running = False
                    load_usb_host_screen(None)
                else:
                    text_area.text += c
                    # print(c, end="")
        except:
            continue
        time.sleep(0.01)


def read_usb_host_keyboard(device=None):
    print("reading from usb host as keyboard")
    global usbhost_menu
    display_group.pop(-1)
    text_area = label.Label(terminalio.FONT, text="", color=0xF000F0, x=10, y=50)
    display_group.append(text_area)
    start_kbd_read_task(device, text_area)


def EmptyFunc(na=None):
    pass

# function to load and show the USB Host connection
def load_usb_host_screen(user_data=None):
    global usbhost_menu, kbdbuf
    kbdbuf = array.array("B", [0] * 8)
    menu_items = [
        MenuItem("< Back", go_back_to, main_menu)
    ]
    print("Finding usb devices:")
    devices = usb.core.find(find_all=True)
    count = 0
    time.sleep(0.01)
    for device in devices:
        print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
        menu_items.append(
            MenuItem(f"Read {device.product}", read_usb_host_keyboard, device)
        )
        count += 1
    if count == 0:
        print("  X No USB devices.")
        menu_items.append(
            MenuItem(f"X No USB Devices", EmptyFunc)
        )
    usbhost_menu = USBHostMenu("USB Host", menu_items)
    clear_group()
    usbhost_menu.draw(display_group)
    set_current_view(usbhost_menu)


# function calls to load when MenuItems are selected.
# this one loads the ducky menu view
def load_ducky_menu(user_data=None):
    global ducky_menu
    ducky_menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Load from /SD" if sd_card_init_success else "No SD Card found... :/", load_sd_files, "None"),
    ]
    ducky_menu = DuckyMenu("Ducky Menu", ducky_menu_items)
    print("trying to load Ducky Menu")
    print("user_data:", user_data)
    clear_group()
    ducky_menu.draw(display_group)
    set_current_view(ducky_menu)



# this is the call to run the actual ducky script HID command
# imports are buried here to release from RAM once no longer used.
def run_duck(duck_file):
    keyboard = Keyboard(usb_hid.devices)
    keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)

    duck_file = f"{DUCKY_DIR}/{duck_file}"

    border = 8
    x, y = (border, 108)
    pwidth, pheight = (224, 10)

    progress_bar = HorizontalProgressBar(
        (x, y), (pwidth, pheight), direction=HorizontalFillDirection.LEFT_TO_RIGHT
    )

    while len(display_group) > 0:
        display_group.pop()

    text_area = label.Label(terminalio.FONT, text=f"File: \n{duck_file}", color=0xF0F0F0, x=0, y=10, scale=2)
    
    display_group.append(text_area)
    display_group.append(progress_bar)

    print("RELEASE THE QUACKING:", duck_file)
    duck = Ducky(duck_file, keyboard, keyboard_layout)

    result = 0
    while result < 100:
        result = duck.loop()  # send every char from the text file to USB as HID Keyboard
        fresult = result if (progress_bar.value < progress_bar.maximum) else progress_bar.maximum
        progress_bar.value = max(0, min(100, fresult))
        
    print("THE DUCK HAS QUACKED!")
    time.sleep(0.01)
    ducky_menu.draw(display_group)


# sd files loader for Ducky Menu
def load_sd_files(user_data=None):
    global ducky_menu
    print("Load SD Card files")
    if sd_card_init_success:
        ducky_menu.items.pop(-1)
        ducks = os.listdir(DUCKY_DIR)
        for duck in ducks:
            if duck[0] == ".":
                continue
            print(duck)
            ducky_menu.items.append(MenuItem(duck, run_duck, duck))
        ducky_menu.draw(display_group)
        print(ducks)
    else:
        print("SD CARD NOT INITIALIZED, Check SD Card is present.")


# call to set current view to display
def go_back_to(menu_to_return):
    clear_group()
    global display_group
    menu_to_return.draw(display_group)
    set_current_view(menu_to_return)


def back_menu_item(back_to_menu):
    return MenuItem("< Back", go_back_to, back_to_menu),


def load_wifi_settings_screen(user_data=None):
    print("load_wifi_settings_screen")


def load_wifi_menu_screen(user_data=None):
    global wifi_menu, main_menu
    print("load wifi menu screen")
    clear_group()
    menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Settings", load_wifi_settings_screen),
        MenuItem("Attacks", EmptyFunc),
        MenuItem("Sniff", EmptyFunc),
        MenuItem("Connect", EmptyFunc),
        MenuItem("Start AP", EmptyFunc),
    ]
    wifi_menu = Menu("Wifi Menu", menu_items)
    wifi_menu.draw(display_group)
    set_current_view(wifi_menu)


# function to check for SD card and show contents
def scan_sd_card(user_data=None):
    print("trying to scan SD Card")
    clear_group()
    

def load_sd_card_menu_screen(user_data=None):
    print("load sd card menu screen")
    clear_group()


# main starting function
def main():
    buttons = Buttons()

    main_menu_items = [
        MenuItem("Ducky Script", load_ducky_menu, "DUCKS!"),
        MenuItem("USB Host (MAX3421e)", load_usb_host_screen),
        MenuItem("WiFi", load_wifi_menu_screen),
        MenuItem("SDCard", load_sd_card_menu_screen)
    ]

    global main_menu
    main_menu = Menu("Main Menu", main_menu_items)
    main_menu.draw(display_group)
    display.root_group = display_group
    
    # set the current_menu to the desired starting view
    global current_menu
    current_menu = main_menu

    # Main Loop
    print("looping")
    while True:
        current_menu.handle_input(buttons, display_group)
        time.sleep(0.001)

print("starting")
time.sleep(0.25)
display_group = displayio.Group()

if __name__ == "__main__":
    main()