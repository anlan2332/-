#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百考通AI写作平台后端安装脚本
自动安装所有依赖和配置
"""

import os
import sys
import subprocess
import platform
import venv
from pathlib import Path

def print_banner():
    """打印安装横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                百考通AI写作平台后端安装程序                    ║
    ║                Baikaotong AI Backend Installer               ║
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
        print("   请升级Python后重试")
        input("按回车键退出...")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")

def create_virtual_environment():
    """创建虚拟环境"""
    print("🔧 创建虚拟环境...")
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("⚠️  虚拟环境已存在，跳过创建")
        return True
    
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ 虚拟环境创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建虚拟环境失败: {e}")
        return False

def get_pip_executable():
    """获取pip可执行文件路径"""
    system = platform.system().lower()
    if system == "windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def get_python_executable():
    """获取Python可执行文件路径"""
    system = platform.system().lower()
    if system == "windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def install_dependencies():
    """安装依赖"""
    print("📦 安装Python依赖...")
    
    pip_path = get_pip_executable()
    if not pip_path.exists():
        print("❌ pip不存在，虚拟环境可能创建失败")
        return False
    
    try:
        # 升级pip
        print("  - 升级pip...")
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # 安装基础依赖
        dependencies = [
            "flask>=3.0.0",
            "flask-cors>=4.0.0",
            "flask-sqlalchemy>=3.0.0",
            "python-dotenv>=1.0.0",
            "openai>=1.0.0",
            "requests>=2.31.0"
        ]
        
        for dep in dependencies:
            print(f"  - 安装 {dep}...")
            subprocess.run([str(pip_path), "install", dep], 
                          check=True, capture_output=True)
        
        # 生成requirements.txt
        print("  - 生成requirements.txt...")
        result = subprocess.run([str(pip_path), "freeze"], 
                               capture_output=True, text=True, check=True)
        
        with open("requirements.txt", "w") as f:
            f.write(result.stdout)
        
        print("✅ 依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装依赖失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def create_directory_structure():
    """创建目录结构"""
    print("📁 创建目录结构...")
    
    directories = [
        "src/database",
        "src/static",
        "src/templates",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  - 创建目录: {directory}")
    
    print("✅ 目录结构创建完成")

def create_environment_file():
    """创建环境变量文件"""
    print("⚙️  创建环境配置...")
    
    env_content = """# API密钥配置
OPENAI_API_KEY=039c31ba-ebd5-429b-8e88-593eb0e0dc67
RESEARCH_API_KEY=039c31ba-ebd5-429b-8e88-593eb0e0dc67

# Flask配置
FLASK_ENV=development
SECRET_KEY=asdf#FGSgvasgf$5$WGT

# 数据库配置
DATABASE_URL=sqlite:///database/app.db

# CORS配置
CORS_ORIGINS=*

# 服务器配置
HOST=0.0.0.0
PORT=5000
DEBUG=True
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ 环境配置文件已创建")

def create_startup_scripts():
    """创建启动脚本"""
    print("📝 创建启动脚本...")
    
    # Windows批处理文件
    windows_script = """@echo off
echo 启动百考通AI写作平台后端...
cd /d "%~dp0"
call venv\\Scripts\\activate
python start.py
pause
"""
    
    with open("start.bat", "w", encoding="utf-8") as f:
        f.write(windows_script)
    
    # Linux/Mac shell脚本
    unix_script = """#!/bin/bash
echo "启动百考通AI写作平台后端..."
cd "$(dirname "$0")"
source venv/bin/activate
python start.py
"""
    
    with open("start.sh", "w", encoding="utf-8") as f:
        f.write(unix_script)
    
    # 设置执行权限
    try:
        os.chmod("start.sh", 0o755)
    except:
        pass
    
    print("✅ 启动脚本已创建")

def create_readme():
    """创建README文件"""
    print("📖 创建说明文档...")
    
    readme_content = """# 百考通AI写作平台后端

## 快速启动

### Windows用户
双击 `start.bat` 文件即可启动

### Linux/Mac用户
运行以下命令：
```bash
./start.sh
```

或者手动启动：
```bash
source venv/bin/activate
python start.py
```

## 访问地址

- 主页: http://localhost:5000
- API健康检查: http://localhost:5000/api/health

## API接口

### 论文相关 (/api/paper/)
- POST /generate-title - 智能选题
- POST /generate-outline - 生成大纲
- POST /generate-content - 生成内容
- POST /polish-content - 润色修改
- POST /reduce-ai-detection - AIGC降重
- POST /format-paper - 格式调整

### 文献检索 (/api/research/)
- POST /search-literature - 文献检索
- POST /get-paper-details - 获取论文详情
- POST /generate-references - 生成参考文献
- POST /analyze-trends - 分析研究趋势
- POST /recommend-topics - 推荐研究主题

### 聊天助手 (/api/chat/)
- POST /send-message - 发送消息
- GET /get-conversation - 获取对话历史
- POST /clear-conversation - 清空对话

## 配置说明

环境变量配置在 `.env` 文件中：
- OPENAI_API_KEY: OpenAI API密钥
- RESEARCH_API_KEY: 研究API密钥
- SECRET_KEY: Flask密钥
- DATABASE_URL: 数据库连接

## 技术栈

- Flask 3.0+ - Web框架
- SQLAlchemy - 数据库ORM
- Flask-CORS - 跨域支持
- OpenAI - AI接口
- SQLite - 数据库

## 目录结构

```
baikaotong-backend/
├── src/
│   ├── routes/          # API路由
│   ├── models/          # 数据模型
│   ├── database/        # 数据库文件
│   ├── static/          # 静态文件
│   └── main.py          # 主程序
├── venv/                # 虚拟环境
├── .env                 # 环境变量
├── requirements.txt     # 依赖列表
├── start.py            # 启动脚本
├── install.py          # 安装脚本
├── start.bat           # Windows启动
└── start.sh            # Linux/Mac启动
```

## 故障排除

1. 如果启动失败，请检查Python版本（需要3.8+）
2. 确保所有依赖已正确安装
3. 检查端口5000是否被占用
4. 查看控制台错误信息

## 联系支持

如有问题，请查看控制台输出的错误信息。
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 说明文档已创建")

def test_installation():
    """测试安装"""
    print("🧪 测试安装...")
    
    python_path = get_python_executable()
    if not python_path.exists():
        print("❌ Python可执行文件不存在")
        return False
    
    try:
        # 测试导入主要模块
        result = subprocess.run([
            str(python_path), "-c", 
            "import flask, flask_cors, dotenv; print('所有模块导入成功')"
        ], capture_output=True, text=True, check=True)
        
        print("✅ 安装测试通过")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装测试失败: {e.stderr}")
        return False

def main():
    """主安装函数"""
    try:
        print_banner()
        print("开始安装百考通AI写作平台后端...")
        print("=" * 60)
        
        # 检查Python版本
        check_python_version()
        
        # 创建虚拟环境
        if not create_virtual_environment():
            print("❌ 虚拟环境创建失败")
            input("按回车键退出...")
            sys.exit(1)
        
        # 安装依赖
        if not install_dependencies():
            print("❌ 依赖安装失败")
            input("按回车键退出...")
            sys.exit(1)
        
        # 创建目录结构
        create_directory_structure()
        
        # 创建环境配置
        create_environment_file()
        
        # 创建启动脚本
        create_startup_scripts()
        
        # 创建说明文档
        create_readme()
        
        # 测试安装
        if not test_installation():
            print("⚠️  安装测试失败，但基本安装已完成")
        
        print("=" * 60)
        print("🎉 安装完成！")
        print("")
        print("启动方法:")
        if platform.system().lower() == "windows":
            print("  - 双击 start.bat 文件")
        else:
            print("  - 运行: ./start.sh")
        print("  - 或运行: python start.py")
        print("")
        print("访问地址: http://localhost:5000")
        print("=" * 60)
        
        input("按回车键退出...")
        
    except KeyboardInterrupt:
        print("\n❌ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()

