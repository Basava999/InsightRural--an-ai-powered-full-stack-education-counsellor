// Live Counselling Dashboard Component
// Real-time statistics and seat availability tracking

const DashboardComponent = {
    isActive: false,
    animationFrameId: null,
    updateInterval: null,

    // Simulated live data
    liveData: {
        totalSeats: 228450,
        filledSeats: 0,
        onlineUsers: 0,
        predictionsToday: 0,
        lastUpdated: new Date()
    },

    // Category-wise data
    categoryData: {
        GM: { total: 114225, filled: 0 },
        OBC: { total: 68535, filled: 0 },
        SC: { total: 34267, filled: 0 },
        ST: { total: 11423, filled: 0 }
    },

    // College type data
    collegeTypeData: {
        Government: { total: 45, filled: 0 },
        Private: { total: 183, filled: 0 }
    },

    // Important dates
    importantDates: [
        { event: 'Round 1 Option Entry', date: new Date('2026-02-10'), status: 'upcoming' },
        { event: 'Round 1 Seat Allotment', date: new Date('2026-02-20'), status: 'upcoming' },
        { event: 'Document Verification', date: new Date('2026-02-25'), status: 'upcoming' },
        { event: 'Round 2 Begins', date: new Date('2026-03-05'), status: 'upcoming' },
        { event: 'Final Allotment', date: new Date('2026-03-25'), status: 'upcoming' }
    ],

    init() {
        this.renderDashboard();
        this.setupEventListeners();
        console.log('📊 Dashboard initialized');
    },

    setupEventListeners() {
        // Listen for navigation to dashboard
        document.addEventListener('featureChange', (e) => {
            if (e.detail === 'dashboard') {
                this.activate();
            } else {
                this.deactivate();
            }
        });
    },

    activate() {
        this.isActive = true;
        this.startLiveUpdates();
        this.animateCounters();
    },

    deactivate() {
        this.isActive = false;
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    },

    startLiveUpdates() {
        // Simulate live data updates
        this.updateInterval = setInterval(() => {
            if (!this.isActive) return;

            // Simulate seat filling
            const fillRate = Math.random() * 50 + 10;
            this.liveData.filledSeats = Math.min(
                this.liveData.filledSeats + fillRate,
                this.liveData.totalSeats * 0.65
            );

            // Simulate online users
            this.liveData.onlineUsers = Math.floor(1500 + Math.random() * 500);

            // Update predictions counter
            this.liveData.predictionsToday += Math.floor(Math.random() * 3);

            // Update category data
            Object.keys(this.categoryData).forEach(cat => {
                const rate = Math.random() * 20;
                this.categoryData[cat].filled = Math.min(
                    this.categoryData[cat].filled + rate,
                    this.categoryData[cat].total * 0.65
                );
            });

            this.liveData.lastUpdated = new Date();
            this.updateDisplay();

        }, 3000);
    },

    animateCounters() {
        const counters = document.querySelectorAll('.counter-value');

        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const duration = 2000;
            const start = 0;
            const startTime = performance.now();

            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Easing function
                const easeOutExpo = 1 - Math.pow(2, -10 * progress);
                const current = Math.floor(start + (target - start) * easeOutExpo);

                counter.textContent = current.toLocaleString('en-IN');

                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };

            requestAnimationFrame(animate);
        });
    },

    updateDisplay() {
        // Update main counters
        const filledEl = document.getElementById('filled-seats');
        const usersEl = document.getElementById('online-users');
        const predictionsEl = document.getElementById('predictions-count');

        if (filledEl) {
            filledEl.textContent = Math.floor(this.liveData.filledSeats).toLocaleString('en-IN');
        }
        if (usersEl) {
            usersEl.textContent = this.liveData.onlineUsers.toLocaleString('en-IN');
        }
        if (predictionsEl) {
            predictionsEl.textContent = this.liveData.predictionsToday.toLocaleString('en-IN');
        }

        // Update progress bars
        this.updateProgressBars();

        // Update timestamp
        const timestampEl = document.getElementById('last-updated');
        if (timestampEl) {
            timestampEl.textContent = this.liveData.lastUpdated.toLocaleTimeString('en-IN');
        }
    },

    updateProgressBars() {
        Object.keys(this.categoryData).forEach(cat => {
            const bar = document.getElementById(`progress-${cat.toLowerCase()}`);
            if (bar) {
                const percent = (this.categoryData[cat].filled / this.categoryData[cat].total) * 100;
                bar.style.width = `${percent}%`;
            }
        });
    },

    getTimeRemaining(date) {
        const now = new Date();
        const diff = date - now;

        if (diff <= 0) return { expired: true };

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        return { days, hours, minutes, expired: false };
    },

    renderDashboard() {
        // Find or create dashboard section
        let section = document.getElementById('dashboard-section');

        if (!section) {
            section = document.createElement('div');
            section.id = 'dashboard-section';
            section.className = 'dashboard-section';

            // Insert after chat container
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.appendChild(section);
            }
        }

        const nextEvent = this.importantDates[0];
        const timeRemaining = this.getTimeRemaining(nextEvent.date);

        section.innerHTML = `
            <div class="dashboard-header">
                <h2>📊 Live Counselling Dashboard</h2>
                <div class="live-indicator">
                    <span class="pulse-dot"></span>
                    <span>LIVE</span>
                </div>
            </div>
            
            <!-- Countdown Timer -->
            <div class="countdown-section">
                <div class="countdown-event">${nextEvent.event}</div>
                <div class="countdown-timer">
                    <div class="countdown-unit">
                        <span class="countdown-value" id="countdown-days">${timeRemaining.days}</span>
                        <span class="countdown-label">Days</span>
                    </div>
                    <div class="countdown-separator">:</div>
                    <div class="countdown-unit">
                        <span class="countdown-value" id="countdown-hours">${timeRemaining.hours}</span>
                        <span class="countdown-label">Hours</span>
                    </div>
                    <div class="countdown-separator">:</div>
                    <div class="countdown-unit">
                        <span class="countdown-value" id="countdown-mins">${timeRemaining.minutes}</span>
                        <span class="countdown-label">Mins</span>
                    </div>
                </div>
            </div>
            
            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card gradient-green">
                    <div class="stat-icon">🎓</div>
                    <div class="stat-info">
                        <span class="stat-value counter-value" data-target="${this.liveData.totalSeats}" id="total-seats">${this.liveData.totalSeats.toLocaleString('en-IN')}</span>
                        <span class="stat-label">Total Seats</span>
                    </div>
                </div>
                
                <div class="stat-card gradient-blue">
                    <div class="stat-icon">✅</div>
                    <div class="stat-info">
                        <span class="stat-value" id="filled-seats">0</span>
                        <span class="stat-label">Seats Filled</span>
                    </div>
                    <div class="stat-trend up">↑ Live</div>
                </div>
                
                <div class="stat-card gradient-purple">
                    <div class="stat-icon">👥</div>
                    <div class="stat-info">
                        <span class="stat-value" id="online-users">0</span>
                        <span class="stat-label">Students Online</span>
                    </div>
                    <div class="stat-trend neutral">●</div>
                </div>
                
                <div class="stat-card gradient-orange">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-info">
                        <span class="stat-value" id="predictions-count">0</span>
                        <span class="stat-label">Predictions Today</span>
                    </div>
                    <div class="stat-trend up">↑</div>
                </div>
            </div>
            
            <!-- Category Progress -->
            <div class="category-progress-section">
                <h3>📈 Category-wise Seat Filling Progress</h3>
                <div class="progress-list">
                    ${Object.entries(this.categoryData).map(([cat, data]) => `
                        <div class="progress-item">
                            <div class="progress-header">
                                <span class="progress-label">${cat}</span>
                                <span class="progress-value">${Math.floor(data.filled).toLocaleString('en-IN')} / ${data.total.toLocaleString('en-IN')}</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill ${cat.toLowerCase()}" id="progress-${cat.toLowerCase()}" style="width: 0%"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Timeline -->
            <div class="timeline-section">
                <h3>📅 Important Dates</h3>
                <div class="timeline">
                    ${this.importantDates.map((item, idx) => {
            const remaining = this.getTimeRemaining(item.date);
            const statusClass = remaining.expired ? 'completed' : (idx === 0 ? 'active' : 'upcoming');
            return `
                            <div class="timeline-item ${statusClass}">
                                <div class="timeline-dot"></div>
                                <div class="timeline-content">
                                    <div class="timeline-event">${item.event}</div>
                                    <div class="timeline-date">${item.date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</div>
                                    ${!remaining.expired ? `<div class="timeline-remaining">${remaining.days} days left</div>` : '<div class="timeline-remaining completed">Completed</div>'}
                                </div>
                            </div>
                        `;
        }).join('')}
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="quick-actions">
                <button class="action-btn primary" onclick="DashboardComponent.goToPredictor()">
                    🎯 Predict Your College
                </button>
                <button class="action-btn secondary" onclick="DashboardComponent.showDocuments()">
                    📁 Document Checklist
                </button>
                <button class="action-btn tertiary" onclick="DashboardComponent.downloadReport()">
                    📄 Download Guide
                </button>
            </div>
            
            <div class="dashboard-footer">
                <span>Last updated: <span id="last-updated">${this.liveData.lastUpdated.toLocaleTimeString('en-IN')}</span></span>
                <span class="data-note">* Data is simulated for demonstration</span>
            </div>
        `;

        // Start countdown timer update
        this.startCountdownTimer();
    },

    startCountdownTimer() {
        setInterval(() => {
            const nextEvent = this.importantDates[0];
            const remaining = this.getTimeRemaining(nextEvent.date);

            const daysEl = document.getElementById('countdown-days');
            const hoursEl = document.getElementById('countdown-hours');
            const minsEl = document.getElementById('countdown-mins');

            if (daysEl) daysEl.textContent = remaining.days;
            if (hoursEl) hoursEl.textContent = remaining.hours;
            if (minsEl) minsEl.textContent = remaining.minutes;

        }, 60000); // Update every minute
    },

    goToPredictor() {
        // Navigate to predictor
        document.querySelector('[data-feature="predictor"]')?.click();
    },

    showDocuments() {
        // Navigate to documents
        document.querySelector('[data-feature="documents"]')?.click();
    },

    downloadReport() {
        // Show download modal or trigger PDF
        alert('📄 Download feature available after predictions!');
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    DashboardComponent.init();
});

// Export
window.DashboardComponent = DashboardComponent;
