"""Widget: GitHub"""

import pendulum

from templates import loader_env
from .widget import Widget, WidgetFetchDataException, WidgetInitException


__all__ = ["GitHub"]


#
# GitHub Widget
#
class GitHub(Widget):
  """GitHub Repository Information"""

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [
      ("owner",        str),
      ("repository",   str),
      ("description",  bool,  False),
      ("license",      bool,  False),
      ("avatar",       bool,  True),
      ("showrelease",  bool,  True),
      ("stats",        bool,  True),
    ],
    cache="1h",
    ignore=["name"]
  )

  SCRIPT = True
  STYLES = True
  POST_FETCH = True
  URL_BASE = "https://api.github.com/repos"

  CONTENT_TEMPLATE = "widgets/github_body.html"

  def init(self):
    """Validate the parameters."""

    owner = self.params["owner"]
    repository = self.params["repository"]

    if owner is None or repository is None:
      raise WidgetInitException("Required parameters: owner, repository")

  def fetch_data(self):
    """Fetch the repository information."""

    owner = self.params["owner"]
    repository = self.params["repository"]
    headers = headers = { "User-Agent": self.user_agent }

    url = f"{self.URL_BASE}/{owner}/{repository}"
    response = self.web_fetch("GET", url, headers=headers)
    if not response.ok:
      raise WidgetFetchDataException(f"Failed to fetch the GitHub info for {owner}/{repository}")
    data = response.json()

    data = self.augment_date_fields(
      data,
      ("created_at", "updated_at", "pushed_at")
    )

    data["stars_count"] = data.pop("stargazers_count", None)
    data["open_issues_count"] = data.pop("open_issues", None)

    if self.params["showrelease"]:
      # Fetch the releases
      url = f"{url}/releases"
      response_releases = self.web_fetch("GET", url, headers=headers)
      if response_releases.ok:
        # We'll only bother showing releases if we get a successful
        # response.
        releases = response_releases.json()
        if isinstance(releases, list) and len(releases) > 0:
          latest_release = releases[-1]

          latest_release = self.augment_date_fields(
            latest_release,
            ("created_at", "updated_at", "published_at")
          )

          author_fields = ("login", "avatar_url")
          data["latest_release"] = {
            "author": {
              k: v
              for k, v in latest_release["author"].items()
              if k in author_fields
            },
          }

          release_fields = (
            "name",
            "tag_name",
            "reactions"
            "created_at",
            "created_at_ts",
            "published_at",
            "published_at_ts",
            "updated_at",
            "updated_at_ts",
          )

          data["latest_release"].update({
            k: v
            for k, v in latest_release.items()
            if k in release_fields
          })

    template = loader_env.get_template(self.CONTENT_TEMPLATE)

    context = {}
    context.update(data)
    context.update({
      "params": self.params,
    })

    html = template.render(context)
    data["html"] = html

    return data

  def augment_date_fields(self, data: dict, date_fields: list | tuple) -> dict:
    """Created a *_ts: timestamp key-pair based on the date values."""

    for fld in date_fields:
      try:
        ts = pendulum.parse(data.get(fld)).int_timestamp
        data[fld + "_ts"] = ts
      except Exception:
        pass

    return data
