# How to create a new Widget

Creating a widget is fairly simple once you are familiar with the
structure what understand what's happening.

There are several components at play:
- Widget code (Python, required);
- Widget code (JavaScript, if required);
- Widget styles (CSS, if required);
- Whether or not the widget requires fetching of data;
- All the possible Widget parameters;

## Python Code

Widgets must use the **Widget** parent class. They also have attributes
to define if they require CSS and JS files to be loaded.

```python
# Import the important widget code (the 'Widget' class is the most
# important here.
from .widget import *


# Only import the important data when 'import *' is used. We do this so
# that we dpn't polute the namespace where it is getting imported.
__all__ = ["MyNewWidget"]


class MyNewWidget(Widget):
  # SCRIPT: bool
  # True = automatically include "static/widgets/mynewwidget.js"
  SCRIPT = True

  # STYLE: bool
  # True = automatically include "templates/styles/widgets/mynewwidget.css"
  STYLE = True

  # POST_FETCH: bool
  # Indicates whether or not the widget requires fetching data. We don't
  # want to fetch data during the Widget initialization process because
  # it would block and make everything appear to be slow. Instead, we
  # set POST_FETCH = True and the JS will request the data for us once
  # the page is rendered.
  POST_FETCH = True

  # If you want to use caching for the web_fetch() method (described
  # later) you need to set this flag:
  HAS_REQUESTS_SESSION = True
  REQUEST_SESSION_TIMEOUT = 3600  # generic value, overwritten by the cache argument.

  # Define the arguments
  ARGUMENTS = Widget.MAKE_ARGUMENTS(...)
```

In order to make your widget available, you must import it in the
*\_\_init\_\_.py* file:

```python
from .mynewwidget import *
```

### The **ARGUMENTS** definition

Widget.MAKE\_ARGUMENTS takes 3 arguments:
- **Arguments Definition**: a list of tuples containing the argument name,
type/validator, and default value (optional, defaults to None);
- **cache**: this tells the Widget to cache the results of the 'fetch\_data'
method for a predefined amout of time;
- **ignore**: a list of paramter names to ignore -- the base Widget class has
a default argument of 'name' which may not be suitable; you may also
inherit from an existing widget and want to not include some of that
Widget's arguments;

#### Argument Definition Example

Let's say your widget has two possible parameters: author (a string) and
limit (a number), you'd create the following arguments:

```python
  [
    ("author", str),
    ("limit",  int, 10),
  ]
```

This tells the handler what arguments to load from the yaml file and, in
turn, ignore all parameters not defined for this widget. This structure
is also used with the **--show-config** argument.


#### Methods

***web\_fetch()***

The base Widget class implements this method so all Widgets will have it.
This uses requests\_cache in the backend so it will create sessions (cache
files) if needed -- based on whether or not your widget defined the
**cache** argument.

Use it like this:
```python

  headers = { "User-Agent": self.user_agent }
  url = "http://localhost:8001/personal-api/get-data/30"
  response = self.web_fetch("GET", url, headers=headers)
  results = response.json()
  return results
```

***fetch\_data()***

Your widgets should implement the *fetch\_data()* method. This method will
be called if *POST\_FETCH* is True. This should return a dictionary that
will, in turn, be sent back as JSON data.

```python
  def fetch_data(self):
    # ... slow, heavy work
    return { "my_content_data": "Widgets make me happy!" }
```

## JS Code

The JavaScript should look something like this:

```javascript
/* Your one-liner description */

defineInformerWidget(() => {

  class WidgetName extends informer.Widget {
    start() {
      // Grab the DOM nodes required when updating this widget
      this.content = this.node.querySelector(".widgetname-content");
    }

    receiveData(data) {
      // We've received our "POST_FETCH" data. We need to parse it and
      // update the screen accordingly. In this example we expect the
      // received data to contain a property named "my_content_data"
      // which is a string. We see this in the fetch_data()
      this.content.innerText = data.my_content_data;
    }
  }

  informer.createWidgetsForClass(WidgetName);
  // If the Widget name differs from the class name, then use the second
  // parameter to specify the widget this handles:
  //   informer.createWidgetsForClass(WidgetName, "mywidget");

});

```

## HTML Template

The HTML template has 2 parts: the header (usually text, defined with
a "widget-header" class) and the content (defined with the widget-box
class). The widget-header styles indicate that the text should be
displayed in uppercase.

```html
<div class="widget-header">MY HEADER</div>
<div class="widget-box">
    <div class="widget-content"></div>
</div>
```

This template is simple. It is the template for our JS example above.
It has a single updatable DOM node named "widget-content". This is the
node we "grab" i the JS' *start()* code and is the node we update when we
receive the data.
