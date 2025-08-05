# helper functions and classes
from .display import display_group

# empty objects in the group to show
def clear_group(full=False):
    global display_group
    while len(display_group) > (1 if not full else 0):
        display_group.pop()


# current_menu = None


# storage class for passing as argument in Menu building
class ArgStore:
    def __init__(self, _data):
        self.data = _data


# empty function for setup
def EmptyFunc(null=None):
    pass

