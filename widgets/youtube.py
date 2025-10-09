"""Widget: YouTube Videos."""

from .widget import WidgetInitException
from .rss import RSS


__all__ = ["YouTube"]


class YouTube(RSS):
  """Fetches the YouTube channel feed (RSS)."""

  STR_LIST = (str, list)

  ARGUMENTS = RSS.MAKE_ARGUMENTS(
    [("channel_id", STR_LIST)],
    ignore=["url"]
  )

  CLASSNAME = "rss"
  YOUTUBE_FEED_URL = "https://www.youtube.com/feeds/videos.xml"

  def init(self):
    """Validate that we have a sane parameters."""

    channel_id = self.params["channel_id"]
    if not channel_id:
      raise WidgetInitException("Missing 'channel_id' parameter. It is required.'")

    channel_ids = channel_id if isinstance(channel_id, list) else [channel_id]
    self.params["url"] = [ f"{self.YOUTUBE_FEED_URL}?channel_id={channel_id}" for channel_id in channel_ids ]

    limit = self.params["limit"]
    if limit is not None and limit <= 0:
      raise WidgetInitException(f"Invalid argument: limit={limit} (must be greater than 0).")
