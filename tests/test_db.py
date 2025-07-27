import sqlite3

db_path = r'C:\Users\oiuv\.moonpalace\moonpalace.sqlite'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print('数据库连接成功')
    print('数据表:', tables)
    
    # 检查moonshot_requests表的记录数
    cursor.execute('SELECT COUNT(*) FROM moonshot_requests')
    count = cursor.fetchone()[0]
    print(f'moonshot_requests表记录数: {count}')
    
    # 获取前5条记录示例
    if count > 0:
        cursor.execute('SELECT id, request_method, request_path, response_status_code, created_at FROM moonshot_requests LIMIT 5')
        rows = cursor.fetchall()
        print('\n前5条记录示例:')
        for row in rows:
            print(f'ID: {row[0]}, Method: {row[1]}, Path: {row[2]}, Status: {row[3]}, Time: {row[4]}')
    
    conn.close()
    
except Exception as e:
    print('错误:', str(e))