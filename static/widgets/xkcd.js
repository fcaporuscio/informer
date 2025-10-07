/* xkcd Widget JS */

defineInformerWidget(() => {

  informer.requireWidget("Garfield", () => {
    class xkcd extends informer.widgetClasses.Garfield {};
    informer.createWidgetsForClass(xkcd);
  });

});
