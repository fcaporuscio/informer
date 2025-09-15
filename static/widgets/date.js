/* Date Widget JS */

window.addEventListener('load', (event) => {

  /*
  ** Date Widget
  */
  class DateWidget extends informer.Widget {
    start() {
      this.date = this.node.querySelector(".date");
      this.time = this.node.querySelector(".time");
      this.formatter = new informer.DateFormatter();

      if(this.params.time !== true) {
        if(this.time) {
          this.time.className += " hidden";
        }
      }

      this.updateWidget();
    }

    _initParams(params) {
      params = params || {};

      if(params.offset_seconds === undefined) {
        params.offset_seconds = 0;
      }

      return params
    }

    getDateFormat() {
      if(this.params.datefmt) {
        return this.params.datefmt;
      }

      // Return the default
      return "${month} ${day}, ${year}"
    }

    getTimeFormat() {
      if(this.params.timefmt) {
        return this.params.timefmt;
      }

      // Return the default
      return "${hour:12}:${minute:0} ${ampm}"
    }

    updateWidget() {
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

      var untilNextMinute = 60 - currentDate.getSeconds();
      var fn = ((ctx) => {
        return () => {
          ctx.updateWidget();
        }
      })(this);
      setTimeout(fn, untilNextMinute * 1000);
    }
  }

  informer.createWidgetsForClass(DateWidget, "date");

});
