"""Core functions related to files."""

import hashlib

from core.config import *
from templates import *


__all__ = ["get_bundle_hash", "load_bundle_contents"]


def get_bundle_hash(bundle_files: list, bundle_type: str) -> str:
  """Returns the md5 hash for the file bundle."""

  bundled_text = load_bundle_contents(bundle_files, bundle_type)
  md5 = hashlib.md5(b"Informer")
  md5.update(bundled_text.encode())
  return md5.hexdigest()


def load_bundle_contents(bundle_files: list, bundle_type: str) -> str:
  """Load the contents of the bundle and return is as a single string."""

  if isinstance(bundle_files, str):
    bundle_files = sorted(bundle_files.split(","))
  if not isinstance(bundle_files, list):
    return ""

  cfg = Config()
  bundled_text = ""

  if bundle_type == "css":
    for filename in bundle_files:
      try:
        template = loader_env.get_template(f"styles/widgets/{filename}.css")
        bundled_text += f"/* {filename} */\n\n" + template.render({ "theme": cfg.theme }) + "\n\n\n"
      except Exception as e:
        print(make_bundle_file_error_message(bundle_type, e))

  elif bundle_type == "js":
    for filename in bundle_files:
      try:
        with open(f"./static/widgets/{filename}.js") as fp:
          file_text = fp.read()
          bundled_text += file_text
          bundled_text += "\n\n\n"
      except Exception as e:
        print(make_bundle_file_error_message(bundle_type, e))

  elif bundle_type == "informerjs":
    for filename in bundle_files:
      try:
        with open(f"./static/{filename}.js") as fp:
          file_text = fp.read()
          bundled_text += file_text
          bundled_text += "\n\n\n"
      except Exception as e:
        print(make_bundle_file_error_message(bundle_type, e))

  elif bundle_type == "informercss":
    for filename in bundle_files:
      try:
        with open(f"./templates/styles/{filename}.css") as fp:
          file_text = fp.read()
          bundled_text += file_text
          bundled_text += "\n\n\n"
      except Exception as e:
        print(make_bundle_file_error_message(bundle_type, e))

  return bundled_text


def make_bundle_file_error_message(bundle_type: str, error: Exception):
  """Returns a string showing the error."""
  return f"Unable to load {bundle_type} file: {str(error)}"
