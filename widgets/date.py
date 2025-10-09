"""Widget: Date"""

import pendulum

from .widget import Widget


__all__ = ["Date"]


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

    timezone = self.params["timezone"]
    now = pendulum.now()

    try:
      nowTZ = now.in_timezone(timezone)
    except pendulum.tz.exceptions.InvalidTimezone as e:
      raise Exception(f"Invalid Timezone: '{str(e)}'")

    offset_seconds = nowTZ.offset - now.offset
    self.params["offset_seconds"] = offset_seconds
