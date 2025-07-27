# -*- coding: utf-8 -*-
import os
import sys
import webbrowser
import time
import threading
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def start_browser(host, port):
    """延迟启动浏览器"""
    time.sleep(2)
    url = f'http://{host}:{port}'
    webbrowser.open(url)

def main():
    # 从环境变量获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    db_path = os.getenv('DATABASE_PATH', './database.sqlite')
    
    print("=== SQLite3 数据库查看器 ===")
    print(f"数据库路径: {os.path.abspath(db_path)}")
    print(f"应用地址: http://{host}:{port}")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print("按 Ctrl+C 停止服务")
    print()
    
    # 检查数据库文件
    if not os.path.exists(db_path):
        print(f"警告: 数据库文件不存在 - {db_path}")
        print("请检查 .env 文件中的 DATABASE_PATH 配置")
        print()
    
    # 启动Flask应用
    try:
        from app import app
        # 只在非调试模式或主进程中打开浏览器
        if not debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            browser_thread = threading.Thread(target=start_browser, args=(host, port))
            browser_thread.daemon = True
            browser_thread.start()
        
        app.run(debug=debug, host=host, port=port)
    except KeyboardInterrupt:
        print("应用已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()