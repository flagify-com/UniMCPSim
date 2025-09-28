        // 检查认证状态
        function checkAuth() {
            const jwt = localStorage.getItem('jwt_token');
            if (!jwt) {
                // 如果没有token，跳转到登录页
                window.location.href = '/login';
                return false;
            }
            return jwt;
        }

        // 注销函数
        function logout() {
            // 确认注销
            if (confirm('确定要注销吗？')) {
                // 清除本地存储的JWT token
                localStorage.removeItem('jwt_token');
                // 跳转到登录页面
                window.location.href = '/login';
            }
        }

        // 通用API调用函数，自动添加JWT认证头
        async function apiCall(url, options = {}) {
            const jwt = checkAuth();
            if (!jwt) return null;

            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwt}`
                }
            };

            const mergedOptions = {
                ...defaultOptions,
                ...options,
                headers: {
                    ...defaultOptions.headers,
                    ...(options.headers || {})
                }
            };

            try {
                const response = await fetch(url, mergedOptions);

                // 如果返回401，清除token并跳转到登录页
                if (response.status === 401) {
                    localStorage.removeItem('jwt_token');
                    window.location.href = '/login';
                    return null;
                }

                return response;
            } catch (error) {
                console.error('API调用失败:', error);
                throw error;
            }
        }

        // 全局状态
        let playbooks = [];
        let currentPage = 1;
        const itemsPerPage = 20;
        
        // DOM 元素
        const alertContainer = document.getElementById('alert-container');
        const playbooksTable = document.getElementById('playbooks-tbody');
        const totalCount = document.getElementById('total-count');
        const enabledCount = document.getElementById('enabled-count');
        const disabledCount = document.getElementById('disabled-count');
        const paginationInfo = document.getElementById('pagination-info');
        const prevPageBtn = document.getElementById('prev-page');
        const nextPageBtn = document.getElementById('next-page');
        const pageNumbers = document.getElementById('page-numbers');
        
        // 显示通知
        function showAlert(message, type = 'success') {
            const alert = document.createElement('div');
            alert.className = type === 'error' ? 'error' : 'success';
            alert.textContent = message;
            alertContainer.innerHTML = '';
            alertContainer.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 3000);
        }
        
        // 格式化日期
        function formatDate(dateStr) {
            if (!dateStr) return '-';
            try {
                const date = new Date(dateStr);
                return date.toLocaleString('zh-CN');
            } catch {
                return '-';
            }
        }
        
        // 切换剧本状态
        async function togglePlaybook(playbookId, enabled) {
            try {
                const response = await apiCall(`/api/admin/playbooks/${playbookId}/toggle`, {
                    method: 'POST',
                    body: JSON.stringify({ enabled: enabled })
                });

                if (!response) return;
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert(`剧本 ${playbookId} 已${enabled ? '启用' : '禁用'}`, 'success');
                    // 更新本地状态 (注意：比较时统一转换为字符串)
                    const playbook = playbooks.find(p => String(p.id) === String(playbookId));
                    if (playbook) {
                        playbook.enabled = enabled;
                        updateStats();
                    }
                } else {
                    showAlert(result.error || '操作失败', 'error');
                    // 回滚开关状态
                    const toggle = document.querySelector(`input[data-id="${playbookId}"]`);
                    if (toggle) {
                        toggle.checked = !enabled;
                    }
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
                // 回滚开关状态
                const toggle = document.querySelector(`input[data-id="${playbookId}"]`);
                if (toggle) {
                    toggle.checked = !enabled;
                }
            }
        }
        
        // 更新统计
        function updateStats() {
            const total = playbooks.length;
            const enabled = playbooks.filter(p => p.enabled).length;
            const disabled = total - enabled;
            
            totalCount.textContent = total;
            enabledCount.textContent = enabled;
            disabledCount.textContent = disabled;
        }
        
        // 渲染剧本表格
        function renderPlaybooks() {
            if (playbooks.length === 0) {
                playbooksTable.innerHTML = `
                    <tr>
                        <td colspan="4" class="loading">
                            <div>暂无剧本数据</div>
                        </td>
                    </tr>
                `;
                updatePagination();
                return;
            }
            
            // 计算分页数据
            const totalPages = Math.ceil(playbooks.length / itemsPerPage);
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;
            const currentPlaybooks = playbooks.slice(startIndex, endIndex);
            
            playbooksTable.innerHTML = currentPlaybooks.map(playbook => `
                <tr>
                    <td>
                        <span class="playbook-id" data-id="${playbook.id}">${String(playbook.id)}</span>
                    </td>
                    <td>
                        <div class="playbook-display-name">${playbook.displayName || playbook.name}</div>
                    </td>
                    <td>${formatDate(playbook.syncTime)}</td>
                    <td>
                        <label class="switch">
                            <input type="checkbox" data-id="${playbook.id}" ${playbook.enabled ? 'checked' : ''}>
                            <span class="slider"></span>
                        </label>
                    </td>
                </tr>
            `).join('');
            
            // 绑定开关事件
            playbooksTable.querySelectorAll('input[type="checkbox"]').forEach(toggle => {
                toggle.addEventListener('change', (e) => {
                    const playbookId = e.target.dataset.id; // 保持字符串格式避免精度丢失
                    const enabled = e.target.checked;
                    togglePlaybook(playbookId, enabled);
                });
            });
            
            // 绑定剧本ID点击事件
            playbooksTable.querySelectorAll('.playbook-id').forEach(playbookIdElement => {
                playbookIdElement.addEventListener('click', (e) => {
                    const playbookId = e.target.dataset.id; // 保持字符串格式避免精度丢失
                    showPlaybookDetail(playbookId);
                });
            });
            
            updateStats();
            updatePagination();
        }
        
        // 加载剧本数据
        async function loadPlaybooks() {
            try {
                const response = await apiCall('/api/admin/playbooks');
                if (!response) return;

                const result = await response.json();
                
                if (result.success) {
                    playbooks = result.data;
                    renderPlaybooks();
                } else {
                    showAlert(result.error || '加载剧本数据失败', 'error');
                    playbooksTable.innerHTML = `
                        <tr>
                            <td colspan="4" class="loading">
                                <div>加载失败，请刷新页面重试</div>
                            </td>
                        </tr>
                    `;
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
                playbooksTable.innerHTML = `
                    <tr>
                        <td colspan="4" class="loading">
                            <div>网络错误，请检查连接</div>
                        </td>
                    </tr>
                `;
            }
        }
        
        // 显示剧本详情
        async function showPlaybookDetail(playbookId) {
            const modal = document.getElementById('playbook-modal');
            const modalBody = document.getElementById('modal-body');
            
            modal.style.display = 'block';
            modalBody.innerHTML = '<div class="loading">加载中...</div>';
            
            try {
                const response = await apiCall(`/api/admin/playbooks/${playbookId}`);
                if (!response) {
                    modal.style.display = 'none';
                    return;
                }

                const result = await response.json();
                
                if (result.success) {
                    const playbook = result.data;
                    let params = [];
                    
                    // 解析参数
                    if (playbook.playbookParams) {
                        try {
                            params = JSON.parse(playbook.playbookParams);
                        } catch (e) {
                            console.warn('参数解析失败:', e);
                        }
                    }
                    
                    modalBody.innerHTML = `
                        <div class="detail-section">
                            <div class="detail-label">剧本ID</div>
                            <div class="detail-value">${String(playbook.id)}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">剧本名称</div>
                            <div class="detail-value">${playbook.name}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">显示名称</div>
                            <div class="detail-value">${playbook.displayName || playbook.name}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">分类</div>
                            <div class="detail-value">${playbook.playbookCategory}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">描述</div>
                            <div class="detail-value">${playbook.description || '无描述'}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">创建时间</div>
                            <div class="detail-value">${formatDate(playbook.createTime)}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">更新时间</div>
                            <div class="detail-value">${formatDate(playbook.updateTime)}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">最后同步</div>
                            <div class="detail-value">${formatDate(playbook.syncTime)}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">状态</div>
                            <div class="detail-value">${playbook.enabled ? '已启用' : '已禁用'}</div>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-label">参数信息 (${params.length} 个)</div>
                            <div class="detail-value">
                                ${params.length === 0 ? '无参数' : params.map(param => `
                                    <div class="param-item">
                                        <div class="param-name">
                                            ${param.cefColumn || param.key || '未知参数'}
                                            <span class="param-type">${param.valueType || param.type || 'string'}</span>
                                            ${param.required ? '<span class="param-required">必填</span>' : ''}
                                        </div>
                                        ${param.cefDesc ? `<div class="param-description">${param.cefDesc}</div>` : ''}
                                        ${param.description ? `<div class="param-description">${param.description}</div>` : ''}
                                        ${param.defaultValue ? `<div class="param-description">默认值: ${param.defaultValue}</div>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                } else {
                    modalBody.innerHTML = `<div class="error">加载失败: ${result.error || '未知错误'}</div>`;
                }
            } catch (error) {
                modalBody.innerHTML = `<div class="error">网络错误: ${error.message}</div>`;
            }
        }
        
        // 关闭Modal
        function closeModal() {
            document.getElementById('playbook-modal').style.display = 'none';
        }
        
        // 更新分页信息和控件
        function updatePagination() {
            const totalPages = Math.ceil(playbooks.length / itemsPerPage);
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = Math.min(startIndex + itemsPerPage, playbooks.length);
            
            // 更新分页信息
            if (playbooks.length === 0) {
                paginationInfo.textContent = '显示第 0-0 条，共 0 条';
            } else {
                paginationInfo.textContent = `显示第 ${startIndex + 1}-${endIndex} 条，共 ${playbooks.length} 条`;
            }
            
            // 更新按钮状态
            prevPageBtn.disabled = currentPage === 1;
            nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;
            
            // 生成页码
            renderPageNumbers(totalPages);
        }
        
        // 渲染页码
        function renderPageNumbers(totalPages) {
            pageNumbers.innerHTML = '';
            
            if (totalPages <= 1) {
                return;
            }
            
            const maxVisiblePages = 5;
            let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
            
            if (endPage - startPage < maxVisiblePages - 1) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }
            
            // 显示第一页和省略号
            if (startPage > 1) {
                pageNumbers.appendChild(createPageButton(1));
                if (startPage > 2) {
                    pageNumbers.appendChild(createEllipsis());
                }
            }
            
            // 显示页码
            for (let page = startPage; page <= endPage; page++) {
                pageNumbers.appendChild(createPageButton(page));
            }
            
            // 显示省略号和最后一页
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    pageNumbers.appendChild(createEllipsis());
                }
                pageNumbers.appendChild(createPageButton(totalPages));
            }
        }
        
        // 创建页码按钮
        function createPageButton(page) {
            const button = document.createElement('div');
            button.className = `page-number ${page === currentPage ? 'active' : ''}`;
            button.textContent = page;
            button.onclick = () => goToPage(page);
            return button;
        }
        
        // 创建省略号
        function createEllipsis() {
            const ellipsis = document.createElement('div');
            ellipsis.className = 'page-number ellipsis';
            ellipsis.textContent = '...';
            return ellipsis;
        }
        
        // 跳转到指定页
        function goToPage(page) {
            if (page >= 1 && page <= Math.ceil(playbooks.length / itemsPerPage)) {
                currentPage = page;
                renderPlaybooks();
            }
        }
        
        // 点击Modal背景关闭
        function setupModalEvents() {
            const modal = document.getElementById('playbook-modal');
            const closeBtn = document.getElementById('close-modal-btn');
            
            // 关闭按钮事件
            closeBtn.addEventListener('click', closeModal);
            
            // 点击背景关闭
            modal.addEventListener('click', function(event) {
                if (event.target === modal) {
                    closeModal();
                }
            });
        }
        
        // 密码显示/隐藏功能
        function togglePasswordVisibility(inputId) {
            const input = document.getElementById(inputId);
            const eyeIcon = document.getElementById(inputId + '-eye');
            
            if (input.type === 'password') {
                input.type = 'text';
                eyeIcon.textContent = '🙈';
            } else {
                input.type = 'password';
                eyeIcon.textContent = '👁️';
            }
        }
        
        // 测试连接功能
        async function testConnection() {
            const testBtn = document.getElementById('test-connection-btn');
            const connectionStatus = document.getElementById('connection-status');
            
            testBtn.disabled = true;
            testBtn.textContent = '测试中...';
            connectionStatus.textContent = '测试中...';
            connectionStatus.className = 'status-warning';
            
            try {
                const response = await apiCall('/api/admin/config/test', {
                    method: 'POST',
                    body: JSON.stringify({}) // 发送空对象，使用当前数据库配置
                });

                if (!response) return;
                
                const data = await response.json();
                
                if (data.success) {
                    connectionStatus.textContent = '连接成功';
                    connectionStatus.className = 'status-success';
                    showAlert('API连接测试成功！', 'success');
                } else {
                    connectionStatus.textContent = '连接失败';
                    connectionStatus.className = 'status-error';
                    showAlert(`连接测试失败: ${data.message}`, 'error');
                }
            } catch (error) {
                connectionStatus.textContent = '连接失败';
                connectionStatus.className = 'status-error';
                showAlert(`连接测试失败: ${error.message}`, 'error');
            }
            
            testBtn.disabled = false;
            testBtn.textContent = '测试连接';
        }
        
        // 保存配置功能
        async function saveConfiguration() {
            const saveBtn = document.getElementById('save-config-btn');
            const configValid = document.getElementById('config-valid');
            const configUpdated = document.getElementById('config-updated');
            
            saveBtn.disabled = true;
            saveBtn.textContent = '保存中...';
            
            // 收集配置数据
            const apiUrl = document.getElementById('soar-api-url').value.trim();
            const apiToken = document.getElementById('soar-api-token').value.trim();
            const timeout = parseInt(document.getElementById('soar-timeout').value);
            const syncInterval = parseInt(document.getElementById('sync-interval').value);

            // 收集标签
            const labelElements = document.querySelectorAll('.label-tag .label-name');
            const labels = Array.from(labelElements).map(el => el.textContent.trim()).filter(label => label);

            // 构建配置数据
            const configData = {
                soar_api_url: apiUrl,
                soar_timeout: timeout,
                sync_interval: syncInterval,
                soar_labels: labels
            };
            
            // 检查Token是否被修改（如果不是打码格式，说明用户输入了新Token）
            if (!apiToken.includes('***')) {
                configData.soar_api_token = apiToken;
            }
            // 如果是打码格式，则不包含Token字段，后端会保持原有Token
            
            // 验证必填项
            if (!apiUrl || !apiToken || !timeout || labels.length === 0) {
                showAlert('请填写所有必填项并至少添加一个标签', 'error');
                saveBtn.disabled = false;
                saveBtn.textContent = '保存配置';
                return;
            }
            
            try {
                const response = await apiCall('/api/admin/config', {
                    method: 'POST',
                    body: JSON.stringify(configData)
                });

                if (!response) return;
                
                const data = await response.json();
                
                if (data.success) {
                    configValid.textContent = '配置有效';
                    configValid.className = 'status-success';
                    configUpdated.textContent = new Date().toLocaleString('zh-CN');
                    showAlert('配置保存成功！', 'success');
                } else {
                    configValid.textContent = '配置无效';
                    configValid.className = 'status-error';
                    showAlert(`配置保存失败: ${data.message}`, 'error');
                }
            } catch (error) {
                configValid.textContent = '配置无效';
                configValid.className = 'status-error';
                showAlert(`配置保存失败: ${error.message}`, 'error');
            }
            
            saveBtn.disabled = false;
            saveBtn.textContent = '保存配置';
        }
        
        // 标签管理功能
        function addLabel() {
            const labelInput = document.getElementById('label-input');
            const labelsList = document.getElementById('labels-list');
            const labelName = labelInput.value.trim();
            
            if (!labelName) {
                showAlert('请输入标签名称', 'warning');
                return;
            }
            
            // 检查重复
            const existingLabels = Array.from(document.querySelectorAll('.label-tag .label-name'))
                .map(el => el.textContent.trim());
            
            if (existingLabels.includes(labelName)) {
                showAlert('标签已存在', 'warning');
                return;
            }
            
            // 创建标签元素
            const labelElement = document.createElement('div');
            labelElement.className = 'label-tag';
            labelElement.innerHTML = `
                <span class="label-name">${labelName}</span>
                <button type="button" class="label-remove" onclick="this.parentElement.remove()">×</button>
            `;
            
            labelsList.appendChild(labelElement);
            labelInput.value = '';
        }
        
        // 初始化
        // 加载系统配置
        async function loadSystemConfig() {
            try {
                const response = await apiCall('/api/admin/config');
                if (!response) return;

                const data = await response.json();
                
                if (data.success && data.data) {
                    // 填充表单字段
                    document.getElementById('soar-api-url').value = data.data.soar_api_url || '';
                    document.getElementById('soar-api-token').value = data.data.soar_api_token || '';
                    document.getElementById('soar-timeout').value = data.data.soar_timeout || 30;
                    document.getElementById('sync-interval').value = data.data.sync_interval || 14400;
                    
                    // 填充标签列表
                    const labelsList = document.getElementById('labels-list');
                    labelsList.innerHTML = '';
                    
                    const labels = data.data.soar_labels && Array.isArray(data.data.soar_labels) 
                        ? data.data.soar_labels 
                        : ['MCP']; // 默认显示MCP标签
                    
                    labels.forEach(label => {
                        const labelElement = document.createElement('div');
                        labelElement.className = 'label-tag';
                        labelElement.innerHTML = `
                            <span class="label-name">${label}</span>
                            <button type="button" class="label-remove" onclick="this.parentElement.remove()">×</button>
                        `;
                        labelsList.appendChild(labelElement);
                    });
                }
            } catch (error) {
                console.error('加载系统配置失败:', error);
                showAlert('加载系统配置失败', 'error');
                
                // 即使加载失败，也显示默认的MCP标签
                const labelsList = document.getElementById('labels-list');
                labelsList.innerHTML = '';
                const labelElement = document.createElement('div');
                labelElement.className = 'label-tag';
                labelElement.innerHTML = `
                    <span class="label-name">MCP</span>
                    <button type="button" class="label-remove" onclick="this.parentElement.remove()">×</button>
                `;
                labelsList.appendChild(labelElement);
            }
        }

        // Token管理功能
        let tokens = [];

        // 加载Token列表
        async function loadTokens() {
            try {
                const response = await apiCall('/api/admin/tokens');
                if (!response) return;

                const result = await response.json();

                if (result.success) {
                    tokens = result.data;
                    renderTokens();
                } else {
                    showAlert(result.error || '加载Token数据失败', 'error');
                    document.getElementById('tokens-tbody').innerHTML = `
                        <tr>
                            <td colspan="7" class="loading">
                                <div>加载失败，请刷新页面重试</div>
                            </td>
                        </tr>
                    `;
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
                document.getElementById('tokens-tbody').innerHTML = `
                    <tr>
                        <td colspan="7" class="loading">
                            <div>网络错误，请检查连接</div>
                        </td>
                    </tr>
                `;
            }
        }

        // 渲染Token表格
        function renderTokens() {
            const tokensTable = document.getElementById('tokens-tbody');

            if (tokens.length === 0) {
                tokensTable.innerHTML = `
                    <tr>
                        <td colspan="7" class="loading">
                            <div>暂无Token数据</div>
                        </td>
                    </tr>
                `;
                return;
            }

            tokensTable.innerHTML = tokens.map(token => {
                const isExpired = token.expires_at && new Date(token.expires_at) < new Date();
                const maskedToken = token.token.substring(0, 8) + '***' + token.token.substring(token.token.length - 4);

                return `
                    <tr>
                        <td>${token.name}</td>
                        <td>
                            <span class="playbook-id" style="font-size: 0.8rem; cursor: default;">${maskedToken}</span>
                        </td>
                        <td style="white-space: nowrap; font-size: 0.85rem;">${formatDate(token.created_at)}</td>
                        <td style="white-space: nowrap; font-size: 0.85rem;">${token.expires_at ? formatDate(token.expires_at) : '永不过期'}</td>
                        <td style="white-space: nowrap; font-size: 0.85rem;">${formatDate(token.last_used_at)}</td>
                        <td>
                            <span style="color: ${isExpired ? '#e53e3e' : (token.is_active ? '#48bb78' : '#cbd5e0')}">
                                ${isExpired ? '已过期' : (token.is_active ? '活跃' : '禁用')}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;"
                                    onclick="deleteToken(${token.id})">删除</button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // 显示创建Token模态框
        function showCreateTokenModal() {
            document.getElementById('create-token-modal').style.display = 'block';
            document.getElementById('token-name').value = '';
            document.getElementById('token-expires').value = '';
        }

        // 关闭创建Token模态框
        function closeCreateTokenModal() {
            document.getElementById('create-token-modal').style.display = 'none';
        }

        // 创建Token
        async function createToken() {
            const name = document.getElementById('token-name').value.trim();
            const expiresInDays = document.getElementById('token-expires').value;

            if (!name) {
                showAlert('请输入Token名称', 'error');
                return;
            }

            try {
                const response = await apiCall('/api/admin/tokens', {
                    method: 'POST',
                    body: JSON.stringify({
                        name: name,
                        expires_in_days: expiresInDays ? parseInt(expiresInDays) : null
                    })
                });

                if (!response) return;

                const result = await response.json();

                if (result.success) {
                    closeCreateTokenModal();

                    // 显示新创建的Token值
                    document.getElementById('new-token-value').value = result.token;
                    document.getElementById('show-token-modal').style.display = 'block';

                    // 重新加载Token列表
                    loadTokens();
                    showAlert('Token创建成功！', 'success');
                } else {
                    showAlert(result.error || 'Token创建失败', 'error');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
            }
        }

        // 关闭显示Token值模态框
        function closeShowTokenModal() {
            document.getElementById('show-token-modal').style.display = 'none';
            document.getElementById('new-token-value').value = '';
        }

        // 复制Token到剪贴板
        async function copyTokenToClipboard() {
            const tokenInput = document.getElementById('new-token-value');
            try {
                await navigator.clipboard.writeText(tokenInput.value);
                showAlert('Token已复制到剪贴板', 'success');
            } catch (error) {
                // 兼容旧浏览器
                tokenInput.select();
                document.execCommand('copy');
                showAlert('Token已复制到剪贴板', 'success');
            }
        }

        // 删除Token
        async function deleteToken(tokenId) {
            if (!confirm('确定要删除这个Token吗？删除后无法恢复！')) {
                return;
            }

            try {
                const response = await apiCall(`/api/admin/tokens/${tokenId}`, {
                    method: 'DELETE'
                });

                if (!response) return;

                const result = await response.json();

                if (result.success) {
                    showAlert('Token删除成功', 'success');
                    loadTokens(); // 重新加载Token列表
                } else {
                    showAlert(result.error || 'Token删除失败', 'error');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'error');
            }
        }

        // 将refreshStats定义为全局函数
        function refreshStats() {
            // 获取所有统计信息（包括剧本和应用统计）
            apiCall('/api/admin/stats')
                .then(response => {
                    if (!response) return;
                    return response.json();
                })
                .then(data => {
                    if (!data) return;
                    if (data.success && data.stats) {
                        // 更新剧本统计
                        document.getElementById('total-playbooks').textContent = data.stats.total_playbooks || '-';
                        document.getElementById('enabled-playbooks').textContent = data.stats.enabled_playbooks || '-';
                        document.getElementById('disabled-playbooks').textContent = data.stats.disabled_playbooks || '-';
                        
                        // 更新应用统计
                        document.getElementById('total-apps').textContent = data.stats.total_apps || '-';
                        
                        // 更新最后同步时间
                        if (data.stats.last_sync_time) {
                            const lastSync = new Date(data.stats.last_sync_time).toLocaleString('zh-CN');
                            document.getElementById('last-sync').textContent = lastSync;
                        }
                    }
                })
                .catch(error => console.error('Error fetching stats:', error));
        }
        
        // Tab切换功能
        function showTab(tabName) {
            // 隐藏所有section
            document.getElementById('playbooks-section').style.display = 'none';
            document.getElementById('tokens-section').style.display = 'none';
            document.getElementById('config-section').style.display = 'none';
            document.getElementById('stats-section').style.display = 'none';

            // 移除所有导航项的active类
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });

            // 显示对应的section
            if (tabName === 'playbooks') {
                document.getElementById('playbooks-section').style.display = 'block';
                document.getElementById('nav-playbooks').classList.add('active');
            } else if (tabName === 'tokens') {
                document.getElementById('tokens-section').style.display = 'block';
                document.getElementById('nav-tokens').classList.add('active');
                loadTokens(); // 加载Token列表
            } else if (tabName === 'config') {
                document.getElementById('config-section').style.display = 'block';
                document.getElementById('nav-config').classList.add('active');
                loadSystemConfig(); // 加载系统配置
            } else if (tabName === 'stats') {
                document.getElementById('stats-section').style.display = 'block';
                document.getElementById('nav-stats').classList.add('active');
                refreshStats(); // 刷新统计信息
            }
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            // 页面加载时检查认证
            if (!checkAuth()) {
                return; // checkAuth会处理跳转
            }

            // 添加导航事件监听器
            document.getElementById('nav-playbooks').addEventListener('click', (e) => {
                e.preventDefault();
                showTab('playbooks');
            });

            document.getElementById('nav-tokens').addEventListener('click', (e) => {
                e.preventDefault();
                showTab('tokens');
            });

            document.getElementById('nav-config').addEventListener('click', (e) => {
                e.preventDefault();
                showTab('config');
            });

            document.getElementById('nav-stats').addEventListener('click', (e) => {
                e.preventDefault();
                showTab('stats');
            });

            // 注销按钮事件监听器
            document.getElementById('logout-btn').addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
            setupModalEvents();
            
            // 设置分页按钮事件
            prevPageBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    goToPage(currentPage - 1);
                }
            });
            
            nextPageBtn.addEventListener('click', () => {
                const totalPages = Math.ceil(playbooks.length / itemsPerPage);
                if (currentPage < totalPages) {
                    goToPage(currentPage + 1);
                }
            });
            
            loadPlaybooks();
            
            // 定期刷新（每30秒）
            setInterval(loadPlaybooks, 30000);
        });
