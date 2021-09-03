from typing import Optional
from fastapi import Depends, FastAPI
import uvicorn
import logging
import pandas as pd
import numpy as np
import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
logger = logging.getLogger('uvicorn')
mecab = MeCab.Tagger('-Owakati')
# ストップワード(pos指定)
stopWords = ["BOS/EOS", "助詞", "助動詞", "記号"]


@app.get("/api")
def root():
    logger.info("Root API called")
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
