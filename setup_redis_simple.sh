#!/bin/bash
# 简化的Redis设置脚本

echo "设置Redis环境..."

# 清理旧的容器和镜像
echo "清理旧的Docker资源..."
docker-compose down
docker system prune -f

# 创建Redis数据目录（如果不存在）
echo "创建Redis数据目录..."
mkdir -p ./redis_data

# 设置目录权限
echo "设置目录权限..."
chmod 755 ./redis_data

echo "Redis环境设置完成！"
echo "现在可以运行: docker-compose up --build"
