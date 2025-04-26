# syntax=docker/dockerfile:1

ARG NODE_VERSION=22.14.0
FROM node:${NODE_VERSION}-bookworm-slim

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
ENV CI=true

WORKDIR /usr/src/app

COPY package.json package-lock.json* ./
RUN npm ci

RUN npx playwright install --with-deps chromium

COPY . .

RUN npm run build

CMD ["npm", "run", "test:e2e"]
