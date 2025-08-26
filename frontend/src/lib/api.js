// مكتبة للتعامل مع API الخاص بالواجهة الخلفية

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  // تعيين التوكن
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  // الحصول على التوكن
  getToken() {
    return this.token || localStorage.getItem('access_token');
  }

  // إنشاء headers للطلبات
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  // طلب HTTP عام
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'حدث خطأ في الطلب');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // طلبات GET
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  // طلبات POST
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // طلبات PUT
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // طلبات DELETE
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // === Auth APIs ===
  
  async login(username, password) {
    const response = await this.post('/auth/login', { username, password });
    if (response.access_token) {
      this.setToken(response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
    }
    return response;
  }

  async register(userData) {
    const response = await this.post('/auth/register', userData);
    if (response.access_token) {
      this.setToken(response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
    }
    return response;
  }

  async logout() {
    try {
      await this.post('/auth/logout');
    } finally {
      this.setToken(null);
      localStorage.removeItem('refresh_token');
    }
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('لا يوجد refresh token');
    }

    const response = await this.post('/auth/refresh', { refresh_token: refreshToken });
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    return response;
  }

  async getProfile() {
    return this.get('/auth/profile');
  }

  async updateProfile(data) {
    return this.put('/auth/profile', data);
  }

  async changePassword(currentPassword, newPassword) {
    return this.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  // === Voucher APIs ===

  async createBatch(batchData) {
    return this.post('/vouchers/batches', batchData);
  }

  async getBatches(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/vouchers/batches${queryString ? '?' + queryString : ''}`);
  }

  async getBatch(batchId) {
    return this.get(`/vouchers/batches/${batchId}`);
  }

  async getBatchVouchers(batchId, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/vouchers/batches/${batchId}/vouchers${queryString ? '?' + queryString : ''}`);
  }

  async printBatch(batchId, options = {}) {
    const response = await fetch(`${this.baseURL}/vouchers/batches/${batchId}/print`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(options),
    });

    if (!response.ok) {
      throw new Error('فشل في طباعة الدفعة');
    }

    return response.blob();
  }

  async exportBatch(batchId) {
    const response = await fetch(`${this.baseURL}/vouchers/batches/${batchId}/export`, {
      method: 'POST',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('فشل في تصدير الدفعة');
    }

    return response.blob();
  }

  async redeemVoucher(code, additionalData = {}) {
    return this.post('/vouchers/redeem', { code, ...additionalData });
  }

  async checkVoucher(code) {
    return this.post('/vouchers/check', { code });
  }

  async activateVoucher(voucherId) {
    return this.post(`/vouchers/vouchers/${voucherId}/activate`);
  }

  async deactivateVoucher(voucherId) {
    return this.post(`/vouchers/vouchers/${voucherId}/deactivate`);
  }

  async resetVoucher(voucherId) {
    return this.post(`/vouchers/vouchers/${voucherId}/reset`);
  }

  async getSessions(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/vouchers/sessions${queryString ? '?' + queryString : ''}`);
  }

  async terminateSession(sessionId) {
    return this.post(`/vouchers/sessions/${sessionId}/terminate`);
  }

  // === Admin APIs ===

  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.get(`/admin/users${queryString ? '?' + queryString : ''}`);
  }

  async createUser(userData) {
    return this.post('/admin/users', userData);
  }

  async updateUser(userId, userData) {
    return this.put(`/admin/users/${userId}`, userData);
  }

  async deleteUser(userId) {
    return this.delete(`/admin/users/${userId}`);
  }

  async getDashboardStats(days = 30) {
    return this.get(`/admin/dashboard/stats?days=${days}`);
  }

  async getNetworkSettings() {
    return this.get('/admin/network-settings');
  }

  async createNetworkSettings(settingsData) {
    return this.post('/admin/network-settings', settingsData);
  }

  async updateNetworkSettings(settingsId, settingsData) {
    return this.put(`/admin/network-settings/${settingsId}`, settingsData);
  }

  async getRouters() {
    return this.get('/admin/routers');
  }

  async createRouter(routerData) {
    return this.post('/admin/routers', routerData);
  }

  async testRouterConnection(routerId) {
    return this.post(`/admin/routers/${routerId}/test`);
  }

  async getRouterConfiguration(routerId) {
    return this.get(`/admin/routers/${routerId}/configuration`);
  }

  async getUsageReport(days = 30) {
    return this.get(`/admin/reports/usage?days=${days}`);
  }

  // === Health Check ===
  
  async healthCheck() {
    return this.get('/health');
  }

  async getApiInfo() {
    return this.get('/info');
  }
}

// إنشاء مثيل واحد من ApiClient
const apiClient = new ApiClient();

export default apiClient;

