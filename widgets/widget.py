"""Base Widget Class"""

import json
import logging
import pendulum
import requests
import requests_cache

from core.cache import *
from templates import *


__all__ = [
  "Widget",
  "WidgetException",
  "WidgetLoadException",
  "WidgetArgumentException",
  "WidgetArgumentValueException",
  "WidgetInitException",
  "WidgetFetchDataException",
  "WidgetInvalidWebFetchMethod",
  "WidgetWebFetchException",
]


#
# Exceptions
#
class WidgetException(Exception):
  """Base Exception for Widgets."""
  pass


class WidgetLoadException(WidgetException):
  """Exception during the loading the of Widget."""
  pass


class WidgetArgumentException(WidgetLoadException):
  """Invalid Widget argument."""
  pass


class WidgetArgumentValueException(WidgetLoadException):
  """Invalid argument value for the Widget."""
  pass


class WidgetInitException(WidgetException):
  """Exception during Widget init."""
  pass


class WidgetFetchDataException(WidgetException):
  """Exception during data fetching for the Widget (from JS, post-load)."""
  pass


class WidgetInvalidWebFetchMethod(WidgetException):
  """Invalid request method used for the Widget Web Fetch."""
  pass


class WidgetWebFetchException(WidgetException):
  """Exception during the Widget Web Fetch."""
  pass



#
# Widget Logging
#
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#
# Widget Parameters Class and JSON Encoder
#
class ParamsJSONEncoder(json.JSONEncoder):
  def default(self, o: any):
    if isinstance(o, Widget):
      return str(o)
    return super(ParamsJSONEncoder, self).default(o)


class Params:
  """Simple setter/getter backed by a dictionary."""
  def __init__(self):
    self.__dict__ = {}

  def __getitem__(self, key: str):
    return self.__dict__.get(key)

  def __setitem__(self, key: str, value: any) -> None:
    self.__dict__[key] = value

  def __repr__(self) -> str:
    return str(self)

  def __str__(self) -> str:
    return self.json

  @property
  def json(self) -> str:
    """Returns the JSON representation of our params data."""
    return json.dumps(self.__dict__, cls=ParamsJSONEncoder)

  @property
  def configArgs(self) -> str:
    """Returns the JSON representation of Widget configuration args.
    This method has a blacklist of widget types it must ignore."""

    blacklist = ("tabs",)
    return json.dumps({
      k: v
      for k, v in self.__dict__.items()
      if k not in blacklist
    } or None, cls=ParamsJSONEncoder)


#
# Widget
# Base Class
#
class Widget:
  """Base class. All widgets must inherit from this class. All widgets
  should implement the 'html' property. This is the HTML fragment that
  gets added to the page."""

  USER_AGENT = ""

  # Set if you want to include other top-level class names aside from
  # the default 'widget' class.
  WIDGET_CLASS_NAME = ""

  # If a widget is cacheable, use the following param name
  PARAM_CACHE = "cache"

  # This is the base widget template. No one needs to use this except
  # this class. It is meant to create the widget container with the
  # appropriate classes.
  TEMPLATE_BASE_HTML = "widget_base.html"
  
  # Define a list of ("name", validator) options where name will be the
  # property name and validator is a type of a callable. A field is
  # considered valid if 1) it is of that type, or 2) the callable
  # returns something thuthy.
  ARGUMENTS = [
    ("name", str),
  ]

  # If there are sub-args (let's say one of the args is a list), then we
  # can specify what arguments are expected, but these are not validated.
  # These are just to show when using the --show-config arg.
  ARGUMENTS_CONFIG = []

  # Use the following if you need to 'mimic' another widget and load its
  # classes, css and JS files (eg. CLASSNAME = "rss").
  CLASSNAME = None

  # By default the template filename is the widget's name (lower case)
  # followed by ".html". You can set an alternate template for your
  # instance by changing this value.
  TEMPLATE = ""

  # Script (JS) and Styles (CSS). Set to True to load using the default
  # name: widget's name + ".js"/".css". Alternatively, you can set this
  # the the name of the file you wish to load -- the name without the
  # extension (eg. STYLES = "mycustomname" would load "mycustomname.css")
  SCRIPT = ""  # True or "file.js" (True will use default name)
  STYLES = ""  # True or "file.css" (True will use default name)

  # Set to True if a request to obtain the widget's data is needed after
  # the page has rendered. Any widget that needs to fetch any type of
  # data should set this to True and implement the 'fetch_data()' method.
  POST_FETCH = False

  # Requests and Caching
  HAS_REQUESTS_SESSION = False
  REQUESTS_SESSION_CACHE_TIMEOUT = 60  # Default timeout (gets ignored if widget has a 'cache' param)

  @classmethod
  def MAKE_ARGUMENTS(cls, arguments_list: list | tuple, cache: str | None = None, ignore: list | tuple | None = None) -> list[tuple | list]:
    """Specify the Widget arguments and cache (using a duration_code
    such as '1m', '5m', '1h', etc). We will automatically include all
    the base arguments. We can ignore base arguments by including
    the names in the ignore list."""

    assert isinstance(arguments_list, (list, tuple))
    if not isinstance(ignore, (list, tuple)):
      ignore = []
    assert all([ isinstance(ignore_item, str) for ignore_item in ignore ]), f"All items in the ignore list should be str."

    args = cls.ARGUMENTS + list(arguments_list)
    if isinstance(cache, str):
      # Make sure it's a valid duration code
      CACHE.duration_to_ts(cache)  # will raise an exception if invalid!
      args.append((cls.PARAM_CACHE, str, cache))

    if ignore:
      args = [ arg for arg in args if arg[0] not in ignore ]

    # Return non-duplicate data
    return args

  def __init__(self, *args, **kwargs):
    self.logger = logging.getLogger(__name__)
    self._init_cache()

    self.args = args
    self.kwargs = kwargs
    self.params = Params()
    self._init_args()

    if self.POST_FETCH:
      self.params["fetch"] = True

    try:
      self.init()
    except Exception as e:
      raise WidgetInitException(str(e)) from e

  def __repr__(self) -> str:
    return f"Widget-{self.classname}"

  #
  # Properties
  #
  @property
  def classname(self) -> str:
    return self.CLASSNAME or self.__class__.__name__

  @property
  def cache_widget_type(self):
    return self.classname.lower()

  @property
  def widgetclass(self) -> str:
    """Returns the base class name to be used at the top-level
    container for the HTML fragment."""

    loadedCls = "loaded" if not self.POST_FETCH else ""
    alternateCls = f" {self.WIDGET_CLASS_NAME}" if self.WIDGET_CLASS_NAME else ""

    return f"widget widget-{self.classname.lower()} {self.uniqueclass} {loadedCls}{alternateCls}".strip()

  @property
  def uniqueclass(self) -> str:
    return f"wid-{id(self)}"

  @property
  def html(self) -> str:
    """This property needs to get overwritten by the widget class. By
    default we include a fragment that let's us know the widget's html
    property is missing!"""

    rendered_html = self.render()
    return rendered_html

  @property
  def script_tag(self) -> str:
    """This returns the script tag, if SCRIPT is set."""
    script_name = self.script_name
    if script_name:
      return f"""<script type="text/javascript" src="/static/widgets/{script_name}.js" defer></script>"""
    return ""

  @property
  def script_name(self) -> str:
    """Returns the script (JS) file name required for this widget."""
    if self.SCRIPT:
      script_name = self.SCRIPT if not isinstance(self.SCRIPT, bool) else f"{self.classname.lower()}"
      return script_name
    return ""

  @property
  def style_tag(self) -> str:
    """This returns the script tag, if SCRIPT is set."""
    style_name = self.style_name
    if style_name:
      return f"""<link rel="stylesheet" href="styles/widgets/{style_name}.css">"""
    return ""

  @property
  def style_name(self) -> str:
    """Returns the style (CSS) file name required for this widget."""
    if self.STYLES:
      style_name = self.STYLES if not isinstance(self.STYLES, bool) else f"{self.classname.lower()}"
      return style_name
    return ""

  @property
  def user_agent(self) -> str:
    return self.USER_AGENT or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

  #
  # Private Methods
  #
  def _init_cache(self) -> None:
    """Initialize the cache for this widget type."""
    CACHE.init_cache(self.cache_widget_type)

  def _init_args(self) -> None:
    """Initialize the arguments configured in self.ARGUMENTS. This will
    validate and make the property available to the "param" property."""

    type_set = (list, tuple, set)

    # Remove duplicate arg declarations (if any).
    d_arg_decl = { widget_args[0]: widget_args for widget_args in self.ARGUMENTS }
    all_arguments = list(d_arg_decl.values())

    for widget_args in all_arguments:
      try:
        # We need 2 entries minimum: name, type/validator.
        # The third option, default value, is optional and will default
        # to None if not specified.
        assert len(widget_args) >= 2
      except AssertionError as e:
        raise WidgetArgumentException(f"Invalid argument definition: {widget_args}")

      # Grab the name, type/validator, and default value.
      name, validator = widget_args[:2]
      default_value = widget_args[2] if len(widget_args) > 2 else None

      # Validate the argument supplied.
      assert isinstance(name, str) and len(name) > 0
      assert isinstance(validator, type) \
        or isinstance(validator, type_set) \
        or callable(validator)

      arg = self.kwargs.get(name)
      if arg is None and default_value is not None:
        arg = default_value

      valid = False
      valid = isinstance(arg, validator) \
        if isinstance(validator, type) \
          or isinstance(validator, type_set) \
        else validator(arg)

      if valid:
        self.params[name] = arg
      elif arg is not None:
        raise WidgetArgumentValueException(
          f"Parameter '{name}' (" \
          f"{str(validator).replace('<', '&lt;').replace('>', '&gt;')}" \
          f") is invalid in the configuration file. The validation failed")

  def _build_log_message(self, message: str) -> str:
    return f"[{self.__class__.__name__}] {message}"

  def _get_template_file(self) -> str:
    """Get the widget's template filename."""
    template_file = self.TEMPLATE
    if not template_file:
      template_file = f"{self.classname.lower()}.html"
    return template_file

  #
  # Public Methods
  #
  def init(self) -> None:
    """Widgets should override this if they have work to do during the
    __init__."""
    return

  def get_requests(self, cache_duration: int | str | None = None) -> requests_cache.CachedSession:
    """Returns the requests_cache's session or plain requests object
    based on the widget configuration. You may optionally specify the
    cache_duration (either the amount of seconds or the cache code, such
    as: 1m, 5m, 1h, 1d, etc.)."""

    if self.HAS_REQUESTS_SESSION:
      cache_duration = cache_duration or self.params[self.PARAM_CACHE]
      if isinstance(cache_duration, str):
        try:
          cache_duration = CACHE.duration_to_ts(cache_duration, as_seconds=True)
        except InvalidCacheDuration:
          cache_duration = None
      if not isinstance(cache_duration, int):
        cache_duration = self.REQUESTS_SESSION_CACHE_TIMEOUT

      return CACHE.get_requests_session(self, cache_duration)
    else:
      return requests

  def elapsed_since(self, dt: pendulum.DateTime) -> str:
    """Returns an approximate elapsed from from NOW, from minutes to
    weeks."""

    if dt is None:
      return None

    now = pendulum.now()
    em = int((now - dt).total_minutes())
    eh = 0
    ed = 0
    ew = 0

    while em >= 60:
      eh += 1
      em -= 60

    while eh >= 24:
      ed += 1
      eh -= 24

    while ed >= 7:
      ew += 1
      ed -= 7

    elapsed = f"{ew}w" if ew else f"{ed}d" if ed else f"{eh}h" if eh else f"{em}m"
    return elapsed

  def get_cache_key(self) -> str | None:
    """Return the key to be used for caching the results from
    fetch_data(). This should be used when possible to ensure we don't
    perform heavy parsing on the data fetched from the web (ie. we cache
    the final parsed data for a bit so that we save some time at the
    cost of memory usage). Return None to not use internal caching."""
    return None

  def cache_get(self, key: str) -> any:
    """Retrieves cache data. Returns None if there is no cached data or
    if it is expired."""
    results = CACHE.get_cache(self.cache_widget_type, key)
    if results is not None:
      msg = "Retrieved Cache"
      if key != self.classname:
        msg = f"{msg} [{key}]"
      self.log_debug(msg)
    return results

  def cache_set_short(self, key: str, data: any, duration_code: str) -> bool:
    """We will cache for half the duration, as long as the
    duration code is not shorter than 2 minutes."""

    o = duration_seconds = CACHE.duration_to_ts(duration_code, as_seconds=True)
    if duration_seconds > 120:
      h = lambda mins: mins // 2 // 60
      new_duration = h(duration_seconds)
      while new_duration >= 120:
        new_duration = h(new_duration * 60)
      duration_code = f"{new_duration}m"

    return self.cache_set(key, data, duration_code)

  def cache_set(self, key: str, data: any, duration_code: str) -> bool:
    """Stores cache data."""
    return CACHE.set_cache(self.cache_widget_type, key, data, duration_code)

  def log_debug(self, message: str):
    return self.logger.debug(self._build_log_message(message))

  def log_info(self, message: str):
    return self.logger.info(self._build_log_message(message))

  def get_template(self, template_file: str = None):
    """Return the template engine."""
    template_file = template_file or self._get_template_file()
    try:
      return loader_env.get_template(f"widgets/{template_file}")
    except Exception as e:
      print(f"ERROR loading template '{template_file}': {str(e)}")
    return None

  def get_render_context(self) -> dict:
    """Overwrite this method to expose more data to the template."""
    return {}

  def get_render_context_extras(self) -> dict:
    """If the widget needs to supply extra data to the template (something
    that is not the minimal default) then they need to overwrite this
    method and return a dictionary with the extra details."""

    return {}

  def render(self) -> str:
    """Render the template."""
    template_base = self.get_template(self.TEMPLATE_BASE_HTML)
    template = self.get_template()

    if template is not None and template_base is not None:
      context = {}
      extras = self.get_render_context_extras()
      if isinstance(extras, dict):
        context.update(**extras)

      context.update(**self.get_render_context())
      context.update(**{ "params": self.params, "widgetclass": self.widgetclass, "this": self })

      widget_html = template.render(context)
      context["widget_html"] = widget_html
      return template_base.render(context)

    # No template, no problem!
    return f"""<div class="widget widget-error">""" \
           f"""Missing: templates/widgets/<b>{self._get_template_file()}</b>""" \
           f"""</div>"""

  def fetch_data(self) -> dict:
    """Fetch the data for this widget (this would be initiated by the
    JS, post-load). This should get overwritten if the widget has post
    fetching."""

    return {}

  def web_fetch(self, method: str, url, allowed_status_codes: int | list = 200, **kwargs):
    """Calls requests.<method>(url, **kwargs). If the response status
    code is not in the allowed_status_codes list then we'll raise
    WidgetFetchDataException. Otherwise we will return the response. You
    can specify a customer cache_duration in the kwargs to set this
    request's cache timeout (overriding the default behavior)."""

    cache_duration = kwargs.pop("cache_duration", None)

    try:
      assert isinstance(method, str)

      # If the user supplied a single int (default) convert it to a list
      # to normalize the verification.
      if isinstance(allowed_status_codes, int):
        allowed_status_codes = [allowed_status_codes]

      assert isinstance(allowed_status_codes, list)
    except AssertionError as e:
      raise WidgetWebFetchException(str(e)) from e

    method = method.lower()

    req = self.get_requests(cache_duration)
    requests_method = getattr(req, method, None)

    if not callable(requests_method):
      raise WidgetInvalidWebFetchMethod(method)

    is_request_cache_session = hasattr(req, "cache") and hasattr(req.cache, "delete")
    if not is_request_cache_session and "expire_after" in kwargs:
      # This argument does not exist for the real requests object.
      kwargs.pop("expire_after", None)

    self.log_debug(f"web_fetch {method.upper()} {url}")
    try:
      response = requests_method(url, **kwargs)
    except Exception as e:
      raise WidgetFetchDataException(str(e))

    if response.status_code not in allowed_status_codes:
      if is_request_cache_session:
        self.log_debug(f"Received Status Code {response.status_code}, deleting cache for {url}")
        req.cache.delete(urls=[url])
      raise WidgetFetchDataException(f"Got status {response.status_code} for {url}.")

    return response
