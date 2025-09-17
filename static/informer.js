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

    start() {}

    _initParams(params) {
      params = params || {};

      if(params.offset_seconds === undefined) {
        params.offset_seconds = 0;
      }

      return params
    }

    _fullyLoaded() {
      informer.addClass(this.node, "loaded");
    }

    _fetchData(force) {
      if(this.params.fetch === true || force === true) {
        informer.fetchWidgetData(this);
      }
      else {
        this._fullyLoaded();
      }
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
    }

    formatDate(date, format) {
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
      for(var i = 0, il = classes.length; i < il; i++) {
        var curCls = classes[i];
        if(curCls !== clsName) {
          final += " " + curCls;
        }
      }
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
