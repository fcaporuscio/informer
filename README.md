# Informer

Stay informed with whatever interests you. It is written in Python (3.11)
and uses Flask and Jinja2 at the core.

This starts a web server that will serve pages customized via a YAML
configuration file.

This project currently has very simple widgets to demonstrate how it all
comes together. It would be great to see widget contributions! I think this
is a great project for anyone as it isn't very complicated and you can get
new widgets up and running.

---

## Requirements

**Core**

- [cssminifier](https://pypi.org/project/cssminifier/)
- [feedparser](https://pypi.org/project/feedparser/)
- [Flask](https://pypi.org/project/Flask/)
- [Flask-APScheduler](https://pypi.org/project/Flask-APScheduler/)
- [Flask-Cors](https://pypi.org/project/flask-cors/)
- [Jinja2](https://pypi.org/project/Jinja2/)
- [pendulum](https://pypi.org/project/pendulum/)
- [PyYAML](https://pypi.org/project/PyYAML/)
- [requests](https://pypi.org/project/requests/)
- [requests-cache](https://pypi.org/project/requests-cache/)
- [retry-requests](https://pypi.org/project/retry-requests/)
- [rjsmin](https://pypi.org/project/rjsmin/)

**Open-Meteo Requirements**

- [openmeteo-requests](https://pypi.org/project/openmeteo-requests/)
- [numpy](https://pypi.org/project/numpy/)
- [pandas](https://pypi.org/project/pandas/)


The open-meteo requirements are kept separate because the dependencies
are large. Unless you intend to use the open-meteo widget, there is no
need to install these. These dependencies are stored in the **openmeteo**
group.

The requirements will be automatically synchronized on run:

```sh
# Install all the requirements
uv run informer.py

# Install all requirements except those for specifically for openmeteo
uv run --no-group openmeteo informer.py

# Install all requirements except those for specifically for jsmin
uv run --no-group jsmin informer.py
```

You can combine any number of --no-group items. The Docker image is
automatically built with all dependencies installed.

---

## Tree Structure

```
root                     : informer.py and config fil
  ├── core               : Core Python files
  ├── static             : Core JS
  │     └── widgets      : Widget JS
  ├── templates          : Template Loader
  │     ├── styles       : Core CSS
  │     │     └── widgets: Widget CSS
  │     └── widgets      : Widget HTML
  └── widgets            : Widget Python files
```

---

## Widgets

Below are all the existing widgets at this point. They are all available to be used.

- **chucknorris**: Chuck Norris facts
- **date**: display the time -- either your current time or from another timezone
- **garfield**: display the daily Garfield comic strip
- **gitea**: display basic information about a Gitea repository
- **github**: display basic information about a GitHub repository
- **rss**: displays RSS feed entries
- **lobsters**: displays RSS feed entries given a Lobsters tag
- **openmeteo**: displays basic weather details (fetches more than currently displayed). This widget needs some love!
- **reddit**: displays RSS feed entries given a Subreddit name
- **ronswanson**: displays Ron Swanson quotes
- **sitestatus**: displays the status (OK or ISSUE) with accessing a URL. Multiple URLs
may be defined
- **tabs**: group widgets under different sub-areas (tabs)
- **youtube**: get a video list from a specific channel
- **xkcd**: displays the latest xkcd comic

You can use the --show-config *widget_name* to see the configuration items for this widget:
```bash

python informer.py --show-config sitestatus

```

returns the following:
```text
Here are the parameter details for the SiteStatus widget:

widgets:
  - type: sitestatus
    name: str                   # default = None
    urls: list                  # default = None
      - name: str             
        url: str              
        accept_status: list   
    cache: str                  # default = 1m
```

## The 'cache' parameter

This indicates the cache duration. You must specify an integer and unit
value where the units are:
- **s**: seconds
- **m**: minutes
- **h**: hours
- **d**: days

Examples:
- **1m** = 1 minute
- **5m** = 5 minutes
- **2h** = 2 hours
- **1d** = 1 day

---

# Sample informer.yml

```yaml
pages:
  - name: Home
    slug: home
    title: Informer Home Page

    columns:
      - size: slim
        widgets:
          - type: date
            name: "New York"
            timezone: America/New_York
            datefmt: "${month} ${day}, ${year}"
            time: true
            timefmt: "${hour:12}:${minute:0}${ampm}"

          - type: sitestatus
            urls:
              - url: https://reddit.com/
                name: Reddit
              - url: https://news.ycombinator.com/
                name: Hacker News
              - url: https://lobste.rs/
                name: Lobsters
              - url: https://www.theregister.com/
                name: The Register
              - url: https://slashdot.org/
                name: Slashdot

      - size: wide
        widgets:
          - type: tabs
            tabs:
              - name: Tech News
                widgets:
                  - type: rss
                    url: https://www.wired.com/feed/category/gear/latest/rss
                    images: true
                    cache: 3h

                  - type: rss
                    url: https://www.wired.com/feed/category/science/latest/rss
                    images: true
                    cache: 3h

                  - type: rss
                    url: https://rss.slashdot.org/Slashdot/slashdot
                    showname: true
                    images: true
                    cache: 3h

                  - type: rss
                    url: https://techcrunch.com/feed/
                    images: true
                    cache: 3h

              - name: World News
                widgets:
                  - type: rss
                    url: https://feeds.bbci.co.uk/news/world/rss.xml
                    images: true
                    cache: 1h

                  - type: rss
                    url: https://www.cnbc.com/id/100727362/device/rss/rss.html
                    images: true
                    cache: 3h

                  - type: rss
                    url: https://www.cbsnews.com/latest/rss/world
                    images: true
                    cache: 1h

      - size: slim
        widgets:
          - type: youtube
            channel_id: UCeeFfhMcJa1kjtfZAGskOCA
            showname: true
            images: true
            cache: 1d

  - name: Programming
    columns:
      - size: slim
        widgets:
          - type: date
            name: "New York"
            timezone: America/New_York
            time: true
            timefmt: "${hour:12}:${minute:0}${ampm}"

      - size: wide
        widgets:
          - type: tabs
            tabs:
              - name: Python
                widgets:
                  - type: rss
                    url: https://blog.python.org/feeds/posts/default?alt=rss
                    cache: 1d
                    images: true

                  - type: reddit
                    subreddit: Python
                    cache: 3h
                    images: true
                    name: Reddit

                  - type: lobsters
                    tag: Python
                    cache: 3h
                    images: true
                    name: Lobsters

              - name: Go
                widgets:
                  - type: rss
                    url: https://golang.ch/feed/
                    images: true
                    cache: 3h

                  - type: reddit
                    subreddit: Golang
                    cache: 1d
                    images: true
                    name: Reddit

                  - type: lobsters
                    tag: go
                    cache: 1d
                    images: true
                    name: Lobsters

              - name: Rust
                widgets:
                  - type: rss
                    url: https://without.boats/index.xml
                    name: Rust News
                    cache: 1d
                    images: true

                  - type: reddit
                    subreddit: Rust
                    cache: 1d
                    images: true
                    name: Reddit

                  - type: lobsters
                    tag: rust
                    cache: 1d
                    images: true
                    name: Lobsters

              - name: Zig
                widgets:
                  - type: rss
                    url: https://ziglang.org/devlog/index.xml
                    cache: 1d
                    images: true

                  - type: reddit
                    subreddit: Zig
                    cache: 1d
                    images: true
                    name: Reddit

                  - type: lobsters
                    tag: zig
                    cache: 1d
                    images: true
                    name: Lobsters
```

---

## Theme

The default Theme definition can be found in core/config.py. All theme
items can be overwritten in your yml file by using the names defined in
the config file as follows:

```yaml
theme:
  - page_background_color: black
  - accent_color: "#2e8ed8"
  - section_color: goldenrod
  - section_active_color: gold
  - link_visited_color: gray
  - link_color: "#ffffff"
  - widget_colored_header: false
  - widget_background_color: "#202020"
  - widget_color: lightgray
  - widget_border_color: "#323232"
  - success_color: "#3f8f75"
  - failure_color: "#c24f3f"
```

---

# Contributions

You have an idea? Great! Make it come to life via a widget!

Here are some widget ideas:

- **Calendar**: This may be combined with the existing date widget;
- **Disk Space**: All disks or selected disks (total/free)
- **CPU Usage**: Percentage, per core, graphs, etc.
- **Memory Usage**: Current usage along with historical, graph, etc.
