// PWA Utilities
// Handles service worker registration and install prompts

const PWA = {
    deferredPrompt: null,
    isInstalled: false,

    async init() {
        // Check if already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            console.log('📱 Running as installed PWA');
        }

        // Register service worker
        await this.registerServiceWorker();

        // Setup install prompt
        this.setupInstallPrompt();

        // Check for updates
        this.checkForUpdates();
    },

    async registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            console.log('Service Worker not supported');
            return;
        }

        try {
            const registration = await navigator.serviceWorker.register('/service-worker.js', {
                scope: '/'
            });

            console.log('✅ Service Worker registered:', registration.scope);

            // Check for updates
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;

                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        this.showUpdateNotification();
                    }
                });
            });

            return registration;
        } catch (error) {
            console.error('Service Worker registration failed:', error);
        }
    },

    setupInstallPrompt() {
        // Capture install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;

            // Show install button after delay
            setTimeout(() => {
                this.showInstallButton();
            }, 30000); // Show after 30 seconds
        });

        // Track installation
        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.hideInstallButton();
            this.showInstallSuccess();
            console.log('🎉 PWA installed successfully');
        });
    },

    showInstallButton() {
        if (this.isInstalled) return;

        const banner = document.createElement('div');
        banner.id = 'install-banner';
        banner.className = 'install-banner';
        banner.innerHTML = `
            <div class="install-content">
                <div class="install-icon">📱</div>
                <div class="install-text">
                    <strong>Install InsightRural</strong>
                    <small>Get quick access from your home screen</small>
                </div>
            </div>
            <div class="install-actions">
                <button class="install-btn" id="install-btn">Install</button>
                <button class="install-dismiss" id="install-dismiss">✕</button>
            </div>
        `;

        document.body.appendChild(banner);

        // Animate in
        requestAnimationFrame(() => {
            banner.classList.add('visible');
        });

        // Button handlers
        document.getElementById('install-btn')?.addEventListener('click', () => {
            this.promptInstall();
        });

        document.getElementById('install-dismiss')?.addEventListener('click', () => {
            this.hideInstallButton();
        });
    },

    hideInstallButton() {
        const banner = document.getElementById('install-banner');
        if (banner) {
            banner.classList.remove('visible');
            setTimeout(() => banner.remove(), 300);
        }
    },

    async promptInstall() {
        if (!this.deferredPrompt) return;

        this.deferredPrompt.prompt();

        const { outcome } = await this.deferredPrompt.userChoice;
        console.log(`Install prompt outcome: ${outcome}`);

        this.deferredPrompt = null;
        this.hideInstallButton();
    },

    showInstallSuccess() {
        const toast = document.createElement('div');
        toast.className = 'pwa-toast success';
        toast.innerHTML = `
            <div class="toast-icon">🎉</div>
            <div class="toast-message">
                <strong>App Installed!</strong>
                <small>Open from your home screen anytime</small>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('visible');
        }, 100);

        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    showUpdateNotification() {
        const toast = document.createElement('div');
        toast.className = 'pwa-toast update';
        toast.innerHTML = `
            <div class="toast-icon">🔄</div>
            <div class="toast-message">
                <strong>Update Available!</strong>
                <small>Refresh for the latest version</small>
            </div>
            <button class="toast-action" onclick="location.reload()">Refresh</button>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('visible');
        }, 100);
    },

    async checkForUpdates() {
        if (!('serviceWorker' in navigator)) return;

        const registration = await navigator.serviceWorker.ready;

        // Check for updates periodically
        setInterval(() => {
            registration.update();
        }, 60000); // Check every minute
    },

    // Check online status
    get isOnline() {
        return navigator.onLine;
    },

    // Show offline indicator
    showOfflineIndicator() {
        let indicator = document.getElementById('offline-indicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = '📶 Offline Mode';
            document.body.appendChild(indicator);
        }

        indicator.classList.add('visible');
    },

    hideOfflineIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.classList.remove('visible');
        }
    }
};

// Add PWA styles
const pwaStyles = document.createElement('style');
pwaStyles.textContent = `
    /* Install Banner */
    .install-banner {
        position: fixed;
        bottom: -100px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        box-shadow: 0 8px 32px rgba(16, 163, 127, 0.4);
        z-index: 9999;
        transition: all 0.3s ease;
        max-width: 90%;
        width: 450px;
    }
    
    .install-banner.visible {
        bottom: 20px;
    }
    
    .install-content {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .install-icon {
        font-size: 2rem;
    }
    
    .install-text {
        display: flex;
        flex-direction: column;
    }
    
    .install-text strong {
        font-size: 1rem;
    }
    
    .install-text small {
        opacity: 0.8;
        font-size: 0.8rem;
    }
    
    .install-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    .install-btn {
        padding: 0.6rem 1.2rem;
        background: white;
        color: #10a37f;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .install-btn:hover {
        transform: scale(1.05);
    }
    
    .install-dismiss {
        padding: 0.6rem;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
    }
    
    /* PWA Toast */
    .pwa-toast {
        position: fixed;
        bottom: -100px;
        right: 20px;
        background: #1a1a2e;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .pwa-toast.visible {
        bottom: 20px;
    }
    
    .pwa-toast.success {
        border-color: #10a37f;
    }
    
    .pwa-toast.update {
        border-color: #1e90ff;
    }
    
    .toast-icon {
        font-size: 1.5rem;
    }
    
    .toast-message {
        display: flex;
        flex-direction: column;
    }
    
    .toast-message small {
        opacity: 0.7;
        font-size: 0.8rem;
    }
    
    .toast-action {
        padding: 0.5rem 1rem;
        background: #1e90ff;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        margin-left: auto;
    }
    
    /* Offline Indicator */
    .offline-indicator {
        position: fixed;
        top: -40px;
        left: 50%;
        transform: translateX(-50%);
        background: #ef4444;
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 0 0 12px 12px;
        font-size: 0.85rem;
        font-weight: 500;
        z-index: 9999;
        transition: top 0.3s ease;
    }
    
    .offline-indicator.visible {
        top: 0;
    }
    
    @media (max-width: 480px) {
        .install-banner {
            flex-direction: column;
            text-align: center;
            width: calc(100% - 40px);
        }
        
        .install-content {
            flex-direction: column;
        }
    }
`;
document.head.appendChild(pwaStyles);

// Online/offline event listeners
window.addEventListener('online', () => {
    PWA.hideOfflineIndicator();
    console.log('🌐 Back online');
});

window.addEventListener('offline', () => {
    PWA.showOfflineIndicator();
    console.log('📶 Gone offline');
});

// Initialize PWA
document.addEventListener('DOMContentLoaded', () => {
    PWA.init();
});

// Export
window.PWA = PWA;
