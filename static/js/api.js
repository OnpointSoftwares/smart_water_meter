// Smart Water Meter API Helper Functions
// Production-ready API utilities for dynamic data handling

// CSRF Token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API Configuration
const API_BASE_URL = '/api';
const API_ENDPOINTS = {
    dashboard: `${API_BASE_URL}/dashboard/stats/`,
    devices: `${API_BASE_URL}/devices/`,
    alerts: `${API_BASE_URL}/alerts/`,
    waterUsage: `${API_BASE_URL}/data/`,
    waterUsageList: `${API_BASE_URL}/data/list/`,
};

// Default headers for API requests
const getDefaultHeaders = () => ({
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken'),
});

// API Request wrapper with error handling
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: getDefaultHeaders(),
        credentials: 'same-origin',
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Dashboard API functions
const DashboardAPI = {
    async getStats() {
        return await apiRequest(API_ENDPOINTS.dashboard);
    }
};

// Device API functions
const DeviceAPI = {
    async getAll() {
        return await apiRequest(API_ENDPOINTS.devices);
    },
    
    async create(deviceData) {
        return await apiRequest(API_ENDPOINTS.devices, {
            method: 'POST',
            body: JSON.stringify(deviceData),
        });
    },
    
    async update(deviceId, deviceData) {
        return await apiRequest(`${API_ENDPOINTS.devices}${deviceId}/`, {
            method: 'PUT',
            body: JSON.stringify(deviceData),
        });
    },
    
    async delete(deviceId) {
        return await apiRequest(`${API_ENDPOINTS.devices}${deviceId}/`, {
            method: 'DELETE',
        });
    }
};

// Alert API functions
const AlertAPI = {
    async getAll() {
        return await apiRequest(API_ENDPOINTS.alerts);
    },
    
    async resolve(alertId) {
        return await apiRequest(`${API_ENDPOINTS.alerts}${alertId}/resolve/`, {
            method: 'POST',
        });
    },
    
    async delete(alertId) {
        return await apiRequest(`${API_ENDPOINTS.alerts}${alertId}/`, {
            method: 'DELETE',
        });
    }
};

// Water Usage API functions
const WaterUsageAPI = {
    async getList(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${API_ENDPOINTS.waterUsageList}?${queryString}` : API_ENDPOINTS.waterUsageList;
        return await apiRequest(url);
    },
    
    async create(usageData) {
        return await apiRequest(API_ENDPOINTS.waterUsage, {
            method: 'POST',
            body: JSON.stringify(usageData),
        });
    }
};

// Notification helper
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 90px; right: 20px; z-index: 1055; min-width: 300px; max-width: 400px;';
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${getNotificationIcon(type)} me-2"></i>
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle-fill',
        danger: 'exclamation-triangle-fill',
        warning: 'exclamation-triangle-fill',
        info: 'info-circle-fill',
        primary: 'info-circle-fill'
    };
    return icons[type] || 'info-circle-fill';
}

// Loading state helper
function setLoadingState(element, isLoading, loadingText = 'Loading...') {
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            ${loadingText}
        `;
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || element.innerHTML;
    }
}

// Format utilities
const FormatUtils = {
    number(value, decimals = 2) {
        return parseFloat(value).toFixed(decimals);
    },
    
    currency(value, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(value);
    },
    
    date(dateString) {
        return new Date(dateString).toLocaleDateString();
    },
    
    datetime(dateString) {
        return new Date(dateString).toLocaleString();
    },
    
    timeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        if (diffHours < 24) return `${diffHours} hours ago`;
        if (diffDays < 7) return `${diffDays} days ago`;
        return this.date(dateString);
    }
};

// Export for use in other scripts
window.API = {
    Dashboard: DashboardAPI,
    Device: DeviceAPI,
    Alert: AlertAPI,
    WaterUsage: WaterUsageAPI,
    showNotification,
    setLoadingState,
    FormatUtils,
    getCookie
};
