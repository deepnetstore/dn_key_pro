# DN-KEY Pro Tools

This directory contains utility tools for the DN-KEY Pro device.

## Available Tools

### dn_key_pro_recovery.py

A comprehensive recovery and testing tool for the DN-KEY Pro ESP32-S3 device.

**Features:**
- Hardware recovery sequences
- Software recovery via esptool
- UF2 flashing with error handling
- Device detection and monitoring
- Cross-platform support (macOS, Linux, Windows*)

**Usage:**
```bash
# Run comprehensive recovery (recommended)
python3 dn_key_pro_recovery.py

# Run interactive mode
python3 dn_key_pro_recovery.py --interactive

# Run comprehensive recovery explicitly
python3 dn_key_pro_recovery.py --comprehensive
```

**Requirements:**
- Python 3.6+
- esptool (pip install esptool)
- pyserial (pip install pyserial) - optional but recommended

**OS Compatibility:**
- **macOS**: Full support - tested and working
- **Linux**: Full support - tested and working
- **Windows**: Limited support - may require additional drivers and configuration

**What it does:**
- Detects connected devices (serial, UF2 volumes, USB)
- Provides step-by-step hardware recovery guidance
- Attempts firmware flashing via esptool or UF2
- Monitors device status changes
- Tests device communication
- Comprehensive logging for troubleshooting

**When to use:**
- Device is not responding
- Firmware needs to be reflashed
- Device is stuck in bootloader mode
- Hardware recovery is needed
- Troubleshooting device connectivity issues

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required dependencies:
   ```bash
   pip install esptool pyserial
   ```
3. Run the recovery tool as needed

## Troubleshooting

- **Permission errors on Linux**: May need to add user to dialout group
- **Driver issues on Windows**: May need CH340/ESP32-S3 drivers
- **Port busy errors**: Device may be running firmware (this is normal)
- **No devices detected**: Try hardware recovery sequence

For detailed guidance, run the tool in interactive mode.
