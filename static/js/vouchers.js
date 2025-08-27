// Vouchers management JavaScript
class VouchersManager {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.currentFilter = {};
        this.selectedVouchers = new Set();
        this.init();
    }

    init() {
        this.loadVouchers();
        this.loadBatches();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Create voucher batch form
        const createForm = document.getElementById('create-voucher-form');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createVoucherBatch();
            });
        }

        // Bulk actions
        const bulkActionBtn = document.getElementById('bulk-action-btn');
        if (bulkActionBtn) {
            bulkActionBtn.addEventListener('click', () => {
                this.showBulkActions();
            });
        }

        // Filters
        const filterForm = document.getElementById('filter-form');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.applyFilters();
            });
        }

        // Clear filters
        const clearFiltersBtn = document.getElementById('clear-filters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Print vouchers
        const printBtn = document.getElementById('print-vouchers');
        if (printBtn) {
            printBtn.addEventListener('click', () => {
                this.printSelectedVouchers();
            });
        }

        // Export vouchers
        const exportBtn = document.getElementById('export-vouchers');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportVouchers();
            });
        }
    }

    async loadVouchers() {
        try {
            showLoading(document.getElementById('vouchers-container'));

            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.itemsPerPage,
                ...this.currentFilter
            });

            const response = await app.apiCall(`/vouchers?${params}`);
            this.displayVouchers(response.vouchers);
            this.updatePagination(response.total, response.pages, response.current_page);

        } catch (error) {
            console.error('Error loading vouchers:', error);
            app.showAlert('خطأ في تحميل الكروت', 'error');
        }
    }

    displayVouchers(vouchers) {
        const container = document.getElementById('vouchers-container');
        if (!container) return;

        if (vouchers.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <p class="text-secondary">لا توجد كروت</p>
                </div>
            `;
            return;
        }

        const vouchersHTML = vouchers.map(voucher => `
            <tr>
                <td>
                    <input type="checkbox" 
                           class="voucher-checkbox" 
                           value="${voucher.id}"
                           ${this.selectedVouchers.has(voucher.id) ? 'checked' : ''}>
                </td>
                <td>
                    <div class="voucher-code" onclick="app.copyToClipboard('${voucher.code}')">
                        ${voucher.code}
                    </div>
                </td>
                <td>${voucher.batch_id || '-'}</td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(voucher.status)}">
                        ${this.getStatusText(voucher.status)}
                    </span>
                </td>
                <td>${voucher.duration_hours} ساعة</td>
                <td>${voucher.data_limit_mb ? voucher.data_limit_mb + ' MB' : 'غير محدود'}</td>
                <td>${app.formatDate(voucher.created_at)}</td>
                <td>${voucher.used_at ? app.formatDate(voucher.used_at) : '-'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" 
                                onclick="vouchers.viewVoucher(${voucher.id})">
                            عرض
                        </button>
                        ${voucher.status === 'active' ? `
                            <button class="btn btn-sm btn-warning" 
                                    onclick="vouchers.editVoucher(${voucher.id})">
                                تعديل
                            </button>
                            <button class="btn btn-sm btn-danger" 
                                    onclick="vouchers.disableVoucher(${voucher.id})">
                                تعطيل
                            </button>
                        ` : ''}
                        ${voucher.qr_code_data ? `
                            <button class="btn btn-sm btn-secondary" 
                                    onclick="vouchers.showQRCode('${voucher.code}', '${voucher.qr_code_data}')">
                                QR
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>
                                <input type="checkbox" id="select-all-vouchers">
                            </th>
                            <th>كود الكرت</th>
                            <th>الدفعة</th>
                            <th>الحالة</th>
                            <th>المدة</th>
                            <th>البيانات</th>
                            <th>تاريخ الإنشاء</th>
                            <th>تاريخ الاستخدام</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${vouchersHTML}
                    </tbody>
                </table>
            </div>
        `;

        // Setup select all checkbox
        const selectAllCheckbox = document.getElementById('select-all-vouchers');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.selectAllVouchers(e.target.checked);
            });
        }

        // Setup individual checkboxes
        document.querySelectorAll('.voucher-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedVouchers.add(parseInt(e.target.value));
                } else {
                    this.selectedVouchers.delete(parseInt(e.target.value));
                }
                this.updateBulkActions();
            });
        });
    }

    async createVoucherBatch() {
        try {
            const form = document.getElementById('create-voucher-form');
            const formData = new FormData(form);
            
            const data = {
                count: parseInt(formData.get('count')),
                duration_hours: parseInt(formData.get('duration_hours')),
                data_limit_mb: formData.get('data_limit_mb') ? 
                    parseInt(formData.get('data_limit_mb')) : null
            };

            const response = await app.apiCall('/vouchers/batch', 'POST', data);
            
            app.showAlert(response.message, 'success');
            app.closeModals();
            this.loadVouchers();
            this.loadBatches();

        } catch (error) {
            console.error('Error creating voucher batch:', error);
            app.showAlert('خطأ في إنشاء الكروت', 'error');
        }
    }

    async loadBatches() {
        try {
            const response = await app.apiCall('/vouchers/batches');
            this.displayBatches(response.batches);
        } catch (error) {
            console.error('Error loading batches:', error);
        }
    }

    displayBatches(batches) {
        const container = document.getElementById('batches-container');
        if (!container) return;

        if (batches.length === 0) {
            container.innerHTML = '<p class="text-secondary">لا توجد دفعات</p>';
            return;
        }

        const batchesHTML = batches.map(batch => `
            <div class="card">
                <div class="card-header">
                    <h4 class="card-title">دفعة: ${batch.batch_id}</h4>
                    <button class="btn btn-sm btn-primary" 
                            onclick="vouchers.printBatch('${batch.batch_id}')">
                        طباعة
                    </button>
                </div>
                <div class="card-body">
                    <div class="batch-stats">
                        <div class="stat">
                            <div class="stat-value">${batch.total_count}</div>
                            <div class="stat-label">إجمالي الكروت</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${batch.active_count}</div>
                            <div class="stat-label">كروت نشطة</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${batch.used_count}</div>
                            <div class="stat-label">كروت مستخدمة</div>
                        </div>
                    </div>
                    <div class="batch-date">
                        <small>تاريخ الإنشاء: ${app.formatDate(batch.created_at)}</small>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = batchesHTML;
    }

    async printBatch(batchId) {
        try {
            const response = await app.apiCall(`/vouchers/batch/${batchId}/print`);
            this.openPrintWindow(response.vouchers);
        } catch (error) {
            console.error('Error loading batch for print:', error);
            app.showAlert('خطأ في تحضير الطباعة', 'error');
        }
    }

    openPrintWindow(vouchers) {
        const printWindow = window.open('', '_blank');
        const vouchersHTML = vouchers.map(voucher => `
            <div class="voucher-card">
                <h3>كرت واي فاي</h3>
                <div class="voucher-code">${voucher.code}</div>
                <div class="voucher-info">
                    <p>المدة: ${voucher.duration_hours} ساعة</p>
                    ${voucher.data_limit_mb ? `<p>البيانات: ${voucher.data_limit_mb} MB</p>` : ''}
                    <p>صالح حتى: ${app.formatDate(voucher.expires_at)}</p>
                </div>
                ${voucher.qr_code ? `
                    <div class="qr-container">
                        <img src="${voucher.qr_code}" class="qr-code" alt="QR Code">
                    </div>
                ` : ''}
                <div class="instructions">
                    <p>امسح الكود أو ادخل الرقم في صفحة الدخول</p>
                </div>
            </div>
        `).join('');

        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>طباعة الكروت</title>
                <style>
                    body { font-family: Arial, sans-serif; direction: rtl; }
                    .voucher-print { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
                    .voucher-card { 
                        border: 2px solid #000; 
                        padding: 1rem; 
                        text-align: center; 
                        break-inside: avoid;
                        margin-bottom: 1rem;
                    }
                    .voucher-code { 
                        font-size: 1.5rem; 
                        font-weight: bold; 
                        margin: 1rem 0;
                        font-family: 'Courier New', monospace;
                    }
                    .qr-code { max-width: 100px; height: auto; }
                    .instructions { font-size: 0.8rem; margin-top: 1rem; }
                    @media print {
                        .voucher-print { grid-template-columns: repeat(2, 1fr); }
                    }
                </style>
            </head>
            <body>
                <div class="voucher-print">
                    ${vouchersHTML}
                </div>
            </body>
            </html>
        `);

        printWindow.document.close();
        printWindow.focus();
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 500);
    }

    showQRCode(code, qrData) {
        const modal = document.getElementById('qr-modal');
        if (modal) {
            const qrImage = modal.querySelector('.qr-display');
            const codeElement = modal.querySelector('.voucher-code-display');
            
            if (qrImage) qrImage.src = qrData;
            if (codeElement) codeElement.textContent = code;
            
            app.showModal('qr-modal');
        }
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

    selectAllVouchers(checked) {
        document.querySelectorAll('.voucher-checkbox').forEach(checkbox => {
            checkbox.checked = checked;
            if (checked) {
                this.selectedVouchers.add(parseInt(checkbox.value));
            } else {
                this.selectedVouchers.delete(parseInt(checkbox.value));
            }
        });
        this.updateBulkActions();
    }

    updateBulkActions() {
        const bulkActionsContainer = document.getElementById('bulk-actions');
        const selectedCount = this.selectedVouchers.size;
        
        if (bulkActionsContainer) {
            if (selectedCount > 0) {
                bulkActionsContainer.style.display = 'block';
                bulkActionsContainer.querySelector('.selected-count').textContent = selectedCount;
            } else {
                bulkActionsContainer.style.display = 'none';
            }
        }
    }

    applyFilters() {
        const form = document.getElementById('filter-form');
        const formData = new FormData(form);
        
        this.currentFilter = {};
        for (let [key, value] of formData.entries()) {
            if (value) {
                this.currentFilter[key] = value;
            }
        }
        
        this.currentPage = 1;
        this.loadVouchers();
    }

    clearFilters() {
        this.currentFilter = {};
        this.currentPage = 1;
        
        const form = document.getElementById('filter-form');
        if (form) {
            form.reset();
        }
        
        this.loadVouchers();
    }

    updatePagination(total, pages, currentPage) {
        const paginationContainer = document.getElementById('pagination');
        if (!paginationContainer) return;

        let paginationHTML = '';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `
                <button class="btn btn-secondary" onclick="vouchers.goToPage(${currentPage - 1})">
                    السابق
                </button>
            `;
        }

        // Page numbers
        for (let i = Math.max(1, currentPage - 2); i <= Math.min(pages, currentPage + 2); i++) {
            paginationHTML += `
                <button class="btn ${i === currentPage ? 'btn-primary' : 'btn-secondary'}" 
                        onclick="vouchers.goToPage(${i})">
                    ${i}
                </button>
            `;
        }

        // Next button
        if (currentPage < pages) {
            paginationHTML += `
                <button class="btn btn-secondary" onclick="vouchers.goToPage(${currentPage + 1})">
                    التالي
                </button>
            `;
        }

        paginationContainer.innerHTML = paginationHTML;

        // Update info
        const infoElement = document.getElementById('pagination-info');
        if (infoElement) {
            const start = ((currentPage - 1) * this.itemsPerPage) + 1;
            const end = Math.min(currentPage * this.itemsPerPage, total);
            infoElement.textContent = `عرض ${start}-${end} من ${total}`;
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadVouchers();
    }
}

// Initialize vouchers manager
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.vouchers-page')) {
        window.vouchers = new VouchersManager();
    }
});
