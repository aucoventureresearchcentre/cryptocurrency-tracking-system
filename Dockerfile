# 前端应用Dockerfile
FROM node:16-alpine as build

# 设置工作目录
WORKDIR /app

# 添加 node_modules 到 PATH
ENV PATH /app/node_modules/.bin:$PATH

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci --silent

# 复制应用代码
COPY . ./

# 设置API URL参数
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# 构建应用
RUN npm run build

# 生产环境阶段
FROM nginx:alpine

# 复制构建文件到Nginx服务目录
COPY --from=build /app/build /usr/share/nginx/html

# 复制Nginx配置
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
