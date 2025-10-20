"""Informer"""

import argparse
import json
import hashlib
import os
import signal
import sys
import types

from flask import Flask, Response, redirect, request, url_for
from flask_compress import Compress
from flask_cors import CORS
from flask_apscheduler import APScheduler

from core.cache import CACHE
from core.config import Config, ConfigLoadException
from core.files import BUNDLER
from core.page import Page
from templates import loader_env
from widgets import WIDGETS_BY_TYPE, Widget, WidgetFinder


__version__ = "1.0.8"


CONFIG_FILENAME_DEFAULT = "informer.yml"
CONFIG_FILEPATH_DEFAULT = f"{os.path.join(os.path.dirname(__file__), CONFIG_FILENAME_DEFAULT)}"
HOST_DEFAULT = "localhost"
PORT_DEFAULT = 8080

CACHE_COMMAND = "cache"
CACHE_COMMAND_LIST = "list"
CACHE_COMMAND_CLEAN = "clean"
CACHE_COMMAND_PRUNE = "prune"
ALL_CACHE_COMMANDS = (CACHE_COMMAND_LIST, CACHE_COMMAND_CLEAN, CACHE_COMMAND_PRUNE)

CACHE_CONTROL = "public, max-age=31536000, immutable"


# Create the Flask App and setup CORS.
app = Flask(__name__)
Compress(app)
CORS(app)


#
# Methods
#
def main():
  """This is the entry point for the CLI."""
  # Get out parser and parse the user-supplied args (or defaults).
  parser = get_argument_parser()
  args = parser.parse_args()

  if args.show_config:
    widget_type = args.show_config
    widgetCls = WIDGETS_BY_TYPE[widget_type]

    print(f"Here are the parameter details for the {widgetCls.__name__} widget:")
    print("")
    print("widgets:")
    print(f"  - type: {widget_type}")

    d_arg_decl = { widget_args[0]: widget_args for widget_args in widgetCls.ARGUMENTS }
    all_arguments = list(d_arg_decl.values())

    args_config = dict(widgetCls.ARGUMENTS_CONFIG)

    for params in all_arguments:
      default_value = params[2] if len(params) > 2 else None
      name, validator = params[:2]

      if isinstance(validator, type):
        validator_str = validator.__name__
      elif isinstance(validator, (list, tuple)) and all([ isinstance(v, type) for v in validator ]):
        validator_str = "|".join([ _validator.__name__ for _validator in validator ])
      elif callable(validator):
        validator_str = f"{validator.__name__}() function"
      else:
        validator_str = "unknown"

      param_str = f"    {name:}: {validator_str}"
      print(f"{param_str:<30s}  # default = {str(default_value)}")

      if name in args_config:
        for idx, sub_args in enumerate(args_config[name]):
          sub_name, sub_validator = sub_args[:2]

          if isinstance(sub_validator, type):
            sub_validator_str = sub_validator.__name__
          elif callable(sub_validator):
            sub_validator_str = f"{validator.__name__}() function"
          else:
            sub_validator_str = "unknown"

          if idx == 0:
            hyphen = "-"
          else:
            hyphen = " "

          sub_param_str = f"      {hyphen} {sub_name}: {sub_validator_str}"
          print(f"{sub_param_str:<30s}")

    return

  # Let's make sure the configuration file exists.
  if not os.path.exists(args.config):
    print(f"Unable to load the configuration file: '{args.config}'")
    print("\nYou can specify a custom config file using the --config argument.")
    print("")
    parser.print_help()
    return 1

  # Initialize our config and start our Flask app.
  _ = Config(args.config)

  if args.command == CACHE_COMMAND:
    if not args.action:
      args.action = CACHE_COMMAND_LIST

    if args.action.lower() not in ALL_CACHE_COMMANDS:
      print(f"Use one of the following commands: "
            f"{', '.join(ALL_CACHE_COMMANDS)}.")
      return

    handle_cache_command(args)
    return

  # Let's start with the version!
  print(f" * Informer v{__version__}")
  print(f" * Config file: {args.config}")

  start_cache_cleanup_scheduler()
  app.run(host=args.host, port=args.port)


def get_argument_parser() -> argparse.ArgumentParser:
  """Create the argument parser and return it."""
  parser = argparse.ArgumentParser(description="Informer - Stay Informed", add_help=False)

  # Arguments
  parser.add_argument("--host", "-h", type=str, default=HOST_DEFAULT,
                      help=f"Host (default={HOST_DEFAULT}).")
  parser.add_argument("--port", "-p", type=int, default=PORT_DEFAULT,
                      help=f"Port (default={PORT_DEFAULT}).")
  parser.add_argument("--config", type=str, default=CONFIG_FILEPATH_DEFAULT,
                      help=f"Config file path (default={CONFIG_FILEPATH_DEFAULT}).")
  parser.add_argument("--show-config", type=str, choices=WIDGETS_BY_TYPE.keys(),
                      help="Show the configurable parameters for a widget.")
  parser.add_argument("-H", "--help", action="help",
                      help="Show this help message and exit.")

  subparsers = parser.add_subparsers(dest="command", help="Available commands")
  cache_parser = subparsers.add_parser(CACHE_COMMAND, help="Manage the app cache.")
  cache_subparsers = cache_parser.add_subparsers(dest="action", help="Cache actions")
  _ = cache_subparsers.add_parser(CACHE_COMMAND_LIST, help="List cached files.")
  _ = cache_subparsers.add_parser(CACHE_COMMAND_PRUNE, help="Prune caches")
  clean_parser = cache_subparsers.add_parser(CACHE_COMMAND_CLEAN, help="Clean/Delete cached files.")
  clean_parser.add_argument("widget", nargs="?", help="Specific widget to clean.")

  return parser


def handle_cache_command(args: argparse.Namespace) -> None:
  """The 'cache' command was used in the command-line. Let's take care
  of it!"""

  if args.action == CACHE_COMMAND_LIST:
    num_files = CACHE.list_cached_files()
    if num_files == 0:
      print("\nYou have no cache files.")

  elif args.action == CACHE_COMMAND_CLEAN:
    num_cleaned = CACHE.clean_cache(args.widget)
    if num_cleaned == 0:
      msg = "\nYou have no cache files to clean"
      if args.widget is not None:
        msg += f" for '{args.widget}'"
      msg += "!"

      print(msg)

  elif args.action == CACHE_COMMAND_PRUNE:
    # We need to prune existing and valid cache files as well as
    # delete cache files that are no longer valid (ie. the current
    # config files has no references to an existing cache file).

    # Load the config and determine all the widget types + duration
    # combinations

    try:
      config = Config().load()
    except ConfigLoadException as e:
      error = str(e)
      error = error.replace("<pre>", "").replace("</pre>", "")
      print(error)
      return

    pages = config.get("pages")
    all_widgets = []
    for page in pages:
      cols = page.get("columns")
      if not cols or not isinstance(cols, list):
        continue
      for col in cols:
        widgets = col.get("widgets")
        if not widgets or not isinstance(widgets, list):
          continue
        all_widgets.extend(widgets)

    page = {
      "name": "p",
      "slug": "p",
      "columns": [{
        "size": "wide",
        "widgets": all_widgets,
      }],
    }

    all_widgets = WidgetFinder(page).find_widgets()
    num_removed = CACHE.remove_invalid_cache_files(all_widgets)
    num_pruned = CACHE.prune_cache()
    if num_pruned == 0 and num_removed == 0:
      print("\nThere are no cache files to prune or remove!")

  else:
    print("Invalid cache command: '{args.action}'")


def get_config_hash(config: dict) -> str:
  """Returns the MD5 Hash for this config."""
  config_str = json.dumps(config, sort_keys=True, ensure_ascii=True, indent=0)
  md5 = hashlib.md5(b"InformerConfig")
  md5.update(config_str.encode())
  return md5.hexdigest()


#
# App Routes
#
@app.route("/", methods=["GET"])
def get_page():
  """The root will redirect to the first defined page in the config
  file."""

  try:
    config = Config().load()
  except ConfigLoadException as e:
    return f"<h4>{str(e)}</h4>", 500

  # Find the first defined page and redirect to it.
  pages = config.get("pages")
  if isinstance(pages, list):
    p = next((page for page in pages if isinstance(page, dict) and "name" in page), None)
    slug = p.get("slug", p["name"])
    if slug:
      return redirect(url_for("get_named_page", page=slug), code=302)
  return f"<h4>404 No Pages Defined: check '{Config().config_path}'</h4>", 404


@app.route("/<page>", methods=["GET"])
def get_named_page(page: str):
  """Will load the config information for this specific page."""

  user_agent = request.headers.get("User-Agent")
  Widget.USER_AGENT = user_agent

  try:
    config = Config().load()
  except ConfigLoadException as e:
    return f"<h4>{str(e)}</h4>", 500

  config_hash = get_config_hash(config)

  # Find the config for the desired page and instantiate the Page()
  # object.
  pages = config.get("pages")
  if isinstance(pages, list):
    page_config = next((p for p in pages if isinstance(p, dict) and page in [ p.get("slug"), p.get("name") ]), None)
  else:
    page_config = None

  if page_config is None:
    # This page simply does not exist
    return "<h4>404 Page Not Found</h4>", 404

  # In case the slug was not defined in the config, we'll set it to the
  # value we are using.
  page_config["slug"] = page
  theme = Config().theme

  # Instantiate our Page and return its html.
  p = Page(config, page_config, theme, f"{__version__}-{config_hash}")
  return p.html


@app.route("/informer.css", methods=["GET"])
def get_stylesheet():
  """Returns our main stylesheet CSS. We include 'theme' in the template
  context so that we can use this data in the template."""

  with app.test_client() as client:
    return client.get("/bundle_informercss.informercss")


@app.route("/bundle_<bundle_files>.<bundle_type>", methods=["GET"])
def bundler(bundle_files, bundle_type):
  """CSS/JS bundler."""

  bundled_text = BUNDLER.load_bundle_contents(bundle_files, bundle_type)
  response = Response(bundled_text)
  response.headers["Content-Type"] = "text/javascript" if bundle_type in ("js", "informerjs") else "text/css"
  response.headers["Cache-Control"] = CACHE_CONTROL
  response.headers["Pragma"] = "no-cache"
  response.headers["Expires"] = "0"

  return response


@app.route("/styles/widgets/<custom_css>", methods=["GET"])
def get_custom_stylesheet(custom_css: str):
  """Returns the CSS that is used by a widget. We include 'theme' in the
  template context so that we can use this data in the template."""

  cfg = Config()
  template = loader_env.get_template(f"styles/widgets/{custom_css}")
  response = Response(template.render({ "theme": cfg.theme, "settings": cfg.global_settings }))
  response.headers["Content-Type"] = "text/css"
  response.headers["Cache-Control"] = CACHE_CONTROL
  response.headers["Pragma"] = "no-cache"
  response.headers["Expires"] = "0"

  return response


@app.route("/widget/<widget_type>/data", methods=["POST"])
def widget_data(widget_type: str) -> dict:
  """This method should return JSON. It is used by some widget JS to
  fetch the widget data post-load. We do the loading post-load so that
  we don't stall the initial page load with potentially blocking
  requests."""

  params = request.json
  if not isinstance(params, dict):
    params = {}
  if "params" in params:
    params = params["params"]

  # Get widget id and make sure we return the ID with the data
  widget_id = request.args.get("widget_id")

  data = {}

  # Make sure we can find this widget!
  widgetCls = WIDGETS_BY_TYPE.get(widget_type)
  if widgetCls is None:
    data["error"] = f"Invalid widget type '{widget_type}'."
  else:
    try:
      widget = widgetCls(**params)

      cache_key = widget.get_cache_key()
      if cache_key is not None:
        widget_data = widget.cache_get(cache_key)
      else:
        widget_data = None

      if widget_data is None:
        widget_data = widget.fetch_data()

      if isinstance(widget_data, dict):
        data.update(widget_data)

        if cache_key is not None:
          widget.cache_set_short(cache_key, data, widget.params["cache"] or "1m")

      # data.update(widget.fetch_data())
    except Exception as e:
      data["error"] = str(e)

  response = {}
  response.update(data)
  response.update({ "widget_id": widget_id })

  return response


#
# Cache Cleanup Task
#
def cache_cleanup():
  print("[Task] Cache Cleanup")
  CACHE.clear_expired()


def start_cache_cleanup_scheduler():
  scheduler = APScheduler()
  scheduler.add_job(id='Cache Cleaner', func=cache_cleanup, trigger="interval", seconds=10 * 60)
  scheduler.start()


#
# Signals
#
def handle_shutdown(signum: int, frame: types.FrameType | None) -> None:
  """A signal has been received and a shutdown is required."""
  print(f"\nReceived signal {signum}. Performing graceful shutdown...")
  sys.exit(0)


#
# Prepare and Start!
#
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


if __name__ == '__main__':
  # Development
  main()
else:
  # WSGI - Setup the config path
  Config(CONFIG_FILEPATH_DEFAULT)
  start_cache_cleanup_scheduler()
