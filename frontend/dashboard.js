/* =====================================
   DASHBOARD CONTENT MANAGEMENT
   =====================================
   This file handles dynamic content swapping in dashboard pages.
   It provides functions to load different sections without page refreshes.
   
   Key Features:
   - Dynamic sidebar navigation
   - Content area updates via JavaScript
   - API data fetching for each section
   - Error handling for failed loads
   ===================================== */

// =================================================================
// DASHBOARD CONFIGURATION
// =================================================================

/**
 * Dashboard configuration object containing all content definitions
 * Each content type has a title, API endpoint, and render function
 */
const DASHBOARD_CONTENT = {
    // Main dashboard overview with statistics
    dashboard: {
        title: 'Dashboard Overview',
        icon: 'fas fa-chart-pie',
        loadData: loadDashboardStats,
        render: renderDashboardOverview
    },
    
    // Employee management section
    employees: {
        title: 'Employee Management',
        icon: 'fas fa-user-tie',
        loadData: loadEmployees,
        render: renderEmployeesTable
    },
    
    // Payroll management section
    payrolls: {
        title: 'Payroll Management',
        icon: 'fas fa-money-check-alt',
        loadData: loadPayrolls,
        render: renderPayrollsTable
    },
    
    // Company management section (Admin only)
    companies: {
        title: 'Company Management',
        icon: 'fas fa-building',
        loadData: loadCompanies,
        render: renderCompaniesTable,
        requiresRole: 'Admin'
    },
    
    // User management section (Admin only)
    users: {
        title: 'User Management',
        icon: 'fas fa-users',
        loadData: loadUsers,
        render: renderUsersTable,
        requiresRole: 'Admin'
    },
    
    // Reports section
    reports: {
        title: 'Reports & Analytics',
        icon: 'fas fa-chart-bar',
        loadData: loadReports,
        render: renderReports
    },
    
    // Settings section
    settings: {
        title: 'System Settings',
        icon: 'fas fa-cog',
        loadData: loadSettings,
        render: renderSettings
    }
};

// =================================================================
// MAIN CONTENT SWITCHING FUNCTION
// =================================================================

/**
 * Main function to switch dashboard content
 * This is called when user clicks on sidebar navigation items
 * 
 * @param {string} contentType - Type of content to load (dashboard, employees, etc.)
 * @param {Event} event - Optional click event (to prevent default behavior)
 */
async function switchContent(contentType, event = null) {
    // Prevent default link behavior if event provided
    if (event) {
        event.preventDefault();
    }
    
    console.log('Switching to content:', contentType);
    
    // Get content configuration
    const config = DASHBOARD_CONTENT[contentType];
    if (!config) {
        console.error('Unknown content type:', contentType);
        showMessage('Content not found', 'error');
        return;
    }
    
    // Check role permissions if required
    if (config.requiresRole && getUserRole() !== config.requiresRole) {
        showMessage(`Access denied. ${config.requiresRole} role required.`, 'error');
        return;
    }
    
    try {
        // Update page title and header
        updatePageHeader(config.title, config.icon);
        
        // Update sidebar active state
        updateSidebarActive(contentType);
        
        // Show loading state in main content area
        showContentLoading();
        
        // Load data from API
        const data = await config.loadData();
        
        // Render content with loaded data
        config.render(data);
        
    } catch (error) {
        console.error('Error switching content:', error);
        showContentError(error.message || 'Failed to load content');
    }
}

// =================================================================
// UI UPDATE FUNCTIONS
// =================================================================

/**
 * Update page header with new title and icon
 * @param {string} title - Page title to display
 * @param {string} icon - Font Awesome icon class
 */
function updatePageHeader(title, icon) {
    // Update main content header
    const contentHeader = document.querySelector('.content-header h1');
    if (contentHeader) {
        contentHeader.innerHTML = `<i class="${icon}"></i> ${title}`;
    }
    
    // Update browser page title
    document.title = `${title} - PayrollPro Dashboard`;
}

/**
 * Update sidebar to show active navigation item
 * @param {string} activeType - Currently active content type
 */
function updateSidebarActive(activeType) {
    // Remove active class from all nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Add active class to current item
    const activeLink = document.querySelector(`[data-page="${activeType}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

/**
 * Show loading spinner in main content area
 */
function showContentLoading() {
    const mainContent = document.getElementById('mainContent');
    if (mainContent) {
        mainContent.innerHTML = `
            <div class="content-loading">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin fa-2x"></i>
                </div>
                <p>Loading content...</p>
            </div>
        `;
    }
}

/**
 * Show error message in main content area
 * @param {string} message - Error message to display
 */
function showContentError(message) {
    const mainContent = document.getElementById('mainContent');
    if (mainContent) {
        mainContent.innerHTML = `
            <div class="content-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle fa-2x"></i>
                </div>
                <h3>Error Loading Content</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">
                    <i class="fas fa-refresh"></i> Retry
                </button>
            </div>
        `;
    }
}

// =================================================================
// DATA LOADING FUNCTIONS
// =================================================================

/**
 * Load dashboard statistics and overview data
 * @returns {Promise<Object>} Dashboard stats object
 */
async function loadDashboardStats() {
    try {
        // Load multiple data sources in parallel for dashboard overview
        const [dbStats, recentPayrolls, pendingApprovals] = await Promise.all([
            apiGet('/test-db/'),                    // Database connectivity and counts
            apiGet('/payrolls/?limit=5'),           // Recent payrolls
            apiGet('/payrolls/?status=Pending')     // Pending approvals
        ]);
        
        return {
            stats: dbStats.data,
            recentPayrolls: recentPayrolls.results || recentPayrolls,
            pendingApprovals: pendingApprovals.results || pendingApprovals
        };
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        throw new Error('Failed to load dashboard statistics');
    }
}

/**
 * Load employee data from API
 * @returns {Promise<Array>} Array of employee objects
 */
async function loadEmployees() {
    try {
        const response = await apiGet('/employees/');
        return response.results || response;
    } catch (error) {
        console.error('Error loading employees:', error);
        throw new Error('Failed to load employee data');
    }
}

/**
 * Load payroll data from API
 * @returns {Promise<Array>} Array of payroll objects
 */
async function loadPayrolls() {
    try {
        const response = await apiGet('/payrolls/');
        return response.results || response;
    } catch (error) {
        console.error('Error loading payrolls:', error);
        throw new Error('Failed to load payroll data');
    }
}

/**
 * Load company data from API (Admin only)
 * @returns {Promise<Array>} Array of company objects
 */
async function loadCompanies() {
    try {
        const response = await apiGet('/companies/');
        return response.results || response;
    } catch (error) {
        console.error('Error loading companies:', error);
        throw new Error('Failed to load company data');
    }
}

/**
 * Load user data from API (Admin only)
 * @returns {Promise<Array>} Array of user objects
 */
async function loadUsers() {
    try {
        const response = await apiGet('/users/');
        return response.results || response;
    } catch (error) {
        console.error('Error loading users:', error);
        throw new Error('Failed to load user data');
    }
}

/**
 * Load reports data from API
 * @returns {Promise<Object>} Reports data object
 */
async function loadReports() {
    try {
        // This would typically load various report data
        const response = await apiGet('/dashboard/reports/');
        return response;
    } catch (error) {
        console.error('Error loading reports:', error);
        throw new Error('Failed to load reports data');
    }
}

/**
 * Load settings data from API
 * @returns {Promise<Object>} Settings data object
 */
async function loadSettings() {
    try {
        // This would typically load system settings
        return {
            company_info: {
                name: 'PayrollPro Demo Company',
                email: 'admin@payrollpro.com'
            },
            system_settings: {
                auto_backup: true,
                email_notifications: true
            }
        };
    } catch (error) {
        console.error('Error loading settings:', error);
        throw new Error('Failed to load settings data');
    }
}

// =================================================================
// CONTENT RENDERING FUNCTIONS
// =================================================================

/**
 * Render dashboard overview with statistics cards and recent activity
 * @param {Object} data - Dashboard data containing stats and recent items
 */
function renderDashboardOverview(data) {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="dashboard-overview">
            <!-- Statistics Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-building text-primary"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${data.stats.total_companies || 0}</h3>
                        <p>Total Companies</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-users text-success"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${data.stats.total_employees || 0}</h3>
                        <p>Total Employees</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-money-check-alt text-warning"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${data.stats.total_payrolls || 0}</h3>
                        <p>Total Payrolls</p>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-clock text-danger"></i>
                    </div>
                    <div class="stat-content">
                        <h3>${data.stats.pending_payrolls || 0}</h3>
                        <p>Pending Approvals</p>
                    </div>
                </div>
            </div>
            
            <!-- Recent Activity Section -->
            <div class="dashboard-sections">
                <div class="section">
                    <div class="section-header">
                        <h4><i class="fas fa-clock"></i> Recent Payrolls</h4>
                        <a href="#" onclick="switchContent('payrolls')" class="view-all-link">
                            View All <i class="fas fa-arrow-right"></i>
                        </a>
                    </div>
                    <div class="recent-items">
                        ${renderRecentPayrolls(data.recentPayrolls)}
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-header">
                        <h4><i class="fas fa-exclamation-circle"></i> Pending Approvals</h4>
                    </div>
                    <div class="pending-items">
                        ${renderPendingApprovals(data.pendingApprovals)}
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render recent payrolls list
 * @param {Array} payrolls - Array of recent payroll objects
 * @returns {string} HTML string for recent payrolls
 */
function renderRecentPayrolls(payrolls) {
    if (!payrolls || payrolls.length === 0) {
        return '<p class="no-data">No recent payrolls found.</p>';
    }
    
    return payrolls.map(payroll => `
        <div class="item">
            <div class="item-info">
                <strong>${payroll.employee_name || 'Unknown Employee'}</strong>
                <span class="item-detail">${formatCurrency(payroll.final_salary || 0)}</span>
            </div>
            <div class="item-meta">
                <span class="status status-${payroll.status?.toLowerCase()}">${payroll.status}</span>
                <span class="date">${formatDate(payroll.created_at)}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Render pending approvals list
 * @param {Array} approvals - Array of pending approval objects
 * @returns {string} HTML string for pending approvals
 */
function renderPendingApprovals(approvals) {
    if (!approvals || approvals.length === 0) {
        return '<p class="no-data">No pending approvals.</p>';
    }
    
    return approvals.map(approval => `
        <div class="item">
            <div class="item-info">
                <strong>${approval.employee_name || 'Unknown Employee'}</strong>
                <span class="item-detail">${formatCurrency(approval.final_salary || 0)}</span>
            </div>
            <div class="item-actions">
                <button class="btn btn-sm btn-success" onclick="approvePayroll(${approval.id})">
                    <i class="fas fa-check"></i> Approve
                </button>
                <button class="btn btn-sm btn-danger" onclick="rejectPayroll(${approval.id})">
                    <i class="fas fa-times"></i> Reject
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Render employees table with search and actions
 * @param {Array} employees - Array of employee objects
 */
function renderEmployeesTable(employees) {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="table-container">
            <!-- Table Header with Actions -->
            <div class="table-header">
                <div class="table-title">
                    <h4><i class="fas fa-user-tie"></i> Employee Management</h4>
                </div>
                <div class="table-actions">
                    <button class="btn btn-primary" onclick="openAddEmployeeModal()">
                        <i class="fas fa-plus"></i> Add Employee
                    </button>
                </div>
            </div>
            
            <!-- Search and Filter -->
            <div class="table-filters">
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" id="employeeSearch" placeholder="Search employees..." 
                           onkeyup="filterEmployees()">
                </div>
            </div>
            
            <!-- Employees Table -->
            <div class="table-responsive">
                <table class="data-table" id="employeesTable">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Role</th>
                            <th>Company</th>
                            <th>Base Salary</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${renderEmployeeRows(employees)}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

/**
 * Render individual employee table rows
 * @param {Array} employees - Array of employee objects
 * @returns {string} HTML string for table rows
 */
function renderEmployeeRows(employees) {
    if (!employees || employees.length === 0) {
        return '<tr><td colspan="6" class="no-data">No employees found.</td></tr>';
    }
    
    return employees.map(employee => `
        <tr>
            <td>
                <div class="user-info">
                    <strong>${employee.full_name || 'Unknown'}</strong>
                    <small>${employee.user_details?.email || 'No email'}</small>
                </div>
            </td>
            <td><span class="role-badge">${employee.role || 'N/A'}</span></td>
            <td>${employee.company?.name || 'N/A'}</td>
            <td>${formatCurrency(employee.base_salary || 0)}</td>
            <td>
                <span class="status-badge ${employee.is_active ? 'active' : 'inactive'}">
                    ${employee.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="editEmployee(${employee.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee(${employee.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Render payrolls table with filtering and status management
 * @param {Array} payrolls - Array of payroll objects
 */
function renderPayrollsTable(payrolls) {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="table-container">
            <div class="table-header">
                <div class="table-title">
                    <h4><i class="fas fa-money-check-alt"></i> Payroll Management</h4>
                </div>
                <div class="table-actions">
                    <button class="btn btn-primary" onclick="openCreatePayrollModal()">
                        <i class="fas fa-plus"></i> Create Payroll
                    </button>
                </div>
            </div>
            
            <div class="table-filters">
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" id="payrollSearch" placeholder="Search payrolls..." 
                           onkeyup="filterPayrolls()">
                </div>
                <select id="statusFilter" onchange="filterPayrolls()">
                    <option value="">All Status</option>
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Paid">Paid</option>
                </select>
            </div>
            
            <div class="table-responsive">
                <table class="data-table" id="payrollsTable">
                    <thead>
                        <tr>
                            <th>Employee</th>
                            <th>Company</th>
                            <th>Base Salary</th>
                            <th>Bonuses</th>
                            <th>Deductions</th>
                            <th>Final Salary</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${renderPayrollRows(payrolls)}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

/**
 * Render individual payroll table rows
 * @param {Array} payrolls - Array of payroll objects
 * @returns {string} HTML string for table rows
 */
function renderPayrollRows(payrolls) {
    if (!payrolls || payrolls.length === 0) {
        return '<tr><td colspan="8" class="no-data">No payrolls found.</td></tr>';
    }
    
    return payrolls.map(payroll => `
        <tr>
            <td>
                <div class="user-info">
                    <strong>${payroll.employee_name || 'Unknown'}</strong>
                </div>
            </td>
            <td>${payroll.company_name || 'N/A'}</td>
            <td>${formatCurrency(payroll.base_salary || 0)}</td>
            <td>${formatCurrency(payroll.bonuses || 0)}</td>
            <td>${formatCurrency(payroll.deductions || 0)}</td>
            <td><strong>${formatCurrency(payroll.final_salary || 0)}</strong></td>
            <td>
                <span class="status-badge status-${payroll.status?.toLowerCase()}">
                    ${payroll.status || 'Unknown'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewPayroll(${payroll.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${payroll.status === 'Pending' ? `
                        <button class="btn btn-sm btn-outline-success" onclick="approvePayroll(${payroll.id})">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Render companies table (Admin only)
 * @param {Array} companies - Array of company objects
 */
function renderCompaniesTable(companies) {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="table-container">
            <div class="table-header">
                <div class="table-title">
                    <h4><i class="fas fa-building"></i> Company Management</h4>
                </div>
                <div class="table-actions">
                    <button class="btn btn-primary" onclick="openAddCompanyModal()">
                        <i class="fas fa-plus"></i> Add Company
                    </button>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Company Name</th>
                            <th>Bank Balance</th>
                            <th>Created By</th>
                            <th>Created Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${renderCompanyRows(companies)}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

/**
 * Render individual company table rows
 * @param {Array} companies - Array of company objects
 * @returns {string} HTML string for table rows
 */
function renderCompanyRows(companies) {
    if (!companies || companies.length === 0) {
        return '<tr><td colspan="5" class="no-data">No companies found.</td></tr>';
    }
    
    return companies.map(company => `
        <tr>
            <td><strong>${company.name || 'Unknown'}</strong></td>
            <td><strong class="text-success">${formatCurrency(company.bank_balance || 0)}</strong></td>
            <td>${company.created_by?.username || 'Unknown'}</td>
            <td>${formatDate(company.created_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="editCompany(${company.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCompany(${company.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Render users table (Admin only)
 * @param {Array} users - Array of user objects
 */
function renderUsersTable(users) {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="table-container">
            <div class="table-header">
                <div class="table-title">
                    <h4><i class="fas fa-users"></i> User Management</h4>
                </div>
                <div class="table-actions">
                    <button class="btn btn-primary" onclick="openAddUserModal()">
                        <i class="fas fa-plus"></i> Add User
                    </button>
                </div>
            </div>
            
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Full Name</th>
                            <th>Role</th>
                            <th>Company</th>
                            <th>Created Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${renderUserRows(users)}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

/**
 * Render individual user table rows
 * @param {Array} users - Array of user objects
 * @returns {string} HTML string for table rows
 */
function renderUserRows(users) {
    if (!users || users.length === 0) {
        return '<tr><td colspan="6" class="no-data">No users found.</td></tr>';
    }
    
    return users.map(user => `
        <tr>
            <td><strong>${user.username || 'Unknown'}</strong></td>
            <td>${user.full_name || 'N/A'}</td>
            <td><span class="role-badge role-${user.role?.toLowerCase()}">${user.role || 'N/A'}</span></td>
            <td>${user.company?.name || 'N/A'}</td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" onclick="editUser(${user.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Render reports section with charts and analytics
 * @param {Object} data - Reports data object
 */
function renderReports(data) {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="reports-container">
            <div class="reports-header">
                <h4><i class="fas fa-chart-bar"></i> Reports & Analytics</h4>
                <div class="report-actions">
                    <button class="btn btn-outline-primary" onclick="exportReport('pdf')">
                        <i class="fas fa-file-pdf"></i> Export PDF
                    </button>
                    <button class="btn btn-outline-success" onclick="exportReport('excel')">
                        <i class="fas fa-file-excel"></i> Export Excel
                    </button>
                </div>
            </div>
            
            <div class="reports-content">
                <div class="report-section">
                    <h5>Payroll Summary</h5>
                    <p>Detailed payroll reports will be displayed here.</p>
                    <p><em>This section would typically contain charts and detailed analytics.</em></p>
                </div>
                
                <div class="report-section">
                    <h5>Employee Statistics</h5>
                    <p>Employee distribution and statistics will be shown here.</p>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render settings section with system configuration options
 * @param {Object} data - Settings data object
 */
function renderSettings(data) {
    const mainContent = document.getElementById('mainContent');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="settings-container">
            <div class="settings-header">
                <h4><i class="fas fa-cog"></i> System Settings</h4>
            </div>
            
            <div class="settings-content">
                <div class="settings-section">
                    <h5>Company Information</h5>
                    <form class="settings-form">
                        <div class="form-group">
                            <label for="companyName">Company Name</label>
                            <input type="text" id="companyName" value="${data.company_info?.name || ''}" 
                                   class="form-control">
                        </div>
                        <div class="form-group">
                            <label for="companyEmail">Company Email</label>
                            <input type="email" id="companyEmail" value="${data.company_info?.email || ''}" 
                                   class="form-control">
                        </div>
                    </form>
                </div>
                
                <div class="settings-section">
                    <h5>System Settings</h5>
                    <form class="settings-form">
                        <div class="form-group">
                            <div class="form-check">
                                <input type="checkbox" id="autoBackup" 
                                       ${data.system_settings?.auto_backup ? 'checked' : ''} 
                                       class="form-check-input">
                                <label for="autoBackup" class="form-check-label">
                                    Enable Auto Backup
                                </label>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="form-check">
                                <input type="checkbox" id="emailNotifications" 
                                       ${data.system_settings?.email_notifications ? 'checked' : ''} 
                                       class="form-check-input">
                                <label for="emailNotifications" class="form-check-label">
                                    Enable Email Notifications
                                </label>
                            </div>
                        </div>
                    </form>
                </div>
                
                <div class="settings-actions">
                    <button class="btn btn-primary" onclick="saveSettings()">
                        <i class="fas fa-save"></i> Save Settings
                    </button>
                    <button class="btn btn-outline-secondary" onclick="resetSettings()">
                        <i class="fas fa-undo"></i> Reset to Defaults
                    </button>
                </div>
            </div>
        </div>
    `;
}

// =================================================================
// INITIALIZATION AND EVENT HANDLERS
// =================================================================

/**
 * Initialize dashboard functionality when page loads
 * Sets up sidebar navigation and loads initial content
 */
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Set up sidebar navigation click handlers
    const navLinks = document.querySelectorAll('.nav-link[data-page]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const contentType = this.getAttribute('data-page');
            switchContent(contentType);
        });
    });
    
    // Load default content (dashboard overview)
    switchContent('dashboard');
    
    // Set up sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    console.log('Dashboard initialized successfully');
}

/**
 * Toggle sidebar collapsed state for mobile responsiveness
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on a dashboard page
    if (document.querySelector('.dashboard-wrapper')) {
        initializeDashboard();
    }
});

// =================================================================
// PLACEHOLDER ACTION FUNCTIONS
// =================================================================
// These functions would be implemented based on specific requirements

function approvePayroll(payrollId) {
    console.log('Approve payroll:', payrollId);
    // Implementation would go here
}

function rejectPayroll(payrollId) {
    console.log('Reject payroll:', payrollId);
    // Implementation would go here
}

function editEmployee(employeeId) {
    console.log('Edit employee:', employeeId);
    // Implementation would go here
}

function deleteEmployee(employeeId) {
    console.log('Delete employee:', employeeId);
    // Implementation would go here
}

function openAddEmployeeModal() {
    console.log('Open add employee modal');
    // Implementation would go here
}

function openCreatePayrollModal() {
    console.log('Open create payroll modal');
    // Implementation would go here
}

function exportReport(format) {
    console.log('Export report:', format);
    // Implementation would go here
}

function saveSettings() {
    console.log('Save settings');
    // Implementation would go here
}

console.log('Dashboard.js loaded successfully');
