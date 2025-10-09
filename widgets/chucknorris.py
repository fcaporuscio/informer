"""Widget: ChuckNorris"""

import random

from .widget import Widget, WidgetFetchDataException


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

  # We cache the "cateogries" for a year (since these don't change
  # often, maybe never). We store this value in ALTERNATE_CACHE_DURATIONS
  # so that the cache file will be considered valid when attempting to
  # prune the cache.
  CACHE_DURATION_1Y = "365d"
  ALTERNATE_CACHE_DURATIONS = [CACHE_DURATION_1Y]

  def get_cache_key(self):
    """We use the classname as the cache key, so if the widget is found
    on multiple pages it will still find the cache."""
    return self.classname

  def fetch_data(self):
    """Chuck Norris can roundhouse-kick fetched data in the face... with
    his fist."""

    headers = { "User-Agent": self.user_agent }

    # Retrieve the category list
    response = self.web_fetch("GET",
                              self.URL_CATEGORIES,
                              headers=headers,
                              timeout=2,
                              cache_duration=self.CACHE_DURATION_1Y)

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
      raise WidgetFetchDataException(f"Failed to fetch the feed: {self.URL + qs}")

    results = response.json()
    return results
