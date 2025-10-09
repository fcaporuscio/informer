/* Informer JS: Core */

window.addEventListener('load', (event) => {

  console.log("[ Informer ] Preparing Page...");

  /*
  ** Widget base class. Widgets should extend this classes unless they
  ** are simple, static widgets!
  */
  class Widget {
    constructor(node, params, unique_id) {
      this.node = node;
      this.params = this._initParams(params);

      if(typeof(unique_id) == "number") {
        this.widget_id = unique_id;
      }

      this.fetchData = ((ctx) => {
        return () => {
          ctx._fetchData();
        }
      })(this);


      this.start();
      setTimeout(this.fetchData);

      if(this.params?.name) {
        this._log(`Created Widget (${this.params.name})`);
      }
      else {
        this._log("Created Widget");
      }
    }

    _log(message) {
      if(this.widget_id) {
        console.log(`[ ${this.constructor.name}/${this.widget_id} ] ${message}`)
      }
      else {
        console.log(`[ ${this.constructor.name} ] ${message}`)
      }
    }

    _initParams(params) {
      params = params || {};

      if(params.offset_seconds === undefined) {
        params.offset_seconds = 0;
      }

      return params
    }

    _fullyLoaded() {
      informer.addClass(this.node, "loaded");

      var loaderNode = this.node.querySelector(".loader");
      while(loaderNode) {
        informer.removeClass(loaderNode, "loader");
        loaderNode = this.node.querySelector(".loader");
      }
    }

    _fetchData(force) {
      if(this.params.fetch === true || force === true) {
        informer.fetchWidgetData(this);
      }
      else {
        this._fullyLoaded();
      }
    }

    start() {}

    /**
     * Sets up fields for the current Widget. The fields_arr is an array
     * of 2 items: [field_name, querySelector string].
     * 
     * Example:
     *     setupDomFields([["my_field", ".fields.my-field"]])
     * 
     * This will create:
     *     this.my_field = this.node.querySelector('.fields.my-field')
     */
    setupDomFields(fields_arr) {
      const widget = this;

      fields_arr.forEach(field_def => {
        const [field_name, qs] = field_def;

        if(widget[field_name] !== undefined) {
          console.error(`setupDomFields: cannot assign '${field_name}' to widget since this field already exists`);
        }
        else {
          widget[field_name] = widget.node.querySelector(qs);
        }

      });
    }

    refresh() {
      this._log("Requesting Refresh");
      this._fetchData(true);
    }

    setRefreshInterval(seconds) {
      var fn = ((ctx) => {
        return () => {
          ctx.refresh();
        }
      })(this);

      this._log("Setting Refresh Interval to " + seconds.toString() + " second" + (seconds != 1 ? "s" : "") + ".");
      setInterval(fn, seconds * 1000);
    }

    receivingData(data) {
      if(data.error) {
        informer.setWidgetError(this, data.error);
      }
      else {
        this.receiveData(data);
      }

      this._fullyLoaded();
      this._log("Received Data");
    }

    receiveData(data) {
      console.log("Received data that is getting dropped.", data);
    }
  }


  /*
  ** Date Formatter
  */
  class DateFormatter {
    constructor() {
      this._months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
      ]

      this.default_format = "${month:short} ${day}, ${year} ${hour:12}:${minute:0}${ampm}";

    }

    formatDate(date, format) {

      if(format === undefined) {
        format = this.default_format;
      }

      var result = format;
      var formatters = {
        "${year}": this._format_Y,

        "${month}": this._format_month,
        "${month:number}": this._format_M,
        "${month:short}": this._format_month_abbrev,

        "${day}": this._format_D,
        "${day:0}": this._format_D_0,

        "${hour}": this._format_H24,
        "${hour:24}": this._format_H24,
        "${hour:12}": this._format_H12,
        "${hour:24:0}": this._format_H24_0,
        "${hour:12:0}": this._format_H12_0,

        "${minute}": this._format_minute,
        "${minute:0}": this._format_minute0,

        "${ampm}": this._format_AMPM_lower,
        "${ampm:upper}": this._format_AMPM_upper,
      }

      var fmtFn, value;

      for(var formatter in formatters) if(formatters.hasOwnProperty(formatter)) {
        if(result.indexOf(formatter) > -1) {
          fmtFn = formatters[formatter];
          value = fmtFn.apply(this, [date]) || "";
          result = result.replace(formatter, value);
        }
      }

      return result
    }

    _format_Y(date) {
      return date.getFullYear().toString();
    }

    _format_M(date) {
      var month = date.getMonth() + 1;
      return String(month).padStart(2, "0");
    }

    _format_D(date) {
      return date.getDate().toString();
    }

    _format_D_0(date) {
      return String(this._format_D(date)).padStart(2, "0");
    }

    _format_H24(date) {
      return date.getHours().toString();
    }

    _format_H24_0(date) {
      return this._format_H24(date).padStart(2, "0");
    }

    _format_H12(date) {
      var hour = date.getHours();
      if(hour == 0) {
        hour = 12;
      }
      else if(hour > 12) {
        hour -= 12;
      }

      return hour.toString();
    }

    _format_H12_0(date) {
      return this._format_H12(date).padStart(2, "0");
    }

    _format_minute(date) {
      return date.getMinutes().toString();
    }

    _format_minute0(date) {
      return this._format_minute(date).padStart(2, "0");
    }

    _format_AMPM_lower(date) {
      var hour = date.getHours();
      if(hour >= 12) return "pm";
      return "am";
    }

    _format_AMPM_upper(date) {
      console.log(this);
      return this._format_AMPM_lower(date).toUpperCase();
    }

    _format_month(date) {
      return this._months[date.getMonth()];
    }

    _format_month_abbrev(date) {
      return this._months[date.getMonth()].slice(0, 3);
    }
  }


  /*
  ** Informer
  */
  class Informer {
    constructor() {
      this.Widget = Widget;
      this.DateFormatter = DateFormatter;

      this.node = document.getElementById("app");
      this.cls_tab_hidden = "tab-hidden";
      this.tabs = undefined;
      this.widgets = {};
      this.widgetClasses = {};  // loaded class definitions will be stored here.
      this.widgetParams = {};
      this._curWidgetID = 0;
      this.theme = {};
      this.initApp();
    }

    initApp() {
      // Find all tab groups and only show the content of the first
      // container.
      var widget_tabs = document.getElementsByClassName("widget-tabs");
      for(var i = 0, il = widget_tabs.length; i < il; i++) {
        var widget_tab = widget_tabs.item(i);
        var tab_containers = widget_tab.getElementsByClassName("tab-container");
        for(var j = 0, jl = tab_containers.length; j < jl; j++) {
          var tab_container = tab_containers.item(j);
          // Set the proper classes
          if(j == 0) {
            this.addRemoveClass(tab_container, "tab-content-visible", "tab-content-hidden");
          }
          else {
            this.addRemoveClass(tab_container, "tab-content-hidden", "tab-content-visible");
          }
        }
      }
    }

    setWidgetParams(widgetParams) {
      this.widgetParams = widgetParams;
    }

    getWidgetParamsByWID(wid) {
      var params = this.widgetParams?.[wid];
      if(params) {
        params["wid"] = wid;
      }
      return params;
    }

    setTheme(theme) {
      this.theme = theme;
    }

    addClass(node, clsName) {
      if((" " + node.className + " ").indexOf(" " + clsName + " ") == -1) {
        node.className += " " + clsName;
      }
    }

    hasClass(node, clsName) {
      return (" " + node.className + " ").indexOf(" " + clsName + " ") > -1;
    }

    removeClass(node, clsName) {
      var classes = node.className.split(" ");
      var final = "";

      classes.forEach(cls => {
        final += (cls != clsName) ? ` ${cls}` : "";
      });

      node.className = final.trim();
    }

    addRemoveClass(node, addCls, removeCls) {
      this.removeClass(node, removeCls);
      this.addClass(node, addCls);
    }

    /*
    ** Retrieve the WID (class) from a node. Returns null if one cannot
    ** be found. This is a unique ID per widget. Even widgets of the
    ** same type will get a unique id.
    */
    getWIDFromNode(node) {
      var classes = node.className.split(" ");
      for(var i = 0, il = classes.length; i < il; i++) {
        var cls = classes[i];
        if(cls.startsWith("wid-")) {
          return cls;
        }
      }

      return null;
    }

    /*
    ** Instantiate widget classes (for those that require an active
    ** object) and store them. The widget type is the type used from the
    ** config file. The widgetClass is used to create the object:
    **
    **   new WidgetClass(node, parameters)
    **
    ** The node is the DOM element handled by the widget. Parameters
    ** are the parameters supplied in the config file.
    */
    createWidgetsForClass(widgetClass, widgetType) {

      if(widgetType === undefined) {
        widgetType = widgetClass.name.toLowerCase();
      }

      // Store te class definition if we don't already have it.
      if(this.widgetClasses[widgetClass.name] === undefined) {
        this.widgetClasses[widgetClass.name] = widgetClass;
      }

      var widgetsByWID = {};
      var widgetNodes = Array.from(document.getElementsByClassName("widget-" + widgetType));
      var createdWidgets = [];

      var createWidget = ((informer, widgetsByWID, createdWidgets) => {
        return (node) => {
          let wid = informer.getWIDFromNode(node);
          if(wid) {
            var unique_id =  ++this._curWidgetID;  // Assign a unique ID to use for data fetching
            var wObj = new widgetClass(node, informer.getWidgetParamsByWID(wid), unique_id);
            wObj.widget_id = unique_id;
            wObj.widget_type = widgetType;
            createdWidgets.push(wObj);
            widgetsByWID[wid] = wObj;
          }
        }
      })(this, widgetsByWID, createdWidgets);

      if(typeof(widgetClass) == "function") {
        widgetNodes.forEach(createWidget);
      }

      this.widgets[widgetType] = createdWidgets;
    }

    fetchWidgetData(widget) {
      var params = {};
      for(var k in widget.params) if(widget.params.hasOwnProperty(k) && k != "fetch") {
        params[k] = widget.params[k];
      }

      const encodedParams = JSON.stringify(params);
      const fetchOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ params: params }),
      };

      fetch("/widget/" + widget.widget_type + "/data?widget_id=" + encodeURIComponent(widget.widget_id), fetchOptions)
        .then(response => response.json())
        .then(data => {
          widget.receivingData(data);
        })
        .catch(err => {
          console.log("There was an error", err);
        })
    }

    setWidgetError(widget, error_message) {
      this.addClass(widget.node, "widget-error");
      widget.node.innerHTML = `<div>${error_message}</div>`;
    }

    get_date_formatter() {
      this._df = (this?._df) ? this._df : new this.DateFormatter();
      return this._df;
    }

    ts_to_dt(ts, date_format) {
      // Grab the timestamp (seconds) and generate a date based on the
      // supplied format. If no format is supplied we will use a default.

      const df = this.get_date_formatter();

      if(date_format === undefined) {
        date_format = df.default_format;
      }

      if(ts) {
        return df.formatDate(new Date(ts * 1000), date_format);
      }
      return "";
    }

    loadScript(url) {
      const informer = this;

      return new Promise((resolve, reject) => {
        console.log(`[ Informer ] Loading Requirement: ${url}`);

        const script = document.createElement("script");
        script.type = "text/javascript";
        script.src = url;

        script.addEventListener("load", () => resolve(url));
        script.onerror = () => reject(new Error(`Failed to load script: ${url}`));

        document.head.appendChild(script);
      });
    }

    requireWidget(widgetClassName, onReady, widgetJSName) {
      // Another class is a dependency to this one, so we need to make
      // sure it has been loaded before we attempt to use it.

      /*
      Example:

      Let's assume our widget needs to extend SiteStatus instead
      of informer.Widget:

      requireWidget('SiteStatus', () => {
        // The JS file 'sitestatus.js' is now loaded and therefore the
        // SiteStatus class is available. We can create our new class
        // like this:
        //
        // class MyNewClass extends informer.widgetClasses.SiteStatus {};
        //
        // informer.widgetClasses holds all classes that have been
        // loaded. Note that these are not instances, they are the class
        // definitions.
      });
      */

      var fn = ((informer, widgetClassName, onReady, widgetJSName) => {
        return function() {
          if(widgetJSName === undefined) {
            widgetJSName = `${widgetClassName.toLowerCase()}.js`;
          }

          if(typeof(widgetJSName) == "string" && widgetJSName.slice(-3) != ".js") {
            widgetJSName = widgetJSName + ".js";
          }

          if(informer.widgetClasses[widgetClassName] === undefined) {
            const filepath = `/static/widgets/${widgetJSName}`;
            informer.loadScript(filepath)
              .then(onReady)
              .catch((err) => {
                console.error(`Failure to load ${widgetJSName}`, {
                  message: err.message,
                  error_filename: err.fileName,
                  error_lineno: err.lineNumber,
                  filename_to_load: filepath
                });
              });
          }
          else {
            // Already loaded!
            onReady();
          }
        }
      })(this, widgetClassName, onReady, widgetJSName);

      // We do this at the end of the stack so that there is a chance
      // that the dependency is already loaded.
      setTimeout(fn, 0);
    }
  }

  // Make sure the active 'page' link is in view.
  const page_link = document.querySelector("#navbar a.nav-link.active");
  const page_link_next = document.querySelector("#navbar a.nav-link.active + a.nav-link");
  if(page_link_next && page_link_next?.scrollIntoView) {
    page_link_next.scrollIntoView();
  }
  if(page_link && page_link?.scrollIntoView) {
    page_link.scrollIntoView();
    window.scrollTo(0, 0);
  }

  // Create our informer object and notify anyone who is listening!
  // (our Page should be listening for this event so that it can
  // send all the widget params over to the informer object).
  window.informer = new Informer();

  console.log("[ Informer ] Ready");

  var informerReady = new CustomEvent('onInformerReady', {
    detail: {
      informer: informer
    }
  });

  document.dispatchEvent(informerReady);

});
