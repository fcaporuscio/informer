/* Gitea Widget JS */

defineInformerWidget(() => {

  informer.requireWidget("GitHub", () => {
    class Gitea extends informer.widgetClasses.GitHub {};
    informer.createWidgetsForClass(Gitea);
  });

});
