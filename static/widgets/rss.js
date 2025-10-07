/* RSS Widget JS */

defineInformerWidget(() => {

  class RSS extends informer.Widget {
    start() {
      this.rss_name = this.node.querySelector(".rss-name");
      this.rss_items = this.node.querySelector(".rss-items");
      this.more_link = this.node.querySelector("a.show-more");

      this.more_link.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        informer[ informer.hasClass(this.node, "full") ? "removeClass" : "addClass" ](this.node, "full");
      });
    }

    receiveData(data) {
      if(data.name) {
        this.rss_name.innerText = data.name;
        informer.removeClass(this.rss_name, "hidden");
      }
      else {
        informer.addClass(this.rss_name, "hidden");
      }
      this.rss_items.innerHTML = data.html;

      if(data.has_more_to_show) {
        informer.addClass(this.node, "has-more");
      }
    }
  }

  informer.createWidgetsForClass(RSS);

});
