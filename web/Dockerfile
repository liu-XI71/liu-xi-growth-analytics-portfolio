FROM node:22-alpine AS build
WORKDIR /workspace/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
COPY data/contracts/hash_vectors.json /workspace/data/contracts/hash_vectors.json
ARG VITE_BASE_PATH=/
ARG VITE_API_BASE_URL=/
ENV VITE_BASE_PATH=$VITE_BASE_PATH
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/web/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=6 CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
