"""Widget: Date"""

import pendulum

from .widget import Widget, WidgetInitException


__all__ = ["Date"]


class InvalidDateException(Exception):
  pass


#
# Date Widget
#
class Date(Widget):
  """Displays a date with optional time."""

  ARGUMENTS = Widget.MAKE_ARGUMENTS([
    ("time",     bool),
    ("name",     str),
    ("datefmt",  str),
    ("timefmt",  str),
    ("timezone", str),
    ("showtz",   bool, False),
  ])

  SCRIPT = True
  STYLES = False

  def init(self):
    """Initialize out widget according to the parameters supplied."""
    try:
      self.params["offset_seconds"] = self._get_offset()
    except InvalidDateException as e:
      raise WidgetInitException(str(e)) from e

  def _get_offset(self):
    """Gets the current timezone offset (seconds, integer) between the
    host's timezone and the specified timezone."""

    timezone = self.params["timezone"]
    now = pendulum.now()

    try:
      nowTZ = now.in_timezone(timezone)
    except pendulum.tz.exceptions.InvalidTimezone as e:
      raise InvalidDateException(f"Invalid Timezone: '{str(e)}'")

    return nowTZ.offset - now.offset

  def fetch_data(self):
    """Return the offset so the the JS can adjust."""
    offset = self._get_offset()
    return { "offset_seconds": offset }
