# helper functions and classes
from .display import display_group

# empty objects in the group to show
def clear_group(end_value=1):
    global display_group
    while len(display_group) > end_value:
        display_group.pop()
        

# storage class for passing as argument in Menu building
class ArgStore:
    def __init__(self, _data):
        self.data = _data


# empty function for setup
def EmptyFunc(null=None):
    pass

