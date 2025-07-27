#!/usr/bin/env python3
"""
测试配置文件是否正确加载
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 测试配置
print("=== SQLite3 数据库查看器 配置测试 ===")
print()

# 数据库路径
DB_PATH = os.getenv('DATABASE_PATH', './database.sqlite')
print(f"数据库路径: {DB_PATH}")
print(f"绝对路径: {os.path.abspath(DB_PATH)}")
print(f"文件存在: {'是' if os.path.exists(DB_PATH) else '否'}")

if os.path.exists(DB_PATH):
    size = os.path.getsize(DB_PATH)
    print(f"文件大小: {size} bytes ({size/1024/1024:.2f} MB)")

print()

# 服务器配置
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', 8000))
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

print(f"服务器配置:")
print(f"  主机: {HOST}")
print(f"  端口: {PORT}")
print(f"  调试: {'开启' if DEBUG else '关闭'}")

print()
print("=== 配置测试完成 ===")

# 如果数据库不存在，创建示例数据库
if not os.path.exists(DB_PATH):
    print(f"\n数据库文件不存在，正在创建示例数据库: {DB_PATH}")
    import sqlite3
    
    # 确保目录存在
    os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)
    
    # 创建示例数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建示例表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入示例数据
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)", 
                   ("admin", "admin@example.com"))
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)", 
                   ("user1", "user1@example.com"))
    cursor.execute("INSERT OR IGNORE INTO products (name, price, stock) VALUES (?, ?, ?)", 
                   ("示例产品", 99.99, 100))
    
    conn.commit()
    conn.close()
    print("示例数据库创建完成！")