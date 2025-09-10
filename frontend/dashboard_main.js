// Dashboard Main JavaScript File
class DashboardApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.apiBaseUrl = 'http://127.0.0.1:8000/payroll/api';
        this.authToken = localStorage.getItem('authToken') || null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthentication();
        this.loadPage('dashboard');
        this.startPeriodicUpdates();
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.loadPage(page);
            });
        });

        // Sidebar toggle
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Profile dropdown
        document.getElementById('profileDropdown').addEventListener('click', () => {
            this.toggleProfileDropdown();
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Select all checkboxes
        document.getElementById('selectAllPayrolls')?.addEventListener('change', (e) => {
            this.toggleAllPayrollSelection(e.target.checked);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.profile-dropdown')) {
                this.closeProfileDropdown();
            }
        });
    }

    checkAuthentication() {
        if (!this.authToken) {
            window.location.href = 'login.html';
            return;
        }
        
        // Verify token with backend
        this.fetchWithAuth('/test-db/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Authentication failed');
                }
                return response.json();
            })
            .then(data => {
                console.log('Authentication verified:', data);
                this.updateStats(data.data);
            })
            .catch(error => {
                console.error('Authentication error:', error);
                this.logout();
            });
    }

    async fetchWithAuth(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.apiBaseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${this.authToken}`
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        return fetch(url, mergedOptions);
    }

    loadPage(pageName) {
        this.showLoading();
        
        // Update active navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`).classList.add('active');

        // Update page title
        this.updatePageTitle(pageName);

        // Hide all pages
        document.querySelectorAll('.page-content').forEach(page => {
            page.classList.remove('active');
        });

        // Show selected page
        document.getElementById(`${pageName}Page`).classList.add('active');

        // Load page-specific data
        this.loadPageData(pageName);
        
        this.currentPage = pageName;
        this.hideLoading();
    }

    updatePageTitle(pageName) {
        const titles = {
            dashboard: { title: 'Dashboard', subtitle: 'Overview of your payroll system' },
            employees: { title: 'Employee Management', subtitle: 'Manage employee records and information' },
            payrolls: { title: 'Payroll Management', subtitle: 'Create and manage employee payrolls' },
            companies: { title: 'Company Management', subtitle: 'Manage company profiles and settings' },
            users: { title: 'User Management', subtitle: 'Manage system users and permissions' },
            reports: { title: 'Reports & Analytics', subtitle: 'Generate comprehensive reports' },
            settings: { title: 'System Settings', subtitle: 'Configure system preferences' }
        };

        const pageInfo = titles[pageName] || { title: 'Dashboard', subtitle: 'PayrollPro Admin' };
        document.getElementById('pageTitle').textContent = pageInfo.title;
        document.getElementById('pageSubtitle').textContent = pageInfo.subtitle;
    }

    async loadPageData(pageName) {
        try {
            switch (pageName) {
                case 'dashboard':
                    await this.loadDashboardData();
                    break;
                case 'employees':
                    await this.loadEmployeesData();
                    break;
                case 'payrolls':
                    await this.loadPayrollsData();
                    break;
                case 'companies':
                    await this.loadCompaniesData();
                    break;
                case 'users':
                    await this.loadUsersData();
                    break;
                case 'reports':
                    await this.loadReportsData();
                    break;
                case 'settings':
                    await this.loadSettingsData();
                    break;
            }
        } catch (error) {
            console.error(`Error loading ${pageName} data:`, error);
            this.showToast('Error loading data', 'error');
        }
    }

    async loadDashboardData() {
        try {
            // Load dashboard stats
            const statsResponse = await this.fetchWithAuth('/dashboard/stats/');
            const statsData = await statsResponse.json();
            
            if (statsResponse.ok) {
                this.updateDashboardStats(statsData);
            }

            // Load recent activity (mock data for now)
            this.loadRecentActivity();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    updateDashboardStats(data) {
        document.getElementById('totalCompanies').textContent = data.company_balance || 0;
        document.getElementById('totalEmployees').textContent = data.total_employees || 0;
        document.getElementById('pendingPayrolls').textContent = data.pending_payrolls || 0;
        document.getElementById('totalPayrolls').textContent = data.total_payroll_amount || 0;
    }

    updateStats(data) {
        if (data) {
            document.getElementById('totalCompanies').textContent = data.total_companies || 0;
            document.getElementById('totalEmployees').textContent = data.total_employees || 0;
            document.getElementById('pendingPayrolls').textContent = data.pending_payrolls || 0;
            document.getElementById('totalPayrolls').textContent = data.total_payrolls || 0;
        }
    }

    loadRecentActivity() {
        const activityList = document.getElementById('activityList');
        const activities = [
            {
                type: 'success',
                message: 'Payroll approved for John Doe',
                time: '2 minutes ago'
            },
            {
                type: 'warning',
                message: 'New employee registration pending',
                time: '15 minutes ago'
            },
            {
                type: 'success',
                message: 'Monthly report generated',
                time: '1 hour ago'
            }
        ];

        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item ${activity.type}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>${activity.message}</span>
                    <small style="color: var(--gray-500);">${activity.time}</small>
                </div>
            </div>
        `).join('');
    }

    async loadEmployeesData() {
        try {
            const response = await this.fetchWithAuth('/employees/');
            const data = await response.json();
            
            if (response.ok) {
                this.renderEmployeesTable(data.results || data);
            } else {
                this.showToast('Failed to load employees', 'error');
            }
        } catch (error) {
            console.error('Error loading employees:', error);
            this.showToast('Error loading employees', 'error');
        }
    }

    renderEmployeesTable(employees) {
        const tbody = document.getElementById('employeesTableBody');
        
        if (!employees || employees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--gray-500);">No employees found</td></tr>';
            return;
        }

        tbody.innerHTML = employees.map(employee => `
            <tr>
                <td>${employee.user?.first_names || ''} ${employee.user?.last_names || ''}</td>
                <td>${employee.role || 'N/A'}</td>
                <td>${employee.company?.name || 'N/A'}</td>
                <td>$${parseFloat(employee.base_salary || 0).toLocaleString()}</td>
                <td><span class="status ${employee.is_active ? 'active' : 'inactive'}">${employee.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="viewEmployee(${employee.id})">View</button>
                    <button class="btn btn-warning btn-sm" onclick="editEmployee(${employee.id})">Edit</button>
                </td>
            </tr>
        `).join('');
    }

    async loadPayrollsData() {
        try {
            const response = await this.fetchWithAuth('/payrolls/');
            const data = await response.json();
            
            if (response.ok) {
                this.renderPayrollsTable(data.results || data);
            } else {
                this.showToast('Failed to load payrolls', 'error');
            }
        } catch (error) {
            console.error('Error loading payrolls:', error);
            this.showToast('Error loading payrolls', 'error');
        }
    }

    renderPayrollsTable(payrolls) {
        const tbody = document.getElementById('payrollsTableBody');
        
        if (!payrolls || payrolls.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--gray-500);">No payrolls found</td></tr>';
            return;
        }

        tbody.innerHTML = payrolls.map(payroll => `
            <tr>
                <td><input type="checkbox" class="payroll-select" value="${payroll.id}"></td>
                <td>${payroll.employee?.user?.first_names || ''} ${payroll.employee?.user?.last_names || ''}</td>
                <td>${String(payroll.month).padStart(2, '0')}/${payroll.year}</td>
                <td>$${parseFloat(payroll.employee?.base_salary || 0).toLocaleString()}</td>
                <td>$${parseFloat(payroll.bonus || 0).toLocaleString()}</td>
                <td>$${parseFloat(payroll.deductions || 0).toLocaleString()}</td>
                <td>$${parseFloat(payroll.final_salary || 0).toLocaleString()}</td>
                <td><span class="status ${payroll.status.toLowerCase()}">${payroll.status}</span></td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="viewPayroll(${payroll.id})">View</button>
                    ${payroll.status === 'Pending' ? `<button class="btn btn-success btn-sm" onclick="approvePayroll(${payroll.id})">Approve</button>` : ''}
                </td>
            </tr>
        `).join('');
    }

    async loadCompaniesData() {
        try {
            const response = await this.fetchWithAuth('/companies/');
            const data = await response.json();
            
            if (response.ok) {
                this.renderCompaniesTable(data.results || data);
            } else {
                this.showToast('Failed to load companies', 'error');
            }
        } catch (error) {
            console.error('Error loading companies:', error);
            this.showToast('Error loading companies', 'error');
        }
    }

    renderCompaniesTable(companies) {
        const tbody = document.getElementById('companiesTableBody');
        
        if (!companies || companies.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--gray-500);">No companies found</td></tr>';
            return;
        }

        tbody.innerHTML = companies.map(company => `
            <tr>
                <td>${company.name}</td>
                <td>$${parseFloat(company.bank_balance || 0).toLocaleString()}</td>
                <td>${company.created_by?.username || 'N/A'}</td>
                <td>${new Date(company.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="viewCompany(${company.id})">View</button>
                    <button class="btn btn-warning btn-sm" onclick="editCompany(${company.id})">Edit</button>
                </td>
            </tr>
        `).join('');
    }

    async loadUsersData() {
        try {
            const response = await this.fetchWithAuth('/users/');
            const data = await response.json();
            
            if (response.ok) {
                this.renderUsersTable(data.results || data);
            } else {
                this.showToast('Failed to load users', 'error');
            }
        } catch (error) {
            console.error('Error loading users:', error);
            this.showToast('Error loading users', 'error');
        }
    }

    renderUsersTable(users) {
        const tbody = document.getElementById('usersTableBody');
        
        if (!users || users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--gray-500);">No users found</td></tr>';
            return;
        }

        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.user?.username || 'N/A'}</td>
                <td>${user.user?.email || 'N/A'}</td>
                <td>${user.role}</td>
                <td>${user.company?.name || 'N/A'}</td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="viewUser(${user.id})">View</button>
                    <button class="btn btn-warning btn-sm" onclick="editUser(${user.id})">Edit</button>
                </td>
            </tr>
        `).join('');
    }

    async loadReportsData() {
        // Mock implementation for reports
        console.log('Loading reports data...');
        this.showToast('Reports feature coming soon', 'info');
    }

    async loadSettingsData() {
        // Mock implementation for settings
        console.log('Loading settings data...');
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('collapsed');
    }

    toggleProfileDropdown() {
        const dropdown = document.getElementById('profileDropdown');
        dropdown.classList.toggle('active');
    }

    closeProfileDropdown() {
        const dropdown = document.getElementById('profileDropdown');
        dropdown.classList.remove('active');
    }

    toggleAllPayrollSelection(checked) {
        document.querySelectorAll('.payroll-select').forEach(checkbox => {
            checkbox.checked = checked;
        });
    }

    handleSearch(query) {
        console.log('Searching for:', query);
        // Implement search functionality based on current page
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: var(--space-3);">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; cursor: pointer; margin-left: auto;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('userRole');
        window.location.href = 'login.html';
    }

    startPeriodicUpdates() {
        // Update dashboard stats every 30 seconds
        setInterval(() => {
            if (this.currentPage === 'dashboard') {
                this.loadDashboardData();
            }
        }, 30000);
    }
}

// Global functions for button actions
window.refreshDashboard = () => {
    dashboard.loadDashboardData();
    dashboard.showToast('Dashboard refreshed', 'success');
};

window.viewEmployee = (id) => {
    console.log('Viewing employee:', id);
    dashboard.showToast('Employee details feature coming soon', 'info');
};

window.editEmployee = (id) => {
    console.log('Editing employee:', id);
    dashboard.showToast('Edit employee feature coming soon', 'info');
};

window.viewPayroll = (id) => {
    console.log('Viewing payroll:', id);
    dashboard.showToast('Payroll details feature coming soon', 'info');
};

window.approvePayroll = async (id) => {
    try {
        const response = await dashboard.fetchWithAuth(`/payrolls/${id}/mark_as_paid/`, {
            method: 'POST'
        });
        
        if (response.ok) {
            dashboard.showToast('Payroll approved successfully', 'success');
            dashboard.loadPayrollsData();
        } else {
            dashboard.showToast('Failed to approve payroll', 'error');
        }
    } catch (error) {
        console.error('Error approving payroll:', error);
        dashboard.showToast('Error approving payroll', 'error');
    }
};

window.approveSelectedPayrolls = async () => {
    const selectedPayrolls = Array.from(document.querySelectorAll('.payroll-select:checked'))
        .map(checkbox => parseInt(checkbox.value));
    
    if (selectedPayrolls.length === 0) {
        dashboard.showToast('Please select payrolls to approve', 'warning');
        return;
    }

    try {
        const response = await dashboard.fetchWithAuth('/payrolls/approve_payrolls/', {
            method: 'POST',
            body: JSON.stringify({ payroll_ids: selectedPayrolls })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            dashboard.showToast(`${data.approved_count} payrolls approved successfully`, 'success');
            dashboard.loadPayrollsData();
        } else {
            dashboard.showToast('Failed to approve payrolls', 'error');
        }
    } catch (error) {
        console.error('Error approving payrolls:', error);
        dashboard.showToast('Error approving payrolls', 'error');
    }
};

window.viewCompany = (id) => {
    console.log('Viewing company:', id);
    dashboard.showToast('Company details feature coming soon', 'info');
};

window.editCompany = (id) => {
    console.log('Editing company:', id);
    dashboard.showToast('Edit company feature coming soon', 'info');
};

window.viewUser = (id) => {
    console.log('Viewing user:', id);
    dashboard.showToast('User details feature coming soon', 'info');
};

window.editUser = (id) => {
    console.log('Editing user:', id);
    dashboard.showToast('Edit user feature coming soon', 'info');
};

window.showAddEmployeeModal = () => {
    dashboard.showToast('Add employee feature coming soon', 'info');
};

window.showAddPayrollModal = () => {
    dashboard.showToast('Add payroll feature coming soon', 'info');
};

window.showAddCompanyModal = () => {
    dashboard.showToast('Add company feature coming soon', 'info');
};

window.showAddUserModal = () => {
    dashboard.showToast('Add user feature coming soon', 'info');
};

window.generateReport = () => {
    dashboard.showToast('Report generation feature coming soon', 'info');
};

window.saveSettings = () => {
    dashboard.showToast('Settings saved successfully', 'success');
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardApp();
});

// Example API testing functions
window.testDatabaseConnection = async () => {
    try {
        const response = await dashboard.fetchWithAuth('/test-db/');
        const data = await response.json();
        console.log('Database test result:', data);
        dashboard.showToast('Database connection successful', 'success');
        return data;
    } catch (error) {
        console.error('Database test failed:', error);
        dashboard.showToast('Database connection failed', 'error');
        return null;
    }
};

// Example fetch functions for testing
window.fetchEmployees = async () => {
    try {
        const response = await dashboard.fetchWithAuth('/employees/');
        const data = await response.json();
        console.log('Employees:', data);
        return data;
    } catch (error) {
        console.error('Error fetching employees:', error);
        return null;
    }
};

window.fetchPayrolls = async () => {
    try {
        const response = await dashboard.fetchWithAuth('/payrolls/');
        const data = await response.json();
        console.log('Payrolls:', data);
        return data;
    } catch (error) {
        console.error('Error fetching payrolls:', error);
        return null;
    }
};

window.fetchCompanies = async () => {
    try {
        const response = await dashboard.fetchWithAuth('/companies/');
        const data = await response.json();
        console.log('Companies:', data);
        return data;
    } catch (error) {
        console.error('Error fetching companies:', error);
        return null;
    }
};
