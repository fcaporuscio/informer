/* Chuck Norris Widget JS */

window.addEventListener('load', (event) => {

  class ChuckNorris extends informer.Widget {
    start() {
      this.container = this.node.querySelector(".container");
      this.quote = this.container.querySelector(".quote");
      this.icon = this.container.querySelector(".icon");
    }

    receiveData(data) {
      if(data.error || !data?.value) {
        informer.setWidgetError(this, data.error);
        return;
      }

      this.quote.innerText = data.value;

      if(this.icon != null) {
        this.icon.src = data.icon_url;

        this.icon.addEventListener('load', (event) => {
          informer.removeClass(this.icon, "hidden");
        });
      }

      informer.removeClass(this.container, "loader");
    }
  }

  informer.createWidgetsForClass(ChuckNorris);

});
