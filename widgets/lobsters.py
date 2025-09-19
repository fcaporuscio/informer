"""Widget: Lobsters Videos."""

from .widget import *
from .rss import *


__all__ = ["Lobsters"]


class Lobsters(RSS):
  """Fetches the Lobsters tag feed (RSS)."""

  STR_LIST = (str, list)

  ARGUMENTS = RSS.MAKE_ARGUMENTS(
    [("tag", STR_LIST)],
    ignore=["url"]
  )

  CLASSNAME = "rss"

  def init(self):
    """Validate that we have a sane parameters."""

    tag = self.params["tag"]
    if not tag:
      raise WidgetInitException("Missing 'tag' parameter. It is required.'")

    tags = tag if isinstance(tag, list) else [tag]
    self.params["url"] = [ f"https://lobste.rs/t/{tag}.rss" for tag in tags ]

    limit = self.params["limit"]
    if limit is not None and limit <= 0:
      raise WidgetInitException(f"Invalid argument: limit={limit} (must be greater than 0).")
