
"""Widget: Ron Swanson."""

from .widget import *


__all__ = ["RonSwanson"]


class RonSwanson(Widget):
  """Fetches a randon Ron Swanson Quote."""

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [("number", int,  1)],
    cache="5m",
    ignore=["name"]
  )

  POST_FETCH = True
  SCRIPT = True
  URL = "https://ron-swanson-quotes.herokuapp.com/v2/quotes"

  HAS_REQUESTS_SESSION = True

  def get_cache_key(self):
    return self.classname

  def fetch_data(self):
    """Get a quote from Ron!"""

    headers = headers = { "User-Agent": self.user_agent }
    response = self.web_fetch("GET", f"{self.URL}/{self.params['number']}", headers=headers, timeout=2)

    if not response.ok:
      raise WidgetFetchDataException(f"Failed to fetch a Ron Swanson quote!")

    all_results = response.json()

    if not isinstance(all_results, list):
      results = [all_results]

    results = {
      "quotes": all_results,
    }

    return results
