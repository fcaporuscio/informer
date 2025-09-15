"""Page is the core Class that creates the HTML page by combining the
styles, css, javascript to load along with the widget HTML fragments."""

__all__ = ["Page"]


from core.files import *
from templates import *
from widgets import *


#
# Page
#
class Page:
  def __init__(self, full_config: dict, page_config: dict, theme: dict, version: str) -> None:
    """Gather all items required to build the page (stylesheets, scripts,
    widgets, etc)."""

    assert isinstance(full_config, dict)
    assert isinstance(page_config, dict)

    self.full_config = full_config
    self.config = page_config
    self.title = page_config.get("title", page_config.get("name", "Page"))
    self.theme = theme
    self.version = version

    # Create all widgets that belong to this page.
    self.widgets = WidgetFinder(self.config).find_widgets()

    # Extract all custom script and style tags
    script_files = set()
    style_files = set()

    # Get styles and scripts from each widget.
    for widget in self.widgets:
      w = widget.get("_widget")
      if w is None:
        continue

      script_filename = w.script_name
      if script_filename:
        script_files.add(script_filename)

      style_filename = w.style_name
      if style_filename:
        style_files.add(style_filename)

    self.script_files = script_files
    self.style_files = style_files

  @property
  def html(self) -> str:
    """Returns the HTML of the page."""

    pages = [
      { "name": cfg["name"], "slug": cfg.get("slug", cfg["name"]) }
      for cfg in self.full_config.get("pages")
      if isinstance(cfg, dict) and "name" in cfg
    ]

    template = loader_env.get_template("widgets/page.html")
    content = template.render({
      # All defined pages (so that we can show the links in the
      # navigation area.
      "pages": pages,

      # Our page title
      "title": self.title,

      # The config consists of the entire page config tree.
      "config": self.config,

      # All script files required to be loaded for this page.
      # "script_tags": self.script_tags,
      "script_files": self.script_files,

      # All style files required to be loaded for this page.
      # "style_tags": self.style_tags,
      "style_files": self.style_files,

      # All page widgets so that we have access to their params.
      "widgets": self.widgets,

      # Theme
      "theme": self.theme,

      # Version
      "version": self.version,

      # Hashes
      "css_hash": self.css_hash,
      "informerccs_hash": self.informercss_hash,
      "informerjs_hash": self.informerjs_hash,
      "js_hash": self.js_hash,
    })

    return content

  @property
  def css_hash(self):
    filenames = sorted(self.style_files)
    return get_bundle_hash(filenames, "css")

  @property
  def js_hash(self):
    filenames = sorted(self.script_files)
    return get_bundle_hash(filenames, "js")

  @property
  def informercss_hash(self):
    filenames = ["informer"]
    return get_bundle_hash(filenames, "informercss")

  @property
  def informerjs_hash(self):
    filenames = ["informer"]
    return get_bundle_hash(filenames, "informerjs")
