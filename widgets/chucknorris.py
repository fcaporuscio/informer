"""Widget: ChuckNorris"""

import random

from .widget import *


__all__ = ["ChuckNorris"]


#
# ChuckNorris Widget
#
class ChuckNorris(Widget):
  """Chuck Norris eats docstrings for breakfast."""

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [("explicit", bool, False)],
    cache="5m",
    ignore=["name"]
  )

  SCRIPT = True
  POST_FETCH = True
  URL = "https://api.chucknorris.io/jokes/random"
  URL_CATEGORIES = "https://api.chucknorris.io/jokes/categories"

  HAS_REQUESTS_SESSION = True

  def get_cache_key(self):
    return self.classname

  def fetch_data(self):
    """Chuck Norris can roundhouse-kick fetched data in the face... with
    his fist."""

    headers = { "User-Agent": self.user_agent }

    # Retrieve the category list
    response = self.web_fetch("GET", self.URL_CATEGORIES, headers=headers, timeout=2, cache_duration="1d")
    if response.ok:
      categories = response.json()
      if not self.params["explicit"] and "explicit" in categories:
        categories.remove("explicit")
    else:
      categories = []

    category = random.choice(categories)

    qs = f"?category={category}" if category else ""
    response = self.web_fetch("GET", self.URL + qs, headers=headers, timeout=2)

    if not response.ok:
      raise WidgetFetchDataException(f"Failed to fetch the feed: {url}")

    results = response.json()
    return results
