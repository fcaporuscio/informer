/* Gitea Widget JS */

window.addEventListener('load', (event) => {

  // We piggy back on the GitHub class since we'll be doing the same
  // work.  We must first ensure that the GitHub class has been loaded.
  const dependency = "/static/widgets/github.js";

  const ready = () => {
    class Gitea extends informer.widgetClasses.GitHub {};
    informer.createWidgetsForClass(Gitea);
  };

  if(informer.widgetClasses.GitHub === undefined) {
    informer.loadScript(dependency, () => {
      ready();
    });
  }
  else {
    // Already loaded!
    ready();
  }

});
