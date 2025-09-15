import random

from templates import *
from .widget import *


__all__ = ["Quote"]


#
# Quotes shamelessly stolen from the internet!
#

RANDOM_QUOTES = [
  ("The only thing we have to fear is fear itself.",
   "Franklin D. Roosevelt"),

  ("That which does not kill us makes us stronger.",
   "Friedrich Nietzsche"),

  ("To be, or not to be, that is the question.",
   "William Shakespeare"),

  ("All that glitters is not gold.",
   "William Shakespeare"),

  ("Two roads diverged in a wood, and I—I took the one less traveled by, And that has made all the difference.",
   "Robert Frost"),

  ("The journey of a thousand miles begins with a single step.",
   "Lao Tzu"),

  ("You must be the change you wish to see in the world.",
   "Mahatma Gandhi"),

  ("Life is what happens when you're busy making other plans.",
   "John Lennon"),

  ("The only true wisdom is in knowing you know nothing.",
   "Socrates"),

  ("Believe you can and you're halfway there.",
   "Theodore Roosevelt"),

  ("Don't watch the clock; do what it does. Keep going.",
   "Sam Levenson"),

  ("The future belongs to those who believe in the beauty of their dreams.",
   "Eleanor Roosevelt"),

  ("What doesn't kill you makes you stronger.",
   "Friedrich Nietzsche"),

  ("Success is not final, failure is not fatal: It is the courage to continue that counts.",
   "Winston Churchill"),

  ("The best way to predict the future is to create it.",
   "Peter Drucker"),

  ("It always seems impossible until it's done.",
   "Nelson Mandela"),

  ("If you can dream it, you can do it.",
   "Walt Disney"),

  ("Houston, we have a problem.",
  "Jim Lovell"),

  ("Elementary, my dear Watson.",
  "Sherlock Holmes"),

  ("Frankly, my dear, I don't give a damn.",
  "Rhett Butler (Gone with the Wind)"),

  ("May the Force be with you.",
  "Star Wars"),

  ("I'm not superstitious, but I am a little stitious.",
  "Michael Scott (The Office)"),

  ("To thine own self be true.",
  "William Shakespeare"),

  ("The course of true love never did run smooth.",
  "William Shakespeare"),

  ("Love is a battlefield.",
  "Pat Benatar"),

  ("The greatest thing you'll ever learn is just to love and be loved in return.",
   "Nat King Cole"),
]


#
# Quote Widget
#
class Quote(Widget):
  """Displays static text."""

  ARGUMENTS = Widget.MAKE_ARGUMENTS([
    ("text",            str),
    ("text_classes",    str),
    ("subtext",         str),
    ("subtext_classes", str),
    ("random",          bool, False),
  ])

  def init(self):
    if(self.params.random):
      random_quote = random.choice(RANDOM_QUOTES)
      text, subtext = random_quote
      self.params["text"] = text
      self.params["subtext"] = f" - {subtext}"
