# Build stage
ARG NODE_IMAGE=node:18-alpine
FROM ${NODE_IMAGE} AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
ARG NGINX_IMAGE=nginx:stable-alpine
FROM ${NGINX_IMAGE} AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
