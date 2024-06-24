FROM --platform=linux/amd64 scenespark:base-202406211024
ENV TZ=Asia/Shanghai
ARG DEBIAN_FRONTEND=noninteractive

EXPOSE 8000

WORKDIR /app/
COPY . /app/

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["uvicorn","app.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "300"]
