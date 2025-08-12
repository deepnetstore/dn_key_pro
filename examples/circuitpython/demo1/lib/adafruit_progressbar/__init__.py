# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_progressbar`
================================================================================

Dynamic progress bar widget for CircuitPython displays


* Author(s): Brent Rubell and Hugo Dahl

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# imports
try:
    from typing import List, Tuple, Union
except ImportError:
    pass  # No harm if the module isn't located
import displayio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ProgressBar.git"


class ProgressBarBase(displayio.TileGrid):
    """The base class for dynamic progress bar widgets.

    :param position: The coordinates (x, y) of the top left corner
    :type position: Tuple[int, int]
    :param size: The size (width, height) of the progress bar
    :type size: Tuple[int, int]
    :param bar_color: The color of the bar representing the value. This can
                            be a hexadecimal value for color (0x224466).
                            Default: 0x00FF00 (Solid green)
    :type bar_color: int
    :param border_color: The color of the border around the progress bar. This
                            can be a hexadecimal value for color (0x4488BB).
                            Default: 0xFFFFFF (White)
    :type border_color: int
    :param fill_color: The colour of the bar representing the remainder of the
                            value. i.e. if the current value is 42%, the 42 value
                            is represented by the bar_color parameter. The remainder,
                            58%, will be displayed in this color. This can also
                            be a hexadecimal value for color (0xEE7755).
                            Default: 0x000000 (Black)
    :type fill_color: int
    :param margin_size: The thickness (in pixels) of the margin between the border and
        the bar. If it is 1 or larger, will be filled in by the color of the
        "fill_color" parameter.
    :type margin_size: int
    :param value_range: Specify the range of allowed values for which the progress
                        should be displayed. When setting the "value" property,
                        this range is the one against which its progression will be determined.
                        Default: (0.0, 1.0)
    :type value_range: Tuple[int, int] or Tuple[float, float]
    """

    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        value: Union[int, float] = 0,
        bar_color=0x00FF00,
        border_color=0xFFFFFF,
        fill_color=0x000000,
        border_thickness: int = 1,
        margin_size: int = 1,
        value_range: Union[Tuple[int, int], Tuple[float, float]] = (0, 100),
    ) -> None:
        if value_range[0] >= value_range[1]:
            raise ValueError("The minimum value must be less than the maximum value")

        if size[0] <= 0 or size[1] <= 0:
            raise ValueError("The width and the height must be greater than zero")

        if not value_range[0] <= value <= value_range[1]:
            raise ValueError("The starting value must be within the range of minimum to maximum")

        _edge_size = 2 * margin_size + 2 * border_thickness

        if _edge_size >= size[0]:
            raise ValueError(
                "The size of the borders and margins combined must be "
                "less than the width of the widget"
            )

        if _edge_size >= size[1]:
            raise ValueError(
                "The size of the borders and margins combined must be "
                "less than the height of the widget"
            )

        self._progress = 0.0
        self._widget_size = size
        self._position = position

        self._bitmap = displayio.Bitmap(size[0], size[1], 3)
        self._palette = displayio.Palette(3)
        self._border_thickness = border_thickness
        self._margin_size = margin_size
        self._range = value_range
        self._progress = 0.0

        self._old_value = self.minimum
        self._value = self.minimum

        self.fill = fill_color
        self.bar_color = bar_color
        self.border_color = border_color

        # Setup value and old_value to handle the change to the new
        # initial value later.
        self._value = self.minimum
        self._old_value = self.minimum

        super().__init__(
            self._bitmap,
            pixel_shader=self._palette,
            x=self._position[0],
            y=self._position[1],
        )

        self._draw_outline()
        self.value = value

    #     _bitmap: displayio.Bitmap  # The bitmap used for the bar/value
    #     _position: (int, int)  # The (x,y) coordinates of the top-left corner
    #     _widget_size: (int, int)  # The dimensions of the progress bar
    #     _palette: displayio.Palette(3)  # The palette to be used
    #     _progress: float  # The value to represent, between 0.0 and 100.0
    #     _border_thickness: int  # The thickness of the border around the control, in pixels
    #     _margin_size: bool  # Whether we should display a margin between
    #       the border and the value/bar
    #     # The minimum and maximum values we can represent
    #     _range: (int, int) or (float, float)

    #     Color palette index to property mapping:
    #       0:  Bar fill color
    #       1:  Border color
    #       2:  Background fill color

    @property
    def widget_size(self) -> int:
        """The size at the outer edge of the control, returned as a tuple (width, height)

        :rtype: int
        """
        return self._widget_size

    @property
    def widget_width(self) -> Tuple[int, int]:
        """The total width of the widget, in pixels. Includes the border and margin.

        :rtype: Tuple[int, int]
        """
        return self.widget_size[0]

    @property
    def border_thickness(self) -> int:
        """Gets the currently configured thickness of the border (in pixels)

        :rtype: int
        """
        return self._border_thickness

    @property
    def widget_height(self) -> int:
        """The total height of the widget, in pixels. Includes the border and margin.

        :rtype: int
        """
        return self.widget_size[1]

    @property
    def border_color(self) -> int:
        """Returns the currently configured value for the color of the
        outline (border) of the widget.

        :rtype: int
        """
        return self._border_color

    @border_color.setter
    def border_color(self, color: Union[int, Tuple[int, int, int]]) -> None:
        """Sets the color of the border of the widget. Set it to 'None'
        if a border should still be part of the widget but not displayed.

        :param color: The color to be used for the border
        :type int/None/Tuple[int, int, int]:

        :rtype: None
        """

        if not (isinstance(color, int) or color is None):
            raise TypeError("A color must be represented by a integer value")

        self._border_color = color

        if color is None:
            self._palette[1] = 0x00
            self._palette.make_transparent(1)
        else:
            self._palette[1] = color
            self._palette.make_opaque(1)

    @property
    def fill(self) -> int:
        """The fill of the progress bar. Can be a hex value for a color or ``None`` for
        transparent.

        :rtype: int
        """
        return self._fill_color

    @fill.setter
    def fill(self, color: Union[int, Tuple[int, int, int]]) -> None:
        """Sets the fill of the progress bar. Can be a hex value for a color or ``None`` for
        transparent.

        :param color: The color to use for the widget's background
        :type color: int/None/Tuple[int, int, int]
        """
        self._fill_color = color
        if color is None:
            self._palette[0] = 0x00
            self._palette.make_transparent(0)
        else:
            self._palette[0] = color
            self._palette.make_opaque(0)

    @property
    def bar_color(self) -> int:
        """The color of the bar's fill

        :rtype: int/None
        """

        return self._bar_color

    @bar_color.setter
    def bar_color(self, color: Union[int, Tuple[int, int, int]]) -> None:
        """Sets the color of the bar

        :param color: The color to use for the bar
        :type color: int/None/Tuple[int, int, int]

        :rtype: None
        """

        self._bar_color = color

        if color is None:
            self._palette[2] = 0x00
            self._palette.make_transparent(2)
        else:
            self._palette[2] = color
            self._palette.make_opaque(2)

    @property
    def value(self) -> Union[int, float]:
        """
        The current value of the control, used to determine its progress/ratio
        :rtype: int/float
        """
        return self._value

    @value.setter
    def value(self, value: Union[int, float]) -> None:
        """Sets the current value of the progress within the min-max range

        :param value: The new value for the progress status
        :type value: int/float

        :rtype: None
        """

        if not isinstance(value, (int, float)):
            raise TypeError("The value to set must be either an integer or a float")

        if not self.minimum <= value <= self.maximum:
            raise ValueError(
                f"The value must be between minimum ({self.minimum}) and maximum ({self.maximum})"
            )

        # Save off the previous value, so we can pass it in the
        # call to "Render"
        self._old_value = self._value
        self._value = value
        # Convert value to float since we may be dealing with
        # integer types, and we can't work with integer division
        # to get a ratio (position) of "value" within range.
        self._set_progress(self.get_value_ratio(value))

    @property
    def progress(self) -> float:
        """Gets the current displayed value of the widget.

        :return: The current progress ratio
        :rtype: float
        """
        return self._progress

    @progress.setter
    def progress(self, value: float) -> None:
        """Sets the current displayed value of the widget. This will update the
        `value` property to an approximation based on the allowed range. The calculation
        used to determine the approximate value is
        `((self.minimum + (self.maximum - self.minimum)) * progress)`.
        For the most accurate representation of a given value, it is recommended to set the
        property "value" to the desired value.

        Example: If the range for the widget is 0-10, setting a progress value of "35"
        will result in `value` being "3.5", since 3.5 is the 35% value of the range between
        0 and 10. The value determined from this method makes no assumptions or checks based on
        the type of the "value" field.

        :param value: The new value which should be displayed by the progress
                            bar. Must be between 0.0-100.0
        :type value: float

        :rtype: None
        """

        if not isinstance(value, (float, int)):
            raise TypeError("'progress' must be an int or a float")

        if not 0.0 <= value <= 100.0:
            raise ValueError("'progress' must be between 0 and 100")

        self.value = (self.minimum + (self.maximum - self.minimum)) * (value * 0.01)

    # Bit of a hack to be able to work around the shim "ProgressBar" class
    # to be able to handle values as it used to.
    def _set_progress(self, value: float) -> None:
        """Sets the value for the underlying variable _progress, then
        calls self.render() with the appropriate values.

        :param value: The value to which self.progress should be set
        :type value: float
        :rtype: None
        """

        self._progress = round(value, 4)
        self._render(self._old_value, self._value, value)

    @property
    def range(self) -> Tuple[Union[int, float], Union[int, float]]:
        """The range which can be handled as a Tuple(min,max)

        :rtype: Tuple(int/float, int/float)
        """
        return self._range

    @property
    def minimum(self) -> Union[int, float]:
        """The minimum (lowest) value which can be displayed

        :rtype: int/float
        """
        return self.range[0]

    @property
    def maximum(self) -> Union[int, float]:
        """The maximum (highest) value which can be displayed

        :rtype: int/float
        """
        return self.range[1]

    def _draw_outline(self) -> None:
        """Draws the outline (border) of the progressbar, with a thickness value
        from self.border_thickness.

        :rtype None:
        """
        stroke = self.border_thickness

        # draw outline rectangle
        for _w in range(self.widget_width):
            for line in range(stroke):
                self._bitmap[_w, line] = 1
                self._bitmap[_w, self.widget_height - 1 - line] = 1
        for _h in range(self.widget_height):
            for line in range(stroke):
                self._bitmap[line, _h] = 1
                self._bitmap[self.widget_width - 1 - line, _h] = 1

    def fill_width(self) -> int:
        """Returns the amount of horizontal space within the widget
        which can be used for value display. This is typically the
        width of the widget as defined, minus any visually reserved space.

        :rtype: int
        """

        return self.widget_width - self._get_fill_border_size()

    def fill_height(self) -> int:
        """Returns the amount of vertical space within the widget
        which can be used for value display. This is typically the
        width of the widget as defined, minus any visually reserved
        space.

        :rtype: int
        """

        return self.widget_height - self._get_fill_border_size()

    def _get_fill_border_size(self) -> int:
        """Determines any visual space reserved for the widget
        based on the defined border thickness, and whether a margin
        should be placed between the border and the bar.
        The value is calculated as (2 x border_thickness) minus
        (2 x margin_size). The value for margin_size is either 0 (zero)
        or 1 (one) depending on the value of margin_size when the
        widget was created.

        :rtype: int
        """

        return (2 * self.border_thickness) + (2 * self.margin_size)

    @property
    def margin_size(self) -> int:
        """Returns the size of the margin on a single side of the display

        :return int:
        """
        return self._margin_size

    @margin_size.setter
    def margin_size(self, value: int) -> None:
        """Sets the new size of the margin to be used between the border
        (if displayed) and the value bar.

        :param value: The new size of the margin between the border
        and value bar on all sides of the widget.
        :type value: int

        :rtype: None
        """

        if not isinstance(value, int):
            raise TypeError("The margin size must be an integer")

        margin_spacing = (2 * value) + (2 * self._border_thickness)

        if margin_spacing >= self.widget_width:
            raise ValueError(
                "The size of the borders and margins combined can total the same or more"
                "than the widget's width."
            )

        if margin_spacing >= self.widget_height:
            raise ValueError(
                "The size of the borders and margins combined can total the same or more"
                "than the widget's height."
            )

        self._margin_size = value
        self._set_progress(self._progress)  # For a render pass

    def get_value_ratio(self, value: Union[int, float]) -> float:
        """Gets the ratio (percentage) of a given value within the
        range of self.minimum and self.maximum.

        :param value: The value for which the ration should be calculated
        :type value: int/float

        :return: The ratio of value:range
        :rtype: float
        """

        if self.maximum == self.minimum:
            return 0.0

        return (float(value) - self.minimum) / (self.maximum - self.minimum)

    def _get_value_sizes(self, _old_ratio: float, _new_ratio: float) -> Tuple[int, int]:
        return 0, 0

    def _get_max_fill_size(self) -> int:
        return 0

    def _get_ratios(
        self, _old_value: Union[int, float], _new_value: Union[int, float]
    ) -> Tuple[float, float]:
        return self.get_value_ratio(_old_value), self.get_value_ratio(_new_value)

    def _adjust_size_for_range_limits(
        self, _new_value_size: int, _new_value: Union[int, float]
    ) -> int:
        # If we have *ANY* value other than "zero" (minimum), we should
        #   have at least one element showing
        if _new_value_size == 0 and _new_value > self.minimum:
            _new_value_size = 1

        # Conversely, if we have *ANY* value other than 100% (maximum),
        #   we should NOT show a full bar.
        if _new_value_size == self._get_max_fill_size() and _new_value < self.maximum:
            _new_value_size -= 1

        return _new_value_size

    def _get_sizes_min_max(self) -> Tuple[int, int]:
        return 0, min(self.fill_width(), self.fill_height())

    def _invert_fill_direction(self) -> bool:
        return False

    def _get_horizontal_fill(self, _start: int, _end: int, _incr: int) -> Tuple[int, int, int]:
        return 0, self.fill_width(), 1  # Subclass must return values

    def _get_vertical_fill(self, _start: int, _end: int, _incr: int) -> Tuple[int, int, int]:
        return 0, self.fill_height(), 1  # Subclass must return values

    def _render(
        self,
        _old_value: Union[int, float],
        _new_value: Union[int, float],
        _progress_value: float,
    ) -> None:
        """
        Does the work of actually creating the graphical representation of
            the value (percentage, aka "progress") to be displayed.

        :param _old_value: The previously displayed value
        :type _old_value: int/float
        :param _new_value: The new value to display
        :type _new_value: int/float
        :param _progress_value: The value to display, as a percentage, represented
            by a float from 0.0 to 1.0 (0% to 100%)
        :type _progress_value: float
        :rtype: None
        """

        _prev_ratio, _new_ratio = self._get_ratios(_old_value, _new_value)
        _old_value_size, _new_value_size = self._get_value_sizes(_prev_ratio, _new_ratio)

        # Adjusts for edge cases, such as 0-width non-zero value, or 100% width
        # non-maximum values
        _new_value_size = self._adjust_size_for_range_limits(_new_value_size, _new_value)

        # Default values for increasing value
        _color = 2
        _incr = 1
        _start = max(_old_value_size, 0)
        _end = max(_new_value_size, 0)

        if _old_value_size >= _new_value_size:
            # Override defaults to be decreasing
            _color = 0  # Clear
            _incr = -1  # Iterate range downward
            _start = max(_old_value_size, 0) - 1
            _end = max(_new_value_size, 0) - 1
            # If we're setting to minimum, make sure we're clearing by
            #  starting one "bar" further
            if _new_value == self.minimum:
                _start += 1

        _render_offset = self.margin_size + self.border_thickness

        vert_start, vert_end, vert_incr = self._get_vertical_fill(_start, _end, _incr)
        horiz_start, horiz_end, horiz_incr = self._get_horizontal_fill(_start, _end, _incr)

        vert_start += _render_offset
        vert_end += _render_offset
        horiz_start += _render_offset
        horiz_end += _render_offset

        for vertical_position in range(vert_start, vert_end, vert_incr):
            for horizontal_position in range(horiz_start, horiz_end, horiz_incr):
                self._bitmap[horizontal_position, vertical_position] = _color
