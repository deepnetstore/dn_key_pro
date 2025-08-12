import os
import time
import board
import busio
import digitalio
import storage
import adafruit_sdcard

# spi bus used by SD Card, stored globably
spi_0 = None

# location in SD card to load scripts from
DUCKY_DIR = "/DUCKY_SCRIPTS/"

sd_card_init_success = False

print("Trying SD CARD setup")
# Initialize SD Card
try:
    spi_0 = busio.SPI(board.SD_CLK, MISO=board.SD_D0, MOSI=board.SD_DI)
    while not spi_0.try_lock():
        pass
    spi_0.configure(baudrate=2400000)
    spi_0.unlock()
    # spi_0 = busio.SPI(board.SD_CLK, MISO=board.SD_D0, MOSI=board.SD_DI)
    # sdcard = sdcardio.SDCard(spi_0, board.D7, baudrate=2000000)
    cs = digitalio.DigitalInOut(board.SD_CS)
    sdcard = adafruit_sdcard.SDCard(spi_0, cs)
    vfs = storage.VfsFat(sdcard)
    time.sleep(0.25)
    storage.mount(vfs, "/")
    time.sleep(0.5)
    print("SD Card Mounted")
    sd_card_init_success = True
except OSError as e:
    print(f"SD Card Error: {e}")


def print_directory(path, tabs=0):
    for file in os.listdir(path):
        if file == "?" or file[0] == ".":
            continue
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " bytes"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<32} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

# if sd_card_init_success:
#     print_directory("/")
