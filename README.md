# DN-KEY Pro

Advanced IoT device for educational and security research purposes.

## Overview

The DN-KEY Pro is a custom ESP32-S3-based IoT device designed for prototyping, development, and educational use. It features an OLED display, SD card slot, RGB LED, and physical buttons for interactive development.

## Hardware Features

- **Processor**: ESP32-S3 with dual-core Xtensa LX7 (reprogrammable)
- **Display**: 128x64 OLED display
- **Storage**: MicroSD card slot
- **Connectivity**: WiFi, Bluetooth LE
- **Interface**: USB-C, I2C, SPI, RGB LED, physical buttons
- **Bootloader**: TinyUF2 for easy firmware updates

## Software

- **Firmware**: CircuitPython with custom board definitions
- **Development**: Python-based development environment
- **Examples**: Comprehensive examples in the `examples/` directory
- **Tools**: Recovery and utility tools in the `tools/` directory

## Getting Started

1. **Hardware Setup**: Connect your DN-KEY Pro via USB-C
2. **Firmware**: The device comes pre-loaded with CircuitPython
3. **Development**: Copy example code to the device and start coding
4. **Examples**: Check the `examples/` directory for sample projects

## Examples

- **DC33 Demo**: Comprehensive demo showcasing some device capabilities
- **Basic Tests**: Display, pin, and connectivity tests
- **Setup Scripts**: Device configuration and setup utilities

## Development Options

The ESP32-S3 is fully reprogrammable and supports multiple development environments:

- **CircuitPython**: Python-based development (pre-installed)
- **Arduino IDE**: C/C++ development with Arduino framework
- **ESP-IDF**: Espressif's native development framework
- **PlatformIO**: Cross-platform development environment

## Documentation

- **Hardware**: Schematics and PCB files in `hardware/`
- **Firmware**: CircuitPython board definitions in `firmware/`
- **Tools**: Recovery and utility tools in `tools/`

## Recovery and Troubleshooting

If your device needs recovery or troubleshooting:
- Use the recovery tool in `tools/dn_key_pro_recovery.py`
- Follow the hardware recovery sequences
- Check the tools README for instructions

## Development

This repository contains the official DN-KEY Pro development files, examples, and documentation. For questions or support, please refer to the documentation or contact DEEPNET.

## License

Proprietary - DEEPNET LLC
