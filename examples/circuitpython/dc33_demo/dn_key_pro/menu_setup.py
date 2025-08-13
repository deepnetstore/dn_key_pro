import time
import terminalio
from adafruit_display_text import label

from .battery import max17, update_battery_levels
from .buttons import Buttons

# location helpers for drawing text locations
MENU_START_X = 16
MENU_START_Y = 32
MENU_ITEM_HEIGHT = 20


# Items have a text to display, a function to call and an argument to pass
# The action function will be called passing in the user_data as an agument
# when enter button has been pressed over a Menu choice
class MenuItem:
    def __init__(self, text, action, user_data=None):
        self.text = text
        self.action = action
        self.user_data = user_data

    def execute(self):
        self.action(self.user_data)


# Base class for basic Menu drawing and updating
# to be inherited by other classes to share common calls
# to change view, set a global 'current_view' and update
# that variable to the desired Menu class to display.
# clearing of old group will be required before 
# reloading the next view 
class MenuBase:
    def __init__(self, title, items, n_items=5):
        self.title = title
        self.items = items
        self.N_ITEMS = n_items      # set number of items shown on display space
        self.view_start = 0         # Index of the first item visible in the view
        self.selected_index = 0
        self.pressed = False
        self.battery_label = label.Label(terminalio.FONT, text=f"BAT:100.0%", color=0xF9F9BE, x=240, y=4, scale=1)

    def draw(self, group):
        '''
        this is a dummy function that needs to be overridden by 
        a user's customer menu sub class. 
        See DuckyMenu below for example
        '''
        print("MUST BE IMPLEMENTED/OVERRIDDEN BY A SUBCLASS")
        
    def _adjust_view(self):
        """Adjusts the view_start to keep the selected item visible."""
        if self.selected_index < self.view_start:
            self.view_start = self.selected_index
        elif self.selected_index >= self.view_start + 5: # 5 is the max items on screen
            self.view_start = self.selected_index - 4

    def buttons_released(self, buttons):
        return not buttons.pressed(Buttons.UP) and not buttons.pressed(Buttons.DOWN) and not buttons.pressed(Buttons.ENTER)

    def handle_input(self, buttons, display_group):
        # uncomment if a battery is soldered
        if not max17 is None:
            update_battery_levels()
            self.battery_label.text = f"BAT:{max17.cell_percent:.1f}%"

        if self.pressed and self.buttons_released(buttons):
            time.sleep(0.15)
            self.pressed = False

        elif buttons.pressed(Buttons.UP) and not self.pressed:
            # print("button up:", Buttons.UP, self.selected_index)
            time.sleep(0.015)
            self.pressed = True
            self.selected_index = (self.selected_index - 1) % len(self.items)
            self._adjust_view()  # Adjust view after changing selection
            self.draw(display_group)

        elif buttons.pressed(Buttons.DOWN) and not self.pressed:
            # print("button down:", Buttons.DOWN, self.selected_index)
            time.sleep(0.015)
            self.pressed = True
            self.selected_index = (self.selected_index + 1) % len(self.items)
            self._adjust_view()  # Adjust view after changing selection
            self.draw(display_group)

        elif buttons.pressed(Buttons.ENTER) and not self.pressed:
            # print("button enter:", Buttons.ENTER, self.selected_index)
            time.sleep(0.015)
            self.pressed = True
            self.items[self.selected_index].execute()


    def draw_items(self, group, *, offset_x=0, offset_y=0):
        group.append(self.battery_label)
        for i in range(min(self.N_ITEMS, len(self.items))):    # only draw N items at a time
            item_index = self.view_start + i        # update item index to show
            if item_index < len(self.items):        # note: view_start is adjusted on user input
                color = 0xFF00FF if item_index == self.selected_index else 0xF0F0F0
                text_area = label.Label(terminalio.FONT, text=self.items[item_index].text, color=color, x=MENU_START_X + offset_x, y=MENU_START_Y + i * MENU_ITEM_HEIGHT, scale=2)
                group.append(text_area)
