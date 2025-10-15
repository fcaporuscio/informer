/* Gitea Widget JS */

InformerOnLoad(() => {

  informer.requireWidget("GitHub", () => {
    class Gitea extends informer.widgetClasses.GitHub {};
    informer.createWidgetsForClass(Gitea);
  });

});
