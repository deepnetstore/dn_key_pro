#!/usr/bin/env python3
"""
DN-KEY Pro Recovery and Flashing Tool
=====================================

A user-friendly recovery and flashing tool for the DN-KEY Pro ESP32-S3 device.
Based on the robust logic from the multi-device flashing script.

This script will:
1. Erase the device flash memory
2. Flash TinyUF2 bootloader
3. Flash CircuitPython firmware
4. Copy a sample code.py file to the device

Requirements:
- Python 3.6+
- esptool (pip install esptool)
- pyserial (pip install pyserial) - optional but recommended
"""

import os
import sys
import time
import subprocess
import platform
import shutil
from pathlib import Path

# =============================================================================
# USER CONFIGURATION - MODIFY THESE PATHS FOR YOUR SYSTEM
# =============================================================================

# TinyUF2 build directory (where the compiled TinyUF2 files are located)
# Example: "/path/to/your/tinyuf2/ports/espressif"
TINYUF2_DIR = "/path/to/your/tinyuf2/ports/espressif"

# CircuitPython UF2 file (the CircuitPython firmware to flash)
# Example: "/path/to/your/circuitpython_firmware.uf2"
CIRCUITPYTHON_UF2 = "/path/to/your/circuitpython_firmware.uf2"

# Sample code.py file to copy to the device after flashing
# Example: "/path/to/your/sample_code.py"
SAMPLE_CODE = "/path/to/your/sample_code.py"

# =============================================================================
# ADVANCED CONFIGURATION (usually don't need to change these)
# =============================================================================

# TinyUF2 build paths (relative to TINYUF2_DIR)
# These should match your TinyUF2 build output structure
TINYUF2_PARTITION_TABLE = "_build/deepnet_key_pro_v0r5/partition_table/partition-table.bin"
TINYUF2_OTA_DATA = "_build/deepnet_key_pro_v0r5/ota_data_initial.bin"
TINYUF2_BOOTLOADER = "_build/deepnet_key_pro_v0r5/bootloader/bootloader.bin"
TINYUF2_BINARY = "_build/deepnet_key_pro_v0r5/tinyuf2.bin"

# Flash settings
FLASH_MODE = "dio"
FLASH_FREQ = "80m"
FLASH_SIZE = "8MB"
BAUD_RATE = "460800"

# =============================================================================
# END USER CONFIGURATION
# =============================================================================

class DNKeyProRecovery:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_macos = self.os_type == "darwin"
        self.is_linux = self.os_type == "linux"
        self.is_windows = self.os_type == "windows"
        
        # Colors for output
        self.RED = '\033[0;31m'
        self.GREEN = '\033[0;32m'
        self.YELLOW = '\033[1;33m'
        self.BLUE = '\033[0;34m'
        self.NC = '\033[0m'
        
        # Log file
        self.log_file = Path("recovery_log.txt")
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging to both file and console"""
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
        """Log message with color coding"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if level == "SUCCESS":
            print(f"{self.GREEN}[SUCCESS]{self.NC} {message}")
        elif level == "WARNING":
            print(f"{self.YELLOW}[WARNING]{self.NC} {message}")
        elif level == "ERROR":
            print(f"{self.RED}[ERROR]{self.NC} {message}")
        else:
            print(f"{self.BLUE}[INFO]{self.NC} {message}")
        
        # Also write to log file
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {level}: {message}\n")
    
    def check_configuration(self):
        """Check if all required files and paths exist"""
        self.log("Checking configuration...")
        
        issues = []
        
        # Check TinyUF2 directory
        if not Path(TINYUF2_DIR).exists():
            issues.append(f"TinyUF2 directory not found: {TINYUF2_DIR}")
        else:
            self.log(f"✓ TinyUF2 directory found: {TINYUF2_DIR}")
        
        # Check TinyUF2 files
        tinyuf2_files = [
            (TINYUF2_PARTITION_TABLE, "Partition table"),
            (TINYUF2_OTA_DATA, "OTA data"),
            (TINYUF2_BOOTLOADER, "Bootloader"),
            (TINYUF2_BINARY, "TinyUF2 binary")
        ]
        
        for file_path, description in tinyuf2_files:
            full_path = Path(TINYUF2_DIR) / file_path
            if not full_path.exists():
                issues.append(f"{description} not found: {full_path}")
            else:
                self.log(f"✓ {description} found: {full_path}")
        
        # Check CircuitPython UF2
        if not Path(CIRCUITPYTHON_UF2).exists():
            issues.append(f"CircuitPython UF2 not found: {CIRCUITPYTHON_UF2}")
        else:
            self.log(f"✓ CircuitPython UF2 found: {CIRCUITPYTHON_UF2}")
        
        # Check sample code
        if not Path(SAMPLE_CODE).exists():
            issues.append(f"Sample code not found: {SAMPLE_CODE}")
        else:
            self.log(f"✓ Sample code found: {SAMPLE_CODE}")
        
        if issues:
            self.log("Configuration issues found:", "ERROR")
            for issue in issues:
                self.log(f"  - {issue}", "ERROR")
            self.log("Please update the configuration variables at the top of this script.", "ERROR")
            return False
        
        self.log("Configuration check passed!", "SUCCESS")
        return True
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        self.log("Checking dependencies...")
        
        missing_deps = []
        
        # Check esptool
        esptool_found = False
        for cmd in [['esptool.py', 'version'], ['python', '-m', 'esptool', 'version'], ['python3', '-m', 'esptool', 'version']]:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    esptool_found = True
                    self.log(f"✓ esptool found: {' '.join(cmd)}")
                    break
            except:
                continue
        
        if not esptool_found:
            missing_deps.append("esptool")
        
        # Check pyserial
        try:
            import serial
            self.log("✓ pyserial found")
        except ImportError:
            missing_deps.append("pyserial")
        
        if missing_deps:
            self.log("Missing dependencies:", "WARNING")
            for dep in missing_deps:
                self.log(f"  - {dep}", "WARNING")
            
            self.log("Installation commands:", "INFO")
            if "esptool" in missing_deps:
                self.log("  pip install esptool", "INFO")
            if "pyserial" in missing_deps:
                self.log("  pip install pyserial", "INFO")
            
            response = input("\nWould you like to install missing dependencies now? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return self.install_dependencies(missing_deps)
            else:
                self.log("Continuing without installing dependencies. Some features may not work.", "WARNING")
                return False
        
        self.log("All dependencies found!", "SUCCESS")
        return True
    
    def install_dependencies(self, missing_deps):
        """Install missing dependencies"""
        self.log("Installing missing dependencies...")
        
        install_commands = {
            "esptool": "pip install esptool",
            "pyserial": "pip install pyserial"
        }
        
        for dep in missing_deps:
            if dep in install_commands:
                self.log(f"Installing {dep}...")
                try:
                    cmd = install_commands[dep].split()
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        self.log(f"✓ {dep} installed successfully!", "SUCCESS")
                    else:
                        self.log(f"Failed to install {dep}: {result.stderr}", "ERROR")
                        return False
                except Exception as e:
                    self.log(f"Failed to install {dep}: {e}", "ERROR")
                    return False
        
        return True
    
    def find_esptool(self):
        """Find esptool installation"""
        for cmd in [['esptool.py'], ['python', '-m', 'esptool'], ['python3', '-m', 'esptool']]:
            try:
                result = subprocess.run(cmd + ['version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return cmd
            except:
                continue
        return None
    
    def detect_devices(self):
        """Detect connected devices"""
        self.log("Scanning for connected devices...")
        
        devices = []
        
        if self.is_macos:
            # macOS: look for /dev/cu.usbmodem* devices
            for port in Path("/dev").glob("cu.usbmodem*"):
                if port.exists() and port.is_char_device():
                    devices.append(str(port))
        elif self.is_linux:
            # Linux: look for /dev/ttyUSB* and /dev/ttyACM* devices
            for pattern in ["ttyUSB*", "ttyACM*"]:
                for port in Path("/dev").glob(pattern):
                    if port.exists() and port.is_char_device():
                        devices.append(str(port))
        elif self.is_windows:
            # Windows: look for COM ports
            try:
                result = subprocess.run(['wmic', 'path', 'Win32_SerialPort', 'get', 'DeviceID'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'COM' in line:
                            devices.append(line.strip())
            except:
                pass
        
        if devices:
            self.log(f"Found {len(devices)} device(s):", "SUCCESS")
            for device in devices:
                self.log(f"  - {device}")
        else:
            self.log("No devices found!", "WARNING")
        
        return devices
    
    def get_device_mac(self, device_port):
        """Get device MAC address for identification"""
        esptool_cmd = self.find_esptool()
        if not esptool_cmd:
            return "unknown"
        
        try:
            result = subprocess.run(esptool_cmd + ['--chip', 'esp32s3', '-p', device_port, 'chip_id'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'MAC:' in line:
                        return line.split('MAC:')[1].strip()
        except:
            pass
        
        return "unknown"
    
    def erase_device(self, device_port, device_id):
        """Erase device flash memory"""
        self.log(f"[{device_id}] Erasing flash memory...")
        
        esptool_cmd = self.find_esptool()
        if not esptool_cmd:
            self.log("esptool not found!", "ERROR")
            return False
        
        try:
            cmd = esptool_cmd + [
                '--chip', 'esp32s3', '-p', device_port, '-b', BAUD_RATE, 'erase_flash'
            ]
            
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log(f"[{device_id}] Flash erased successfully!", "SUCCESS")
                time.sleep(2)
                return True
            else:
                self.log(f"[{device_id}] Flash erase failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"[{device_id}] Error during flash erase: {e}", "ERROR")
            return False
    
    def flash_tinyuf2(self, device_port, device_id):
        """Flash TinyUF2 bootloader"""
        self.log(f"[{device_id}] Flashing TinyUF2...")
        
        esptool_cmd = self.find_esptool()
        if not esptool_cmd:
            self.log("esptool not found!", "ERROR")
            return False
        
        try:
            # Change to TinyUF2 directory
            original_cwd = os.getcwd()
            os.chdir(TINYUF2_DIR)
            
            cmd = esptool_cmd + [
                '--chip', 'esp32s3', '-p', device_port, '-b', BAUD_RATE,
                '--before=default_reset', '--after=hard_reset',
                'write_flash', '--flash_mode', FLASH_MODE, '--flash_freq', FLASH_FREQ, 
                '--flash_size', FLASH_SIZE,
                '0x8000', TINYUF2_PARTITION_TABLE,
                '0xe000', TINYUF2_OTA_DATA,
                '0x0', TINYUF2_BOOTLOADER,
                '0x410000', TINYUF2_BINARY
            ]
            
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Change back to original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                self.log(f"[{device_id}] TinyUF2 flashed successfully!", "SUCCESS")
                time.sleep(2)
                return True
            else:
                self.log(f"[{device_id}] TinyUF2 flash failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"[{device_id}] Error during TinyUF2 flash: {e}", "ERROR")
            return False
    
    def wait_for_volume(self, volume_name, max_attempts=30):
        """Wait for a volume to appear"""
        self.log(f"Waiting for {volume_name} volume...")
        
        for i in range(max_attempts):
            if self.is_macos:
                volume_path = f"/Volumes/{volume_name}"
            elif self.is_linux:
                volume_path = f"/media/{os.getenv('USER', 'user')}/{volume_name}"
            elif self.is_windows:
                volume_path = f"{volume_name}:\\"
            else:
                volume_path = f"/mnt/{volume_name}"
            
            if Path(volume_path).exists():
                self.log(f"{volume_name} volume found!", "SUCCESS")
                return volume_path
            
            time.sleep(2)
        
        self.log(f"{volume_name} volume did not appear", "ERROR")
        return None
    
    def flash_circuitpython(self, device_id):
        """Flash CircuitPython firmware"""
        self.log(f"[{device_id}] Flashing CircuitPython...")
        
        # Wait for DN_BOOT volume
        volume_path = self.wait_for_volume("DN_BOOT")
        if not volume_path:
            self.log(f"[{device_id}] DN_BOOT volume not found", "ERROR")
            return False
        
        # Copy CircuitPython UF2 to volume
        try:
            uf2_dest = Path(volume_path) / Path(CIRCUITPYTHON_UF2).name
            shutil.copy2(CIRCUITPYTHON_UF2, uf2_dest)
            self.log(f"[{device_id}] CircuitPython UF2 copied successfully!", "SUCCESS")
        except Exception as e:
            self.log(f"[{device_id}] Failed to copy CircuitPython UF2: {e}", "ERROR")
            return False
        
        # Wait for device to reboot with CircuitPython
        self.log(f"[{device_id}] Waiting for device to reboot with CircuitPython...")
        time.sleep(8)
        
        # Wait for DN-S3-PY volume
        volume_path = self.wait_for_volume("DN-S3-PY")
        if not volume_path:
            self.log(f"[{device_id}] DN-S3-PY volume not found", "ERROR")
            return False
        
        self.log(f"[{device_id}] CircuitPython installed successfully!", "SUCCESS")
        return True
    
    def copy_sample_code(self, device_id):
        """Copy sample code to the device"""
        self.log(f"[{device_id}] Copying sample code...")
        
        # Find DN-S3-PY volume
        volume_path = self.wait_for_volume("DN-S3-PY")
        if not volume_path:
            self.log(f"[{device_id}] DN-S3-PY volume not found", "ERROR")
            return False
        
        try:
            code_dest = Path(volume_path) / "code.py"
            shutil.copy2(SAMPLE_CODE, code_dest)
            self.log(f"[{device_id}] Sample code copied successfully!", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"[{device_id}] Failed to copy sample code: {e}", "ERROR")
            return False
    
    def comprehensive_recovery(self):
        """Execute comprehensive recovery procedure"""
        self.log("=== DN-KEY Pro Comprehensive Recovery ===")
        
        # Step 1: Check configuration
        if not self.check_configuration():
            return False
        
        # Step 2: Check dependencies
        if not self.check_dependencies():
            self.log("Some dependencies are missing. Please install them first.", "WARNING")
        
        # Step 3: Detect devices
        devices = self.detect_devices()
        if not devices:
            self.log("No devices found. Please connect your DN-KEY Pro device.", "ERROR")
            return False
        
        # Step 4: Process each device
        success_count = 0
        for device_port in devices:
            device_id = Path(device_port).name.replace('cu.usbmodem', '').replace('ttyUSB', '').replace('ttyACM', '').replace('COM', '')
            
            self.log(f"Processing device: {device_id} ({device_port})")
            
            # Get device MAC
            device_mac = self.get_device_mac(device_port)
            if device_mac != "unknown":
                self.log(f"Device MAC: {device_mac}")
            
            # Step 4a: Erase device
            if not self.erase_device(device_port, device_id):
                self.log(f"[{device_id}] Erase failed - skipping device", "ERROR")
                continue
            
            # Step 4b: Flash TinyUF2
            if not self.flash_tinyuf2(device_port, device_id):
                self.log(f"[{device_id}] TinyUF2 flash failed - skipping device", "ERROR")
                continue
            
            # Step 4c: Flash CircuitPython
            if not self.flash_circuitpython(device_id):
                self.log(f"[{device_id}] CircuitPython flash failed - skipping device", "ERROR")
                continue
            
            # Step 4d: Copy sample code
            if not self.copy_sample_code(device_id):
                self.log(f"[{device_id}] Sample code copy failed", "WARNING")
            
            success_count += 1
            self.log(f"[{device_id}] Device recovery completed successfully!", "SUCCESS")
        
        # Final summary
        self.log("=== Recovery Summary ===")
        self.log(f"Successfully recovered: {success_count} out of {len(devices)} device(s)", "SUCCESS")
        
        if success_count > 0:
            self.log("🎉 Recovery completed successfully!", "SUCCESS")
            self.log("Your DN-KEY Pro device(s) should now be running CircuitPython with the sample code.", "SUCCESS")
        else:
            self.log("❌ No devices were successfully recovered.", "ERROR")
            self.log("Please check the log file for detailed error information.", "INFO")
        
        return success_count > 0

def main():
    """Main function"""
    print("DN-KEY Pro Recovery Tool")
    print("========================")
    print()
    
    recovery = DNKeyProRecovery()
    
    # Show OS information
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("Usage: python3 dn_key_pro_recovery.py [--help]")
            print()
            print("Options:")
            print("  --help    Show this help message")
            print("  (no args) Run comprehensive recovery")
            return
        else:
            print("Unknown option. Use --help for usage information.")
            return
    
    # Run comprehensive recovery
    recovery.comprehensive_recovery()

if __name__ == "__main__":
    main() 