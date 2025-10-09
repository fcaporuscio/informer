"""Widget: Site Status."""

import random

from templates import loader_env
from core.cache import CACHE
from .widget import Widget, WidgetInitException


__all__ = ["SiteStatus"]


#
# SiteStatus Widget
#
class SiteStatus(Widget):
  """Verify one or more site statuses."""
  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [("urls", list)],
    cache="1m"
  )

  ARGUMENTS_CONFIG = [
    ("urls", [
      ("name",           str),
      ("url",            str),
      ("accept_status", list)
    ]),
  ]

  SCRIPT = True
  STYLES = True
  POST_FETCH = True

  STATUS_OK = 200
  HAS_REQUESTS_SESSION = True

  def init(self):
    """Validate required arguments."""

    if not self.params["name"]:
      self.params["name"] = "Site Status"

    urls = self.params["urls"]
    if not isinstance(urls, list):
      raise WidgetInitException(f"The 'urls' parameter is required.")

    # Run though each URL definition and make sure all is fine, set
    # defaults along the way!
    for idx, url_entry in enumerate(urls, 1):
      assert isinstance(url_entry, dict)
      assert "url" in url_entry

      status_accept = url_entry.get("status_accept")
      if not isinstance(status_accept, list):
        status_accept = []

      # Write this back (it may not have been in the settings but we
      # want the value to be ready when needed).
      url_entry["status_accept"] = status_accept

      # Make sure STATUS_OK is included in the status_accept list.
      if self.STATUS_OK not in status_accept:
        status_accept.append(self.STATUS_OK)

  def fetch_data(self):
    """Obtain the site status for each URL in the params."""

    results = {}

    content_template = "widgets/sitestatus_item.html"
    template = loader_env.get_template(content_template)
    items_html = ""

    cache_duration = CACHE.duration_to_ts(self.params["cache"], as_seconds=True)

    for url_entry in self.params["urls"]:
      url = url_entry.get("url")
      status_accept = sorted(url_entry.get("status_accept"))

      random_cache_duration = random.randint(int(max([1, cache_duration // 1.15])), cache_duration)

      if isinstance(url, str) and url and isinstance(status_accept, list) and status_accept:
        try:
          headers = { "User-Agent": self.user_agent }
          # We request stream=True so that we don't actually download the
          # content of the page.
          response = self.web_fetch("GET", url,
                                    headers=headers,
                                    stream=True,
                                    timeout=2,
                                    expire_after=random_cache_duration)
          is_ok = response.status_code in status_accept
          status_code = response.status_code

          el = response.elapsed.total_seconds()
          elapsed = f"{el:0.2f}"

        except Exception:
          is_ok = False
          status_code = "Err"
          elapsed = None

        context = {
          "url": url,
          "status_code": status_code,
          "ok": is_ok,
          "elapsed": elapsed,
        }

        url_no_proto = url.split("://", 1)[-1]
        try:
          domain, uri = url_no_proto.split("/", 1)
          if not uri:
            uri = None
        except Exception:
          domain = url_no_proto.split("/", 1)[0]
          uri = None

        context.update({
          "domain": domain,
          "uri": uri,
          "name": url_entry.get("name"),
        })

        html_fragment = template.render(context)
        items_html += html_fragment

    results["html"] = items_html.strip()
    return results
