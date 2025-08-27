// Network Control JavaScript

let routers = [];
let clients = [];
let networkStats = {};

// Load routers
async function loadRouters() {
    try {
        showLoading();
        const response = await fetch('/api/control/routers', {
            headers: {
                'Authorization': 'Bearer ' + getToken()
            }
        });
        
        if (response.ok) {
            routers = await response.json();
            displayRouters();
            updateRouterStats();
        } else {
            showError('فشل في تحميل بيانات الراوترات');
        }
    } catch (error) {
        showError('حدث خطأ في تحميل الراوترات: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display routers in table
function displayRouters() {
    const tbody = document.getElementById('routers-tbody');
    tbody.innerHTML = '';
    
    routers.forEach(router => {
        const row = document.createElement('tr');
        
        const statusClass = router.status === 'connected' ? 'status-success' : 
                          router.status === 'disconnected' ? 'status-warning' : 'status-error';
        
        const statusText = router.status === 'connected' ? 'متصل' : 
                          router.status === 'disconnected' ? 'غير متصل' : 'خطأ';
        
        const lastSeen = router.last_seen ? 
            new Date(router.last_seen).toLocaleString('ar-SA') : 'غير متاح';
        
        row.innerHTML = `
            <td>${router.name}</td>
            <td>${router.brand} ${router.model || ''}</td>
            <td>${router.ip_address}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${lastSeen}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-info" onclick="testRouterConnection(${router.id})" title="اختبار الاتصال">
                        <i data-feather="wifi"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="editRouter(${router.id})" title="تعديل">
                        <i data-feather="edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteRouter(${router.id})" title="حذف">
                        <i data-feather="trash-2"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    feather.replace();
}

// Load connected clients
async function loadClients() {
    try {
        const response = await fetch('/api/control/network/clients', {
            headers: {
                'Authorization': 'Bearer ' + getToken()
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            clients = data.clients;
            displayClients();
            updateClientStats(data.connected_clients);
        } else {
            showError('فشل في تحميل بيانات المستخدمين');
        }
    } catch (error) {
        showError('حدث خطأ في تحميل بيانات المستخدمين: ' + error.message);
    }
}

// Display clients in table
function displayClients() {
    const tbody = document.getElementById('clients-tbody');
    tbody.innerHTML = '';
    
    clients.forEach(client => {
        const row = document.createElement('tr');
        
        const remainingTime = client.remaining_minutes > 60 ? 
            Math.floor(client.remaining_minutes / 60) + ' ساعة ' + (client.remaining_minutes % 60) + ' دقيقة' :
            client.remaining_minutes + ' دقيقة';
        
        const dataUsed = client.data_used_mb ? 
            client.data_used_mb.toFixed(2) + ' MB' + 
            (client.data_limit_mb ? ' / ' + client.data_limit_mb + ' MB' : ' / غير محدود') :
            '0 MB';
        
        row.innerHTML = `
            <td>${client.voucher_code}</td>
            <td>${client.client_mac || 'غير متاح'}</td>
            <td>${client.client_ip || 'غير متاح'}</td>
            <td>${new Date(client.session_start).toLocaleString('ar-SA')}</td>
            <td>${remainingTime}</td>
            <td>${dataUsed}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-info" onclick="viewClientDetails('${client.voucher_code}')" title="التفاصيل">
                        <i data-feather="info"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="disconnectClient('${client.voucher_code}')" title="قطع الاتصال">
                        <i data-feather="x-circle"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    feather.replace();
}

// Test router connection
async function testRouterConnection(routerId) {
    try {
        showLoading();
        const response = await fetch(`/api/control/routers/${routerId}/test`, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + getToken()
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.connected) {
                showSuccess(data.message);
            } else {
                showWarning(data.message);
            }
            loadRouters(); // Refresh router list
        } else {
            showError(data.error || 'فشل في اختبار الاتصال');
        }
    } catch (error) {
        showError('حدث خطأ في اختبار الاتصال: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Add new router
async function addRouter() {
    const name = document.getElementById('router-name').value;
    const brand = document.getElementById('router-brand').value;
    const model = document.getElementById('router-model').value;
    const ip_address = document.getElementById('router-ip').value;
    const username = document.getElementById('router-username').value;
    const password = document.getElementById('router-password').value;
    const api_port = document.getElementById('router-port').value;
    
    if (!name || !brand || !ip_address || !username || !password) {
        showError('يرجى ملء جميع الحقول المطلوبة');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch('/api/control/routers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getToken()
            },
            body: JSON.stringify({
                name,
                brand,
                model,
                ip_address,
                username,
                password,
                api_port: api_port ? parseInt(api_port) : null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            hideAddRouterModal();
            loadRouters();
            document.getElementById('add-router-form').reset();
        } else {
            showError(data.error || 'فشل في إضافة الراوتر');
        }
    } catch (error) {
        showError('حدث خطأ في إضافة الراوتر: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Create voucher batch with advanced options
async function createVoucherBatch() {
    const quantity = parseInt(document.getElementById('batch-quantity').value);
    const duration_hours = parseInt(document.getElementById('batch-duration').value);
    const data_limit_mb = document.getElementById('batch-data-limit').value;
    const speed_limit_kbps = document.getElementById('batch-speed-limit').value;
    const voucher_type = document.getElementById('batch-voucher-type').value;
    const price = parseFloat(document.getElementById('batch-price').value);
    const voucher_expires_days = parseInt(document.getElementById('batch-expires-days').value);
    
    if (!quantity || !duration_hours || quantity <= 0 || quantity > 1000) {
        showError('يرجى إدخال عدد صحيح للكروت (1-1000)');
        return;
    }
    
    try {
        showLoading();
        const requestData = {
            quantity,
            duration_hours,
            voucher_type,
            price,
            voucher_expires_days,
            base_url: window.location.origin
        };
        
        if (data_limit_mb) requestData.data_limit_mb = parseInt(data_limit_mb);
        if (speed_limit_kbps) requestData.speed_limit_kbps = parseInt(speed_limit_kbps);
        
        const response = await fetch('/api/control/vouchers/create_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getToken()
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            
            // Show batch details
            const batchInfo = `
                <div class="batch-info">
                    <h4>تفاصيل الدفعة</h4>
                    <p><strong>رقم الدفعة:</strong> ${data.batch_id}</p>
                    <p><strong>عدد الكروت:</strong> ${quantity}</p>
                    <p><strong>مدة كل كارت:</strong> ${duration_hours} ساعة</p>
                    ${data_limit_mb ? `<p><strong>حد البيانات:</strong> ${data_limit_mb} ميجابايت</p>` : ''}
                    ${speed_limit_kbps ? `<p><strong>حد السرعة:</strong> ${speed_limit_kbps} كيلوبايت/ثانية</p>` : ''}
                </div>
            `;
            
            showInfo('تم إنشاء الكروت بنجاح!<br>' + batchInfo);
            
            // Reset form
            document.getElementById('batch-quantity').value = 10;
            document.getElementById('batch-duration').value = 24;
            document.getElementById('batch-data-limit').value = '';
            document.getElementById('batch-speed-limit').value = '';
            document.getElementById('batch-voucher-type').value = 'standard';
            document.getElementById('batch-price').value = 0;
            
        } else {
            showError(data.error || 'فشل في إنشاء الكروت');
        }
    } catch (error) {
        showError('حدث خطأ في إنشاء الكروت: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Disconnect client
async function disconnectClient(voucherCode) {
    if (!confirm('هل تريد قطع اتصال هذا المستخدم؟')) return;
    
    try {
        showLoading();
        const response = await fetch(`/api/control/vouchers/${voucherCode}/disconnect`, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + getToken()
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message);
            loadClients(); // Refresh clients list
        } else {
            showError(data.error || 'فشل في قطع الاتصال');
        }
    } catch (error) {
        showError('حدث خطأ في قطع الاتصال: ' + error.message);
    } finally {
        hideLoading();
    }
}

// View client details
async function viewClientDetails(voucherCode) {
    try {
        const response = await fetch(`/api/control/vouchers/${voucherCode}/usage`, {
            headers: {
                'Authorization': 'Bearer ' + getToken()
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            const details = `
                <div class="client-details">
                    <h4>تفاصيل الاتصال</h4>
                    <p><strong>كود الكارت:</strong> ${data.code}</p>
                    <p><strong>الحالة:</strong> ${data.status === 'used' ? 'نشط' : data.status}</p>
                    <p><strong>البيانات المستخدمة:</strong> ${data.data_used_mb.toFixed(2)} MB</p>
                    ${data.data_limit_mb ? `<p><strong>حد البيانات:</strong> ${data.data_limit_mb} MB</p>` : ''}
                    ${data.remaining_data !== null ? `<p><strong>البيانات المتبقية:</strong> ${data.remaining_data.toFixed(2)} MB</p>` : ''}
                    ${data.remaining_time !== null ? `<p><strong>الوقت المتبقي:</strong> ${data.remaining_time} دقيقة</p>` : ''}
                    ${data.session_start ? `<p><strong>بداية الجلسة:</strong> ${new Date(data.session_start).toLocaleString('ar-SA')}</p>` : ''}
                    ${data.session_end ? `<p><strong>نهاية الجلسة:</strong> ${new Date(data.session_end).toLocaleString('ar-SA')}</p>` : ''}
                </div>
            `;
            
            showInfo(details);
        } else {
            showError('فشل في تحميل تفاصيل المستخدم');
        }
    } catch (error) {
        showError('حدث خطأ في تحميل التفاصيل: ' + error.message);
    }
}

// Load network statistics
async function loadNetworkStats() {
    try {
        const response = await fetch('/api/stats/dashboard', {
            headers: {
                'Authorization': 'Bearer ' + getToken()
            }
        });
        
        if (response.ok) {
            networkStats = await response.json();
            updateNetworkStats();
        }
    } catch (error) {
        console.error('Error loading network stats:', error);
    }
}

// Update statistics display
function updateNetworkStats() {
    document.getElementById('active-sessions').textContent = 
        clients.filter(c => c.remaining_minutes > 0).length;
    
    const totalDataUsed = clients.reduce((sum, client) => sum + (client.data_used_mb || 0), 0);
    document.getElementById('data-usage').textContent = totalDataUsed.toFixed(2) + ' MB';
}

function updateRouterStats() {
    const connectedRouters = routers.filter(r => r.status === 'connected').length;
    document.getElementById('connected-routers').textContent = connectedRouters;
}

function updateClientStats(connectedCount) {
    document.getElementById('active-clients').textContent = connectedCount;
}

// Refresh functions
function refreshAll() {
    loadRouters();
    loadClients();
    loadNetworkStats();
}

function refreshClients() {
    loadClients();
}

// Modal functions
function showAddRouterModal() {
    document.getElementById('add-router-modal').style.display = 'block';
}

function hideAddRouterModal() {
    document.getElementById('add-router-modal').style.display = 'none';
}

// Auto-refresh every 30 seconds
setInterval(() => {
    loadClients();
    loadNetworkStats();
}, 30000);

// Auto-refresh router status every 2 minutes
setInterval(() => {
    loadRouters();
}, 120000);