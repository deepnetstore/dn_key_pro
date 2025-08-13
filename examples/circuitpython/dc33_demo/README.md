# DN Key DC33 Demo

Enhanced DN Key demo optimized for speed, visual engagement, and stability.

## Features

### Core Capabilities
- **HID BadUSB**: Execute automated keyboard/mouse commands
- **Terminal Automation**: cmatrix, htop, system commands with visual effects
- **Data Exfiltration**: Chrome password extraction, system information collection
- **Web Navigation**: Automated browser control with globaldatapolice.com showcase
- **Mouse Jiggler**: Touch-controlled mouse movement prevention
- **Visual Feedback**: Enhanced LED animations and color-coded status

### Performance Optimizations
- **Fast Execution**: Reduced delays between commands (0.02s typing, 0.05s sequence delays)
- **Efficient Touch Response**: 0.1s polling rate for responsive control
- **Optimized HID Commands**: Streamlined key combinations and typing sequences
- **Visual Engagement**: Rainbow cycles, pulsing effects, and status indicators

### GlobalDataPolice Integration
- Automated navigation to globaldatapolice.com
- Demonstration of security commands from the help section
- Network scanning, process monitoring, and system analysis showcase
- Enhanced visual feedback during command execution

## Hardware Requirements

- DN Key (regular version, not Pro)
- Touch sensors (TOUCH1, TOUCH2)
- NeoPixel LEDs (2x on EYES pin)
- USB HID capability

## Usage

### Touch Controls
- **Touch 1**: Run next demo sequence (cycles through all demonstrations)
- **Touch 2**: Toggle mouse jiggler on/off

### Demo Sequences
1. **Terminal Automation**: Matrix effects, system monitoring
2. **Chrome Password Dump**: Cross-platform password extraction
3. **System Info Collection**: Comprehensive system information gathering
4. **GlobalDataPolice Showcase**: Security command demonstrations
5. **Web Navigation Demo**: Automated browser control

### LED Status Indicators
- **Green**: Ready/Success state
- **Blue**: Terminal/typing activity
- **Orange**: Mouse jiggler active
- **Yellow**: System info collection
- **Red**: Chrome password extraction
- **Purple**: Command execution
- **Rainbow**: Startup/sequence transitions

## Installation

1. Copy `dn_key_dc33_demo.py` to your DN Key as `code.py`
2. Or use the deployment script:
   ```bash
   ./deploy_dc33_demo.sh
   ```

## Technical Details

### Speed Optimizations
- Typing delay reduced to 0.02s per character
- Key combination delays optimized to 0.1s
- Sequence delays minimized to 0.05s
- Touch polling at 0.1s for responsive control

### Visual Enhancements
- Rainbow cycle effects for transitions
- Pulsing patterns for status indication
- Color-coded activity feedback
- Smooth LED animations

### Stability Features
- Exception handling for all demo sequences
- Automatic recovery from errors
- Touch input debouncing
- Safe HID command execution

### Data Exfiltration Capabilities
- Cross-platform Chrome password extraction (macOS/Linux)
- Comprehensive system information collection
- Timestamped file outputs
- Automatic cleanup of temporary files

## Security Disclaimer

This software is provided for educational and authorized testing purposes only. Users are responsible for ensuring they have proper authorization before using this tool on any system or network. The authors are not responsible for any misuse or damage caused by this software. Use at your own risk and in compliance with applicable laws and regulations.

## Development Notes

Based on the DN Key Pro DC33 demo but optimized for the regular DN Key hardware:
- Adapted for touch-based control instead of menu navigation
- Enhanced visual feedback using NeoPixel LEDs
- Streamlined for faster execution and better engagement
- Integrated globaldatapolice.com command showcase

Manifested by 0x0630ff x Made Evil by gh0st

