/* GitHub Widget JS */

window.addEventListener('load', (event) => {

  class GitHub extends informer.Widget {
    start() {
      this.visibility = this.node.querySelector(".visibility");
      this.content = this.node.querySelector(".content");
      this.date_formatter = new informer.DateFormatter();
      this.date_format = "${month:short} ${day}, ${year} ${hour:12}:${minute:0}${ampm}";
    }

    ts_to_dt(ts) {
      if(ts) {
        return this.date_formatter.formatDate(new Date(ts * 1000), this.date_format);
      }
      return "";
    }

    receiveData(data) {
      this.content.innerHTML = data.html;
      const release_date = this.node.querySelector(".release-date");
      const avatar = this.params.avatar ? this.node.querySelector(".repository .avatar img.avatar") : null;

      // Set the avatar
      if(avatar && data?.owner?.avatar_url) {
        avatar.src = data.owner.avatar_url;
      }

      // Set the repository visibility
      this.visibility.className = "visibility";
      const visibilityClass = (data?.visibility || "").trim().toLowerCase()
      informer.addClass(this.visibility, visibilityClass);
      this.visibility.innerText = data.visibility;

      const last_update = this.node.querySelector(".last-update");
      if(data.pushed_at_ts) {
        const dt_updated_at = new Date(data.pushed_at_ts * 1000);
        last_update.innerText = this.date_formatter.formatDate(dt_updated_at, this.date_format);
        informer.removeClass(last_update, "hidden");
      }
      else {
        informer.addClass(last_update, "hidden");
      }

      // Prepare the latest release data
      const latest_release = data?.latest_release;
      if(latest_release && release_date) {
        const published_at_str = this.ts_to_dt(latest_release?.published_at_ts);

        if(published_at_str) {
          release_date.innerHTML = `<span class="fg-widget">was released on</span> ${published_at_str}`;
        }
      }
    }
  }

  informer.createWidgetsForClass(GitHub);

});
