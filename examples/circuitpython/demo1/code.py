'''
DN Duck.

This code uses a modified Adafruit Ducky Script circuitpython code.
It has been adapted to report the 'percentage' complete of the Ducky script running.
It will report back an Integer value from 0-100; 100 being the completed value.
This value is fed into the Progressbar to be drawn just before running the ducky scripts 
HID command.

How does the display code work?

First, each menu class will be given a list of 'MenuItems' which will hold a text string, 
a function and any possible arguments to pass to the callback function.
eg: 
`main_menu_items = [
    MenuItem("Ducky Script", load_ducky_menu, "DUCKS!"),
    ...
]`
notice this 'main_menu_items' list is passed to the main_menu class object next.
See the MenuItem Class definition for more detail.

Then you will create a Class to hold the information, give it a title and pass in the menuitems
eg: 
`main_menu = Menu("Main Menu", main_menu_items)`

then call the draw method for that class to draw on the display_group.
eg: 
`main_menu.draw(display_group)`
'''

import time
import array
import sys
import supervisor
import usb
import terminalio

from adafruit_display_text import label

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)

# import local .py files
from dn_key_pro import *


# update the current_view variable
def set_current_view(new_view):
    global current_menu
    current_menu = new_view


# Class to implement the Main menu, 
# this inherits from the MenuBase class
class MainMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=0x00F000, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group)
        

# Class to implement the Ducky sctip menu, 
# this inherits from the MenuBase class
class DuckyMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_ {self.title}", color=0x00F000, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


# Class for implementing USB Host device
class USBHostMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=0x00F000, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


# wifi menu setup
class WiFiMenu(MenuBase):
    def draw(self, group):
        print("drawing wifi main menu")
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=0xF00090, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)
        

# the wifi settings
class WiFiSettingsMenu(MenuBase):
    def draw(self, group):
        print("drawing wifi settings menu")
        clear_group()
        # todo: add a solid black box over background



# load the wifi settings screen
def load_wifi_settings_screen(user_data=None):
    print("wifi settings")
    time.sleep(0.01)
    wifi_settings = WiFiSettingsMenu("WiFi Settings")
    wifi_settings.draw(display_group) # todo: finish this function
    

# function calls to load when MenuItems are selected.
def load_new_menu(user_data=None):
    print("Loading New Menu")
    print("user_data:", user_data)
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
        # time.sleep(0.01)


def read_usb_host_keyboard(device=None):
    print("reading from usb host as keyboard")
    global usbhost_menu
    clear_group()
    info_text = label.Label(terminalio.FONT, text="[hit escape to end]", color=0xF000F0, x=170, y=10)
    display_group.append(info_text)
    text_area = label.Label(terminalio.FONT, text="", color=0xF0F0FF, x=10, y=20, scale=2)
    display_group.append(text_area)
    start_kbd_read_task(device, text_area)


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
    time.sleep(0.25)
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
    ducky_menu = DuckyMenu("Ducky Script", ducky_menu_items)
    print("trying to load Ducky Menu")
    print("user_data:", user_data)  # show the argument passed to the MenuItem constructor
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

    clear_group()

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
    global display_group
    clear_group()
    menu_to_return.draw(display_group)
    set_current_view(menu_to_return)


def back_menu_item(back_to_menu):
    return MenuItem("< Back", go_back_to, back_to_menu),


def load_wifi_menu_screen(user_data=None):
    global wifi_menu, main_menu
    print("load wifi menu screen")
    menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Settings", load_wifi_settings_screen),
        MenuItem("Attacks", EmptyFunc),
        MenuItem("Sniff", EmptyFunc),
        MenuItem("Connect", EmptyFunc),
        MenuItem("Start AP", EmptyFunc),
    ]
    wifi_menu = WiFiMenu("Wifi Menu", menu_items)
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
        MenuItem("Ducky Script", load_ducky_menu, "DUCKS!"),  # third item in MenuItem is the passed argument, optional
        MenuItem("USB Host", load_usb_host_screen),
        MenuItem("WiFi", load_wifi_menu_screen),
        MenuItem("SDCard", load_sd_card_menu_screen)
    ]

    global main_menu
    main_menu = MainMenu("Main Menu", main_menu_items)
    main_menu.draw(display_group)
    
    # set the current_menu to the desired starting view
    global current_menu
    current_menu = main_menu

    # Main Loop
    print("looping")
    while True:
        current_menu.handle_input(buttons, display_group)
        time.sleep(0.015)

if __name__ == "__main__":
    print("starting")
    main()
