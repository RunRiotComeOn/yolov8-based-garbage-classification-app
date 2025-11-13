"""
网络连通性诊断工具
用于诊断Android模拟器连接API服务器的问题
"""

import socket
import requests
import subprocess
import sys
from pathlib import Path

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_port_listening(port=8000):
    """检查端口是否在监听"""
    print_section("1. 检查端口监听状态")

    try:
        # 检查端口是否被占用
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()

        if result == 0:
            print(f"✅ 端口 {port} 正在监听")
            return True
        else:
            print(f"❌ 端口 {port} 未在监听")
            print(f"   请确认API服务器是否已启动: python api/main.py")
            return False
    except Exception as e:
        print(f"❌ 检查端口时出错: {e}")
        return False

def check_localhost_api():
    """检查本地API是否可访问"""
    print_section("2. 检查本地API健康状态")

    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API服务正常运行")
            print(f"   - 模型已加载: {data.get('model_loaded')}")
            print(f"   - GPU可用: {data.get('gpu_available')}")
            print(f"   - 使用设备: {data.get('device_in_use')}")
            return True
        else:
            print(f"❌ API返回异常状态码: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ API请求超时")
        print(f"   API服务器可能正在加载模型，请稍等片刻后重试")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到API服务器")
        print(f"   请确认API服务器是否已启动")
        return False
    except Exception as e:
        print(f"❌ 检查API时出错: {e}")
        return False

def check_network_interfaces():
    """检查网络接口和IP地址"""
    print_section("3. 检查网络接口")

    try:
        # 获取本机IP地址
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        print(f"✅ 主机名: {hostname}")
        print(f"✅ 本机IP: {ip_address}")
        print(f"\n💡 如果在局域网测试，Flutter应用应使用: http://{ip_address}:8000")
        print(f"💡 如果在Android模拟器测试，Flutter应用应使用: http://10.0.2.2:8000")

        return True
    except Exception as e:
        print(f"❌ 获取网络信息时出错: {e}")
        return False

def check_firewall():
    """检查防火墙设置（Windows）"""
    print_section("4. 检查Windows防火墙")

    print("🔍 正在检查防火墙规则...")
    print("\n如果防火墙阻止了8000端口，需要添加规则：")
    print("\n【方法1】通过PowerShell添加规则（需要管理员权限）：")
    print('  New-NetFirewallRule -DisplayName "Python API Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow')

    print("\n【方法2】通过图形界面：")
    print("  1. 打开 Windows Defender 防火墙 -> 高级设置")
    print("  2. 入站规则 -> 新建规则")
    print("  3. 规则类型：端口")
    print("  4. 协议：TCP，本地端口：8000")
    print("  5. 操作：允许连接")

    print("\n【方法3】临时关闭防火墙测试（不推荐用于生产）：")
    print("  控制面板 -> Windows Defender 防火墙 -> 启用或关闭 Windows Defender 防火墙")

def test_api_with_image():
    """测试API图片检测功能"""
    print_section("5. 测试图片检测功能")

    # 寻找测试图片
    project_root = Path(__file__).parent.parent
    test_images = list(project_root.glob("**/test*.jpg")) + list(project_root.glob("**/test*.png"))

    if not test_images:
        print("⚠️  未找到测试图片")
        print("   建议：准备一张测试图片，命名为 test_image.jpg")
        return False

    test_image = test_images[0]
    print(f"📸 使用测试图片: {test_image}")

    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            print("📤 发送检测请求...")
            response = requests.post(
                "http://127.0.0.1:8000/v1/detect_trash",
                files=files,
                timeout=60
            )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 检测成功！")
            print(f"   - 检测到 {data['detection_count']} 个物体")
            print(f"   - 推理时间: {data['inference_time_ms']:.2f}ms")

            if data['detections']:
                print(f"\n   检测结果:")
                for i, det in enumerate(data['detections'][:3]):  # 只显示前3个
                    print(f"   [{i+1}] {det['specific_name']} ({det['general_category']}) - 置信度: {det['confidence']:.2f}")

            return True
        else:
            print(f"❌ 检测失败，状态码: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ 检测请求超时（>60秒）")
        print(f"   可能原因：")
        print(f"   1. 模型推理速度太慢（CPU推理）")
        print(f"   2. 图片太大，需要时间处理")
        print(f"   3. 服务器资源不足")
        return False
    except Exception as e:
        print(f"❌ 检测时出错: {e}")
        return False

def provide_solutions():
    """提供解决方案"""
    print_section("常见问题解决方案")

    print("\n【问题1】端口未监听")
    print("  解决：确保API服务器正在运行")
    print("  命令：cd api && python main.py")

    print("\n【问题2】模型加载超时")
    print("  解决：首次启动时模型加载需要时间，请耐心等待")
    print("  说明：可以在API服务器日志中看到加载进度")

    print("\n【问题3】推理时间过长")
    print("  原因：CPU推理速度较慢")
    print("  解决方案：")
    print("  - 使用GPU加速（如果有NVIDIA GPU）")
    print("  - 使用更小的模型（yolov8n代替yolov8s）")
    print("  - 增加Flutter客户端的超时时间")

    print("\n【问题4】Android模拟器无法连接")
    print("  检查：")
    print("  1. API服务器是否监听 0.0.0.0（不是127.0.0.1）")
    print("  2. Flutter配置是否使用 http://10.0.2.2:8000")
    print("  3. Windows防火墙是否允许8000端口")

    print("\n【问题5】防火墙阻止")
    print("  解决：添加防火墙规则允许8000端口（参见上面第4节）")

def main():
    """主函数"""
    print("\n" + "🔧" * 30)
    print("   Android模拟器连接问题诊断工具")
    print("🔧" * 30)

    results = []

    # 1. 检查端口
    results.append(check_port_listening())

    # 2. 检查API健康状态
    results.append(check_localhost_api())

    # 3. 检查网络接口
    results.append(check_network_interfaces())

    # 4. 检查防火墙
    check_firewall()

    # 5. 测试图片检测
    if results[0] and results[1]:  # 如果前面检查通过
        results.append(test_api_with_image())

    # 提供解决方案
    provide_solutions()

    # 总结
    print_section("诊断总结")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ 所有检查通过 ({passed}/{total})")
        print(f"\n🎉 API服务器运行正常！")
        print(f"\n下一步：")
        print(f"1. 确保Android模拟器中Flutter应用配置为: http://10.0.2.2:8000")
        print(f"2. 如果还是超时，检查Windows防火墙设置")
        print(f"3. 尝试在Flutter应用中测试连接")
    else:
        print(f"⚠️  部分检查未通过 ({passed}/{total})")
        print(f"\n请按照上述解决方案修复问题后重新运行此脚本")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()
