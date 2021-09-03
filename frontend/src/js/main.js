(function () {
  // APIのベースURL
  const API_BASE = "http://localhost/api";
  // クエリセレクタのエイリアス
  const qs = (selector) => document.querySelector(selector);
  // API一覧
  const API = {
    COUNT_DATA: `${API_BASE}/countData`,
    SEARCH: `${API_BASE}/search`,
  };

  window.onload = () => {
    // 表示時に登録データ数を取得する
    fetch(API.COUNT_DATA)
      .then((res) => res.json())
      .then((data) => {
        qs("#count-area").innerText = `現在 ${data.count} 件の文書があります。`;
      });
    // 検索実行
    qs("#text-search").addEventListener("click", () => {
      query = qs("#search-query").value;
      console.log(`text:${query}`);
      fetch(`${API.SEARCH}?q=${query}`)
        .then((res) => res.json())
        .then((data) => {
          const list = qs("#search-result");
          list.innerHTML = "";
          data.result.forEach((val, index) => {
            console.log(val);
            list.innerHTML += `<li class="m-3">${val}</li>`;
          });
        });
    });

    qs("#start-chat").addEventListener("click", () => {
      // BOTUIオブジェクト
      const BOTUI = new BotUI("botui-app");
      BOTUI.message
        .bot({
          content: "こんにちは！",
        })
        .then(function () {
          BOTUI.message.add({
            delay: 1500,
            content: "KIA 先端技術研究会テーマ2",
          });
        })
        .then(function () {
          BOTUI.message.add({
            delay: 3000,
            content: "広がり続ける「自然言語処理」の可能性の研究",
          });
        })
        .then(function () {
          BOTUI.message.add({
            delay: 4500,
            content: "何が知りたいですか？",
          });
        })
        .then(function () {
          BOTUI.action.text({
            delay: 5000,
            action: {
              placeholder: "なにか入力してください...",
            },
          });
        });
    });
  };
})();
