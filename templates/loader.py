import re

from jinja2 import Environment, FileSystemLoader
from .htmlcolors import HTML_COLORS


__all__ = ["loader_env"]


re_hex_color = re.compile(r'^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$')
re_measurement = re.compile(r'^(\d+)(px|em|rem|%|vh|vw)')
loader_env = Environment(loader=FileSystemLoader("./templates"))

DEFAULT_COLOR_WHEN_INVALID = HTML_COLORS["TOMATO"]
ACCEPT_COLORS = [
  "transparent",
]


#
# Custom filter functions
#
def get_hex_color(hex_color: str) -> str:
  """Given a color, return the actual HEX color value for it. The input
  hex_color can be one of the following:

    - HTML color name
    - HEX color code (eg. #000000)
    - HEX color code with alpha (eg. #ffffff7f)

  Returns a HEX color value (without alpha)."""

  if not hex_color or isinstance(hex_color, bool):
    return hex_color

  mo = re_hex_color.match(hex_color)
  if mo is None:
    # Some theme settings are measured items, maybe this is the case?
    mo = re_measurement.match(hex_color)
    if mo is not None:
      # This is not a color, leave it as-is!
      return hex_color

    # Maybe the supplied color is its HTML name... let's see if this is
    # the case and convert it to an HTML color if so.
    color_name = hex_color.upper()
    if color_name in HTML_COLORS:
      new_hex_color = HTML_COLORS[color_name]
      if hex_color[0] != "#":
        new_hex_color = new_hex_color[1:]
      mo = re_hex_color.match(new_hex_color)
      if mo is None:
        return hex_color

    else:
      if hex_color in ACCEPT_COLORS:
        return hex_color

      # Invalid/unknown color
      return DEFAULT_COLOR_WHEN_INVALID

  color_start = "#"
  add_color_start = hex_color[0] != color_start
  color = mo.group().lower()
  if add_color_start:
    color = f"{color_start}{color}"

  return color


def get_hex_color_with_alpha(hex_color: str, alpha: int) -> str:
  """Same as get_hex_color() except it will include the alpha value in
  the returned HEX color."""

  if not isinstance(alpha, int) or alpha < 0 or alpha > 255 or not hex_color:
    # Invalid alpha, return the color as-is.
    return hex_color

  color = get_hex_color(hex_color)
  if color is None:
    return hex_color

  if alpha == 255:
    return color

  if len(color) != 7:
    color = color[:7]

  # Add Alpha
  color += f"{alpha:02x}"
  return color


def page_name(name: str) -> str:
  """Returns a normalized name for pages."""

  for repl in (" ", "-", "."):
    name = name.replace(repl, "_")
  return name.lower()


def sorted_list(items: list) -> list:
  """Returns the list, sorted."""
  return sorted(items)


def short_value(value: int | None) -> str | None:
  """Shortes a value (eg. 1234 -> 1.2K)."""

  if value is None:
    return None

  if isinstance(value, str) and value.isdigit():
    value = int(value)

  if not isinstance(value, int):
    return value

  val = str(value)

  if len(val) > 9:
    ret_val = f"{value // 10000000 / 100.0:.1f}B"
  elif len(val) > 6:
    ret_val = f"{value // 10000 / 100.0:.1f}M"
  elif value >= 1000:
    ret_val = f"{value // 10 / 100.0:.1f}K"
  else:
    ret_val = f"{value}"

  return ret_val.replace(".0", "")


#
# Assign custom filters
#
loader_env.filters["hex_color"] = get_hex_color
loader_env.filters["hex_color_alpha"] = get_hex_color_with_alpha
loader_env.filters["page_name"] = page_name
loader_env.filters["sorted"] = sorted_list
loader_env.filters["short_value"] = short_value
