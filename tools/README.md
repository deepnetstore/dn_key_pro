# DN-KEY Pro Tools

This directory contains utility tools for the DN-KEY Pro device.

## Available Tools

### dn_key_pro_recovery.py

A user-friendly recovery and flashing tool for the DN-KEY Pro ESP32-S3 device.

**What it does:**
1. Erases the device flash memory
2. Flashes TinyUF2 bootloader
3. Flashes CircuitPython firmware
4. Copies a sample code.py file to the device

**Features:**
- Simple 4-step recovery process
- Clear configuration variables at the top
- Robust device detection
- Color-coded output and logging
- Cross-platform support (macOS, Linux, Windows*)

**Usage:**
```bash
# Run comprehensive recovery (recommended)
python3 dn_key_pro_recovery.py

# Show help
python3 dn_key_pro_recovery.py --help
```

**Configuration:**
Before running, you **MUST** update the paths at the top of the script:

1. **TINYUF2_DIR**: Path to your TinyUF2 build directory
   ```python
   # Example: "/home/user/tinyuf2/ports/espressif"
   TINYUF2_DIR = "/path/to/your/tinyuf2/ports/espressif"
   ```

2. **CIRCUITPYTHON_UF2**: Path to your CircuitPython UF2 firmware file
   ```python
   # Example: "/home/user/firmware/dn_key_pro_circuitpython.uf2"
   CIRCUITPYTHON_UF2 = "/path/to/your/circuitpython_firmware.uf2"
   ```

3. **SAMPLE_CODE**: Path to the sample code.py file to copy to the device
   ```python
   # Example: "/home/user/examples/dc33_demo/code.py"
   SAMPLE_CODE = "/path/to/your/sample_code.py"
   ```

**Finding the required files:**

- **TinyUF2 files**: These are generated when you build TinyUF2 for the DN-KEY Pro. Look for a directory structure like:
  ```
  tinyuf2/ports/espressif/_build/deepnet_key_pro_v0r5/
  ```

- **CircuitPython UF2**: This is the CircuitPython firmware file for the DN-KEY Pro. It should have a `.uf2` extension.

- **Sample code**: You can use any CircuitPython code file, or copy one from the examples directory.

**Requirements:**
- Python 3.6+
- esptool (pip install esptool)
- pyserial (pip install pyserial) - optional but recommended

**OS Compatibility:**
- **macOS**: Full support - tested and working
- **Linux**: Full support - tested and working
- **Windows**: Limited support - may require additional drivers and configuration

**When to use:**
- Device is not responding
- Firmware needs to be reflashed
- Device is stuck in bootloader mode
- Complete device recovery is needed
- Setting up a new device

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required dependencies:
   ```bash
   pip install esptool pyserial
   ```
3. **Configure the script**: Update the paths at the top of `dn_key_pro_recovery.py`
4. Run the recovery tool

## Troubleshooting

- **Configuration errors**: The script will check all paths and report any issues
- **Permission errors on Linux**: May need to add user to dialout group
- **Driver issues on Windows**: May need CH340/ESP32-S3 drivers
- **Device not detected**: Ensure device is connected and in download mode
- **Path not found errors**: Double-check that all configured paths exist

For detailed guidance, check the log file created by the script.
