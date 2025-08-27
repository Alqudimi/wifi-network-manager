// Dashboard specific JavaScript
class Dashboard {
    constructor() {
        this.statsRefreshInterval = null;
        this.init();
    }

    init() {
        this.loadStats();
        this.startStatsRefresh();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadStats();
            });
        }
    }

    async loadStats() {
        try {
            const response = await app.apiCall('/stats/dashboard');
            this.updateStatsDisplay(response);
            this.updateRecentActivity(response.recent_vouchers || []);
        } catch (error) {
            console.error('Error loading stats:', error);
            app.showAlert('خطأ في تحميل الإحصائيات', 'error');
        }
    }

    updateStatsDisplay(stats) {
        // Update stat cards
        const statElements = {
            'total-vouchers': stats.total_vouchers || 0,
            'active-vouchers': stats.active_vouchers || 0,
            'used-vouchers': stats.used_vouchers || 0,
            'total-networks': stats.total_networks || 0,
            'total-routers': stats.total_routers || 0
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value.toLocaleString('ar-EG');
            }
        });

        // Update usage percentage
        const totalVouchers = stats.total_vouchers || 0;
        const usedVouchers = stats.used_vouchers || 0;
        const usagePercentage = totalVouchers > 0 ? 
            Math.round((usedVouchers / totalVouchers) * 100) : 0;

        const usageElement = document.getElementById('usage-percentage');
        if (usageElement) {
            usageElement.textContent = `${usagePercentage}%`;
        }

        // Update progress bar if exists
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${usagePercentage}%`;
        }
    }

    updateRecentActivity(recentVouchers) {
        const activityContainer = document.getElementById('recent-activity');
        if (!activityContainer) return;

        if (recentVouchers.length === 0) {
            activityContainer.innerHTML = '<p class="text-secondary">لا توجد أنشطة حديثة</p>';
            return;
        }

        const activityHTML = recentVouchers.map(voucher => `
            <div class="activity-item">
                <div class="activity-content">
                    <div class="activity-title">كرت: ${voucher.code}</div>
                    <div class="activity-time">${app.formatDate(voucher.created_at)}</div>
                </div>
                <div class="activity-status">
                    <span class="badge ${this.getStatusBadgeClass(voucher.status)}">
                        ${this.getStatusText(voucher.status)}
                    </span>
                </div>
            </div>
        `).join('');

        activityContainer.innerHTML = activityHTML;
    }

    getStatusBadgeClass(status) {
        const classes = {
            'active': 'badge-success',
            'used': 'badge-info',
            'expired': 'badge-warning',
            'disabled': 'badge-error'
        };
        return classes[status] || 'badge-info';
    }

    getStatusText(status) {
        const statuses = {
            'active': 'نشط',
            'used': 'مستخدم',
            'expired': 'منتهي',
            'disabled': 'معطل'
        };
        return statuses[status] || status;
    }

    startStatsRefresh() {
        // Refresh stats every 30 seconds
        this.statsRefreshInterval = setInterval(() => {
            this.loadStats();
        }, 30000);
    }

    stopStatsRefresh() {
        if (this.statsRefreshInterval) {
            clearInterval(this.statsRefreshInterval);
            this.statsRefreshInterval = null;
        }
    }

    destroy() {
        this.stopStatsRefresh();
    }
}

// Chart functionality (if Chart.js is available)
class DashboardCharts {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        if (typeof Chart !== 'undefined') {
            this.createUsageChart();
            this.createActivityChart();
        }
    }

    async createUsageChart() {
        const canvas = document.getElementById('usage-chart');
        if (!canvas) return;

        try {
            const response = await app.apiCall('/stats/dashboard');
            
            const ctx = canvas.getContext('2d');
            this.charts.usage = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['كروت نشطة', 'كروت مستخدمة', 'كروت منتهية'],
                    datasets: [{
                        data: [
                            response.active_vouchers || 0,
                            response.used_vouchers || 0,
                            response.expired_vouchers || 0
                        ],
                        backgroundColor: [
                            '#10b981',
                            '#3b82f6',
                            '#f59e0b'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                font: {
                                    family: 'Inter'
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating usage chart:', error);
        }
    }

    async createActivityChart() {
        const canvas = document.getElementById('activity-chart');
        if (!canvas) return;

        try {
            // This would need a new API endpoint for time-series data
            const ctx = canvas.getContext('2d');
            this.charts.activity = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد'],
                    datasets: [{
                        label: 'الكروت المستخدمة',
                        data: [12, 19, 15, 25, 22, 30, 28],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                font: {
                                    family: 'Inter'
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                font: {
                                    family: 'Inter'
                                }
                            }
                        },
                        x: {
                            ticks: {
                                font: {
                                    family: 'Inter'
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating activity chart:', error);
        }
    }

    updateCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.update) {
                chart.update();
            }
        });
    }

    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.dashboard-page')) {
        window.dashboard = new Dashboard();
        window.dashboardCharts = new DashboardCharts();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
    if (window.dashboardCharts) {
        window.dashboardCharts.destroy();
    }
});
