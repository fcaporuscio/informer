"""Widget: xkcd"""

from .widget import *


__all__ = ["xkcd"]


#
# xkcd Widget
#
class xkcd(Widget):
  """xkcd."""

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [],
    cache="6h",
    ignore=["name"]
  )

  URL = "https://xkcd.com/info.0.json"

  SCRIPT = True
  STYLES = "comic"
  POST_FETCH = True

  WIDGET_CLASS_NAME = "comic"
  HAS_REQUESTS_SESSION = True
  REQUEST_SESSION_TIMEOUT = 3600  # ensures a minimum cache of 1 hour

  def fetch_data(self):
    """The JS is requesting data (post-load). We need to prepare the
    data and return JSON."""

    headers = { "User-Agent": self.user_agent }
    response = self.web_fetch("GET", self.URL, headers=headers)
    if not response.ok:
      raise WidgetFetchDataException(f"Retrieving the xkcd url failed.")

    results = response.json()
    return results
