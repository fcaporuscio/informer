/* Ron Swanson Widget JS */

window.addEventListener('load', (event) => {

  class RonSwanson extends informer.Widget {
    start() {
      this.container = this.node.querySelector(".container");
      this.quote = this.container.querySelector(".quote");
    }

    receiveData(data) {
      if(data.error || !data?.quotes?.length) {
        informer.setWidgetError(this, data.error);
        return;
      }

      const quotes = data.quotes;
      const randomIdx = (Date.now() % 10) % quotes.length;

      this.quote.innerText = quotes[randomIdx];
      informer.removeClass(this.container, "loader");
    }
  }

  informer.createWidgetsForClass(RonSwanson);

});
