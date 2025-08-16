#!/bin/bash
# Redis数据目录设置脚本

echo "设置Redis数据目录和权限..."

# 创建Redis数据目录
mkdir -p ./redis_data

# 设置正确的权限
chmod 755 ./redis_data

# 获取当前用户ID
USER_ID=$(id -u)
GROUP_ID=$(id -g)

echo "当前用户ID: $USER_ID"
echo "当前组ID: $GROUP_ID"

# 设置目录所有者
sudo chown -R $USER_ID:$GROUP_ID ./redis_data

# 验证权限
echo "Redis数据目录权限:"
ls -la ./redis_data

echo "Redis数据目录设置完成！"
echo "现在可以运行: docker-compose up --build"
