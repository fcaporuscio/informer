"""Widget: Garfield"""

import datetime
import pendulum
import random
import re

from .widget import *


__all__ = ["Garfield"]


#
# Garfield Widget
#
class Garfield(Widget):
  """Garfield. Monday. Spiders."""

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [
      ("title",  bool, True),
      ("random", bool, False),
      ("date",    str),
    ],
    cache="6h",
    ignore=["name"],
  )

  URL_BASE = "http://pt.jikos.cz/garfield"
  MIN_DATE = (1978, 6, 19)

  SCRIPT = True
  STYLES = "comic"
  POST_FETCH = True

  WIDGET_CLASS_NAME = "comic"
  HAS_REQUESTS_SESSION = True
  REQUEST_SESSION_TIMEOUT = 600  # ensures a minimum cache of 10 minutes

  def fetch_data(self):
    """The JS is requesting data (post-load). We need to prepare the
    data and return JSON."""

    is_random = self.params["random"]
    supplied_date = self.params["date"]
    exc = None

    if supplied_date:
      self.log_debug(f"Using supplied date '{supplied_date}'.")
      try:
        date = pendulum.parse(supplied_date, tz="America/New_York")

        earliest_date = self.get_earliest_date()
        latest_date = self.get_latest_date()

        if date < earliest_date or date > latest_date:
          raise WidgetFetchDataException(f"Invalid Garfield date specified. The date must be between "
                                         f"{earliest_date.format('YYYY-MM-DD')} and "
                                         f"{latest_date.format('YYYY-MM-DD')}.")
      except Exception as e:
        if isinstance(e, WidgetFetchDataException):
          exc = str(e)
        else:
          date = None
          try:
            raise WidgetFetchDataException(f"Unable to parse the supplied date: '{supplied_date}'")
          except Exception as e:
            exc = str(e)
    else:
      date = None

    if date is None:
      try:
        date = self.generate_random_date() if is_random else self.get_latest_date()
      except Exception:
        date = pendulum.now().start_of("day")

    if exc is None:
      try:
        url = self._get_garfield_url_for_date(date.year, date.month, date.day)
      except WidgetFetchDataException as e:
        exc = str(e)

    # Prepare and return the results. We only include the URL if we did
    # not encounter an error to limit the bytes transfered (uselessly).
    results = {
      "year": date.year,
      "month": date.month,
      "day": date.day,
    }

    if exc:
      results["error"] = exc
    else:
      results["url"] = url

    return results

  def _get_garfield_url_for_date(self, year: int, month: int, day: int):
    """This is the worker. Fetch the HTML page where all the glorious
    Garfield comics can be found, search for the desired image (based on
    year/mon/day supplied) and return the URL of the image."""

    exc_base = f"Failed to retrieve Garfield for {year}-{month:02d}-{day:02d}."
    month_url = f"{self.URL_BASE}/{year}/{month}/"
    url = ""

    self.log_debug(f"Retrieving Page information: {month_url}")

    response = self.web_fetch("GET", month_url)

    regexp = f"""<img src="([^"]+)\" alt="garfield {day}/{month}/{year}"/>"""
    for line in response.iter_lines():
      line = str(line)
      mo = re.search(regexp, line)
      if mo is not None:
        url = mo.groups()[0]

    if not url:
      raise WidgetFetchDataException(f"{exc_base}. Unable to find a suitable URL.")

    # Return the URL
    return url

  def get_earliest_date(self):
    """Returns the earliest date for which the Garfield comic is
    available."""

    return pendulum.datetime(*self.MIN_DATE)

  def get_latest_date(self):
    """Returns the latest date for which the Garfield comic is
    available."""

    # We give a leeway of 4 hours... just because I don't know when
    # they put the image up!

    return pendulum.now().subtract(hours=4).start_of("day")

  def generate_random_date(self):
    """Generates a random pendulum.datetime object between two given
    datetime objects."""

    start_date = self.get_earliest_date()
    end_date = self.get_latest_date()

    time_difference = end_date - start_date
    total_seconds = int(time_difference.total_seconds())
    random_seconds = random.randrange(total_seconds)
    random_date = start_date + datetime.timedelta(seconds=random_seconds)
    return random_date
