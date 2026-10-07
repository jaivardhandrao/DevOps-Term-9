FROM node:22-alpine AS build
WORKDIR /app
COPY application/frontend/package*.json ./
RUN npm ci
COPY application/frontend/ ./
RUN npm test && npm run build

FROM nginxinc/nginx-unprivileged:1.29-alpine AS runtime
USER root
RUN apk upgrade --no-cache
ENV BACKEND_UPSTREAM=backend:8000
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
USER 101:101
