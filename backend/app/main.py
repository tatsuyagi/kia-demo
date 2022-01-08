# -*- coding: utf-8 -*-

from typing import Optional
from fastapi import Depends, FastAPI, Response
import os
import json
import requests
import uvicorn
import logging
import pandas as pd
import numpy as np
import MeCab
from requests.exceptions import Timeout
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
logger = logging.getLogger('uvicorn')
mecab = MeCab.Tagger('-Owakati')
# ストップワード(pos指定)
stopWords = ["BOS/EOS", "助詞", "助動詞", "記号"]

# APP IDを環境変数から読み込み
RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID", "0000000000000000000")

API_REQ_HEADER = {
    "Accept": "*/*",
    "Content-Type": "application/json"
}
YES_MD5 = "c4836ea5ab623315c893c08dddb9dfd8"
NO_MD5 = "5c7c39d0fd174b2b5ff66699c0d90065"

@app.get("/api")
def root():
    logger.info("Root API called ID=" + RAKUTEN_APP_ID)
    return {"API Status": "OK"}


@app.get("/api/countData")
def root():
    logger.info("Count data API called")
    with open("/data/raw_data.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
    return {"status": "OK", "count": len(lines)}


@ app.get("/api/search")
def search(q: Optional[str] = None, limit: Optional[int] = 3):
    """ クエリ文に類似した文章を検索する"""
    logger.info("q = {}, limit = {}".format(q, limit))

    result = list()
    with open("/data/raw_data.txt", "r", encoding="utf-8") as file:
        corpus = file.readlines()
        # 形態素解析し、分かち書き状態に変換する
        corpus = [mecab.parse(sentence).strip() for sentence in corpus]
        vectorizer = CountVectorizer(
            token_pattern=u'(?u)\\b\\w+\\b', stop_words=stopWords)
        transformer = TfidfTransformer()
        # TF計算
        tf = vectorizer.fit_transform(corpus)
        # TF-IDF計算
        tfidf = transformer.fit_transform(tf)

        # 入力文書に対するコサイン類似度計算
        sample_tf = vectorizer.transform([mecab.parse(q).strip()])
        sample_tfidf = transformer.transform(sample_tf)
        similarity = cosine_similarity(sample_tfidf, tfidf)[0]
        topn_indices = np.argsort(similarity)[::-1][:limit]
        for sim, data in zip(similarity[topn_indices], np.array(corpus)[topn_indices]):
            data = "({:.3f}): {}".format(sim, "".join(data.split()))
            print(data)
            result.append(data)
    return {"status": "OK", "result": result}

def convertTitle(items: list):
    return list(map(lambda x: {'type': 'text', 'value': x['itemName']}, items))

@app.get("/api/rakuten-search")
async def rakutenSearch(text: Optional[str] = None, limit: Optional[int] = 3, callback: Optional[str] = None):
    """ 楽天APIで商品検索を行う"""
    logger.info(
        "Search data API called text={}, callback={}".format(text, callback))
    dic = {}
    result_list = []
    if (text == YES_MD5):
        result_list.append({'type': 'text', 'value': 'お役に立てて、私もうれしいです！'})
        result_list.append({'type': 'text', 'value': '次に検索したいものは何でしょうか？'})
        dic = {'output': result_list}
        contents = callback + '(' + json.dumps(dic) + ')'
        return Response(content=contents, media_type="application/javascript")
    if (text == NO_MD5):
        result_list.append({'type': 'text', 'value': 'それは残念です。。。'})
        result_list.append({'type': 'text', 'value': '次に検索したいものは何でしょうか？'})
        dic = {'output': result_list}
        contents = callback + '(' + json.dumps(dic) + ')'
        return Response(content=contents, media_type="application/javascript")

    # 通常の検索処理
    try:
        ret = requests.post('https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706', data=json.dumps({
            "applicationId": RAKUTEN_APP_ID,
            "keyword": text
        }), headers=API_REQ_HEADER, timeout=5.0)
        logger.info('Rakuten search end (status={})'.format(ret.status_code))
        if (ret.status_code == 200):
            data = ret.json()
            if (len(data['Items']) == 0):
                result_list.append({'type': 'text', 'value': '検索結果がありませんでした。<br/>検索語を変えて再度お試しください。'})
                dic = {'output': result_list}
                contents = callback + '(' + json.dumps(dic) + ')'
                return Response(content=contents, media_type="application/javascript")

            for idx, item in enumerate(data['Items']):
                result_list.append({'type': 'text', 'value': '【結果{}】<a href="{}" target="_blank">{}</a>（{}円）'.format(
                    idx + 1,
                    item['Item']['itemUrl'],
                    item['Item']['itemName'],
                    item['Item']['itemPrice']
                )})
                if (item['Item']['imageFlag'] == 1):
                    result_list.append({'type': 'image', 'value': '{}'.format(item['Item']['mediumImageUrls'].pop()["imageUrl"])})
                if (idx == limit - 1):
                    break
            result_list.append({'type': 'text', 'value': 'お気に入りの品は見つかりましたか？'})
            result_list.append({'type': 'option', 'options': [
                {'label': 'はい', 'value': YES_MD5},
                {'label': 'いいえ', 'value': NO_MD5}
            ]})
            dic = {'output': result_list}
        else:
            dic = {'output': [{'type': 'text', 'value': '検索できなかったです。'}]}
    except Timeout:
        dic = {'output': [{'type': 'text', 'value': 'タイムアウトしました。検索語を変えて再度お試しください。'}]}

    contents = callback + '(' + json.dumps(dic) + ')'
    return Response(content=contents, media_type="application/javascript")
