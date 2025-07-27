# SQLite3 数据库查看器

这是一个通用的基于Flask的Web应用，用于查看和分析任何SQLite3数据库。支持通过环境变量配置数据库路径，提供现代化的Web界面进行数据浏览和分析。

## ✨ 功能特点

- 📊 **可视化数据库结构**：直观展示所有表和字段信息
- 🔍 **智能数据格式化**：自动识别并格式化时间、状态码、URL等常见数据类型
- 📱 **响应式设计**：完美支持桌面和移动端浏览
- ⚡ **高性能**：支持大数据表的分页加载
- 🔧 **通用性强**：适用于任何SQLite3数据库文件
- 🎨 **现代化界面**：基于Bootstrap 5的清爽界面
- 📋 **详细视图**：点击任意行查看完整数据详情
- 🔄 **实时刷新**：一键刷新获取最新数据

## 🚀 快速开始

### 方法1：使用启动脚本 (Windows)
双击运行 `run.bat` 文件，将自动：
1. 检查Python环境
2. 安装所需依赖
3. 启动Web服务
4. 自动打开浏览器

### 方法2：手动启动

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

2. **配置数据库**（可选）：
   - 复制 `.env.example` 为 `.env`
   - 修改 `DATABASE_PATH` 为你的数据库文件路径

3. **启动应用**：
```bash
python app.py
```

4. **访问应用**：
```
http://localhost:8000
```

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件（复制 `.env.example`），支持以下配置：

```bash
# 数据库配置
DATABASE_PATH=./database.sqlite          # SQLite数据库文件路径

# 服务器配置
FLASK_HOST=0.0.0.0                     # 监听地址
FLASK_PORT=8000                        # 监听端口
FLASK_DEBUG=True                       # 调试模式
```

### 数据库路径支持格式

- **相对路径**：`./data/mydb.sqlite`
- **绝对路径**：`/path/to/database.sqlite`
- **Windows路径**：`C:\Users\username\database.sqlite`

## 📖 使用指南

### 1. 连接数据库
启动应用后，系统会自动连接配置的数据库文件。如果数据库不存在，会显示警告信息。

### 2. 浏览数据表
- 左侧面板显示数据库中所有表
- 点击表名查看数据
- 显示每个表的记录数和字段数

### 3. 查看数据
- 表格形式展示数据
- 自动格式化特殊数据类型
- 支持大数据分页显示

### 4. 查看详情
- 点击任意行查看完整记录
- JSON数据自动格式化显示
- 支持复制和查看原始数据

## 🎯 智能数据识别

应用会自动识别并格式化以下数据类型：

| 数据类型 | 识别规则 | 显示效果 |
|---------|----------|----------|
| **HTTP方法** | method, request_method列 | `GET` `POST` `PUT` 等彩色标签 |
| **状态码** | status, code结尾的列 | 2xx(绿色) 4xx(黄色) 5xx(红色) |
| **时间戳** | time, at, date结尾的列 | 本地时间格式 |
| **URL/路径** | http开头或包含:// | 代码格式显示 |
| **JSON数据** | JSON格式字符串 | JSON标签，点击查看详情 |
| **布尔值** | true/false | True/False彩色标签 |
| **长文本** | 超过100字符 | 自动截断，悬停显示完整 |

## 🛠️ 技术栈

- **后端**：Python Flask + SQLite3 + Pandas
- **前端**：HTML5 + Bootstrap 5 + Vanilla JavaScript
- **配置**：python-dotenv
- **部署**：支持Windows/Linux/macOS

## 📁 项目结构

```
SQLite-Viewer/
├── app.py                 # Flask主应用
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── run.bat               # Windows启动脚本
├── templates/
│   └── index.html        # 主页面模板
├── static/
│   ├── css/              # 样式文件
│   └── js/
│       └── app.js        # 前端JavaScript
└── README.md             # 项目文档
```

## 🔧 故障排除

### 数据库连接问题
```bash
# 检查数据库文件是否存在
ls -la /path/to/database.sqlite

# 检查文件权限
chmod 644 /path/to/database.sqlite
```

### 依赖安装问题
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 端口冲突
修改 `.env` 文件：
```bash
FLASK_PORT=8001  # 改为其他端口
```

### 路径问题（Windows）
```bash
# Windows路径使用双反斜杠或正斜杠
DATABASE_PATH=C:\\Users\\username\\database.sqlite
# 或
DATABASE_PATH=C:/Users/username/database.sqlite
```

## 📊 性能优化

- **大数据表**：默认显示前100条记录
- **内存管理**：使用分页加载避免内存溢出
- **缓存机制**：浏览器端缓存表结构信息
- **响应优化**：异步加载提升用户体验

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License - 详见LICENSE文件