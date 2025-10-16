"""Packages that may or may not be installed (not mandatory)."""

__all__ = ["jsmin", "CSSMinifier"]


#
# rjsmin.jsmin
#
try:
  from rjsmin import jsmin
except ModuleNotFoundError:
  def jsmin(s: str) -> str:
    return s


#
# cssminifier.Minifier (as CSSMinifier)
#
try:
  from cssminifier import Minifier as CSSMinifier
except ModuleNotFoundError:
  class CSSMinifier:
    def __init__(self, css: str, *args, **kwargs) -> None:
      self.css = css

    def __call__(self) -> str:
      return self.css
