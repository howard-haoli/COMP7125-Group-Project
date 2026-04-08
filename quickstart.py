#!/usr/bin/env python
"""
快速启动脚本 - 初始化项目并启动服务

使用方法:
    python quickstart.py
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_banner():
    """打印项目banner"""
    print("""
╔════════════════════════════════════════════════════════════╗
║    ReAct 课程可视化系统 - 快速启动脚本                      ║
║    COMP7125 Group Project                                 ║
╚════════════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} 版本正确")


def create_directories():
    """创建必要的目录"""
    dirs = [
        "data",
        "data/chroma_db",
        "data/output",
        "logs"
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ 目录结构已创建")


def install_dependencies():
    """安装依赖"""
    print("\n📦 安装Python依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        sys.exit(1)


def check_ollama():
    """检查Ollama服务"""
    print("\n🔍 检查Ollama服务...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama服务运行中")
            return True
    except Exception:
        pass
    
    print("⚠️  Ollama服务未运行")
    print("   请在新终端中运行: ollama serve")
    return False


def start_api_server():
    """启动API服务器"""
    print("\n🚀 启动FastAPI服务器...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.api.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n⛔ 服务器已停止")


def run_tests():
    """运行测试"""
    print("\n🧪 运行测试...")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 测试失败")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ReAct课程系统快速启动脚本")
    parser.add_argument("--setup", action="store_true", help="初始化项目")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--api", action="store_true", help="启动API服务器")
    
    args = parser.parse_args()
    
    print_banner()
    check_python_version()
    
    if args.setup:
        create_directories()
        install_dependencies()
        print("\n✅ 项目初始化完成！")
        print("\n下一步:")
        print("  1. 启动Ollama: ollama serve")
        print("  2. 启动API: python quickstart.py --api")
        
    elif args.test:
        run_tests()
        
    elif args.api:
        ollama_ok = check_ollama()
        if ollama_ok:
            start_api_server()
        else:
            print("\n❌ 无法启动API服务器")
            sys.exit(1)
    else:
        # 默认执行完整初始化
        create_directories()
        print("\n初始化完成！")
        print("\n快速开始指南:")
        print("  1. 设置环境: cp .env.example .env")
        print("  2. 安装依赖: pip install -r requirements.txt")
        print("  3. 启动Ollama: ollama pull llama2:13b && ollama serve")
        print("  4. 启动API: python quickstart.py --api")
        print("  5. 运行测试: python quickstart.py --test")
        print("\n文档: 详见 REACT_IMPLEMENTATION_PLAN.md")


if __name__ == "__main__":
    main()
