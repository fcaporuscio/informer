"""Widget: RSS"""

import datetime
import feedparser
import pendulum

from templates import loader_env
from .widget import Widget, WidgetFetchDataException, WidgetInitException


__all__ = ["RSS"]


#
# RSS Widget
#
class RSS(Widget):
  """Fetch and parse feed data."""

  STR_LIST = (str, list)

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [
      ("url",         STR_LIST),
      ("limit",       int,       10),
      ("show",        int,       3),
      ("images",     bool,       False),
      ("imagesmall", bool,       False),
      ("showname",   bool,       True),
    ],
    cache="1h"
  )

  SCRIPT = True
  STYLES = True
  POST_FETCH = True

  HAS_REQUESTS_SESSION = True
  REQUESTS_SESSION_CACHE_TIMEOUT = 600  # ensures a minimum cache of 10 minutes

  def init(self):
    """Validate that we have a sane parameters."""

    url = self.params["url"]
    if not url:
      raise WidgetInitException("Missing 'url' parameter. It is required.'")

    limit = self.params["limit"]
    if limit is not None and limit <= 0:
      raise WidgetInitException(f"Invalid argument: limit={limit} (must be greater than 0).")

  def fetch_data(self):
    """Fetch and parse the RSS feed."""

    url = self.params["url"]
    results = self._fetch_data(url)
    return results

  def _fetch_data(self, url: str | list):
    """Fetch and parse the page, returning the final results."""

    if isinstance(url, str):
      url = [url]

    urls = url
    contexts = []
    url_errors = {}
    titles = set()

    show = self.params["show"]
    limit = self.params["limit"]

    headers = {
      "User-Agent": self.user_agent,
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
      "Accept-Encoding": "gzip, deflate",
      "Connection": "keep-alive",
      "Upgrade-Insecure-Requests": "1",
      "Sec-Fetch-Dest": "document",
      "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Site": "none",
      "Sec-Fetch-User": "?1",
    }

    for url in urls:
      # Fetch the raw feed data
      try:
        response = self.web_fetch("GET", url, headers=headers, timeout=2)
        if not response.ok:
          raise WidgetFetchDataException(f"Failed to fetch the feed: {url}")
      except Exception as e:
        url_errors[url] = e
        continue

      # Parse the feed
      feed = feedparser.parse(response.text)

      date_formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
      ]

      content_template = "widgets/rss_item.html"
      template = loader_env.get_template(content_template)
      rss_items_html = ""

      if hasattr(feed.feed, "title") and feed.feed.title:
        titles.add(feed.feed.title)

      # Loop through each entru
      for item in feed.entries[:limit]:
        if hasattr(item, "link"):
          link = item.link
        else:
          link = None

        if hasattr(item, "title"):
          title = item.title
        else:
          title = "NO TITLE"

        tags = set()
        if hasattr(item, "tags"):
          for tag in item.tags:
            if not isinstance(tag, dict):
              continue
            term = tag.get("term")
            if term:
              term = [ t.strip() for t in term.split("/") ]
              for t in term:
                tags.add(t.title())

        item_views = None
        media_statistics = item.get("media_statistics")
        if isinstance(media_statistics, dict):
          if "views" in media_statistics:
            item_views = self.short_value(media_statistics.get("views"))

        if self.params["images"]:
          media_content = item.get("media_content")
          media_thumbnail = item.get("media_thumbnail")

          if media_thumbnail:
            img_url = media_thumbnail[0]["url"]
          elif media_content:
            img_url = media_content[0]["url"]
          else:
            img_url = None

          if img_url is not None:
            # Don't include formats we don't validate (like .mov, for instance)
            valid_ext = ["jpg", "jpeg", "gif", "png", "svg"]
            if not any([ (img_url.split("?")[0]).endswith("." + ext) for ext in valid_ext ]):
              img_url = None
        else:
          img_url = None

        if hasattr(item, "published"):
          pub_date = item.published
        else:
          pub_date = None

        pub_dt = None

        if pub_date is not None:
          for date_format in date_formats:
            try:
              pub_dt = datetime.datetime.strptime(pub_date, date_format)
              pub_dt = pendulum.instance(pub_dt)
              break
            except Exception:
              pass

        context = {
          "params": self.params,
          "widgetclass": self.widgetclass,
          "self": self,
          "title": title,
          "link": link,
          "img_url": img_url,
          "pub_date": pub_dt.format("YYYY-MM-DD h:mmA").lower() if pub_dt is not None else None,
          "pub_ts": pub_dt.int_timestamp if pub_dt is not None else 0,
          "elapsed": self.elapsed_since(pub_dt),
          "tags": sorted(tags),
          "views": item_views,
          "feed_title": feed.feed.title if len(urls) > 1 and hasattr(feed.feed, "title") else None,
        }

        contexts.append(context)

    url_error = list(url_errors.values())
    if len(url_error) == len(set(urls)):
      raise url_error[0]
    elif len(url_error):
      for e in url_error:
        self.logger.debug(f"Issue retrieving feed: {str(e)}")

    # Sort all item contexts
    contexts = sorted(contexts, key=lambda c: c["pub_ts"], reverse=True)

    for idx, context in enumerate(contexts[:limit]):
      is_visible = show > idx if show is not None else True
      context["shown"] = is_visible
      html_fragment = template.render(context)
      rss_items_html += html_fragment

    has_more_to_show = show < limit if show is not None else False

    if titles:
      default_title = " / ".join(titles)
    elif len(urls) == 1 and hasattr(feed.feed, "title"):
      default_title = feed.feed.title
    else:
      default_title = "Unknown Title"

    results = {
      "name": (self.params["name"] or default_title) if self.params["showname"] else None,
      "html": rss_items_html,
      "has_more_to_show": has_more_to_show,
    }

    return results

  def short_value(self, value: int) -> str:
    """Shortes a value (eg. 1234 -> 1.2K)."""

    if value is None:
      return None

    if isinstance(value, str) and value.isdigit():
      value = int(value)

    if not isinstance(value, int):
      return value

    val = str(value)

    if len(val) > 9:
      ret_val = f"{value // 10000000 / 100.0:.1f}B"
    elif len(val) > 6:
      ret_val = f"{value // 10000 / 100.0:.1f}M"
    else:
      ret_val = f"{value // 10 / 100.0:.1f}K"

    return ret_val.replace(".0", "")
