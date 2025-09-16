#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百考通AI写作平台后端启动脚本
一键启动，无需复杂配置
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    百考通AI写作平台后端                        ║
    ║                    Baikaotong AI Backend                     ║
    ║                                                              ║
    ║                    版本: 1.0.0                               ║
    ║                    作者: AI Assistant                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")

def check_virtual_env():
    """检查并激活虚拟环境"""
    print("🔍 检查虚拟环境...")
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("❌ 虚拟环境不存在，请先运行安装脚本")
        sys.exit(1)
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 已在虚拟环境中")
        return True
    else:
        print("⚠️  未在虚拟环境中，尝试激活...")
        return False

def install_dependencies():
    """安装依赖"""
    print("📦 检查并安装依赖...")
    try:
        # 检查requirements.txt是否存在
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt文件不存在")
            return False
        
        # 安装依赖
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖安装完成")
            return True
        else:
            print(f"❌ 依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安装依赖时出错: {e}")
        return False

def check_environment_file():
    """检查环境变量文件"""
    print("🔍 检查环境配置...")
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  .env文件不存在，创建默认配置...")
        create_default_env()
    else:
        print("✅ 环境配置文件存在")
    
    return True

def create_default_env():
    """创建默认环境变量文件"""
    default_env = """# API密钥配置
OPENAI_API_KEY=039c31ba-ebd5-429b-8e88-593eb0e0dc67
RESEARCH_API_KEY=039c31ba-ebd5-429b-8e88-593eb0e0dc67

# Flask配置
FLASK_ENV=development
SECRET_KEY=asdf#FGSgvasgf$5$WGT

# 数据库配置
DATABASE_URL=sqlite:///database/app.db

# CORS配置
CORS_ORIGINS=*
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(default_env)
    print("✅ 默认环境配置已创建")

def check_database():
    """检查数据库"""
    print("🔍 检查数据库...")
    db_dir = Path("src/database")
    if not db_dir.exists():
        print("📁 创建数据库目录...")
        db_dir.mkdir(parents=True, exist_ok=True)
    print("✅ 数据库检查完成")

def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    print("=" * 60)
    print("服务器信息:")
    print("  - 地址: http://localhost:5000")
    print("  - API文档: http://localhost:5000/api/health")
    print("  - 按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 启动Flask应用
        os.chdir(Path(__file__).parent)
        subprocess.run([sys.executable, "src/main.py"])
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def main():
    """主函数"""
    try:
        print_banner()
        
        # 检查Python版本
        check_python_version()
        
        # 检查虚拟环境
        if not check_virtual_env():
            print("❌ 请在虚拟环境中运行此脚本")
            print("   运行命令: source venv/bin/activate (Linux/Mac) 或 venv\\Scripts\\activate (Windows)")
            sys.exit(1)
        
        # 安装依赖
        if not install_dependencies():
            print("❌ 依赖安装失败，请检查网络连接")
            sys.exit(1)
        
        # 检查环境配置
        check_environment_file()
        
        # 检查数据库
        check_database()
        
        # 启动服务器
        start_server()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

