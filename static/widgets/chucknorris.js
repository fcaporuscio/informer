/* Chuck Norris Widget JS */

InformerOnLoad(() => {

  class ChuckNorris extends informer.Widget {
    start() {
      this.setupDomFields([
        "container", "quote"
      ]);
    }

    receiveData(data) {
      this.quote.innerText = data.value;
    }
  }

  informer.createWidgetsForClass(ChuckNorris);

});
