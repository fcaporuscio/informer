"""Widget: YouTube Videos."""

from .widget import *
from .rss import *


__all__ = ["YouTube"]


class YouTube(RSS):
  """Fetches the YouTube channel feed (RSS)."""

  ARGUMENTS = RSS.MAKE_ARGUMENTS(
    [("channel_id", str)],
    ignore=["url"]
  )

  CLASSNAME = "rss"
  YOUTUBE_FEED_URL = "https://www.youtube.com/feeds/videos.xml"

  def init(self):
    """Validate that we have a sane parameters."""

    channel_id = self.params["channel_id"]
    if not channel_id:
      raise WidgetInitException("Missing 'channel_id' parameter. It is required.'")

    self.params["url"] = f"{self.YOUTUBE_FEED_URL}?channel_id={channel_id}"

    limit = self.params["limit"]
    if limit is not None and limit <= 0:
      raise WidgetInitException(f"Invalid argument: limit={limit} (must be greater than 0).")
