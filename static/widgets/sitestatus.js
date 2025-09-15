/* Site Status JS */

window.addEventListener('load', (event) => {

  class SiteStatus extends informer.Widget {
    start() {
      this.content = this.node.querySelector(".sitestatus-content");
      this.setRefreshInterval(1 * 60);
    }

    receiveData(data) {
      if(data.error) {
        informer.setWidgetError(this, data.error);
        return;
      }
      
      this.content.innerHTML = data.html;
      informer.removeClass(this.content, "loader");
    }
  }

  informer.createWidgetsForClass(SiteStatus);

});
