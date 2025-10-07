/* Garfield Widget JS */

defineInformerWidget(() => {

  class Garfield extends informer.Widget {
    start() {
      this.formatter = new informer.DateFormatter();
      this.image_container = this.node.querySelector(".img-container");
      this.image = this.node.querySelector("img.image");
      this.date = this.node.querySelector(".date");
      this.back_button = this.node.querySelector("button");

      this.image.addEventListener("click", (event) => {
        if(this.image.width + 10 > this.image_container.clientWidth) {
          informer.addClass(this.image_container, "full");
        }
      });

      this.back_button.addEventListener("click", (event) => {
        informer.removeClass(this.image_container, "full");
      });
    }

    receiveData(data) {
      if(data?.url) {
        this.image.src = data.url;
        informer.removeClass(this.image_container, "hidden");

        if(data?.safe_title) {
          this.image.setAttribute("title", data.safe_title);
        }
      }

      if(data.year && data.month && data.day) {
        const currentDate = new Date(data.year, data.month - 1, data.day);
        this.date.innerText = this.formatter.formatDate(currentDate, "${month} ${day}, ${year}");
      }
    }
  }

  informer.createWidgetsForClass(Garfield);

});
