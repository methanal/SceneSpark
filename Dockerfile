FROM registry.cn-heyuan.aliyuncs.com/methanal/scenespark:base-202406151709
ENV TZ=Asia/Shanghai
ARG DEBIAN_FRONTEND=noninteractive

EXPOSE 8000

WORKDIR /app/
COPY . /app/

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["uvicorn","main:app", "--host", "0.0.0.0", "--port", "8000"]
