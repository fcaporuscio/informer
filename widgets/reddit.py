"""Widget: Reddit (Subreddit) Feed."""

from .widget import WidgetInitException
from .rss import RSS


__all__ = ["Reddit"]


class Reddit(RSS):
  """Fetches the Subreddit feed (RSS)."""

  STR_LIST = (str, list)

  ARGUMENTS = RSS.MAKE_ARGUMENTS(
    [("subreddit", STR_LIST)],
    ignore=["url"]
  )

  CLASSNAME = "rss"

  def init(self):
    """Validate that we have a sane parameters."""

    subreddit = self.params["subreddit"]
    if not subreddit:
      raise WidgetInitException("Missing 'subreddit' parameter. It is required.'")

    subreddits = subreddit if isinstance(subreddit, list) else [subreddit]
    self.params["url"] = [ f"https://www.reddit.com/r/{subreddit}.rss" for subreddit in subreddits ]

    limit = self.params["limit"]
    if limit is not None and limit <= 0:
      raise WidgetInitException(f"Invalid argument: limit={limit} (must be greater than 0).")
