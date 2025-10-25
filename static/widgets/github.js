/* GitHub Widget JS */

InformerOnLoad(() => {

  class GitHub extends informer.Widget {
    start() {
      this.setupDomFields([
        ["visibility", ".visibility"],
        ["content", ".content"],
        ["link", ".html-link"],
        ["repository_name", ".repository-name"],
        "language"
      ]);
    }

    receiveData(data) {
      this.content.innerHTML = data.html;
      const release_date = this.node.querySelector(".release-date");
      const avatar = this.params.avatar ? this.node.querySelector(".repository .avatar img.avatar") : null;

      // Set the avatar
      if(avatar && data?.owner?.avatar_url) {
        avatar.src = data.owner.avatar_url;
      }

      // Set the link
      if(data?.html_url && this.link) {
        this.link.href = data.html_url;
      }

      if(data?.name && this?.repository_name) {
        this.repository_name.innerText = data.name;
      }

      // Set the repository visibility
      this.visibility.className = "visibility";
      const visibilityClass = (data?.visibility || "").trim().toLowerCase()
      informer.addClass(this.visibility, visibilityClass);
      this.visibility.innerText = data.visibility;

      const last_update = this.node.querySelector(".last-update");
      if(data.updated_at_ts) {
        const dt_updated_at = new Date(data.updated_at_ts * 1000);
        const df = informer.get_date_formatter();
        last_update.innerText = df.formatDate(dt_updated_at);
        informer.removeClass(last_update, "hidden");
      }
      else {
        informer.addClass(last_update, "hidden");
      }

      // Prepare the latest release data
      const latest_release = data?.latest_release;
      if(latest_release && release_date) {
        const published_at_str = informer.ts_to_dt(latest_release?.published_at_ts);

        if(published_at_str) {
          release_date.innerHTML = `<span class="fg-widget">released on</span> ${published_at_str}`;
        }
      }

      if(this?.language) {
        this.language.innerText = (data?.language) ? data.language : "";
      }
    }
  }

  informer.createWidgetsForClass(GitHub);

});
