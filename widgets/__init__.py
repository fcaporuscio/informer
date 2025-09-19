import inspect


__all__ = ["load_widget", "WidgetFinder"]


# Import the base Widget class and all other valid widgets here. They
 # are only considered valid widgets if they are imported here.
from .widget import *
from .chucknorris import *
from .date import *
from .garfield import *
from .lobsters import *
from .reddit import *
from .ronswanson import *
from .rss import *
from .sitestatus import *
from .tabs import *
from .youtube import *
from .xkcd import *


# The following require extra libs to be installed. These will
# automatically get excluded if we cannot import them.
try:
  from .openmeteo import *
except ModuleNotFoundError as e:
  print("Disabled 'openmeteo' Widget -> 'pip install -r requirements-openmeteo.txt'.\n")


#
# WidgetException Widget
# This is not an exception. It is a Widget to show that there was an
# issue instantiating a widget. This widget gets returned instead of
# the failed one.
#
class WidgetException(Widget):
  ARGUMENTS = [
    ("exception", str),
  ]


# Create a mapping of all valid widgets -> name: class
WIDGETS_BY_TYPE = {}
for n in dir():
  o = globals()[n]
  if inspect.isclass(o) and issubclass(o, Widget) and o is not Widget and o is not WidgetException:
    WIDGETS_BY_TYPE[o.__name__.lower()] = o


def load_widget(widget_type: str, **kwargs):
  """Returns the widget class given the widget type. Returns None if
  the widget type is not valid."""

  widgetCls = WIDGETS_BY_TYPE.get(widget_type.lower())
  if widgetCls is not None:
    try:
      widget = widgetCls(**kwargs)
    except (WidgetArgumentException, WidgetArgumentValueException, WidgetInitException) as e:
      # We're encountered a problem with the widget argunment definition.
      # We will return a custom widget that to allow the user to see the
      # Exception information.
      kwargs["exception"] = f"{str(e)} (widget: '{widget_type}')"
      widget = WidgetException(**kwargs)
    except Exception as e:
      print("UNHANDLED EXCEPTION", e)

    return widget

  print(f"Ignoring Widget '{widget_type}' ({kwargs})")
  return None


#
# Widget Finder
# Used to find all widgets defined within a config.
#
class WidgetFinder:
  """Use this class to find widgets within a config. This will add
  '_widget' to the existing widget entry in the config structure. The
  value of _widget will be the instantiated Widget."""

  def __init__(self, config: dict):
    assert isinstance(config, dict)
    self.config = config
    self._widget_id = 0

  def find_widgets(self, config: dict = None):
    """Returns a list of all widgets found in the supplied config."""
    widgets = []

    if config is None:
      config = self.config

    if isinstance(config, dict):
      for k, v in config.items():
        if k == "widgets":
          if isinstance(v, list):
            for widget in v:
              if not isinstance(widget, dict):
                continue
              self._widget_id += 1
              widget["id"] = self._widget_id
              args = { k: v for k, v in widget.items() if k not in ("id", "type") }
              widget["_widget"] = load_widget(widget.get("type"), **args)
              widgets.append(widget)
        if isinstance(v, dict):
          widgets.extend(self.find_widgets(v))
        elif isinstance(v, list):
          for item in v:
            widgets.extend(self.find_widgets(item))

    return widgets
