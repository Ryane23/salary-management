// All the JavaScript code from <script>...</script> in dashboard_admin_new.html goes here.
// For example:
const API_BASE = 'http://127.0.0.1:8000/api';

// Remove all duplicate function definitions below this line!
// Only keep one version of each function (e.g., loadEmployeesPage, loadEmployees, showAddEmployeeForm, etc.)

// Example: Keep only ONE loadEmployeesPage function
function loadEmployeesPage() {
    const contentArea = document.getElementById('contentArea');
    contentArea.innerHTML = `
        <div class="content-card">
            <div class="card-header">
                <h3 class="card-title">
                    <i class="fa-solid fa-users"></i>
                    Employee Management
                </h3>
                <button class="btn btn-primary" onclick="showAddEmployeeForm()">
                    <i class="fa-solid fa-user-plus"></i>
                    Add New Employee
                </button>
            </div>
            <div class="card-content">
                <!-- Add Employee Form (hidden initially) -->
                <div id="addEmployeeForm" style="display: none; background: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #e2e8f0;">
                    <h4 style="margin-bottom: 15px; color: #1e293b;">Add New Employee</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <input type="text" id="firstName" placeholder="First Name" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                        <input type="text" id="lastName" placeholder="Last Name" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                        <input type="text" id="username" placeholder="Username" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                        <input type="email" id="email" placeholder="Email" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                        <input type="text" id="phone" placeholder="Phone" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                        <select id="role" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                            <option value="">Select Role</option>
                            <option value="Admin">Admin</option>
                            <option value="HR">HR</option>
                            <option value="Employee">Employee</option>
                            <option value="Manager">Manager</option>
                        </select>
                        <input type="number" id="baseSalary" placeholder="Base Salary" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                        <input type="password" id="password" placeholder="Password" style="padding: 10px; border: 1px solid #d1d5db; border-radius: 8px;">
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="btn btn-primary" onclick="addEmployee()" style="margin-right: 10px;">
                            <i class="fa-solid fa-save"></i>
                            Save Employee
                        </button>
                        <button class="btn btn-outline" onclick="hideAddEmployeeForm()">
                            Cancel
                        </button>
                    </div>
                </div>
                
                <!-- Employee Table -->
                <div id="employeeData"></div>
            </div>
        </div>
    `;
    setTimeout(() => { loadEmployees(); }, 100);
}

window.loadPageContent = function(section) {
    let file = '';
    switch (section) {
        case 'dashboard':
            file = '/static/dashboard_admin_new.html';
            break;
        case 'analytics':
            file = '/static/admin-sidebar/analytics.html';
            break;
        case 'employees':
            file = '/static/admin-sidebar/employees.html';
            break;
        case 'departments':
            file = '/static/admin-sidebar/departments.html';
            break;
        case 'payroll':
            file = '/static/admin-sidebar/payroll.html';
            break;
        case 'dashboard-stats':
            file = '/static/admin-sidebar/dashboard-stats.html';
            break;
        case 'user-management':
            file = '/static/admin-sidebar/user-management.html';
            break;
        case 'settings':
            file = '/static/admin-sidebar/settings.html';
            break;
        default:
            file = '/static/dashboard_admin_new.html';
    }
    fetch(file)
        .then(res => res.text())
        .then(html => {
            document.getElementById('contentArea').innerHTML = html;
        });
};

window.goToDashboardHome = function() {
    // Remove the hash from the URL without reloading the page
    history.replaceState(null, '', window.location.pathname + window.location.search);
    // Reload the dashboard content (full reload)
    window.location.reload();
    // OR: If you want to just reset the content area without reload:
    // document.getElementById('contentArea').innerHTML = /* main dashboard HTML */;
    // document.getElementById('pageTitle').textContent = 'Dashboard';
}