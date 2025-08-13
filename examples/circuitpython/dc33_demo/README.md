# DN-KEY Pro DC33 Demo

**⚠️ DISCLAIMER: This software is for educational and authorized testing purposes ONLY. Users must have explicit permission before testing on any system or network. The authors are not responsible for any misuse, damage, or legal consequences. Use at your own risk and in compliance with all applicable laws and regulations.**

Enhanced DN-KEY Pro demo featuring comprehensive HID automation, wireless attacks, data exfiltration, and web-based remote control.

## Features

### Core Capabilities
- **HID BadUSB**: Execute Ducky Scripts from SD card with progress tracking
- **WiFi Attacks**: Evil Twin, SSID Spam, Network Scanning, WiFi Status monitoring
- **BLE Operations**: Device scanning, Apple Spam attacks
- **Data Exfiltration**: Chrome password extraction, system information collection
- **Web Control Interface**: Remote OS control via WiFi with OS-specific commands
- **Mouse Jiggler**: Random mouse movements to prevent screen lock
- **USB Host**: Read from USB devices as keyboard input
- **System Status**: Real-time system monitoring and status display

### Hardware Integration
- **Physical Buttons**: Navigate through menus and control functions
- **OLED Display**: Visual feedback and menu navigation with progress bars
- **RGB LEDs**: Status indicators and visual effects
- **WiFi Access Point**: Web interface accessible via device network
- **SD Card Support**: Load and execute Ducky Scripts from SD card
- **USB HID**: Full keyboard, mouse, and media control capabilities

## Hardware Requirements

- DN-KEY Pro (ESP32-S3 based)
- Physical buttons (SWITCH_1, SWITCH_2, BOOT0)
- OLED display (128x64)
- RGB LEDs (2x on EYES pin)
- WiFi radio
- USB HID capability
- SD card (optional, for Ducky Scripts)

## Usage

### Physical Button Controls
- **SWITCH_1**: Navigate up/previous menu item
- **SWITCH_2**: Navigate down/next menu item  
- **BOOT0**: Select/confirm menu item or action

### Main Menu Options
1. **HID BadUSB**: Execute Ducky Scripts from SD card
2. **WiFi Attacks**: Evil Twin, SSID Spam, Network Scanning
3. **BLE Ops**: Bluetooth device scanning and Apple Spam
4. **Data Exfil**: Chrome passwords and system information
5. **Web Control**: Remote control via web interface
6. **Mouse Jiggler**: Toggle random mouse movements
7. **USB Host**: Read from USB devices
8. **System Status**: Monitor system status

### Web Interface
- **Connect to WiFi**: Device creates network "DN-KEY-PRO-XXXX"
- **Access Web Interface**: Visit `http://192.168.4.1` in browser
- **OS-Specific Controls**: Choose your operating system (macOS, Windows, Linux)
- **Execute Commands**: Use media controls, custom commands, or mouse jiggler

### LED Status Indicators
- **Green**: Ready/Success state
- **Blue**: Menu navigation
- **Orange**: Power bank mode
- **Red**: Error state
- **Rainbow**: Startup sequence
- **Pulsing**: Active functions

## Installation

1. Copy `code.py` to your DN-KEY Pro device
2. Optionally add Ducky Scripts to SD card root directory
3. The device will automatically start with menu system
4. For web interface: Connect to device's WiFi network and visit `http://192.168.4.1`

## Development Notes

This demo showcases the full capabilities of the DN-KEY Pro:
- Modular code structure with separate components
- Power bank compatibility for portable use
- Comprehensive attack vector demonstration
- Physical button navigation for standalone operation
- Error handling and recovery
- Demo of data exfiltration capabilities
- Integrated web-based remote control interface

For demonstrations, testing, and learning DN-KEY Pro development.

Manifested by 0x0630ff x Made Evil by gh0st

