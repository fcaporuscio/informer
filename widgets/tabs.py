"""Widget: Tabs"""

from .widget import *


__all__ = ["Tabs"]


#
# Tabs Widget
#
class Tabs(Widget):
  """Tabbed group of widgets. Each group requires a 'name' and 'widgets'
  to be considered valid."""

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [("tabs", list)],
    ignore=["name"]
  )

  ARGUMENTS_CONFIG = [
    ("tabs", [
      ("name", str),
      ("widgets", list),
    ])
  ]

  SCRIPT = True
  STYLES = True

  def get_render_context(self):
    """Exposes extra data for the widget to use."""

    context = super(Tabs, self).get_render_context()
    context.update({
      "tab_group_id": f"g-{self.uniqueclass}",
    })

    return context
