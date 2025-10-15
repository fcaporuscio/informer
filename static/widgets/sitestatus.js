/* Site Status JS */

InformerOnLoad(() => {

  class SiteStatus extends informer.Widget {
    start() {
      this.setupDomFields([
        ["content", ".sitestatus-content"]
      ]);

      this.setRefreshInterval(1 * 60);
    }

    receiveData(data) {
      this.content.innerHTML = data.html;
    }
  }

  informer.createWidgetsForClass(SiteStatus);

});
