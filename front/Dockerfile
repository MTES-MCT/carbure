FROM alpine:latest

RUN apk add --update nodejs npm

ENV WDS_SOCKET_PORT 0

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY index.html ./
RUN npm install
COPY tsconfig.json ./
COPY public ./
COPY src ./

ENV PATH /app/node_modules/.bin:$PATH

CMD ["npm", "run", "start"]
