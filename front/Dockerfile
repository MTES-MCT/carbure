FROM node:24.22.3-alpine3.24

RUN apk add --update git

ENV WDS_SOCKET_PORT 0

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY index.html ./
RUN npm clean-install
COPY tsconfig.json ./
COPY public ./
COPY src ./

ENV PATH /app/node_modules/.bin:$PATH

CMD ["npm", "run", "start"]
