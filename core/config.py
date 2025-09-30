"""Config Loader. Loads the config file and prepares the Themes (uses
defaults that can get overwritten by config settings)."""

import re
import yaml

from templates.loader import get_hex_color, page_name


__all__ = ["Config"]


#
# Config
#
class Config:
  """Singleton that holds is used to load the yaml configuration. It
  also defines the default theme information."""
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def __init__(self, config_path: str = None):
    """We only store if the configuration path if we have it. Otherwise
    we will need to set it later via set_config_path()."""
    if config_path:
      self.set_config_path(config_path)

  def set_config_path(self, config_path: str):
    """Sets the configuration path."""
    self.config_path = config_path

  def load(self, use_cache: bool = False):
    """Load the latest config from disk, or use the cache if we already
    have it and use_cache is True. Typically, we wouldn't want to load
    from cache, as we'd want to make sure we load all the latest updates
    the user may have made."""

    if use_cache and hasattr(self, "_load_data"):
      return self._load_data

    # Parse the config
    try:
      with open(self.config_path) as fp:
        load_data = yaml.safe_load(fp.read())
        load_data = self._sanitize(load_data)
        setattr(self, "_load_data", load_data)
        return load_data
    except Exception as e:
      print(f"Error parsing the config file: {str(e)}")
    return None

  def _sanitize(self, config: dict):
    """Ensures each page has a slug definition and that hidden pages
    get removed. Modifies the config dictionary and returns it."""

    pages = []

    if "pages" in config and isinstance(config["pages"], list):
      for page in config["pages"]:
        if isinstance(page, dict):
          name = page.get("name")
          slug = page.get("slug")

          if name and not slug:
            slug = page_name(name)
            page["slug"] = slug

          if not page.get("hide") is True:
            pages.append(page)
      config["pages"] = pages

    return config

  def _theme_property(self, prop: str):
    """Utility: convert dashes to underscore so that it is accessible
    from the templates via {{ theme.propert_name }}."""
    return prop.replace("-", "_")

  @property
  def theme(self):
    """Return the full theme (default + overrides)."""

    # Prepare the theme information.
    theme = self._get_default_theme()

    # Normalize the color values
    for k, v in theme.items():
      theme[k] = get_hex_color(v)

    # Get the user theme data (these can override the defaults).
    full_config = self.load(use_cache=True)
    if full_config is not None:
      _theme_items = full_config.get("theme")
      if isinstance(_theme_items, list):
        for _theme_item in _theme_items:
          if not isinstance(_theme_item, dict):
            continue
          for k, v in _theme_item.items():
            theme.update({ self._theme_property(k): get_hex_color(v) })

    return theme

  @property
  def global_settings(self):
    """Returns settings defined in the config file."""

    config = self.load(use_cache=True)
    user_settings_items = config.get("settings")
    if not isinstance(user_settings_items, list):
      user_settings_items = []

    user_settings = {}
    for usi in user_settings_items:
      if isinstance(usi, dict) and len(usi) == 1:
        user_settings.update(usi)

    settings = {
      "hide_errors": False,
    }

    settings.update(user_settings)
    return settings

  def _get_default_theme(self):
    """Returns the default theme data. Any of these can be overwritten
    or added from the config file's 'theme' section. All colors must
    be defined as HTML colors (or 'transparent')."""

    return {
      # Page
      "page_background_color": "#222222",
      "accent_color": "#ffa500",

      # Sections (headers, tabs, etc.)
      "section_color": "gray",
      "section_hover_color": "lightgray",
      "section_active_color": "white",

      # Links
      "link_visited_foreground_color": "#666666",
      "link_hover_foreground_color": "white",
      "link_active_foreground_color": "darkgoldenrod",

      # Widgets
      "widget_colored_header": False,
      "widget_background_color": "#292931",
      "widget_foreground_color": "#999999",
      "widget_border_color": "#323232",

      # Misc.
      "success_color": "#3f8f75",
      "failure_color": "#c24f3f",
    }
