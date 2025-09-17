// Smart Water Meter Dashboard JavaScript

// Global variables
let refreshInterval;
let charts = {};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    // Add loading states to cards
    showLoadingStates();
    
    // Set up auto-refresh
    setupAutoRefresh();
    
    // Add event listeners
    setupEventListeners();
    
    // Initialize tooltips
    initializeTooltips();
}

function showLoadingStates() {
    const loadingSpinners = document.querySelectorAll('.loading-spinner');
    loadingSpinners.forEach(spinner => {
        spinner.style.display = 'block';
    });
}

function setupAutoRefresh() {
    // Clear existing interval if any
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Set up new interval for auto-refresh every 30 seconds
    refreshInterval = setInterval(() => {
        if (document.visibilityState === 'visible') {
            loadDashboardData();
        }
    }, 30000);
}

function setupEventListeners() {
    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            loadDashboardData();
        }
    });
    
    // Handle window focus
    window.addEventListener('focus', function() {
        loadDashboardData();
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Utility functions
function formatNumber(num, decimals = 0) {
    if (num === null || num === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Animation utilities
function animateValue(element, start, end, duration = 1000) {
    const startTimestamp = performance.now();
    
    const step = (timestamp) => {
        const elapsed = timestamp - startTimestamp;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (end - start) * easeOutQuart(progress);
        element.textContent = Math.round(current);
        
        if (progress < 1) {
            requestAnimationFrame(step);
        }
    };
    
    requestAnimationFrame(step);
}

function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 90px; right: 20px; z-index: 1050; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="bi bi-${getNotificationIcon(type)}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
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
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Loading state management
function showCardLoading(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-white bg-opacity-75';
        overlay.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
        card.style.position = 'relative';
        card.appendChild(overlay);
    }
}

function hideCardLoading(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        const overlay = card.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// Error handling
function handleApiError(error, context = '') {
    console.error(`API Error ${context}:`, error);
    
    let message = 'An error occurred while loading data.';
    if (error.message) {
        message = error.message;
    } else if (typeof error === 'string') {
        message = error;
    }
    
    showNotification(message, 'danger');
}

// Device status utilities
function getDeviceStatusClass(lastSeen) {
    if (!lastSeen) return 'status-offline';
    
    const now = new Date();
    const lastSeenDate = new Date(lastSeen);
    const diffMinutes = (now - lastSeenDate) / (1000 * 60);
    
    if (diffMinutes < 5) return 'status-online';
    if (diffMinutes < 30) return 'status-warning';
    return 'status-offline';
}

function getDeviceStatusText(lastSeen) {
    if (!lastSeen) return 'Never seen';
    
    const now = new Date();
    const lastSeenDate = new Date(lastSeen);
    const diffMinutes = (now - lastSeenDate) / (1000 * 60);
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${Math.round(diffMinutes)} minutes ago`;
    
    const diffHours = diffMinutes / 60;
    if (diffHours < 24) return `${Math.round(diffHours)} hours ago`;
    
    const diffDays = diffHours / 24;
    return `${Math.round(diffDays)} days ago`;
}

// Chart utilities
function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

function getChartColors() {
    return {
        primary: '#0d6efd',
        success: '#198754',
        danger: '#dc3545',
        warning: '#ffc107',
        info: '#0dcaf0',
        secondary: '#6c757d'
    };
}

// Export functions for use in templates
window.dashboardUtils = {
    formatNumber,
    formatCurrency,
    formatDateTime,
    formatTime,
    animateValue,
    showNotification,
    handleApiError,
    getDeviceStatusClass,
    getDeviceStatusText,
    createGradient,
    getChartColors
};
