let currentTable = '';

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    loadDatabaseInfo();
    loadTables();
});

// 加载数据库信息
async function loadDatabaseInfo() {
    try {
        const response = await fetch('/api/database/info');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('db-path').innerHTML = 
                `<span class="text-danger">${data.error}: ${data.path}</span>`;
            return;
        }
        
        document.getElementById('db-path').innerHTML = 
            `${data.path} (${data.file_size_human})`;
    } catch (error) {
        console.error('加载数据库信息失败:', error);
        document.getElementById('db-path').innerHTML = 
            '<span class="text-danger">数据库连接失败</span>';
    }
}

// 加载所有表
async function loadTables() {
    try {
        const response = await fetch('/api/tables');
        const data = await response.json();
        
        const tablesList = document.getElementById('tables-list');
        tablesList.innerHTML = '';
        
        if (data.tables.length === 0) {
            tablesList.innerHTML = '<p class="text-muted">没有找到数据表</p>';
            return;
        }
        
        data.tables.forEach(table => {
            const item = document.createElement('a');
            item.href = '#';
            item.className = 'list-group-item list-group-item-action';
            item.textContent = table;
            item.onclick = (e) => {
                e.preventDefault();
                selectTable(table);
            };
            tablesList.appendChild(item);
        });
        
        // 默认选择第一个表
        if (data.tables.length > 0) {
            selectTable(data.tables[0]);
        }
    } catch (error) {
        console.error('加载表失败:', error);
        document.getElementById('tables-list').innerHTML = 
            '<p class="text-danger">加载失败</p>';
    }
}

// 选择表
async function selectTable(tableName) {
    currentTable = tableName;
    
    // 更新UI
    document.querySelectorAll('#tables-list .list-group-item').forEach(item => {
        item.classList.remove('active');
        if (item.textContent === tableName) {
            item.classList.add('active');
        }
    });
    
    document.getElementById('table-title').innerHTML = 
        `<i class="bi bi-table"></i> ${tableName}`;
    
    // 清空之前的数据，防止缓存问题
    clearTableData();
    
    loadTableInfo(tableName);
    loadTableData(tableName);
}

// 清空表格数据
function clearTableData() {
    const header = document.getElementById('table-header');
    const body = document.getElementById('table-body');
    const container = document.getElementById('data-container');
    const noData = document.getElementById('no-data');
    
    header.innerHTML = '';
    body.innerHTML = '';
    container.style.display = 'none';
    noData.style.display = 'none';
    document.getElementById('record-count').textContent = '0 条记录';
}

// 加载表信息
async function loadTableInfo(tableName) {
    try {
        const response = await fetch(`/api/table/${tableName}/info`);
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('table-info').innerHTML = 
                `<p class="text-danger">${data.error}</p>`;
            return;
        }
        
        let displaySchema = data.schema;
        let displayFieldsText = '';
        
        if (tableName === 'moonshot_requests') {
            const keyFields = ['id', 'response_content_type', 'response_status_code', 'created_at'];
            displaySchema = keyFields.map(fieldName => 
                data.schema.find(col => col.name === fieldName)
            ).filter(Boolean);
            displayFieldsText = `<div class="text-muted small">列表显示: ${keyFields.join(', ')}</div>`;
        }
        
        document.getElementById('table-info').innerHTML = `
            <p><strong>表名:</strong> ${data.table_name}</p>
            <p><strong>记录数:</strong> ${data.row_count.toLocaleString()}</p>
            <p><strong>总字段数:</strong> ${data.column_count}</p>
            ${displayFieldsText}
            <hr>
            <h6>字段结构:</h6>
            <small>
                ${displaySchema.map(col => 
                    `<div>${col.name} <span class="text-muted">(${col.type})</span></div>`
                ).join('')}
            </small>
        `;
    } catch (error) {
        console.error('加载表信息失败:', error);
    }
}

// 加载表数据
async function loadTableData(tableName, limit = 100) {
    showLoading();
    
    try {
        console.log(`开始加载表 '${tableName}' 的数据...`);
        const response = await fetch(`/api/table/${tableName}?limit=${limit}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('服务器响应错误:', response.status, errorText);
            
            try {
                const errorData = JSON.parse(errorText);
                showDetailedError(errorData);
            } catch (parseError) {
                showError(`服务器错误 ${response.status}: ${errorText}`);
            }
            return;
        }
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('非JSON响应:', text);
            showError('服务器返回了无效的数据格式');
            return;
        }
        
        const data = await response.json();
        
        if (data.error) {
            console.error('数据错误:', data.error);
            showDetailedError(data);
            return;
        }
        
        console.log(`成功加载 ${data.total_rows} 条记录`);
        
        // 确保数据为空时正确显示
        if (!data.data || data.data.length === 0) {
            showNoData();
            return;
        }
        
        displayData(data);
    } catch (error) {
        console.error('网络或解析错误:', error);
        showError(`加载失败: ${error.message}`);
    }
}

// 显示数据
function displayData(data) {
    const container = document.getElementById('data-container');
    const header = document.getElementById('table-header');
    const body = document.getElementById('table-body');
    
    // 更新记录数
    document.getElementById('record-count').textContent = 
        `${data.total_rows} 条记录`;
    
    if (data.data.length === 0) {
        showNoData();
        return;
    }
    
    // 使用原始schema顺序确保表头和数据列顺序一致
    let displaySchema = data.schema || [];
    let displayFields = [];
    
    if (currentTable === 'moonshot_requests') {
        // 列表只显示关键字段：id, response_content_type, response_status_code, created_at
        const keyFields = ['id', 'response_content_type', 'response_status_code', 'created_at'];
        displayFields = keyFields;
        displaySchema = keyFields.map(fieldName => 
            data.schema.find(col => col.name === fieldName)
        ).filter(Boolean);
    } else {
        // 对于其他表，使用schema定义的顺序
        displayFields = displaySchema.map(col => col.name);
    }
    
    // 生成表头 - 严格按照schema顺序
    if (displaySchema.length > 0) {
        const headerRow = document.createElement('tr');
        displaySchema.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col.name;
            th.title = `${col.name} (${col.type})`;
            headerRow.appendChild(th);
        });
        header.innerHTML = '';
        header.appendChild(headerRow);
    } else if (data.data.length > 0) {
        // 如果没有schema，用数据的第一行生成表头
        const headerRow = document.createElement('tr');
        Object.keys(data.data[0]).forEach(key => {
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        });
        header.innerHTML = '';
        header.appendChild(headerRow);
    }
    
    // 生成表格内容 - 严格按照表头顺序
    body.innerHTML = '';
    data.data.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.onclick = () => showDetail(row); // 传递原始完整数据
        
        // 按照displayFields的顺序显示数据
        displayFields.forEach(fieldName => {
            const td = document.createElement('td');
            const value = row[fieldName];
            
            if (value === null || value === undefined) {
                td.innerHTML = '<span class="text-muted">NULL</span>';
            } else if (typeof value === 'string' && value.length > 100) {
                td.textContent = value.substring(0, 100) + '...';
                td.title = value;
            } else if (typeof value === 'object') {
                td.innerHTML = '<span class="badge bg-info">JSON</span>';
            } else if (value === '') {
                td.innerHTML = '<span class="text-muted fst-italic">(空)</span>';
            } else {
                // 通用格式化
                td.innerHTML = formatCellValue(value, fieldName);
            }
            
            tr.appendChild(td);
        });
        
        body.appendChild(tr);
    });
    
    hideLoading();
    container.style.display = 'block';
}

// 通用单元格格式化
function formatCellValue(value, columnName) {
    if (value === null || value === undefined) {
        return '<span class="text-muted">NULL</span>';
    }
    
    const lowerColName = columnName.toLowerCase();
    
    // 布尔值
    if (typeof value === 'boolean') {
        return value ? 
            '<span class="badge bg-success">True</span>' : 
            '<span class="badge bg-secondary">False</span>';
    }
    
    // 状态码
    if (lowerColName.includes('status') || lowerColName.includes('code')) {
        if (typeof value === 'number') {
            let statusClass = 'status-other';
            if (value >= 200 && value < 300) statusClass = 'status-2xx';
            else if (value >= 300 && value < 400) statusClass = 'status-3xx';
            else if (value >= 400 && value < 500) statusClass = 'status-4xx';
            else if (value >= 500) statusClass = 'status-5xx';
            return `<span class="status-code ${statusClass}">${value}</span>`;
        }
    }
    
    // HTTP方法
    if (lowerColName === 'method' || lowerColName === 'request_method') {
        const methodColors = {
            'GET': 'success',
            'POST': 'primary',
            'PUT': 'warning',
            'DELETE': 'danger',
            'PATCH': 'info',
            'HEAD': 'secondary',
            'OPTIONS': 'dark'
        };
        const color = methodColors[value] || 'secondary';
        return `<span class="badge bg-${color}">${value}</span>`;
    }
    
    // 时间戳
    if (lowerColName.includes('time') || lowerColName.includes('at') || lowerColName.includes('date')) {
        try {
            const date = new Date(value);
            if (!isNaN(date.getTime())) {
                return date.toLocaleString();
            }
        } catch (e) {
            // 不是有效日期，按原样显示
        }
    }
    
    // URL或路径
    if (typeof value === 'string' && 
        (value.startsWith('http') || value.startsWith('/') || value.includes('://'))) {
        return `<code>${value}</code>`;
    }
    
    // JSON字符串
    if (typeof value === 'string' && 
        (value.startsWith('{') || value.startsWith('['))) {
        try {
            JSON.parse(value);
            return '<span class="badge bg-info">JSON</span>';
        } catch (e) {
            // 不是有效JSON，按原样显示
        }
    }
    
    // 长文本截断
    if (typeof value === 'string' && value.length > 100) {
        return value.substring(0, 100) + '...';
    }
    
    return value;
}

// 显示详细信息
function showDetail(row) {
    const modal = new bootstrap.Modal(document.getElementById('detailModal'));
    const content = document.getElementById('detail-content');
    
    let displayRow = row;
    
    if (currentTable === 'moonshot_requests') {
        // 对于moonshot_requests表，显示所有request_*和response_*开头的字段
        displayRow = {};
        
        // 按字段类型分组显示
        const requestFields = {};
        const responseFields = {};
        const otherFields = {};
        
        Object.keys(row).forEach(key => {
            if (key.startsWith('request_')) {
                requestFields[key] = row[key];
            } else if (key.startsWith('response_')) {
                responseFields[key] = row[key];
            } else {
                otherFields[key] = row[key];
            }
        });
        
        let html = '<div class="row">';
        
        // 基本信息（id, created_at等）
        if (Object.keys(otherFields).length > 0) {
            html += '<div class="col-12"><h6 class="text-primary">基本信息</h6><hr></div>';
            Object.entries(otherFields).forEach(([key, value]) => {
                html += '<div class="col-md-6 mb-3">' +
                    '<strong>' + key + ':</strong>' +
                    '<div class="json-view">' + formatValue(value) + '</div>' +
                    '</div>';
            });
        }
        
        // 请求相关字段
        if (Object.keys(requestFields).length > 0) {
            html += '<div class="col-12 mt-4"><h6 class="text-info">请求信息</h6><hr></div>';
            Object.entries(requestFields).forEach(([key, value]) => {
                html += '<div class="col-md-6 mb-3">' +
                    '<strong>' + key + ':</strong>' +
                    '<div class="json-view">' + formatValue(value) + '</div>' +
                    '</div>';
            });
        }
        
        // 响应相关字段
        if (Object.keys(responseFields).length > 0) {
            html += '<div class="col-12 mt-4"><h6 class="text-success">响应信息</h6><hr></div>';
            Object.entries(responseFields).forEach(([key, value]) => {
                html += '<div class="col-md-6 mb-3">' +
                    '<strong>' + key + ':</strong>' +
                    '<div class="json-view">' + formatValue(value) + '</div>' +
                    '</div>';
            });
        }
        
        html += '</div>';
        content.innerHTML = html;
    } else {
        // 其他表显示所有字段
        let html = '<div class="row">';
        Object.entries(displayRow).forEach(([key, value]) => {
            html += '<div class="col-md-6 mb-3">' +
                '<strong>' + key + ':</strong>' +
                '<div class="json-view">' + formatValue(value) + '</div>' +
                '</div>';
        });
        html += '</div>';
        content.innerHTML = html;
    }
    
    modal.show();
}

// 格式化值显示
function formatValue(value) {
    if (value === null || value === undefined) {
        return '<span class="text-muted">NULL</span>';
    }
    
    if (value === '') {
        return '<span class="text-muted fst-italic">(空字符串)</span>';
    }
    
    if (typeof value === 'string') {
        // 尝试解析JSON
        try {
            const parsed = JSON.parse(value);
            return `<pre class="mb-0">${JSON.stringify(parsed, null, 2)}</pre>`;
        } catch {
            // 不是JSON，按原样显示，确保空字符串有最小高度
            if (value.trim() === '') {
                return '<span class="text-muted fst-italic">(空白字符)</span>';
            }
            return `<div style="min-height: 1.5em; white-space: pre-wrap; word-break: break-all;">${value}</div>`;
        }
    }
    
    if (typeof value === 'object') {
        return `<pre class="mb-0">${JSON.stringify(value, null, 2)}</pre>`;
    }
    
    return `<div style="min-height: 1.5em;">${value}</div>`;
}

// 刷新数据
function refreshData() {
    if (currentTable) {
        loadTableData(currentTable);
    }
}

// 显示加载中
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('data-container').style.display = 'none';
    document.getElementById('no-data').style.display = 'none';
}

// 隐藏加载中
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// 显示无数据
function showNoData() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('data-container').style.display = 'none';
    document.getElementById('no-data').style.display = 'flex';
    document.getElementById('no-data').innerHTML = `
        <i class="bi bi-inbox display-1 text-muted"></i>
        <h5 class="text-muted mt-3">暂无数据</h5>
        <p class="text-muted">表 ${currentTable} 中没有记录</p>
    `;
    document.getElementById('record-count').textContent = '0 条记录';
}

// 显示错误
function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('data-container').style.display = 'none';
    document.getElementById('no-data').style.display = 'flex';
    document.getElementById('no-data').innerHTML = `
        <i class="bi bi-exclamation-triangle display-1 text-danger"></i>
        <p class="text-danger">${message}</p>
    `;
}

// 显示详细错误信息
function showDetailedError(errorData) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('data-container').style.display = 'none';
    document.getElementById('no-data').style.display = 'flex';
    
    let details = '';
    if (errorData.error_type) {
        details += `<p><strong>错误类型:</strong> ${errorData.error_type}</p>`;
    }
    if (errorData.table_name) {
        details += `<p><strong>表名:</strong> ${errorData.table_name}</p>`;
    }
    
    document.getElementById('no-data').innerHTML = `
        <i class="bi bi-exclamation-triangle display-1 text-danger"></i>
        <h5 class="text-danger">数据加载失败</h5>
        <p>${errorData.error || '未知错误'}</p>
        ${details}
        <button class="btn btn-sm btn-outline-secondary" onclick="showErrorDetails()">
            <i class="bi bi-info-circle"></i> 查看详情
        </button>
    `;
    
    // 存储错误详情用于调试
    window.lastError = errorData;
}

// 显示详细错误信息（调试用）
function showErrorDetails() {
    if (window.lastError) {
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        const content = document.getElementById('error-detail-content');
        
        let html = '<pre class="bg-light p-3 rounded">';
        html += JSON.stringify(window.lastError, null, 2);
        html += '</pre>';
        
        content.innerHTML = html;
        modal.show();
    }
}