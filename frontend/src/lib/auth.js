// مكتبة إدارة المصادقة والمستخدم

import React from 'react';
import apiClient from './api';

class AuthManager {
  constructor() {
    this.user = null;
    this.isAuthenticated = false;
    this.listeners = [];
  }

  // إضافة مستمع للتغييرات في حالة المصادقة
  addListener(callback) {
    this.listeners.push(callback);
  }

  // إزالة مستمع
  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  // إشعار جميع المستمعين بالتغييرات
  notifyListeners() {
    this.listeners.forEach(callback => callback(this.user, this.isAuthenticated));
  }

  // تسجيل الدخول
  async login(username, password) {
    try {
      const response = await apiClient.login(username, password);
      this.user = response.user;
      this.isAuthenticated = true;
      this.notifyListeners();
      return response;
    } catch (error) {
      this.logout();
      throw error;
    }
  }

  // تسجيل مستخدم جديد
  async register(userData) {
    try {
      const response = await apiClient.register(userData);
      this.user = response.user;
      this.isAuthenticated = true;
      this.notifyListeners();
      return response;
    } catch (error) {
      this.logout();
      throw error;
    }
  }

  // تسجيل الخروج
  async logout() {
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('خطأ في تسجيل الخروج:', error);
    } finally {
      this.user = null;
      this.isAuthenticated = false;
      this.notifyListeners();
    }
  }

  // التحقق من حالة المصادقة
  async checkAuth() {
    const token = apiClient.getToken();
    if (!token) {
      this.logout();
      return false;
    }

    try {
      const response = await apiClient.getProfile();
      this.user = response.user;
      this.isAuthenticated = true;
      this.notifyListeners();
      return true;
    } catch (error) {
      // محاولة تجديد التوكن
      try {
        await apiClient.refreshToken();
        const response = await apiClient.getProfile();
        this.user = response.user;
        this.isAuthenticated = true;
        this.notifyListeners();
        return true;
      } catch (refreshError) {
        this.logout();
        return false;
      }
    }
  }

  // تحديث الملف الشخصي
  async updateProfile(data) {
    try {
      const response = await apiClient.updateProfile(data);
      this.user = response.user;
      this.notifyListeners();
      return response;
    } catch (error) {
      throw error;
    }
  }

  // تغيير كلمة المرور
  async changePassword(currentPassword, newPassword) {
    try {
      const response = await apiClient.changePassword(currentPassword, newPassword);
      // بعد تغيير كلمة المرور، قد نحتاج لتسجيل الدخول مرة أخرى
      return response;
    } catch (error) {
      throw error;
    }
  }

  // التحقق من الصلاحيات
  hasRole(role) {
    return this.user && this.user.role === role;
  }

  isAdmin() {
    return this.hasRole('admin');
  }

  isOperator() {
    return this.hasRole('operator') || this.isAdmin();
  }

  isUser() {
    return this.hasRole('user');
  }

  // الحصول على معلومات المستخدم
  getCurrentUser() {
    return this.user;
  }

  // التحقق من حالة المصادقة
  getIsAuthenticated() {
    return this.isAuthenticated;
  }
}

// إنشاء مثيل واحد من AuthManager
const authManager = new AuthManager();

// Hook للاستخدام في React Components
export const useAuth = () => {
  const [user, setUser] = React.useState(authManager.getCurrentUser());
  const [isAuthenticated, setIsAuthenticated] = React.useState(authManager.getIsAuthenticated());

  React.useEffect(() => {
    const handleAuthChange = (newUser, newIsAuthenticated) => {
      setUser(newUser);
      setIsAuthenticated(newIsAuthenticated);
    };

    authManager.addListener(handleAuthChange);

    // التحقق من حالة المصادقة عند تحميل الصفحة
    authManager.checkAuth();

    return () => {
      authManager.removeListener(handleAuthChange);
    };
  }, []);

  return {
    user,
    isAuthenticated,
    login: authManager.login.bind(authManager),
    register: authManager.register.bind(authManager),
    logout: authManager.logout.bind(authManager),
    updateProfile: authManager.updateProfile.bind(authManager),
    changePassword: authManager.changePassword.bind(authManager),
    hasRole: authManager.hasRole.bind(authManager),
    isAdmin: authManager.isAdmin.bind(authManager),
    isOperator: authManager.isOperator.bind(authManager),
    isUser: authManager.isUser.bind(authManager),
  };
};

export default authManager;

