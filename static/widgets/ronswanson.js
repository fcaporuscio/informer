/* Ron Swanson Widget JS */

InformerOnLoad(() => {

  class RonSwanson extends informer.Widget {
    start() {
      this.setupDomFields([
        "container", "quote"
      ]);
    }

    receiveData(data) {
      const quotes = data.quotes;
      const randomIdx = (Date.now() % 10) % quotes.length;

      this.quote.innerText = quotes[randomIdx];
    }
  }

  informer.createWidgetsForClass(RonSwanson);

});
