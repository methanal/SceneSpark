FROM --platform=linux/amd64 python:3.9-bookworm
ENV TZ=Asia/Shanghai
ARG DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y ffmpeg vim curl wget unzip && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/.cache/torch/hub && mkdir -p /root/.cache/whisper

COPY small.pt /root/.cache/whisper/small.pt
# RUN mkdir -p /root/.cache/whisper/ && RUN wget -O /root/.cache/whisper/small.pt https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt

COPY snakers4_silero-vad_master /root/.cache/torch/hub/snakers4_silero-vad_master
# RUN wget https://github.com/snakers4/silero-vad/archive/refs/heads/master.zip -O /tmp/master.zip \
#     && unzip /tmp/master.zip -d /tmp \
#     && mkdir -p /root/.cache/torch/hub/snakers4_silero-vad_master \
#     && mv /tmp/silero-vad-master/* /root/.cache/torch/hub/snakers4_silero-vad_master/ \
#     && rm /tmp/master.zip && rm -rf /tmp/silero-vad-master

WORKDIR /app/
COPY . /app/

RUN mkdir -p ~/.pip && echo "[global]\ntimeout = 320\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\nextra-index-url = http://mirrors.aliyun.com/pypi/simple/" > ~/.pip/pip.conf
RUN pip3 install --upgrade pip wheel && pip3 install --no-cache-dir -r requirements.txt
