"""Widget: Reddit (Subreddit) Feed."""

from .widget import *
from .rss import *


__all__ = ["Reddit"]


class Reddit(RSS):
  """Fetches the Subreddit feed (RSS)."""

  ARGUMENTS = RSS.MAKE_ARGUMENTS(
    [("subreddit", str)],
    ignore=["url"]
  )

  CLASSNAME = "rss"

  def init(self):
    """Validate that we have a sane parameters."""

    subreddit = self.params["subreddit"]
    if not subreddit:
      raise WidgetInitException("Missing 'subreddit' parameter. It is required.'")

    self.params["url"] = f"https://www.reddit.com/r/{subreddit}.rss"

    limit = self.params["limit"]
    if limit is not None and limit <= 0:
      raise WidgetInitException(f"Invalid argument: limit={limit} (must be greater than 0).")
