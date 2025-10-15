/* xkcd Widget JS */

InformerOnLoad(() => {

  informer.requireWidget("Garfield", () => {
    class xkcd extends informer.widgetClasses.Garfield {};
    informer.createWidgetsForClass(xkcd);
  });

});
