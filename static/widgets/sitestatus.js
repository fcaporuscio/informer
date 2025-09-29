/* Site Status JS */

window.addEventListener('load', (event) => {

  class SiteStatus extends informer.Widget {
    start() {
      this.content = this.node.querySelector(".sitestatus-content");
      this.setRefreshInterval(1 * 60);
    }

    receiveData(data) {
      this.content.innerHTML = data.html;
    }
  }

  informer.createWidgetsForClass(SiteStatus);

});
