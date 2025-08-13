import adafruit_max1704x

from .periferals import i2c


max17 = None
try:
    max17 = adafruit_max1704x.MAX17048(i2c)
    print(
        "Found MAX1704x with chip version",
        hex(max17.chip_version),
        "and id",
        hex(max17.chip_id),
    )
except:
    print('no i2c setup, try later, check pull ups..')

# Quick starting allows an instant 'auto-calibration' of the battery. However, its a bad idea
# to do this right when the battery is first plugged in or if there's a lot of load on the battery
# so uncomment only if you're sure you want to 'reset' the chips charge calculator.
# print("Quick starting")
# max17.quick_start = True

def print_battery_levels():   
    if max17 is None:
        return
    print(f" ")
    print(f"Battery voltage: {max17.cell_voltage:.2f} Volts")
    print(f"Battery state  : {max17.cell_percent:.1f} %")
    print(f"Battery alert max  : {max17.voltage_alert_max:.1f} V")
    print(f"Battery alert min  : {max17.voltage_alert_min:.1f} V")
    print(f"Battery activity thresh  : {max17.activity_threshold:.1f} dV")
    print(f"Battery alert  : {max17.active_alert}")
    print(f" ")


bat_counter = 0xfff + 1  # only update the battery every so often
bat_counter_max = 0xfff
def update_battery_levels():
    if max17 is None:
        return
    global bat_counter
    if bat_counter > bat_counter_max:
        print_battery_levels()
        bat_counter = 0
    bat_counter += 1
