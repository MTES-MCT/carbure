FROM node:alpine

ENV CHROME_BIN /usr/bin/chromium-browser
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true

RUN apk add chromium

WORKDIR /app
COPY package.json /app
COPY index.js /app
RUN npm install
