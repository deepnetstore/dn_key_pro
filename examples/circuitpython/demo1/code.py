'''
AI Duck.

The structure and architecture of this code was initially writen by Gemini AI
using this prompt:

[start of prompt] 
"
Hey Gem, I'm working on a circuitpython project using 3 buttons, an SD card, and a 
TFT display with 240 width and 135 height. I need help making a menu system. Can you 
show me code written with Circuitpython to create a menu system using a simple 3 
button input?
please use asyncio and break everything into simple classes, including the buttons 
and use basic enumerations defined as class variables within each class.
for example,
`class Button:
    button_up = 0
    button_enter = 1
    button_down = 2
    buttons = [button_up, button_enter, button_down]
def __init__(self):
`
for each item in the list of menu items, when the button enter is pressed, the 
menu or command should be run coresponding to the chosen menu item.
please add classes for the items in the menu list, and provide a class object 
definition to run a command or load a new menu.
" 
[end of prompt]

Of course it didn't get everything right but it did provide a decently usable 
foundation to build on.

I plan to have Gemini AI write any new code implementation as a class definition 
and then fix what doesn't work myself and maybe with slight help from 'Gem'.

This code uses a modified Adafruit Ducky Script circuitpython code.
It has been adapted to report the 'percentage' complete of the Ducky script running.
It will report back an Integer value from 0-100, 100 being the completed value.
This value is fed into the Progressbar drawn just before running the ducky scripts 
HID command.
'''

import os
import time
import board
import busio
import pwmio
import asyncio
import storage
import sdcardio
# import adafruit_sdcard
import digitalio
import displayio
import terminalio

import audiomixer
import audiocore
import audiobusio

from adafruit_display_text import label
from adafruit_st7789 import ST7789

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

import adafruit_max1704x

time.sleep(0.2)

# LOAD TFT STUFF FIRST!!!

# TFT Configuration
WIDTH = 320
HEIGHT = 172

# Initialize display
TFT_SIZE = 147
BL_PWM_MIN = 65534
BL_PWM_MAX = int(65534 * 3 / 8)

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
display_group = displayio.Group()

i2c_ok = False

try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
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
bat_counter_max = 1024
def update_battery_levels():
    global bat_counter
    if bat_counter > bat_counter_max:
        print_battery_levels()
        bat_counter = 0
    bat_counter += 1

# spi bus used by SD Card, stored globably
spi_0 = None

# location in SD card to load scripts from
DUCKY_DIR = "/sd/DUCKY_SCRIPTS"

sd_card_init_success = False

print("Trying SD CARD setup")
# Initialize SD Card
try:
    spi_0 = busio.SPI(board.D5, MISO=board.D4, MOSI=board.D8)
    # spi_0 = busio.SPI(board.SD_CLK, MISO=board.SD_D0, MOSI=board.SD_DI)
    sdcard = sdcardio.SDCard(spi_0, board.D7, baudrate=2000000)
    # cs = digitalio.DigitalInOut(board.SD_CS)
    # sdcard = adafruit_sdcard.SDCard(spi_0, cs)
    vfs = storage.VfsFat(sdcard)
    time.sleep(0.25)
    storage.mount(vfs, "/sd")
    time.sleep(0.75)
    print("SD Card Mounted")
    sd_card_init_success = True
except OSError as e:
    print(f"SD Card Error: {e}")


def print_directory(path, tabs=0):
    for file in os.listdir(path):
        if file == "?":
            continue  # Issue noted in Learn
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
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)


# print("Files on filesystem:")
# print("====================")
# print_directory("/sd/_KEY_DATA/")
if sd_card_init_success:
    print_directory("/sd/DUCKY_SCRIPTS/")

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
# function will be called with agument when selected by eneter button over Menu choice
class MenuItem:
    def __init__(self, text, action, user_data=None):
        self.text = text
        self.action = action
        self.user_data = user_data

    async def execute(self):
        await self.action(self.user_data)


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

    async def handle_input(self, buttons, display_group):
        if i2c_ok:
            update_battery_levels()
            self.battery_label.text = f"BAT:{max17.cell_percent:.1f}%"

        if buttons.pressed(Buttons.UP):
            self.selected_index = (self.selected_index - 1) % len(self.items)
            print("button up:", Buttons.UP, self.selected_index)
            self._adjust_view()  # Adjust view after changing selection
            self.draw(display_group)
            await asyncio.sleep(0.2)  # Debounce

        elif buttons.pressed(Buttons.DOWN):
            self.selected_index = (self.selected_index + 1) % len(self.items)
            print("button down:", Buttons.DOWN, self.selected_index)
            self._adjust_view()  # Adjust view after changing selection
            self.draw(display_group)
            await asyncio.sleep(0.2)  # Debounce

        elif buttons.pressed(Buttons.ENTER):
            await self.items[self.selected_index].execute()
            print("button enter:", Buttons.ENTER, self.selected_index)
            await asyncio.sleep(0.2)  # Debounce

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


# Special class to test things with...
class SpecialClass(MenuBase):
    cool_value = 13
    def draw(self, group):
        print("specialClass Draw called", self.cool_value)
        clear_group()
        text_area = label.Label(terminalio.FONT, text=self.title, color=0x00F000, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)

    # async def load(self, user_data=None):
    #     print("load something from class method", user_data.title)
    #     clear_group()
    #     self.draw(display_group)
    #     global current_menu
    #     current_menu = self


class SettingsMenu(MenuBase):
    def draw(self, group):
        print("drawing settings")
        

# simple test function to test things
async def do_something_with_class(view_class):
    print("specialClass coolvalue: ", view_class.cool_value)


# function calls to load when MenuItems are selected.
async def do_something(user_data=None):
    print("Doing Something")
    clear_group()
    data = str()
    if isinstance(user_data, dict):
        print("ARG STORE", user_data["delaytime"])
        data = f"{user_data["delaytime"]}" if user_data != None else ""
    else: 
        print("user_data:", user_data)
        data = f"{user_data}" if user_data != None else ""
    text_area = label.Label(terminalio.FONT, text=f"Doing Something...\n{data}", color=0xF0F0F0, x=0, y=10, scale=2)
    display_group.append(text_area)
    if isinstance(user_data, dict):
        for t in [r for r in range(user_data["delaytime"], 0, -1)]:
            text_area.text = f"Doing Something...\n{t}"
            await asyncio.sleep(1)
    else:
        await asyncio.sleep(2)
    main_menu.draw(display_group)


# function calls to load when MenuItems are selected.
async def load_new_menu(user_data=None):
    print("Loading New Menu")
    print("user_data:", user_data)
    clear_group()
    data = f" {user_data}" if user_data != None else ""
    text_area = label.Label(terminalio.FONT, text=f"New Menu Loaded{data}", color=0xF0F0F0, x=10, y=10, scale=2)
    display_group.append(text_area)
    await asyncio.sleep(2)
    main_menu.draw(display_group)


# function calls to load when MenuItems are selected.
# this one loads the ducky menu view
async def load_ducky_menu(user_data=None):
    global ducky_menu
    print("trying to load Ducky Menu")
    print("user_data:", user_data)
    clear_group()
    ducky_menu.draw(display_group)
    global current_menu
    current_menu = ducky_menu


# this is the call to run the actual ducky script HID command
# imports are buried here to release from RAM once no longer used.
async def run_duck(duck_file):
    import usb_hid
    from adafruit_hid.keyboard import Keyboard
    from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

    from dn_ducky import Ducky

    keyboard = Keyboard(usb_hid.devices)
    keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)

    duck_file = f"{DUCKY_DIR}/{duck_file}"

    from adafruit_progressbar.horizontalprogressbar import (
        HorizontalProgressBar,
        HorizontalFillDirection,
    )

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
    await asyncio.sleep(0.1)
    ducky_menu.draw(display_group)


# sd files loader for Ducky Menu
async def load_sd_files(user_data=None):
    global ducky_menu
    print("Load SD Card files")
    if sd_card_init_success:
        ducky_menu.items.pop(-1)
        ducks = os.listdir(DUCKY_DIR)
        for duck in ducks:
            print(duck)
            ducky_menu.items.append(MenuItem(duck, run_duck, duck))
        ducky_menu.draw(display_group)
        print(ducks)
    else:
        print("SD CARD NOT INITIALIZED, Check SD Card is present.")

# srsly, does nothing useful..
async def nothing(user_data=None):
    print("did nothing...", user_data if user_data else "")



# for special test class (it didn't go to plan...)
async def load_something_with_class_obj(user_data=None):
    print("load something", user_data)
    clear_group()
    global specialClass
    specialClass.draw(display_group)
    set_current_view(specialClass)
    # global current_menu
    # current_menu = specialClass


# call to set current view to display
async def go_back_to(menu_to_return):
    clear_group()
    global display_group
    menu_to_return.draw(display_group)
    global current_menu
    current_menu = menu_to_return


# main async function
async def main():
    # global display_group
    buttons = Buttons()

    cool_test_obj = {"delaytime":60}

    main_menu_items = [
        MenuItem("Ducky Script", load_ducky_menu, "DUCKS!"),
        # MenuItem("Do Something", Settings, settings_menu),
        MenuItem("Load New Menu", load_new_menu),
        MenuItem("Item 4", do_something, "TWO"), # reuse a function and pass different argument
        MenuItem("Item 5", do_something, {"delaytime":30}), # reuse a function and pass different argument
        MenuItem("Class View", load_something_with_class_obj, "specialClass"),
        MenuItem("Class View1", load_something_with_class_obj, "option data to pass"),
        MenuItem("Class View2", load_something_with_class_obj, cool_test_obj),
        MenuItem("Class View3", load_something_with_class_obj, None),
        MenuItem("Class View4", load_something_with_class_obj),  # omit the final arg since its optional
    ]

    global main_menu
    main_menu = Menu("Main Menu", main_menu_items)
    main_menu.draw(display_group)
    display.root_group = display_group
    
    # experimenting with using this system in other views
    specialClassItems = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("one thing", nothing, "1 Nope, no info..."),
        MenuItem("2 thing", nothing, "2 Yep, some info..."),
    ]

    global specialClass
    specialClass = SpecialClass("Special Class", specialClassItems)

    # setup items for the Ducky Menu
    ducky_menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Load from /SD" if sd_card_init_success else "No SD Card found... :/", load_sd_files, "None"),
    ]

    # create the ducky menu view to load later
    global ducky_menu
    ducky_menu = DuckyMenu("Ducky Menu", ducky_menu_items)

    # set the current_menu to the desired starting view
    global current_menu
    current_menu = main_menu

    # screen fade in with sound
    # time.sleep(0.1)
    # time.sleep(0.35)
    for i in range(BL_PWM_MIN, BL_PWM_MAX, -655):
        tft_backlight.duty_cycle = i
        time.sleep(0.00125)

    # global battery_text_area
    # battery_text_area = label.Label(terminalio.FONT, text=f"BAT:{max17.cell_percent:.1f}%", color=0xCC99DC, x=180, y=16, scale=2)
    # display_group.append(battery_text_area)
    # print_battery_levels()
    
    print("looping")
    # Main Loop
    while True:
        await current_menu.handle_input(buttons, display_group)
        await asyncio.sleep(0.01)

print("started")
time.sleep(0.001)
# run the async function
asyncio.run(main())


# print("Searching for USB Keyboard...")
# print("nice!!!")
# import board
# import max3421e
# import time
# import usb

# # SPI and CS/IRQ pins (Adjust these to your board's wiring)
# spi = board.SPI()
# cs = board.USB_SS  # Example: adjust to your actual CS pin
# irq = board.USB_INT  # Example: adjust to your actual IRQ pin

# # --- Keyboard specific configurations ---
# # Standard USB HID Keyboard values (common but can vary slightly)
# # Check your keyboard's actual descriptors if it doesn't work.
# KEYBOARD_VID = None  # Vendor ID - Set to None to find any keyboard
# KEYBOARD_PID = None  # Product ID - Set to None to find any keyboard

# host_chip = max3421e.Max3421E(spi, chip_select=cs, irq=irq)

# while True:
#    print("Finding devices:")
#    for device in usb.core.find(find_all=True):
#        print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
#    time.sleep(5)

# # This function is a placeholder for actual key processing
# def process_keyboard_report(report_buffer):
#     # A standard USB HID keyboard report is 8 bytes long.
#     # Byte 0: Modifier keys (Shift, Ctrl, Alt, GUI)
#     # Byte 1: Reserved (usually 0)
#     # Bytes 2-7: Up to 6 keycodes pressed simultaneously
#     print(report_buffer)
#     # Example: Print raw bytes and try to identify a key
#     modifier = report_buffer[0]
#     # Skip report_buffer[1] (reserved)
#     keycodes = report_buffer[2:]

#     # # Basic parsing example for a single key
#     # if any(keycodes): # If any key is pressed
#     #     print(f"Raw HID Report: {report_buffer.hex()}")
#     #     print(f"  Modifier: 0x{modifier:02X}")
#     #     print(f"  Keycodes: {[f'0x{k:02X}' for k in keycodes if k != 0]}")

#     #     # You'd typically map keycodes to characters here.
#     #     # This is where `adafruit_hid.keycode` could be useful.
#     #     # Example: Keycode for 'A' is 0x04.
#     #     # if 0x4 in keycodes:
#     #     #     print("  'A' pressed!")
#     #     # Add more mappings as needed

#     # elif not any(keycodes): # All keys released
#     #     print("  All keys released")

# print("work?")
# device = None
# while device is None:
#     try:
#         # Find a USB device. You can specify vid/pid if known.
#         # usb.core.find returns an iterable of Device objects
#         for dev in usb.core.find(find_all=True):
#             # Check for standard HID keyboard interface (Class 3, SubClass 1, Protocol 1)
#             # This is a common heuristic, but a full parser would inspect report descriptors.
#             if dev.bDeviceClass == 0x03 and dev.bDeviceSubClass == 0x01 and dev.bDeviceProtocol == 0x01:
#                 print(f"Found potential HID keyboard: {dev.idVendor:04x}:{dev.idProduct:04x}")
#                 device = dev
#                 break # Found a device, exit loop

#         if device is None:
#             print("No keyboard found. Retrying in 1 second...")
#             time.sleep(1)

#     except Exception as e:
#         print(f"Error during device scan: {e}")
#         time.sleep(1)


# # Once a device is found
# if device:
#     print(f"USB Device found: {device.idVendor:04x}:{device.idProduct:04x} - {device.manufacturer} {device.product}")

#     # Try to set configuration (usually the first one)
#     try:
#         device.set_configuration()
#         print("Configuration set.")
#     except usb.core.USBError as e:
#         print(f"Could not set configuration: {e}")
#         # This can happen if the device is already configured or busy
#         # You might need to reset the device or power cycle the MAX3421E

#     # Find the HID Interrupt IN endpoint
#     ep_in = None
#     for cfg in device:
#         for intf in cfg:
#             # Check for HID Interface (Class 3)
#             if intf.bInterfaceClass == 0x03:
#                 for ep in intf:
#                     if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN and \
#                        usb.util.endpoint_type(ep.bEndpointAddress) == usb.util.ENDPOINT_INTERRUPT:
#                         ep_in = ep
#                         print(f"Found Interrupt IN Endpoint: 0x{ep_in.bEndpointAddress:02X}")
#                         break
#             if ep_in:
#                 break
#         if ep_in:
#             break

#     if not ep_in:
#         print("No HID Interrupt IN endpoint found for the keyboard.")
#     else:
#         print("Listening for keyboard input...")
#         # Prepare a buffer for the HID report (8 bytes for standard keyboard)
#         report_buffer = bytearray(ep_in.wMaxPacketSize) # Use endpoint's max packet size

#         while True:
#             try:
#                 # Read data from the interrupt endpoint
#                 # The timeout is important to prevent blocking indefinitely
#                 data_read = device.read(ep_in.bEndpointAddress, report_buffer, timeout=100) # 100ms timeout

#                 if data_read: # If data was received
#                     process_keyboard_report(report_buffer)

#             except usb.core.USBError as e:
#                 if e.errno == 110: # errno 110 is timeout
#                     # print("No data received (timeout)")
#                     pass # Expected for interrupt endpoints when no keys are pressed
#                 else:
#                     print(f"USB Read Error: {e}")
#                     # Potentially device disconnected or other issue
#                     # You might want to re-enumerate or reset here
#                     break # Exit loop to try and re-find device
#             except Exception as e:
#                 print(f"An unexpected error occurred during read: {e}")
#                 break
#             time.sleep(0.01) # Small delay to yield to other processes
