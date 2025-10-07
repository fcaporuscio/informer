/* Tabs Widget JS */

defineInformerWidget(() => {

  class Tabs {
    constructor(informer) {
      this.informer = informer;
      this.node = document.getElementById("app");
      this.cls_tab_hidden = "tab-hidden";

      // Find all tab groups and only show the content of the first
      // container.
      var widget_tabs = document.getElementsByClassName("widget-tabs");
      for(var i = 0, il = widget_tabs.length; i < il; i++) {
        var widget_tab = widget_tabs.item(i);
        var tab_containers = widget_tab.getElementsByClassName("tab-container");
        for(var j = 0, jl = tab_containers.length; j < jl; j++) {
          var tab_container = tab_containers.item(j);
          // Set the proper classes
          if(j == 0) {
            this.informer.addRemoveClass(tab_container, "tab-content-visible", "tab-content-hidden");
          }
          else {
            this.informer.addRemoveClass(tab_container, "tab-content-hidden", "tab-content-visible");
          }
        }
      }
    }

    selectTab(elem, tab_id) {
      let all_tab_links = elem.parentNode.children;
      Array.from(all_tab_links).forEach(tab => {
        if(tab == elem) {
          this.informer.addRemoveClass(tab, "tab-active", "tab-inactive");
        }
        else {
          this.informer.addRemoveClass(tab, "tab-inactive", "tab-active");
        }
      });

      var tab = document.getElementById(tab_id);
      var widget_tab = tab.closest(".widget-tabs");
      var tab_containers = widget_tab.getElementsByClassName("tab-container");

      for(var i = 0, il = tab_containers.length; i < il; i++) {
        var tab_container = tab_containers.item(i);

        // We only want to affect the immediate tabs... not tabs from
        // another Tabs widgets further up the tree!
        var parent_container = tab_container.closest(".widget-tabs");
        if(parent_container == widget_tab) {
          switch(tab_container.id) {
            case tab_id:
              this.informer.removeClass(tab_container, "tab-content-hidden");
              this.informer.addClass(tab_container, "tab-content-visible");
              break;

            default:
              this.informer.removeClass(tab_container, "tab-content-visible");
              this.informer.addClass(tab_container, "tab-content-hidden");
              break;
          }
        }
      }
    }
  }

  informer.tabs = new Tabs(informer);

});
