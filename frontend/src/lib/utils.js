import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// تنسيق التاريخ والوقت
export const formatDate = (dateString) => {
  if (!dateString) return 'غير محدد';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('ar-SA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const formatDateTime = (dateString) => {
  if (!dateString) return 'غير محدد';
  
  const date = new Date(dateString);
  return date.toLocaleString('ar-SA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatTime = (dateString) => {
  if (!dateString) return 'غير محدد';
  
  const date = new Date(dateString);
  return date.toLocaleTimeString('ar-SA', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

// تنسيق المدة
export const formatDuration = (minutes) => {
  if (!minutes || minutes === 0) return 'غير محدد';
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (hours === 0) {
    return `${remainingMinutes} دقيقة`;
  } else if (remainingMinutes === 0) {
    return `${hours} ساعة`;
  } else {
    return `${hours} ساعة و ${remainingMinutes} دقيقة`;
  }
};

// تنسيق حجم البيانات
export const formatDataSize = (sizeInMB) => {
  if (!sizeInMB || sizeInMB === 0) return 'غير محدد';
  
  if (sizeInMB < 1024) {
    return `${sizeInMB.toFixed(1)} ميجابايت`;
  } else {
    const sizeInGB = sizeInMB / 1024;
    return `${sizeInGB.toFixed(2)} جيجابايت`;
  }
};

// تنسيق الأرقام
export const formatNumber = (number) => {
  if (number === null || number === undefined) return '0';
  return number.toLocaleString('ar-SA');
};

// تنسيق النسبة المئوية
export const formatPercentage = (value, total) => {
  if (!total || total === 0) return '0%';
  const percentage = (value / total) * 100;
  return `${percentage.toFixed(1)}%`;
};

// التحقق من صحة البريد الإلكتروني
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// تحويل الحالة إلى نص عربي
export const getStatusText = (status) => {
  const statusMap = {
    active: 'نشط',
    inactive: 'غير نشط',
    used: 'مستخدم',
    expired: 'منتهي الصلاحية',
    pending: 'في الانتظار',
    completed: 'مكتمل',
    cancelled: 'ملغي',
  };
  
  return statusMap[status] || status;
};

// تحويل الدور إلى نص عربي
export const getRoleText = (role) => {
  const roleMap = {
    admin: 'مدير',
    operator: 'مشغل',
    user: 'مستخدم',
  };
  
  return roleMap[role] || role;
};

// نسخ النص إلى الحافظة
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback للمتصفحات القديمة
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      return true;
    } catch (err) {
      return false;
    } finally {
      document.body.removeChild(textArea);
    }
  }
};

// تحميل ملف
export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

// تحويل الوقت النسبي (منذ كم من الوقت)
export const timeAgo = (dateString) => {
  if (!dateString) return 'غير محدد';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) {
    return 'منذ لحظات';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `منذ ${minutes} دقيقة`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `منذ ${hours} ساعة`;
  } else if (diffInSeconds < 2592000) {
    const days = Math.floor(diffInSeconds / 86400);
    return `منذ ${days} يوم`;
  } else {
    return formatDate(dateString);
  }
};
