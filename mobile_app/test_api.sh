#!/bin/bash

# API测试脚本
# 用于测试后端API是否正常工作

# 配置
API_URL="${1:-http://localhost:8000}"

echo "====================================="
echo "垃圾分类API测试脚本"
echo "====================================="
echo "API地址: $API_URL"
echo ""

# 测试1: 健康检查
echo "[测试1] 健康检查..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo "✓ 健康检查通过"
    echo "响应: $body"
else
    echo "✗ 健康检查失败 (HTTP $http_code)"
    echo "响应: $body"
fi
echo ""

# 测试2: 根路径
echo "[测试2] 根路径检查..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo "✓ 根路径访问成功"
    echo "响应: $body"
else
    echo "✗ 根路径访问失败 (HTTP $http_code)"
fi
echo ""

# 测试3: 获取分类信息
echo "[测试3] 获取分类信息..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/v1/categories")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo "✓ 分类信息获取成功"
    echo "响应: $body"
else
    echo "✗ 分类信息获取失败 (HTTP $http_code)"
fi
echo ""

# 测试4: 文档访问
echo "[测试4] 检查API文档..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/docs")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    echo "✓ API文档可访问"
    echo "访问地址: $API_URL/docs"
else
    echo "✗ API文档访问失败 (HTTP $http_code)"
fi
echo ""

# 测试5: 图片检测 (需要测试图片)
if [ -f "test_image.jpg" ]; then
    echo "[测试5] 图片检测测试..."
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/v1/detect_trash" \
        -F "image=@test_image.jpg")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        echo "✓ 图片检测成功"
        echo "响应: $body"
    else
        echo "✗ 图片检测失败 (HTTP $http_code)"
        echo "响应: $body"
    fi
    echo ""
else
    echo "[测试5] 跳过 (未找到test_image.jpg)"
    echo "提示: 将测试图片命名为test_image.jpg放在当前目录可测试检测功能"
    echo ""
fi

echo "====================================="
echo "测试完成"
echo "====================================="
echo ""
echo "使用方法:"
echo "  ./test_api.sh                    # 测试本地API"
echo "  ./test_api.sh http://IP:8000     # 测试远程API"
echo ""
echo "如需测试图片检测功能,请准备test_image.jpg文件"
