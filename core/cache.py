"""Global cache."""

import os
import pendulum
import re
import requests_cache


from platformdirs import user_cache_dir


__all__ = ["CACHE", "InvalidCacheDuration"]


class InvalidCacheDuration(Exception):
  """The duration code supplied is not valid."""
  pass


class Cache:
  """This is used to save bits of information that has already been
  parsed (so that we don't need to re-parse it for some time)."""

  CACHE_DIR = ".cache"
  FULL_CACHE_DIR = f"./{CACHE_DIR}"
  USE_USER_CACHE = False  # Only gets set via use_devel_cache_dir().

  re_cache_duration = re.compile(r'^(\d+)(s|m|h|d)')

  def __init__(self):
    self._cache = {}
    self._request_sessions = {}
    self._last_clean = None

  def _human_readable_duration(self, duration_seconds: int) -> str:
    """Convert the duration_seconds to a human-readable format."""
    minute = 60
    hour = minute * 60
    day = hour * 24
    results = {
      "d": 0,
      "h": 0,
      "m": 0,
      "s": duration_seconds
    }

    items = (
      (day, "d"),
      (hour, "h"),
      (minute, "m")
    )

    for item_duration, item_fld in items:
      while results["s"] >= item_duration:
        results[item_fld] += 1
        results["s"] -= item_duration
    parts = [ (results[item_fld], item_fld) for _, item_fld in items if results[item_fld] ]
    if results["s"]:
      parts.append((results["s"], "s"))
    return " ".join([ f"{value}{value_type}" for value, value_type in parts ])

  def use_devel_cache_dir(self):
    """This should only be used when running the development server,
    otherwise we want to use the default where the cache directory is
    in the app directory."""

    self.CACHE_DIR = "informer"
    self.FULL_CACHE_DIR = user_cache_dir(self.CACHE_DIR, self.CACHE_DIR)
    self.USE_USER_CACHE = True

  def get_requests_session(self, widget, duration: int) -> requests_cache.CachedSession:
    """Retrieve the 'requests' to be used to make web requests. This
    may be a requests_cache or plain requests, based on the widget
    configuration."""

    cache_file = f"{self.CACHE_DIR}/requests-{widget.cache_widget_type}-{duration}"
    session = self._request_sessions.get(cache_file)
    if session is not None:
      # Make sure the cache file still exists.
      if not os.path.exists(cache_file):
        session = None

    if session is None:
      session = requests_cache.CachedSession(cache_file,
                                             backend='sqlite',
                                             use_cache_dir=self.USE_USER_CACHE,
                                             expire_after=duration)
      self._request_sessions[cache_file] = session

      now = pendulum.now().int_timestamp
      if self._last_clean is not None and now - self._last_clean > 10 * 60:
        # Let's delete expired caches.
        session.cache.delete(expired=True)
      self._last_clean = now
    return session

  def list_cache_files_meta(self, widget_type: str = None) -> list[dict]:
    """Returns a list containing the current cache files."""

    try:
      filenames = os.listdir(self.FULL_CACHE_DIR)
    except FileNotFoundError:
      filenames = []

    files = []
    for filename in filenames:
      path = os.path.join(f"{self.FULL_CACHE_DIR}", filename)
      toolname, wt, duration = filename.replace(".sqlite", "").split("-")

      if widget_type is not None and widget_type != wt:
        continue

      try:
        duration = int(duration)
      except Exception:
        pass

      stat = os.stat(path)
      files.append({
        "size": stat.st_size,
        "path": path,
        "widget": wt,
        "duration": duration,
        "last_modified": stat.st_mtime,
      })

    return sorted(files, key=lambda o: o['path'])

  def list_cached_files(self) -> int:
    """Lists the cached files and returns the number of files in the
    cache."""

    now = pendulum.now()
    timezone = now.timezone
    tz = timezone.name

    file_data = self.list_cache_files_meta()
    if file_data:
      total_size = 0

      print("")
      print(f"{'Widget':>15s}  {'Duration':<8s}  {'Size (bytes)':>12s}  {'Last Modified':<18s} ")
      print(f"{'-' * 15}  {'-' * 8}  {'-' * 12}  {'-' * 18}")

      for cache_file in file_data:
        total_size += cache_file["size"]
        last_modified = cache_file["last_modified"]
        mod_dt = pendulum.from_timestamp(int(last_modified), tz=tz).format("YYYY-MM-DD h:mmA").lower()
        print(f"{cache_file['widget']:>15s}  "
              f"{self._human_readable_duration(cache_file['duration']):<8s}  "
              f"{cache_file['size']:>12d}  {mod_dt:<18s}")

      print(f"{'-' * 15}  {'-' * 8}  {'-' * 12}  {'-' * 18}")
      print(f"{'total bytes:':<26s} {total_size:>12d}")
      return len(file_data)
    return 0

  def clean_cache(self, widget_type: str = None) -> int:
    """Removes the cached files for the cache directory and return the
    number of files removed."""

    total_removed = 0
    total_size = 0

    file_data = self.list_cache_files_meta(widget_type=widget_type)
    if file_data:
      print(f"\nThere are {len(file_data)} cache file(s) to clean.")
      for cache_file in file_data:
        path = cache_file["path"]
        try:
          print(f"  - Removing {path}...")
          os.unlink(path)
          total_removed += 1
          total_size += cache_file["size"]
        except Exception as e:
          print(f"    * Unable to clean '{path}': {str(e)}")

    if total_removed:
      print(f"\nCleaned {total_removed} cached file(s) for a total of {total_size} bytes ({total_size // 1000} kb).")

    return total_removed

  def duration_to_ts(self, duration_code: str, as_seconds: bool = False) -> int:
    """Converts our cache duration values to an actual timestamp (unless
    as_seconds is True). The duration values have the following format,
    where <n> is an int and is always based from 'now':
      - <n>s: n number of seconds
      - <n>m: n number of minutes
      - <n>h: n number of hours
      - <n>d: n number of days

    Example: 1h would create a timestamp that is 'now + 1 hour', or 3600
    if 'as_seconds' is True.

    Raises InvalidCacheDuration if the duration code is invalid.
    """

    mo = self.re_cache_duration.match(duration_code)
    if mo is None:
      raise InvalidCacheDuration(f"Invalid cache duration '{duration_code}'")

    n, unit = mo.groups()
    n = int(n)

    expires_ts = pendulum.now().int_timestamp

    seconds = 0

    match(unit):
      case "s":
        seconds = n
      case "m":
        seconds = (n * 60)
      case "h":
        seconds = (n * 60 * 60)
      case "d":
        seconds = (n * 60 * 60 * 24)

    expires_ts += seconds
    return expires_ts if as_seconds is not True else seconds

  def init_cache(self, widget_type: str) -> None:
    """Initialize the cache bucket for a specific widget type. Many
    widgets may attempt to initialize for the same type, so we make sure
    we have not already initialized it."""

    if widget_type not in self._cache:
      self._cache[widget_type] = {}

  def set_cache(self, widget_type: str, key: str, data: any, duration_code: str) -> bool:
    """Store cache data for this widget type. Raises an exception if the
    duration code is not valid (see duration_to_ts)."""

    expires_ts = self.duration_to_ts(duration_code)

    now = pendulum.now().int_timestamp
    if now >= expires_ts:
      # Already expired, don't bother!
      return False

    widget_cache = self._cache.get(widget_type)
    if not isinstance(widget_cache, dict):
      widget_cache = {}

    widget_cache[key] = [data, expires_ts]
    self._cache[widget_type] = widget_cache
    return True

  def get_cache(self, widget_type: str, key: any) -> any:
    """Retrieves an item from the cache and returns it. Returns None if
    the data is not in cache or if it is expired. This method will also
    remove the expired cache entry if it is found."""

    now = pendulum.now().int_timestamp

    widget_cache = self._cache.get(widget_type)
    if not isinstance(widget_cache, dict):
      # Definitely not in the cache
      return None

    cache_data = widget_cache.get(key)
    if not isinstance(cache_data, list):
      return None

    data, expires_ts = cache_data
    if expires_ts <= now:
      # Remove this expired cache data!
      del widget_cache[key]
      self._cache[widget_type] = widget_cache
      return None

    # Return the data
    return data

  def clear_expired(self) -> None:
    """Run through all the data and expire the caches that are
    expired."""

    now = pendulum.now().int_timestamp
    to_delete = set()

    for widget_type, widget_cache in self._cache.items():
      for key, cache_data in widget_cache.items():
        if cache_data[1] <= now:
          to_delete.add((widget_type, key))

    for widget_type, key in to_delete:
      # Getting the cache that we know is expired will delete it.
      self.get_cache(widget_type, key)


#
# Create our cache instance
#
CACHE = Cache()
