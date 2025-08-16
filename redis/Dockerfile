# 使用Alpine Linux基础镜像
FROM alpine:3.18

# 设置工作目录
WORKDIR /data

# 安装Redis
RUN apk add --no-cache redis

# 创建Redis用户和组（如果不存在）
RUN addgroup -S redis 2>/dev/null || true && \
    adduser -S -G redis redis 2>/dev/null || true

# 创建必要的目录并设置正确的权限
RUN mkdir -p /data && \
    chown -R redis:redis /data && \
    chmod 755 /data

# 创建Redis配置文件目录
RUN mkdir -p /etc/redis && \
    chown -R redis:redis /etc/redis

# 创建Redis配置文件
RUN echo 'dir /data' > /etc/redis/redis.conf && \
    echo 'appendonly yes' >> /etc/redis/redis.conf && \
    echo 'appendfilename "appendonly.aof"' >> /etc/redis/redis.conf && \
    echo 'appendfsync everysec' >> /etc/redis/redis.conf && \
    echo 'save 900 1' >> /etc/redis/redis.conf && \
    echo 'save 300 10' >> /etc/redis/redis.conf && \
    echo 'save 60 10000' >> /etc/redis/redis.conf && \
    chown redis:redis /etc/redis/redis.conf

# 切换到Redis用户
USER redis

# 暴露端口
EXPOSE 6379

# 启动Redis（使用配置文件）
CMD ["redis-server", "/etc/redis/redis.conf"]
