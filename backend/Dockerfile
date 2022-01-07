FROM python:3.9
RUN apt-get update && apt-get install -y \
  sudo \
  vim \
  mecab \
  libmecab-dev \
  mecab-ipadic-utf8 \
  git \
  make \
  curl \
  xz-utils \
  file \
  g++ \
  unzip

WORKDIR /opt

RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git ; exit 0
RUN cd mecab-ipadic-neologd && \
  ./bin/install-mecab-ipadic-neologd -n -y
RUN echo "dicdir=/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd" > /usr/local/etc/mecabrc

RUN pip install \
  mecab-python3 \
  pandas \
  numpy \
  scikit-learn \
  fastapi \
  uvicorn[standard] \
  requests
