#!/bin/bash
# DN-KEY Pro Serial Monitor
# Connects to the first available USB serial device found on macOS or Linux.
# Press Ctrl+C to exit cleanly.

# Set the baud rate for the connection
BAUD_RATE=115200

# Function to handle cleanup on exit
cleanup() {
    echo -e "\nSerial monitor stopped."
    # Kill any remaining screen sessions
    screen -ls | grep -q "dn_key_serial" && screen -S dn_key_serial -X quit 2>/dev/null
    exit 0
}

# Set up signal handlers for clean exit
trap cleanup SIGINT SIGTERM

# Function to find serial devices
find_serial_device() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # For macOS, use tty.usbmodem devices
        ls /dev/tty.usbmodem* 2>/dev/null | head -n 1
    else
        # For Linux, use ttyACM or ttyUSB devices
        ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null | head -n 1
    fi
}

echo "DN-KEY Pro Serial Monitor"
echo "========================="
echo "Press Ctrl+C to exit"
echo ""

while true; do
    # Find the first available serial device
    SERIAL_PORT=$(find_serial_device)

    # Check if a serial device was found
    if [ -z "$SERIAL_PORT" ]; then
        echo "No USB serial device found. Retrying in 2 seconds..."
        echo "Press Ctrl+C to exit"
        sleep 2
        continue
    fi

    # Attempt to connect to the found USB serial device
    echo "Connecting to $SERIAL_PORT at $BAUD_RATE baud..."
    echo "Press Ctrl+C to exit"
    echo "----------------------------------------"
    
    # Use screen with a named session
    screen -S dn_key_serial "$SERIAL_PORT" "$BAUD_RATE"
    
    # Check exit status
    if [ $? -eq 0 ]; then
        echo "Disconnected from $SERIAL_PORT. Reconnecting in 2 seconds..."
        sleep 2
    else
        # Screen was interrupted, exit the monitor
        break
    fi
done

echo "Serial monitor stopped."
