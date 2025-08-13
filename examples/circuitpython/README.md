# CircuitPython Examples

This directory contains CircuitPython examples and demos for the DN-KEY Pro device.

## Using Examples

Each subdirectory contains a complete example that can be copied to your DN-KEY Pro device.

### Installation Instructions

1. **Copy to Device**: Copy the entire contents of any example folder to your DN-KEY Pro device
2. **Main File**: Ensure `code.py` is in the root of the device (not in a subfolder)
3. **Libraries**: Some examples include required CircuitPython libraries in the `lib/` folder
4. **Assets**: Examples may include images, settings files, or other assets
5. **Configuration**: Check for `settings.toml` or other config files

### Quick Start

```bash
# Copy any example to your device
cp -r examples/circuitpython/[example_name]/* /path/to/dn_key_pro_device/
```

## Device Requirements

- DN-KEY Pro with CircuitPython firmware
- MicroSD card (for examples using SD card features)
- USB connection or power bank

## Troubleshooting

- Ensure all files are copied to the device root
- Check that required libraries are present
- Verify the device has sufficient power
- Monitor serial output for error messages
- Check example-specific README files for additional instructions

## Development

To create your own examples:
1. Start with an existing example as a template
2. Add your custom code to `code.py`
3. Include any required libraries in `lib/`
4. Add a README.md with specific instructions
5. Test thoroughly before distribution