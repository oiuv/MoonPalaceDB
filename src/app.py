from flask import Flask, render_template, jsonify, request
import sqlite3
import pandas as pd
import os
import json
import logging
import math
from datetime import datetime
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# 从环境变量获取数据库路径，默认为data目录下的database.sqlite
DB_PATH = os.getenv('DATABASE_PATH', './data/database.sqlite')

# 配置Flask的JSON处理
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def get_db_connection():
    """创建数据库连接"""
    try:
        logger.info(f"正在连接数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
        logger.info("数据库连接成功")
        return conn
    except sqlite3.Error as e:
        logger.error(f"数据库连接错误: {e}")
        return None

def get_tables():
    """获取数据库中所有表名"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"发现 {len(tables)} 个表: {tables}")
        return tables
    except sqlite3.Error as e:
        logger.error(f"获取表名错误: {e}")
        return []
    finally:
        conn.close()

def get_table_data(table_name, limit=100):
    """获取指定表的数据"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        logger.info(f"开始获取表 '{table_name}' 的数据，限制 {limit} 条")
        
        # 防止SQL注入
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            logger.warning(f"表 '{table_name}' 不存在")
            return []
        
        # 获取表结构信息
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        logger.info(f"表 '{table_name}' 有 {len(columns)} 个字段")
        
        # 检查是否有数据
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]
        logger.info(f"表 '{table_name}' 共有 {total_rows} 条记录")
        
        if total_rows == 0:
            logger.info(f"表 '{table_name}' 为空")
            return []
        
        # 获取表数据 - 倒序显示最新的记录
        # 检查是否有时间相关字段用于排序
        time_columns = [col[1] for col in columns if any(time_word in col[1].lower() 
                      for time_word in ['time', 'date', 'created', 'updated', 'timestamp'])]
        
        if time_columns:
            # 使用找到的时间字段进行倒序排序
            order_column = time_columns[0]  # 使用第一个找到的时间字段
            query = f"SELECT * FROM {table_name} ORDER BY {order_column} DESC LIMIT ?"
            logger.info(f"使用字段 '{order_column}' 进行倒序排序")
        elif any(col[5] == 1 for col in columns):  # 检查是否有主键
            # 使用主键倒序排序
            pk_columns = [col[1] for col in columns if col[5] == 1]
            order_column = pk_columns[0]
            query = f"SELECT * FROM {table_name} ORDER BY {order_column} DESC LIMIT ?"
            logger.info(f"使用主键 '{order_column}' 进行倒序排序")
        else:
            # 没有合适的排序字段，使用默认顺序
            query = f"SELECT * FROM {table_name} LIMIT ?"
            logger.info("没有合适的排序字段，使用默认顺序")
        
        logger.debug(f"执行SQL: {query} 参数: {limit}")
        
        # 使用pandas读取数据，处理可能的编码问题
        try:
            df = pd.read_sql_query(query, conn, params=(limit,))
            logger.info(f"成功获取 {len(df)} 条记录")
            
            # 转换为字典格式，处理特殊数据类型和NaN值
            data = []
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    value = row[col]
                    
                    # 处理pandas的NaN值
                    if pd.isna(value):
                        value = None
                    # 处理可能的二进制数据
                    elif isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except UnicodeDecodeError:
                            value = f"<二进制数据: {len(value)} bytes>"
                    # 处理浮点数
                    elif isinstance(value, float):
                        value = clean_data_for_json(value)
                    
                    record[col] = value
                data.append(record)
            
            # 清理整个数据集
            data = clean_data_for_json(data)
            return data
            
        except Exception as e:
            logger.error(f"Pandas读取数据失败: {e}")
            # 回退到原生sqlite3查询
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            # 获取列名
            column_names = [description[0] for description in cursor.description]
            
            data = []
            for row in rows:
                record = {}
                for i, value in enumerate(row):
                    # 处理NaN和特殊值
                    if value is None:
                        record[column_names[i]] = None
                    elif isinstance(value, float):
                        record[column_names[i]] = clean_data_for_json(value)
                    elif isinstance(value, bytes):
                        try:
                            record[column_names[i]] = value.decode('utf-8')
                        except UnicodeDecodeError:
                            record[column_names[i]] = f"<二进制数据: {len(value)} bytes>"
                    else:
                        record[column_names[i]] = value
                data.append(record)
            
            # 清理数据
            data = clean_data_for_json(data)
            logger.info(f"使用回退方法获取 {len(data)} 条记录")
            return data
            
    except Exception as e:
        logger.error(f"获取表 '{table_name}' 数据错误: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return []
    finally:
        conn.close()

def get_table_schema(table_name):
    """获取表结构信息"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        logger.info(f"获取表 '{table_name}' 的结构信息")
        cursor = conn.cursor()
        
        # 获取基本表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # 获取索引信息
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        schema = []
        for col in columns:
            schema.append({
                'cid': col[0],
                'name': col[1],
                'type': col[2],
                'notnull': col[3],
                'default_value': col[4],
                'pk': col[5],
                'indexed': any(idx[2] == col[1] for idx in indexes)  # 检查是否有索引
            })
        
        logger.info(f"表 '{table_name}' 结构: {len(schema)} 个字段")
        return schema
    except sqlite3.Error as e:
        logger.error(f"获取表 '{table_name}' 结构错误: {e}")
        return []
    finally:
        conn.close()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/tables')
def api_tables():
    """API: 获取所有表名"""
    tables = get_tables()
    return jsonify({'tables': tables})

@app.route('/api/table/<table_name>')
def api_table_data(table_name):
    """API: 获取指定表的数据"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logger.info(f"API请求: 获取表 '{table_name}' 的数据，限制 {limit} 条")
        
        # 验证表名
        if not table_name or not table_name.replace('_', '').isalnum():
            logger.warning(f"无效的表名: {table_name}")
            return jsonify({'error': '无效的表名'}), 400
        
        # 获取数据
        data = get_table_data(table_name, limit)
        schema = get_table_schema(table_name)
        
        if not schema:
            logger.error(f"表 '{table_name}' 结构获取失败")
            return jsonify({'error': '无法获取表结构'}), 500
        
        logger.info(f"API响应: 表 '{table_name}' 返回 {len(data)} 条记录")
        
        # 清理数据确保JSON兼容性
        clean_data = clean_data_for_json(data)
        clean_schema = clean_data_for_json(schema)
        
        return jsonify({
            'data': clean_data,
            'schema': clean_schema,
            'table_name': table_name,
            'total_rows': len(clean_data),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"API错误 - 表 '{table_name}': {type(e).__name__}: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({
            'error': f'数据加载失败: {str(e)}',
            'error_type': type(e).__name__,
            'table_name': table_name
        }), 500

@app.route('/api/table/<table_name>/info')
def api_table_info(table_name):
    """API: 获取表的基本信息"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    try:
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            return jsonify({'error': '表不存在'}), 404
        
        # 获取行数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # 获取表结构
        schema = get_table_schema(table_name)
        
        return jsonify({
            'table_name': table_name,
            'row_count': row_count,
            'column_count': len(schema),
            'schema': schema
        })
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/database/info')
def api_database_info():
    """API: 获取数据库基本信息"""
    if not os.path.exists(DB_PATH):
        return jsonify({'error': '数据库文件不存在', 'path': DB_PATH}), 404
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500
        
        cursor = conn.cursor()
        
        # 获取数据库大小
        file_size = os.path.getsize(DB_PATH)
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 获取总记录数
        total_records = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_records += cursor.fetchone()[0]
            except:
                pass
        
        conn.close()
        
        return jsonify({
            'path': DB_PATH,
            'file_size': file_size,
            'file_size_human': format_file_size(file_size),
            'table_count': len(tables),
            'total_records': total_records,
            'tables': tables
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_file_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def clean_data_for_json(data):
    """清理数据中的NaN和无限值，使其可JSON序列化"""
    if isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, dict):
        return {key: clean_data_for_json(value) for key, value in data.items()}
    elif isinstance(data, float):
        if math.isnan(data):
            return None
        elif math.isinf(data):
            return str(data)  # 将无限值转为字符串
        else:
            return data
    elif isinstance(data, (pd.Timestamp, datetime)):
        return str(data)
    elif data is None:
        return None
    else:
        return data

if __name__ == '__main__':
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"警告: 数据库文件 {DB_PATH} 不存在")
        print(f"请检查 .env 文件中的 DATABASE_PATH 配置")
    else:
        print(f"数据库文件已找到: {DB_PATH}")
        print(f"数据库大小: {os.path.getsize(DB_PATH) / 1024 / 1024:.2f} MB")
    
    # 从环境变量获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"启动服务器: http://{host}:{port}")
    app.run(debug=debug, host=host, port=port)