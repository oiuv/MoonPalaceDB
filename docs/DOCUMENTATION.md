# SQLite3 Database Viewer - Complete Documentation

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Development Guide](#development-guide)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Extension Development](#extension-development)

## Project Overview

This is a comprehensive SQLite3 database visualization tool built with Flask and Bootstrap 5. Originally designed for analyzing API request logs, it supports **any SQLite3 database file** through configuration.

### Key Features
- **Universal Database Support**: Works with any SQLite3 database file
- **Smart Data Recognition**: Automatic formatting of HTTP methods, status codes, timestamps, JSON data
- **Responsive Design**: Perfect for desktop and mobile browsing
- **Real-time Analysis**: Live data refresh and detailed record viewing
- **Performance Optimized**: Pagination for large datasets
- **Security First**: SQL injection protection and input validation

## Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd MoonPalaceDB

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
copy .env.example .env
# Edit .env to set your database path
```

### Running the Application

#### Method 1: Enhanced Startup (Recommended)
```bash
python src/start.py
```
- Auto-opens browser
- Shows startup information
- Better error handling

#### Method 2: Direct Flask
```bash
python src/app.py
```
- Standard Flask development server
- Manual browser opening

## Architecture

### Technical Stack

#### Backend
- **Framework**: Flask 2.3.3 (Lightweight Python Web Framework)
- **Database**: SQLite3 (Embedded Database)
- **Data Processing**: Pandas 2.0.3 (Data Analysis and Processing)
- **Configuration**: python-dotenv (Environment Variable Management)
- **Logging**: Python logging (Multi-level Logging System)

#### Frontend
- **UI Framework**: Bootstrap 5.3.0 (Responsive Design)
- **Icons**: Bootstrap Icons 1.10.0
- **Interaction**: Vanilla JavaScript (Native JS, No Framework Dependencies)
- **Communication**: AJAX (Asynchronous Data Loading)

### Project Structure
```
MoonPalaceDB/
├── src/                    # Source code directory
│   ├── app.py             # Main Flask application
│   └── start.py           # Enhanced startup script
├── tests/                 # Test files
├── data/                  # Database files
├── logs/                  # Log files
├── static/                # Static assets (CSS, JS, images)
├── templates/             # HTML templates
├── docs/                  # Documentation
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

### Core Components

#### 1. Data Access Layer (app.py)
- **Database Connection**: `get_db_connection()` - Secure connection management
- **Table Structure**: `get_tables()`, `get_table_schema()`
- **Data Query**: `get_table_data()` - Smart pagination and sorting
- **Data Cleaning**: `clean_data_for_json()` - Handle NaN and special values

#### 2. API Layer (app.py)
- `GET /` - Main application interface
- `GET /api/tables` - Get all table names
- `GET /api/table/<table_name>` - Get table data with pagination
- `GET /api/table/<table_name>/info` - Get table information
- `GET /api/database/info` - Get database basic information

#### 3. Frontend Presentation Layer (index.html + app.js)
- **Responsive Layout**: Adapts to desktop and mobile devices
- **Real-time Data Loading**: AJAX asynchronous data fetching
- **Smart Formatting**: Automatic data type recognition and display formatting
- **Interactive Optimization**: Click rows for details, one-click refresh, etc.

### Data Flow
```
1. User visits homepage → Loads index.html
2. Page initialization → Calls /api/database/info for database info
3. Load table list → Calls /api/tables for all tables
4. Select table → Calls /api/table/<name> for data
5. Click row → Show detailed data modal
```

## Development Guide

### Environment Setup

#### Configuration (.env)
```bash
# Database Configuration
DATABASE_PATH=./data/database.sqlite

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_DEBUG=True
```

#### Database Path Examples
```bash
# Relative path
DATABASE_PATH=./data/mydb.sqlite

# Absolute path (Windows)
DATABASE_PATH=C:\Users\username\database.sqlite

# Absolute path (Linux/Mac)
DATABASE_PATH=/home/user/database.sqlite
```

### Development Workflow

#### Running Tests
```bash
# Run all tests
python tests/test_config.py
python tests/test_db.py
python tests/test_nan.py
```

#### Test Categories
- **Configuration tests**: Environment variable handling
- **Database tests**: Connection and query validation
- **Data processing tests**: NaN and special value handling

### Frontend Development

#### Key JavaScript Functions
- `loadDatabaseInfo()` - Load database metadata
- `loadTables()` - Load and display table list
- `selectTable(tableName)` - Select and display table data
- `showDetail(row)` - Show detailed row information
- `formatValue(value)` - Format values for display

#### Data Formatting Features
- **NULL values**: Displayed as "NULL" with muted styling
- **Empty strings**: Displayed as "(empty)" with italic styling
- **JSON data**: Auto-formatted with syntax highlighting
- **Timestamps**: Converted to local time format
- **HTTP methods**: Color-coded badges
- **Status codes**: Color-coded by category

## API Reference

### Endpoints

#### GET /api/database/info
Returns database metadata including file size, table count, and total records.

**Response:**
```json
{
  "path": "./data/database.sqlite",
  "file_size": 151374336,
  "file_size_human": "151.37 MB",
  "table_count": 3,
  "total_records": 887,
  "tables": ["table1", "table2", "table3"]
}
```

#### GET /api/tables
Returns list of all tables in the database.

**Response:**
```json
{
  "tables": ["moonshot_requests", "sqlite_sequence", "moonshot_caches"]
}
```

#### GET /api/table/<table_name>
Returns table data with pagination.

**Parameters:**
- `limit` (optional): Number of records to return (default: 100)

**Response:**
```json
{
  "data": [...],
  "schema": [...],
  "table_name": "moonshot_requests",
  "total_rows": 100,
  "status": "success"
}
```

#### GET /api/table/<table_name>/info
Returns table schema and metadata.

**Response:**
```json
{
  "table_name": "moonshot_requests",
  "row_count": 887,
  "column_count": 25,
  "schema": [...]
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `./data/database.sqlite` | Path to SQLite database file |
| `FLASK_HOST` | `0.0.0.0` | Server bind address |
| `FLASK_PORT` | `8000` | Server port |
| `FLASK_DEBUG` | `True` | Enable debug mode |

### Security Configuration
- **SQL Injection Protection**: Parameterized queries
- **Input Validation**: Strict table name and parameter validation
- **Error Handling**: No sensitive system information exposure
- **Path Security**: Directory traversal attack prevention

## Troubleshooting

### Common Issues

#### TemplateNotFound Error
**Cause**: Running from wrong directory
**Solution**: Ensure Flask template_folder is correctly set
```python
app = Flask(__name__, template_folder='../templates', static_folder='../static')
```

#### Database Connection Issues
**Check**: Database file exists and path is correct
**Debug**: Enable debug logging in .env
```bash
FLASK_DEBUG=True
```

#### Browser Opens Twice
**Cause**: Flask debug mode reloads
**Solution**: Fixed in start.py with WERKZEUG_RUN_MAIN check

### Debug Mode
Enable detailed logging:
```bash
# In .env file
FLASK_DEBUG=True
```

### Environment Issues
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify database file
ls -la data/
```

## Extension Development

### Adding New API Endpoints
```python
@app.route('/api/new-endpoint')
def new_endpoint():
    # Your implementation here
    return jsonify({'data': 'response'})
```

### Adding New Data Formatters
Edit `static/js/app.js`:
```javascript
function formatCellValue(value, columnName) {
    // Add your custom formatting logic
    if (columnName === 'custom_field') {
        return customFormat(value);
    }
    // ... existing formatting
}
```

### Adding New Tables
The application automatically detects all tables in the configured database. No code changes needed for new tables.

## Performance Optimization

### Large Datasets
- Use pagination (limit parameter)
- Consider adding indexes on frequently queried columns
- Monitor memory usage with large result sets

### Frontend Optimization
- Enable browser caching for static assets
- Use CDN for Bootstrap and icons
- Minimize JavaScript bundle size

### Backend Optimization
- **Lazy Loading**: Load data on demand to avoid initial load pressure
- **Caching Strategy**: Browser-side table structure caching
- **Pagination**: Limit single load data volume
- **Async Operations**: Non-blocking user interface
- **Resource Optimization**: CDN for static assets

## Deployment

### Production Considerations
- Set `FLASK_DEBUG=False`
- Use a production WSGI server (gunicorn, uWSGI)
- Configure proper logging
- Set up reverse proxy (nginx, Apache)

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "src/start.py"]
```

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

## Extension Points

### Planned Features
- **Data Export**: CSV/Excel export support
- **Chart Analysis**: Add data visualization charts
- **Search Function**: Conditional record filtering
- **RESTful API**: External API endpoints
- **User Authentication**: Login and permission management

### Customization
- **Custom Formatters**: Add new data type formatting
- **Custom Themes**: Modify Bootstrap styling
- **Custom Queries**: Add specialized API endpoints
- **Custom Views**: Create new data presentation modes