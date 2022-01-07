(function () {
  const chatux = new ChatUx();

  //ChatUXの初期化パラメータ
  const initParam = {
    renderMode: "auto",
    api: {
      endpoint:
        "http://localhost/api/rakuten-search",
      method: "GET",
      dataType: "jsonp",
    },
    bot: {
      botPhoto: "https://riversun.github.io/chatbot/bot_icon_operator.png",
      humanPhoto: null,
      widget: {
        sendLabel: "送信",
        placeHolder: "何か話しかけてみてください",
      },
    },
    window: {
      title: "商品検索君",
      infoUrl: "https://github.com/riversun/chatux",
    },
  };
  chatux.init(initParam);
  chatux.start(true);
})();
