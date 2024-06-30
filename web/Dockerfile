FROM node:16 AS build

WORKDIR /app

COPY ./ ./

RUN yarn && yarn build

FROM amd64/nginx:1.21.3 AS release

WORKDIR /usr/share/nginx/html/scenespark/

COPY --from=build /app/build ./
COPY --from=build /app/nginx/default.conf /etc/nginx/conf.d/default.conf
