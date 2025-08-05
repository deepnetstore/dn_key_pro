import board
import max3421e
import usb
import time

from .periferals import spi

cs = board.USB_SS
irq = board.USB_INT

max3421e = max3421e.Max3421E(spi, chip_select=cs, irq=irq)

device = None
vid = None
pid = None

# max3421e test
def test_max3421e():
    global device, vid, pid
    print("Finding devices:")
    time.sleep(0.25)
    for device in usb.core.find(find_all=True):
        print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
        if device == None:
            return None
        vid = device.idVendor
        pid = device.idProduct
        device = usb.core.find(idVendor=vid, idProduct=pid)
        time.sleep(0.1)
        device.set_configuration()
        print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
        # Test to see if the kernel is using the device and detach it.
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        return device
    return None

# uncomment to Run the test function
# device = test_max3421e()
