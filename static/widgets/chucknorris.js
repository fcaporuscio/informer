/* Chuck Norris Widget JS */

window.addEventListener('load', (event) => {

  class ChuckNorris extends informer.Widget {
    start() {
      this.container = this.node.querySelector(".container");
      this.quote = this.container.querySelector(".quote");
    }

    receiveData(data) {
      this.quote.innerText = data.value;
    }
  }

  informer.createWidgetsForClass(ChuckNorris);

});
