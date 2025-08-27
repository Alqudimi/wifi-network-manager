// Main application JavaScript
class WiFiManager {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('auth_token');
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuth();
    }

    setupEventListeners() {
        // Mobile menu toggle
        const menuToggle = document.getElementById('menu-toggle');
        const sidebar = document.querySelector('.sidebar');
        
        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }

        // Global logout
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('logout-btn')) {
                this.logout();
            }
        });

        // Modal close functionality
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close') || 
                e.target.classList.contains('modal')) {
                this.closeModals();
            }
        });

        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('ajax-form')) {
                e.preventDefault();
                this.handleFormSubmit(e.target);
            }
        });
    }

    async checkAuth() {
        if (!this.token) {
            this.redirectToLogin();
            return;
        }

        try {
            const response = await this.apiCall('/auth/verify', 'POST');
            if (response.valid) {
                this.currentUser = response.user;
                this.updateUserInterface();
            } else {
                this.logout();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            this.logout();
        }
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (data) {
            config.body = JSON.stringify(data);
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async login(username, password) {
        try {
            const response = await this.apiCall('/auth/login', 'POST', {
                username,
                password
            });

            if (response.token) {
                this.token = response.token;
                localStorage.setItem('auth_token', this.token);
                this.currentUser = response.user;
                window.location.href = '/';
                return { success: true };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async logout() {
        try {
            await this.apiCall('/auth/logout', 'POST');
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.token = null;
            this.currentUser = null;
            localStorage.removeItem('auth_token');
            this.redirectToLogin();
        }
    }

    redirectToLogin() {
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }

    updateUserInterface() {
        // Update user info in header
        const userElements = document.querySelectorAll('.user-name');
        userElements.forEach(el => {
            el.textContent = this.currentUser.username;
        });

        const roleElements = document.querySelectorAll('.user-role');
        roleElements.forEach(el => {
            el.textContent = this.getRoleText(this.currentUser.role);
        });

        // Hide admin-only elements for non-admins
        if (this.currentUser.role !== 'admin') {
            document.querySelectorAll('.admin-only').forEach(el => {
                el.style.display = 'none';
            });
        }
    }

    getRoleText(role) {
        const roles = {
            'admin': 'مدير',
            'operator': 'مشغل',
            'user': 'مستخدم'
        };
        return roles[role] || role;
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        const container = document.querySelector('.main-content');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    }

    closeModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    async handleFormSubmit(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        const endpoint = form.dataset.endpoint;
        const method = form.dataset.method || 'POST';

        try {
            const response = await this.apiCall(endpoint, method, data);
            
            if (response.message) {
                this.showAlert(response.message, 'success');
            }

            // Close modal if form is in a modal
            const modal = form.closest('.modal');
            if (modal) {
                modal.classList.remove('active');
            }

            // Reload data if needed
            if (typeof window.loadData === 'function') {
                window.loadData();
            }

        } catch (error) {
            this.showAlert(error.message, 'error');
        }
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-EG', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showAlert('تم النسخ للحافظة', 'success');
        }).catch(() => {
            this.showAlert('فشل في النسخ', 'error');
        });
    }
}

// Initialize app
const app = new WiFiManager();

// Utility functions
function confirmDelete(message = 'هل أنت متأكد من الحذف؟') {
    return confirm(message);
}

function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
}

function hideLoading(element, originalContent) {
    if (element) {
        element.innerHTML = originalContent;
    }
}

// Export for global use
window.WiFiManager = WiFiManager;
window.app = app;
