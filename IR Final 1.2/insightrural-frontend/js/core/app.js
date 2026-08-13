// ============================================================================
// InsightRural — Main Application Bootstrap (Production-Ready)
// Error-resilient initialization with global toast notifications
// ============================================================================

// ── Global Toast Notification System ─────────────────────────────────────────
window.Toast = {
    container: null,

    init() {
        if (this.container) return;
        this.container = document.createElement('div');
        this.container.id = 'ir-toast-container';
        this.container.style.cssText = `
            position: fixed; top: 80px; right: 20px; z-index: 10000;
            display: flex; flex-direction: column; gap: 10px;
            pointer-events: none; max-width: 400px;
        `;
        document.body.appendChild(this.container);
    },

    show(message, type = 'info', duration = 4000) {
        this.init();
        const toast = document.createElement('div');
        const icons = { info: 'ℹ️', success: '✅', warning: '⚠️', error: '❌' };
        const colors = {
            info:    'linear-gradient(135deg, #3b82f6, #2563eb)',
            success: 'linear-gradient(135deg, #10a37f, #059669)',
            warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
            error:   'linear-gradient(135deg, #ef4444, #dc2626)'
        };
        toast.style.cssText = `
            background: ${colors[type] || colors.info};
            color: white; padding: 14px 20px; border-radius: 12px;
            font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500;
            box-shadow: 0 8px 30px rgba(0,0,0,0.2); pointer-events: auto;
            display: flex; align-items: center; gap: 10px;
            animation: irToastIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px); line-height: 1.4;
        `;
        toast.innerHTML = `<span style="font-size:18px">${icons[type] || icons.info}</span><span>${message}</span>`;
        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'irToastOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
};

// Inject toast animation CSS
const toastStyle = document.createElement('style');
toastStyle.textContent = `
    @keyframes irToastIn { from { opacity: 0; transform: translateX(40px) scale(0.95); } to { opacity: 1; transform: translateX(0) scale(1); } }
    @keyframes irToastOut { from { opacity: 1; transform: translateX(0); } to { opacity: 0; transform: translateX(40px); } }
`;
document.head.appendChild(toastStyle);


// ── Global Web Audio API Sound Synthesizer ───────────────────────────────────
window.AudioService = {
    audioCtx: null,

    init() {
        if (this.audioCtx) return;
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioContext();
        } catch (e) {
            // Web Audio API not supported — fail silently
        }
    },

    play(type = 'click') {
        this.init();
        if (!this.audioCtx) return;

        if (this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }

        const osc = this.audioCtx.createOscillator();
        const gainNode = this.audioCtx.createGain();
        osc.connect(gainNode);
        gainNode.connect(this.audioCtx.destination);

        const now = this.audioCtx.currentTime;

        if (type === 'click') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, now);
            gainNode.gain.setValueAtTime(0.06, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
            osc.start(now);
            osc.stop(now + 0.12);
        } else if (type === 'success') {
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(523.25, now);
            osc.frequency.setValueAtTime(659.25, now + 0.08);
            osc.frequency.setValueAtTime(783.99, now + 0.16);
            gainNode.gain.setValueAtTime(0.08, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
            osc.start(now);
            osc.stop(now + 0.35);
        } else if (type === 'send') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(660, now);
            osc.frequency.exponentialRampToValueAtTime(1100, now + 0.1);
            gainNode.gain.setValueAtTime(0.05, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
            osc.start(now);
            osc.stop(now + 0.1);
        } else if (type === 'hover') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(1000, now);
            gainNode.gain.setValueAtTime(0.015, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.02);
            osc.start(now);
            osc.stop(now + 0.02);
        }
    }
};

window.playChime = function (type) {
    window.AudioService.play(type);
};


// ── Safe Component Initializer ───────────────────────────────────────────────
function safeInit(name, fn) {
    try {
        fn();
    } catch (e) {
        console.error(`[InsightRural] Failed to initialize ${name}:`, e);
    }
}


// ── Main Application Initialization ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 InsightRural Frontend Initializing...');

    // Initialize state (critical — must succeed)
    safeInit('AppState', () => AppState.init());

    // Initialize core components with error isolation
    safeInit('Sidebar', () => SidebarComponent.init());
    safeInit('Chat', () => ChatComponent.init());

    // Initialize advanced components (each failure is isolated)
    safeInit('JEE Component', () => {
        window.JeeComponent = new JeeCounselingComponent();
    });
    safeInit('NEET Component', () => {
        window.NeetComponent = new NeetCounselingComponent();
    });
    safeInit('Risk Analyzer', () => {
        window.RiskAnalyzerComponent = new RiskAnalyzerComponent();
    });

    // ── Auditory UX Micro-Interactions ───────────────────────────────────────
    document.addEventListener('mouseenter', function (e) {
        const target = e.target.closest('.nav-item, .btn, .btn-primary, .btn-secondary, .tab-btn, .checkbox-item, .predict-submit-btn, .mini-send-btn, .lang-btn, .mic-btn, .speaker-btn, .video-card, .portal-nav-btn, .legend-chip-btn, .tip-chip, .landing-cta-btn, .landing-feature-card, .compare-btn, .generate-essay-btn, .download-pdf-btn, .collapsible-header');
        if (target) {
            window.playChime('hover');
        }
    }, true);

    // ── Global Error Handler (prevents blank screens) ────────────────────────
    window.addEventListener('unhandledrejection', function (event) {
        console.error('[InsightRural] Unhandled promise rejection:', event.reason);
        event.preventDefault(); // Prevent crash
    });

    console.log('✅ InsightRural Frontend Ready');
});