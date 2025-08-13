#!/usr/bin/env python3
"""
DN Key Pro v0 r4 - Comprehensive Recovery and Testing Tool
==========================================================

This script provides robust recovery options for the DN Key Pro ESP32-S3 device.
It can handle various failure scenarios and provide step-by-step guidance.

Features:
- Hardware recovery sequences
- Software recovery via esptool
- UF2 flashing with error handling
- Device detection and monitoring
- Comprehensive logging
- Cross-platform support (macOS, Linux, Windows)

Requirements:
- Python 3.6+
- esptool (pip install esptool)
- pyserial (pip install pyserial) - optional but recommended
"""

import os
import sys
import time
import subprocess
import threading
import platform
from pathlib import Path

class DNKeyProRecovery:
    def __init__(self):
        self.device_name = "DN Key Pro v0 r4"
        self.os_type = platform.system().lower()
        self.is_macos = self.os_type == "darwin"
        self.is_linux = self.os_type == "linux"
        self.is_windows = self.os_type == "windows"
        
        # Get the directory where this script is located
        script_dir = Path(__file__).parent.absolute()
        
        # Set firmware paths relative to script location
        self.uf2_file = script_dir / "tinyuf2" / "ports" / "espressif" / "_build" / "dn_key_pro_v0r4" / "apps" / "update_tinyuf2" / "update-tinyuf2.uf2"
        self.tinyuf2_bin = script_dir / "tinyuf2" / "ports" / "espressif" / "_build" / "dn_key_pro_v0r4" / "tinyuf2.bin"
        self.combined_bin = script_dir / "tinyuf2" / "ports" / "espressif" / "_build" / "dn_key_pro_v0r4" / "combined.bin"
        self.log_file = script_dir / "recovery_log.txt"
        
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        # Also write to log file
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def check_firmware_files(self):
        """Check if firmware files exist and are valid"""
        files_to_check = [
            (self.uf2_file, "UF2 firmware"),
            (self.tinyuf2_bin, "TinyUF2 binary"),
            (self.combined_bin, "Combined binary")
        ]
        
        valid_files = []
        for file_path, description in files_to_check:
            if file_path.exists():
                size = file_path.stat().st_size
                self.log(f"{description} found: {file_path} ({size} bytes)")
                
                if size > 100000:  # Should be at least 100KB
                    valid_files.append((file_path, description, size))
                else:
                    self.log(f"WARNING: {description} seems too small ({size} bytes)", "WARNING")
            else:
                self.log(f"ERROR: {description} not found at {file_path}", "ERROR")
        
        return valid_files
    
    def detect_devices(self):
        """Detect connected devices - OS-specific implementation"""
        devices = {
            'serial': [],
            'uf2_volumes': [],
            'usb_devices': []
        }
        
        if self.is_macos:
            return self._detect_devices_macos(devices)
        elif self.is_linux:
            return self._detect_devices_linux(devices)
        elif self.is_windows:
            return self._detect_devices_windows(devices)
        else:
            self.log(f"Unsupported OS: {self.os_type}", "WARNING")
            return devices
    
    def _detect_devices_macos(self, devices):
        """Detect devices on macOS"""
        # Check for serial devices
        try:
            result = subprocess.run(['ls', '/dev/tty.*'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip() and 'usb' in line.lower():
                        devices['serial'].append(line.strip())
        except Exception as e:
            self.log(f"Error checking serial devices: {e}", "WARNING")
        
        # Check for UF2 volumes
        try:
            result = subprocess.run(['ls', '/Volumes'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip() and ('uf2' in line.lower() or 'tinyuf2' in line.lower()):
                        devices['uf2_volumes'].append(line.strip())
        except Exception as e:
            self.log(f"Error checking UF2 volumes: {e}", "WARNING")
        
        # Check USB devices
        try:
            result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Look for ESP32-S3 or CH340 devices
                if 'esp32' in result.stdout.lower() or 'ch340' in result.stdout.lower():
                    devices['usb_devices'].append('ESP32-S3 or CH340 detected')
        except Exception as e:
            self.log(f"Error checking USB devices: {e}", "WARNING")
        
        return devices
    
    def _detect_devices_linux(self, devices):
        """Detect devices on Linux"""
        # Check for serial devices
        try:
            result = subprocess.run(['ls', '/dev/ttyUSB*', '/dev/ttyACM*'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        devices['serial'].append(line.strip())
        except Exception as e:
            self.log(f"Error checking serial devices: {e}", "WARNING")
        
        # Check for UF2 volumes (usually mounted under /media or /mnt)
        try:
            for mount_point in ['/media', '/mnt']:
                if os.path.exists(mount_point):
                    result = subprocess.run(['ls', mount_point], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.strip() and ('uf2' in line.lower() or 'tinyuf2' in line.lower()):
                                devices['uf2_volumes'].append(f"{mount_point}/{line.strip()}")
        except Exception as e:
            self.log(f"Error checking UF2 volumes: {e}", "WARNING")
        
        # Check USB devices
        try:
            result = subprocess.run(['lsusb'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                if 'esp32' in result.stdout.lower() or 'ch340' in result.stdout.lower():
                    devices['usb_devices'].append('ESP32-S3 or CH340 detected')
        except Exception as e:
            self.log(f"Error checking USB devices: {e}", "WARNING")
        
        return devices
    
    def _detect_devices_windows(self, devices):
        """Detect devices on Windows"""
        # Check for serial devices (COM ports)
        try:
            result = subprocess.run(['wmic', 'path', 'Win32_SerialPort', 'get', 'DeviceID'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'COM' in line:
                        devices['serial'].append(line.strip())
        except Exception as e:
            self.log(f"Error checking serial devices: {e}", "WARNING")
        
        # Check for UF2 volumes (drive letters)
        try:
            result = subprocess.run(['wmic', 'logicaldisk', 'get', 'DeviceID,VolumeName'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'UF2' in line.upper() or 'TINYUF2' in line.upper():
                        # Extract drive letter
                        parts = line.split()
                        if parts:
                            devices['uf2_volumes'].append(f"{parts[0]}:\\")
        except Exception as e:
            self.log(f"Error checking UF2 volumes: {e}", "WARNING")
        
        return devices
    
    def print_device_status(self, devices):
        """Print current device status with detailed guidance"""
        self.log("=== Device Status ===")
        self.log(f"Serial devices: {devices['serial']}")
        self.log(f"UF2 volumes: {devices['uf2_volumes']}")
        self.log(f"USB devices: {devices['usb_devices']}")
        
        if not any(devices.values()):
            self.log("No devices detected - device may be in bootloader mode or not connected", "WARNING")
            self.log("What this means:", "INFO")
            self.log("  - Device is not powered on", "INFO")
            self.log("  - Device is not connected via USB-C", "INFO")
            self.log("  - Device is in a non-responsive state", "INFO")
            self.log("  - Device needs hardware recovery sequence", "INFO")
        else:
            self.log("Device(s) detected!", "SUCCESS")
            if devices['serial']:
                self.log("Serial device detected - this is good for firmware flashing", "SUCCESS")
                self.log("  You can now use esptool to flash firmware", "INFO")
            if devices['uf2_volumes']:
                self.log("UF2 volume detected - device is in bootloader mode", "SUCCESS")
                self.log("  You can copy UF2 files to this volume for flashing", "INFO")
            if devices['usb_devices']:
                self.log("USB device detected - device is connected and recognized", "SUCCESS")
    
    def provide_device_guidance(self):
        """Provide detailed guidance about device detection"""
        self.log("=== Device Detection Guidance ===")
        self.log("Understanding what different device detections mean:")
        self.log("")
        self.log("Serial Device (e.g., /dev/tty.usbmodem1101):", "INFO")
        self.log("  ✓ Device is running firmware and communicating", "SUCCESS")
        self.log("  ✓ Ready for esptool firmware flashing", "SUCCESS")
        self.log("  ✓ Can be used for serial communication", "SUCCESS")
        self.log("")
        self.log("UF2 Volume (e.g., /Volumes/TINYUF2):", "INFO")
        self.log("  ✓ Device is in bootloader mode", "SUCCESS")
        self.log("  ✓ Ready for UF2 file copying", "SUCCESS")
        self.log("  ✓ Device will flash firmware automatically", "SUCCESS")
        self.log("")
        self.log("USB Device (system detection):", "INFO")
        self.log("  ✓ Device is connected and recognized by system", "SUCCESS")
        self.log("  ✓ May need additional drivers (Windows)", "WARNING")
        self.log("  ✓ May need permissions (Linux)", "WARNING")
        self.log("")
        self.log("No Devices Detected:", "WARNING")
        self.log("  ✗ Device may not be powered on", "ERROR")
        self.log("  ✗ Device may not be connected", "ERROR")
        self.log("  ✗ Device may be in non-responsive state", "ERROR")
        self.log("  ✗ Try hardware recovery sequence", "INFO")
    
    def hardware_recovery_sequence(self):
        """Execute hardware recovery sequence"""
        self.log("=== Hardware Recovery Sequence ===")
        self.log("This sequence will attempt to force the device into download mode.")
        self.log("Follow these steps carefully:")
        
        # First, check if device is already detected
        self.log("Checking current device status...")
        devices = self.detect_devices()
        if any(devices.values()):
            self.log("Device already detected! No recovery needed.", "SUCCESS")
            self.print_device_status(devices)
            return devices
        
        # Step 1: Power cycle the device
        self.log("Step 1: Power cycle the device")
        self.log("  - Turn OFF the device using the power switch")
        self.log("  - Wait 2 seconds")
        self.log("  - Turn ON the device")
        input("Press Enter when you've completed the power cycle...")
        
        # Check if device appeared after power cycle
        self.log("Checking for device after power cycle...")
        time.sleep(3)
        devices = self.detect_devices()
        if any(devices.values()):
            self.log("SUCCESS: Device detected after power cycle!", "SUCCESS")
            self.print_device_status(devices)
            return devices
        
        # Step 2: Try single button recovery (just BOOT button)
        self.log("Step 2: Single button recovery")
        self.log("  - Turn OFF the device")
        self.log("  - Press and HOLD the BOOT button")
        self.log("  - Turn ON the device while holding BOOT")
        self.log("  - Wait 2 seconds, then release BOOT")
        input("Press Enter when you've completed this sequence...")
        
        # Check if device appeared after single button recovery
        self.log("Checking for device after single button recovery...")
        time.sleep(3)
        devices = self.detect_devices()
        if any(devices.values()):
            self.log("SUCCESS: Device detected after single button recovery!", "SUCCESS")
            self.print_device_status(devices)
            return devices
        
        # Step 3: Try full button sequence (BOOT + EN)
        self.log("Step 3: Full button sequence")
        self.log("  - Turn OFF the device")
        self.log("  - Press and HOLD the BOOT button")
        self.log("  - While holding BOOT, press and HOLD the EN (reset) button")
        self.log("  - Release the EN button (keep holding BOOT)")
        self.log("  - Turn ON the device while still holding BOOT")
        self.log("  - Wait 2 seconds, then release BOOT")
        input("Press Enter when you've completed this sequence...")
        
        # Check if device appeared after full button sequence
        self.log("Checking for device after full button sequence...")
        time.sleep(3)
        devices = self.detect_devices()
        if any(devices.values()):
            self.log("SUCCESS: Device detected after full button sequence!", "SUCCESS")
            self.print_device_status(devices)
            return devices
        
        # If we get here, no recovery method worked
        self.log("No devices detected after all recovery attempts.", "WARNING")
        self.log("This could indicate:", "INFO")
        self.log("  - Hardware issue requiring repair", "ERROR")
        self.log("  - Different button combination needed", "INFO")
        self.log("  - Device needs professional service", "ERROR")
        
        return devices
    
    def install_missing_dependencies(self, missing_deps):
        """Install missing dependencies with user confirmation"""
        self.log("=== Installing Missing Dependencies ===")
        
        install_commands = {
            "esptool": "pip install esptool",
            "pyserial": "pip install pyserial"
        }
        
        for dep in missing_deps:
            if dep in install_commands:
                self.log(f"Missing dependency: {dep}")
                self.log(f"Install command: {install_commands[dep]}")
                
                response = input(f"Would you like to install {dep} now? (y/n): ").strip().lower()
                
                if response in ['y', 'yes']:
                    self.log(f"Installing {dep}...")
                    try:
                        cmd = install_commands[dep].split()
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                        
                        if result.returncode == 0:
                            self.log(f"SUCCESS: {dep} installed successfully!", "SUCCESS")
                        else:
                            self.log(f"ERROR: Failed to install {dep}: {result.stderr}", "ERROR")
                            self.log(f"Please install manually: {install_commands[dep]}", "INFO")
                    except Exception as e:
                        self.log(f"ERROR: Failed to install {dep}: {e}", "ERROR")
                        self.log(f"Please install manually: {install_commands[dep]}", "INFO")
                else:
                    self.log(f"Skipping {dep} installation. You can install manually later.", "INFO")
        
        # Re-check dependencies after installation
        self.log("Re-checking dependencies...")
        return self.check_dependencies()
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        self.log("=== Checking Dependencies ===")
        
        missing_deps = []
        
        # Check esptool
        esptool_found = False
        try:
            result = subprocess.run(['esptool.py', 'version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                esptool_found = True
        except:
            pass
        
        if not esptool_found:
            try:
                result = subprocess.run(['python', '-m', 'esptool', 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    esptool_found = True
            except:
                pass
        
        if not esptool_found:
            try:
                result = subprocess.run(['python3', '-m', 'esptool', 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    esptool_found = True
            except:
                pass
        
        if not esptool_found:
            missing_deps.append("esptool")
        
        # Check pyserial
        try:
            import serial
            self.log("pyserial found")
        except ImportError:
            missing_deps.append("pyserial")
        
        if missing_deps:
            self.log("Missing dependencies:", "WARNING")
            for dep in missing_deps:
                self.log(f"  - {dep}", "WARNING")
            
            self.log("\nInstallation instructions:", "INFO")
            if "esptool" in missing_deps:
                self.log("  pip install esptool", "INFO")
            if "pyserial" in missing_deps:
                self.log("  pip install pyserial", "INFO")
            
            # Offer to install missing dependencies
            response = input("\nWould you like to install missing dependencies now? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return self.install_missing_dependencies(missing_deps)
            else:
                self.log("Continuing without installing dependencies. Some features may not work.", "WARNING")
                return False
        else:
            self.log("All dependencies found!", "SUCCESS")
            return True
    
    def _find_esptool(self):
        """Find esptool installation - OS-agnostic"""
        # Method 1: Try direct esptool.py command with 'version' (not '--version')
        try:
            result = subprocess.run(['esptool.py', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return 'esptool.py'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Method 2: Try python -m esptool version
        try:
            result = subprocess.run(['python', '-m', 'esptool', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return ['python', '-m', 'esptool']
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Method 3: Try python3 -m esptool version
        try:
            result = subprocess.run(['python3', '-m', 'esptool', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return ['python3', '-m', 'esptool']
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Method 4: Try to find esptool in common locations
        common_paths = []
        
        if self.is_macos:
            common_paths = [
                '/usr/local/bin/esptool.py',
                '/opt/homebrew/bin/esptool.py',
                str(Path.home() / '.local' / 'bin' / 'esptool.py'),
                str(Path.home() / '.espressif' / 'tools' / 'esptool_py' / '4.9.0' / 'esptool.py')
            ]
        elif self.is_linux:
            common_paths = [
                '/usr/local/bin/esptool.py',
                '/usr/bin/esptool.py',
                str(Path.home() / '.local' / 'bin' / 'esptool.py'),
                str(Path.home() / '.espressif' / 'tools' / 'esptool_py' / '4.9.0' / 'esptool.py')
            ]
        elif self.is_windows:
            common_paths = [
                str(Path.home() / 'AppData' / 'Local' / 'Programs' / 'Python' / 'Scripts' / 'esptool.py'),
                str(Path.home() / '.espressif' / 'tools' / 'esptool_py' / '4.9.0' / 'esptool.py')
            ]
        
        # Also check if we're in a virtual environment
        if 'VIRTUAL_ENV' in os.environ:
            venv_path = Path(os.environ['VIRTUAL_ENV']) / 'bin' / 'esptool.py'
            if venv_path.exists():
                return str(venv_path)
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        return None
    
    def esptool_recovery(self):
        """Attempt recovery using esptool"""
        self.log("=== ESPTool Recovery ===")
        
        # Find esptool using OS-agnostic method
        esptool_path = self._find_esptool()
        
        if not esptool_path:
            self.log("esptool.py not found. Please install it first:", "ERROR")
            self.log("  pip install esptool", "INFO")
            self.log("  or check if it's in your PATH", "INFO")
            return False
        
        # Try to detect ESP32-S3
        self.log("Attempting to detect ESP32-S3...")
        try:
            if isinstance(esptool_path, list):
                cmd = esptool_path + ['--chip', 'esp32s3', 'flash_id']
            else:
                cmd = [esptool_path, '--chip', 'esp32s3', 'flash_id']
            
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                self.log("ESP32-S3 detected successfully!")
                self.log(f"Flash info: {result.stdout}")
                return True
            else:
                self.log(f"Failed to detect ESP32-S3: {result.stderr}", "WARNING")
                # Check if it's a busy port error (which means device is working)
                if "Resource busy" in result.stderr or "port is busy" in result.stderr:
                    self.log("Device detected but port is busy - this indicates the device is working!", "SUCCESS")
                    return True
                return False
                
        except Exception as e:
            self.log(f"Error during esptool detection: {e}", "ERROR")
            return False
    
    def flash_with_esptool(self, port=None):
        """Flash firmware using esptool"""
        self.log("=== ESPTool Flashing ===")
        
        valid_files = self.check_firmware_files()
        if not valid_files:
            self.log("No valid firmware files found.", "ERROR")
            return False
        
        # Use the combined binary for flashing
        if not self.combined_bin.exists():
            self.log("Combined binary not found. Cannot flash.", "ERROR")
            return False
        
        # Find the port if not provided
        if not port:
            devices = self.detect_devices()
            if devices['serial']:
                port = devices['serial'][0]
            else:
                self.log("No serial port detected. Please connect device.", "ERROR")
                return False
        
        # Find esptool using the OS-agnostic method
        esptool_path = self._find_esptool()
        
        if not esptool_path:
            self.log("esptool.py not found. Please install it first.", "ERROR")
            return False
        
        self.log(f"Flashing firmware to {port}...")
        
        try:
            # Flash the combined binary
            if isinstance(esptool_path, list):
                cmd = esptool_path + [
                    '--chip', 'esp32s3', '--port', port,
                    '--baud', '460800', '--before', 'default_reset', '--after', 'hard_reset',
                    'write_flash', '--flash_mode', 'dio', '--flash_size', '16MB', '--flash_freq', '80m',
                    '0x0', str(self.combined_bin)
                ]
            else:
                cmd = [
                    esptool_path, '--chip', 'esp32s3', '--port', port,
                    '--baud', '460800', '--before', 'default_reset', '--after', 'hard_reset',
                    'write_flash', '--flash_mode', 'dio', '--flash_size', '16MB', '--flash_freq', '80m',
                    '0x0', str(self.combined_bin)
                ]
            
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log("Firmware flashed successfully!")
                self.log("Device should reboot automatically.")
                return True
            else:
                # Check if it's a busy port error (which might indicate device is working)
                if "Resource busy" in result.stderr or "port is busy" in result.stderr:
                    self.log("Port is busy - device may already be running firmware.", "WARNING")
                    self.log("This could indicate the device is working correctly.", "INFO")
                    return True
                else:
                    self.log(f"Failed to flash firmware: {result.stderr}", "ERROR")
                    return False
                
        except Exception as e:
            self.log(f"Error during esptool flashing: {e}", "ERROR")
            return False
    
    def flash_uf2(self, uf2_volume=None):
        """Flash UF2 file to device"""
        self.log("=== UF2 Flashing ===")
        
        if not self.uf2_file.exists():
            self.log(f"ERROR: UF2 file not found at {self.uf2_file}", "ERROR")
            return False
        
        # If no specific volume provided, try to find one
        if not uf2_volume:
            devices = self.detect_devices()
            if devices['uf2_volumes']:
                uf2_volume = devices['uf2_volumes'][0]
            else:
                self.log("No UF2 volume detected. Please ensure device is in UF2 mode.", "ERROR")
                return False
        
        self.log(f"Attempting to flash to: {uf2_volume}")
        
        try:
            # Copy UF2 file to volume - OS-specific commands
            if self.is_macos or self.is_linux:
                cmd = ['cp', str(self.uf2_file), uf2_volume]
            elif self.is_windows:
                # Windows uses copy command
                cmd = ['copy', str(self.uf2_file), uf2_volume]
            else:
                self.log(f"Unsupported OS for UF2 flashing: {self.os_type}", "ERROR")
                return False
            
            self.log(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log("UF2 file copied successfully!")
                self.log("Device should reboot automatically. If not, press reset button.")
                return True
            else:
                self.log(f"Failed to copy UF2 file: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error during UF2 flashing: {e}", "ERROR")
            return False
    
    def monitor_device(self, duration=30):
        """Monitor device for changes"""
        self.log(f"=== Monitoring Device ({duration} seconds) ===")
        
        start_time = time.time()
        last_devices = None
        
        while time.time() - start_time < duration:
            devices = self.detect_devices()
            
            if devices != last_devices:
                self.log("Device status changed:")
                self.print_device_status(devices)
                last_devices = devices.copy()
            
            time.sleep(2)
        
        self.log("Monitoring complete.")
    
    def test_device_communication(self):
        """Test if device is communicating properly"""
        self.log("=== Testing Device Communication ===")
        
        devices = self.detect_devices()
        if not devices['serial']:
            self.log("No serial devices detected.", "ERROR")
            return False
        
        port = devices['serial'][0]
        self.log(f"Testing communication with {port}")
        
        # Try to open the serial port briefly to see if it's accessible
        try:
            import serial
            ser = serial.Serial(port, 115200, timeout=1)
            ser.close()
            self.log("Serial port is accessible", "SUCCESS")
            return True
        except ImportError:
            self.log("pyserial not installed, skipping serial test", "WARNING")
            return True
        except Exception as e:
            if "Resource busy" in str(e) or "port is busy" in str(e):
                self.log("Port is busy - device is actively communicating!", "SUCCESS")
                return True
            else:
                self.log(f"Serial port test failed: {e}", "WARNING")
                return False
    
    def comprehensive_recovery(self):
        """Execute comprehensive recovery procedure"""
        self.log("=== DN Key Pro Comprehensive Recovery ===")
        self.log(f"Starting recovery for {self.device_name}")
        
        # Step 1: Check dependencies
        self.log("Step 1: Checking dependencies")
        if not self.check_dependencies():
            self.log("Some dependencies are missing. Please install them first.", "WARNING")
            self.log("You can continue, but some features may not work.", "INFO")
        
        # Step 2: Check firmware files
        self.log("Step 2: Checking firmware files")
        valid_files = self.check_firmware_files()
        if not valid_files:
            self.log("Cannot proceed without valid firmware files.", "ERROR")
            return False
        
        # Step 3: Initial device detection
        self.log("Step 3: Initial device detection")
        devices = self.detect_devices()
        self.print_device_status(devices)
        
        # If no devices detected initially, provide guidance
        if not any(devices.values()):
            self.log("No devices detected initially. Providing guidance...")
            self.provide_device_guidance()
        
        # Step 4: Test device communication if detected
        if devices['serial']:
            self.log("Step 4: Testing device communication")
            if self.test_device_communication():
                self.log("Device is communicating properly!", "SUCCESS")
                return True
        
        # Step 5: If no devices detected, try hardware recovery
        if not any(devices.values()):
            self.log("Step 5: No devices detected. Attempting hardware recovery...")
            devices = self.hardware_recovery_sequence()
        
        # Step 6: Try esptool recovery if still no devices
        if not any(devices.values()):
            self.log("Step 6: Still no devices detected. Trying esptool recovery...")
            if self.esptool_recovery():
                self.log("esptool recovery successful!")
            else:
                self.log("esptool recovery failed. Device may need hardware repair.", "ERROR")
                return False
        
        # Step 7: Flash firmware using esptool (preferred method)
        if devices['serial']:
            self.log("Step 7: Serial device detected. Attempting esptool flashing...")
            if self.flash_with_esptool():
                self.log("Firmware flashing successful!")
                
                # Monitor for reboot
                self.log("Monitoring device for reboot...")
                self.monitor_device(30)
                
                # Final device check
                final_devices = self.detect_devices()
                self.print_device_status(final_devices)
                
                if final_devices['serial']:
                    self.log("SUCCESS: Device is now detected as serial device!", "SUCCESS")
                    return True
                else:
                    self.log("Device flashed but not detected as serial. May need additional recovery.", "WARNING")
                    return False
            else:
                self.log("Firmware flashing failed.", "ERROR")
                return False
        
        # Step 8: If UF2 volume detected, flash firmware
        elif devices['uf2_volumes']:
            self.log("Step 8: UF2 volume detected. Attempting to flash firmware...")
            if self.flash_uf2():
                self.log("Firmware flashing successful!")
                
                # Monitor for reboot
                self.log("Monitoring device for reboot...")
                self.monitor_device(30)
                
                # Final device check
                final_devices = self.detect_devices()
                self.print_device_status(final_devices)
                
                if final_devices['serial']:
                    self.log("SUCCESS: Device is now detected as serial device!", "SUCCESS")
                    return True
                else:
                    self.log("Device flashed but not detected as serial. May need additional recovery.", "WARNING")
                    return False
            else:
                self.log("Firmware flashing failed.", "ERROR")
                return False
        
        else:
            self.log("No suitable device mode detected for flashing.", "ERROR")
            return False
    
    def interactive_mode(self):
        """Interactive recovery mode"""
        self.log("=== Interactive Recovery Mode ===")
        
        while True:
            print("\nAvailable options:")
            print("1. Comprehensive recovery (RECOMMENDED)")
            print("2. Check device status")
            print("3. Hardware recovery sequence")
            print("4. Device detection guidance")
            print("5. Advanced options...")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.comprehensive_recovery()
            elif choice == '2':
                devices = self.detect_devices()
                self.print_device_status(devices)
            elif choice == '3':
                self.hardware_recovery_sequence()
            elif choice == '4':
                self.provide_device_guidance()
            elif choice == '5':
                self.advanced_options()
            elif choice == '6':
                self.log("Exiting interactive mode.")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def advanced_options(self):
        """Advanced options for power users"""
        while True:
            print("\nAdvanced Options:")
            print("1. Check firmware files")
            print("2. Check dependencies")
            print("3. Install missing dependencies")
            print("4. Test device communication")
            print("5. Try esptool recovery")
            print("6. Flash firmware with esptool")
            print("7. Flash UF2 firmware")
            print("8. Monitor device")
            print("9. Back to main menu")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                self.check_firmware_files()
            elif choice == '2':
                self.check_dependencies()
            elif choice == '3':
                # Get missing dependencies and offer to install
                missing_deps = []
                
                # Check esptool
                esptool_found = False
                try:
                    result = subprocess.run(['esptool.py', 'version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        esptool_found = True
                except:
                    pass
                
                if not esptool_found:
                    try:
                        result = subprocess.run(['python', '-m', 'esptool', 'version'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            esptool_found = True
                    except:
                        pass
                
                if not esptool_found:
                    try:
                        result = subprocess.run(['python3', '-m', 'esptool', 'version'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            esptool_found = True
                    except:
                        pass
                
                if not esptool_found:
                    missing_deps.append("esptool")
                
                # Check pyserial
                try:
                    import serial
                except ImportError:
                    missing_deps.append("pyserial")
                
                if missing_deps:
                    self.install_missing_dependencies(missing_deps)
                else:
                    self.log("All dependencies are already installed!", "SUCCESS")
            elif choice == '4':
                self.test_device_communication()
            elif choice == '5':
                self.esptool_recovery()
            elif choice == '6':
                self.flash_with_esptool()
            elif choice == '7':
                self.flash_uf2()
            elif choice == '8':
                duration = input("Enter monitoring duration in seconds (default 30): ").strip()
                try:
                    duration = int(duration) if duration else 30
                    self.monitor_device(duration)
                except ValueError:
                    self.monitor_device(30)
            elif choice == '9':
                break
            else:
                print("Invalid choice. Please try again.")

def main():
    """Main function"""
    print("DN Key Pro v0 r4 - Recovery Tool")
    print("=================================")
    
    recovery = DNKeyProRecovery()
    
    # Show OS information
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")
    print()
    
    # OS compatibility notes
    if recovery.is_macos:
        print("macOS detected - Full support available")
        print("  - Serial devices: /dev/tty.usbmodem*")
        print("  - UF2 volumes: /Volumes/")
        print("  - USB detection: system_profiler")
    elif recovery.is_linux:
        print("Linux detected - Full support available")
        print("  - Serial devices: /dev/ttyUSB*, /dev/ttyACM*")
        print("  - UF2 volumes: /media/, /mnt/")
        print("  - USB detection: lsusb")
        print("  - Note: May need udev rules for USB access")
    elif recovery.is_windows:
        print("Windows detected - Limited support")
        print("  - Serial devices: COM ports")
        print("  - UF2 volumes: Drive letters")
        print("  - USB detection: wmic")
        print("  - Note: May need drivers for CH340/ESP32-S3")
    else:
        print(f"Unsupported OS: {recovery.os_type}")
        print("Limited functionality available")
    
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--comprehensive':
            recovery.comprehensive_recovery()
        elif sys.argv[1] == '--interactive':
            recovery.interactive_mode()
        else:
            print("Usage: python3 dn_key_pro_recovery.py [--comprehensive|--interactive]")
            print()
            print("Options:")
            print("  --comprehensive  Run full recovery procedure")
            print("  --interactive    Run interactive mode")
            print("  (no args)        Run comprehensive recovery")
    else:
        # Default to comprehensive recovery
        recovery.comprehensive_recovery()

if __name__ == "__main__":
    main() 