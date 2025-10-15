/* Date Widget JS */

InformerOnLoad(() => {
  /*
  ** Date Widget
  */
  class DateWidget extends informer.Widget {
    start() {
      this.formatter = new informer.DateFormatter();
      this.setupDomFields([
        "date", "time"
      ]);

      if(this.params.time !== true) {
        if(this.time) {
          this.time.className += " hidden";
        }
      }

      this.updateWidget();

      // Syncronize the refresh Interval to execute 1 seconds after
      // the "marker".
      const sync_marker = 300; // 5-minute mark
      const now = parseInt(Date.now() / 1000);
      const next_marker = now - parseInt(now % sync_marker) + sync_marker;
      const seconds_to_next_marker = next_marker - now;

      const fn = ((widget) => {
        return function() {
          widget.setRefreshInterval(5 * 60);
        }
      })(this);

      const delay = Math.max(0, (seconds_to_next_marker + 1));
      setTimeout(fn, delay * 1000);
    }

    _initParams(params) {
      params = params || {};

      if(params.offset_seconds === undefined) {
        params.offset_seconds = 0;
      }

      return params;
    }

    getDateFormat() {
      if(this.params.datefmt) {
        return this.params.datefmt;
      }

      // Return the default
      return "${month} ${day}, ${year}";
    }

    getTimeFormat() {
      if(this.params.timefmt) {
        return this.params.timefmt;
      }

      // Return the default
      return "${hour:12}:${minute:0} ${ampm}";
    }

    updateWidget(do_next) {
      var currentDate = new Date(Date.now() + (this.params.offset_seconds * 1000));
      this.date.innerText = this.formatter.formatDate(currentDate, this.getDateFormat())

      if(this.params.time === true) {
        this.time.innerText = this.formatter.formatDate(currentDate, this.getTimeFormat());
      }
      else {
        if(this.time) {
          this.time.className += " hidden";
        }
      }

      if(do_next === true) {
        var untilNextMinute = 60 - currentDate.getSeconds();
        var fn = ((ctx) => {
          return () => {
            ctx.updateWidget();
          }
        })(this);
        setTimeout(fn, untilNextMinute * 1000);
      }
    }

    receiveData(data) {
      if(typeof(data?.offset_seconds) == "number") {
        this.params.offset_seconds = data.offset_seconds;
        this.updateWidget(false);
      }
    }
  }

  informer.createWidgetsForClass(DateWidget, "date");

});
