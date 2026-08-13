// Live Counselling Dashboard Component - Premium Interactive & UI/UX Experience
// Real-time statistics, interactive SVG seat visualizers, live scrolling candidate streams,
// mini admission simulators, and browser-synthesized audio micro-interactions.

const DashboardComponent = {
    isActive: false,
    animationFrameId: null,
    updateInterval: null,
    activityInterval: null,
    audioCtx: null,

    // Simulated live state
    liveData: {
        totalSeats: 228450,
        filledSeats: 112450,
        onlineUsers: 1420,
        predictionsToday: 843,
        lastUpdated: new Date()
    },

    // Category-wise statistics
    categoryData: {
        GM: { total: 114225, filled: 58210, color: '#10a37f', label: 'General Merit' },
        OBC: { total: 68535, filled: 31400, color: '#3b82f6', label: 'Other Backward Classes' },
        SC: { total: 34267, filled: 17340, color: '#8b5cf6', label: 'Scheduled Castes' },
        ST: { total: 11423, filled: 5500, color: '#f59e0b', label: 'Scheduled Tribes' }
    },

    activeFilterCategory: 'ALL', // ALL or GM, OBC, SC, ST

    // Important dates
    importantDates: [
        { event: 'KEA KCET Round 1 Option Entry', date: new Date(Date.now() + 86400000 * 5), status: 'active' },
        { event: 'KEA KCET Mock Seat Allotment', date: new Date(Date.now() + 86400000 * 8), status: 'upcoming' },
        { event: 'JoSAA JEE Round 1 Seat Allotment', date: new Date(Date.now() + 86400000 * 12), status: 'upcoming' },
        { event: 'NEET UG Counselling Choice Filling', date: new Date(Date.now() + 86400000 * 15), status: 'upcoming' },
        { event: 'KEA Document Verification Ends', date: new Date(Date.now() - 86400000 * 2), status: 'completed' }
    ],

    // Mock candidate pool for live streaming feed
    mockCandidates: [
        { name: 'Basavaraj Gowda', exam: 'KCET', rank: 1420, clg: 'RV College of Engineering', branch: 'Computer Science' },
        { name: 'Aniket R.', exam: 'JEE Main', rank: 3401, clg: 'IIIT Dharwad', branch: 'Data Science' },
        { name: 'Bhumika S.', exam: 'KCET', rank: 4502, clg: 'BMS College of Engineering', branch: 'Information Science' },
        { name: 'Karthik Gowda', exam: 'KCET', rank: 1202, clg: 'MS Ramaiah Institute of Technology', branch: 'Electronics & Communication' },
        { name: 'Prathiksha K.', exam: 'NEET UG', rank: 890, clg: 'Bangalore Medical College', branch: 'MBBS' },
        { name: 'Preetham V.', exam: 'JEE Advanced', rank: 1045, clg: 'IIT Dharwad', branch: 'Computer Science' },
        { name: 'Sneha Patil', exam: 'KCET', rank: 2560, clg: 'RV College of Engineering', branch: 'Aerospace Engineering' },
        { name: 'Manoj Kumar', exam: 'NEET UG', rank: 3410, clg: 'St. John\'s Medical College', branch: 'MBBS' },
        { name: 'Shruti M.', exam: 'KCET', rank: 6200, clg: 'PESSIT Bangalore', branch: 'Computer Science' },
        { name: 'Vinayak M.', exam: 'JEE Main', rank: 4122, clg: 'NITK Surathkal', branch: 'Mechanical Engineering' }
    ],

    init() {
        this.renderDashboard();
        this.setupEventListeners();
        console.log('📊 Premium interactive dashboard initialized');
    },

    // ─── Web Audio API Sound Synthesizer ───────────────────────────────────────
    initAudio() {
        if (this.audioCtx) return;
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioContext();
        } catch (e) {
            console.warn('Web Audio API not supported in this browser.');
        }
    },

    playChime(type = 'click') {
        this.initAudio();
        if (!this.audioCtx) return;

        // Resume context if suspended (browser security policy)
        if (this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }

        const osc = this.audioCtx.createOscillator();
        const gainNode = this.audioCtx.createGain();
        osc.connect(gainNode);
        gainNode.connect(this.audioCtx.destination);

        const now = this.audioCtx.currentTime;

        if (type === 'click') {
            // Soft pleasant woodblock/bell tone
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, now); // A5 note
            gainNode.gain.setValueAtTime(0.08, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
            osc.start(now);
            osc.stop(now + 0.15);
        } else if (type === 'success') {
            // Double ascending chime (pleasant win sound)
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(523.25, now); // C5
            osc.frequency.setValueAtTime(659.25, now + 0.08); // E5
            osc.frequency.setValueAtTime(783.99, now + 0.16); // G5
            gainNode.gain.setValueAtTime(0.1, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
            osc.start(now);
            osc.stop(now + 0.4);
        } else if (type === 'hover') {
            // Very soft click tick
            osc.type = 'sine';
            osc.frequency.setValueAtTime(1200, now);
            gainNode.gain.setValueAtTime(0.02, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.03);
            osc.start(now);
            osc.stop(now + 0.03);
        }
    },

    setupEventListeners() {
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
        this.triggerInitialAnimations();
        
        // Resume simulation stream
        this.startActivityStream();
    },

    deactivate() {
        this.isActive = false;
        if (this.updateInterval) clearInterval(this.updateInterval);
        if (this.activityInterval) clearInterval(this.activityInterval);
    },

    startLiveUpdates() {
        this.updateInterval = setInterval(() => {
            if (!this.isActive) return;

            // Increment seats filled
            const additionalSeats = Math.floor(Math.random() * 8) + 2;
            this.liveData.filledSeats = Math.min(
                this.liveData.filledSeats + additionalSeats,
                this.liveData.totalSeats * 0.92
            );

            // Online count oscillation
            this.liveData.onlineUsers = Math.floor(1200 + Math.random() * 350);

            // Predictions total increase
            this.liveData.predictionsToday += Math.floor(Math.random() * 2) + 1;

            // Increment specific categories
            const categories = Object.keys(this.categoryData);
            const randomCat = categories[Math.floor(Math.random() * categories.length)];
            this.categoryData[randomCat].filled = Math.min(
                this.categoryData[randomCat].filled + additionalSeats,
                this.categoryData[randomCat].total * 0.90
            );

            this.liveData.lastUpdated = new Date();
            this.updateDisplay();
        }, 4000);
    },

    startActivityStream() {
        if (this.activityInterval) clearInterval(this.activityInterval);
        
        this.activityInterval = setInterval(() => {
            if (!this.isActive) return;
            this.pushLiveActivity();
        }, 5000);
    },

    pushLiveActivity() {
        const streamContainer = document.getElementById('activity-feed-container');
        if (!streamContainer) return;

        // Choose random mock candidate
        const cand = this.mockCandidates[Math.floor(Math.random() * this.mockCandidates.length)];
        const bubble = document.createElement('div');
        bubble.className = 'live-activity-bubble';
        
        const timestamp = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        const badges = {
            'KCET': 'kcet-badge',
            'JEE Main': 'jee-badge',
            'JEE Advanced': 'jee-badge',
            'NEET UG': 'neet-badge'
        };
        const badgeClass = badges[cand.exam] || 'kcet-badge';

        bubble.innerHTML = `
            <div class="bubble-header">
                <span class="bubble-tag ${badgeClass}">${cand.exam}</span>
                <span class="bubble-time">${timestamp}</span>
            </div>
            <p class="bubble-msg">
                <strong>${cand.name}</strong> (Rank #${cand.rank.toLocaleString('en-IN')}) secured seat prediction fit at 
                <span class="clg-highlight">${cand.clg}</span> in <em>${cand.branch}</em>.
            </p>
        `;

        streamContainer.appendChild(bubble);
        
        // Maintain last 8 bubbles in list
        const bubbles = streamContainer.querySelectorAll('.live-activity-bubble');
        if (bubbles.length > 8) {
            bubbles[0].classList.add('fade-out');
            setTimeout(() => bubbles[0].remove(), 400);
        }

        // Smooth scroll to bottom
        streamContainer.scrollTo({
            top: streamContainer.scrollHeight,
            behavior: 'smooth'
        });
    },

    animateCounters() {
        const counters = document.querySelectorAll('.counter-value');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            if (isNaN(target)) return;

            let start = 0;
            const duration = 1500;
            const startTime = performance.now();

            const run = (now) => {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const ease = 1 - Math.pow(2, -10 * progress); // Ease out exponential
                const current = Math.floor(start + (target - start) * ease);
                
                counter.textContent = current.toLocaleString('en-IN');
                
                if (progress < 1) {
                    requestAnimationFrame(run);
                }
            };
            requestAnimationFrame(run);
        });
    },

    triggerInitialAnimations() {
        // Redraw Donut Chart with a delay for visual impact
        setTimeout(() => {
            this.drawDonutChart();
            // Seed a few initial stream items
            for (let i = 0; i < 3; i++) {
                setTimeout(() => this.pushLiveActivity(), i * 800);
            }
        }, 150);
    },

    updateDisplay() {
        // Update live counters
        const filledEl = document.getElementById('filled-seats');
        const usersEl = document.getElementById('online-users');
        const predictionsEl = document.getElementById('predictions-count');
        const stampEl = document.getElementById('last-updated');

        if (filledEl) filledEl.textContent = Math.floor(this.liveData.filledSeats).toLocaleString('en-IN');
        if (usersEl) usersEl.textContent = this.liveData.onlineUsers.toLocaleString('en-IN');
        if (predictionsEl) predictionsEl.textContent = this.liveData.predictionsToday.toLocaleString('en-IN');
        if (stampEl) stampEl.textContent = this.liveData.lastUpdated.toLocaleTimeString('en-IN');

        // Refresh SVG Donut and Category values
        this.drawDonutChart();
        this.updateCategoryDetailPanel();
    },

    // ─── SVG Interactive Donut Chart Generator ────────────────────────────────
    drawDonutChart() {
        const svgContainer = document.getElementById('interactive-donut-svg');
        if (!svgContainer) return;

        const radius = 60;
        const circ = 2 * Math.PI * radius; // 376.99
        let currentOffset = 0;

        let gmFilled = this.categoryData.GM.filled;
        let obcFilled = this.categoryData.OBC.filled;
        let scFilled = this.categoryData.SC.filled;
        let stFilled = this.categoryData.ST.filled;

        const totalFilled = gmFilled + obcFilled + scFilled + stFilled;
        if (totalFilled === 0) return;

        const dataSlices = [
            { category: 'GM', filled: gmFilled, color: this.categoryData.GM.color },
            { category: 'OBC', filled: obcFilled, color: this.categoryData.OBC.color },
            { category: 'SC', filled: scFilled, color: this.categoryData.SC.color },
            { category: 'ST', filled: stFilled, color: this.categoryData.ST.color }
        ];

        let pathsHTML = '';

        dataSlices.forEach(slice => {
            const ratio = slice.filled / totalFilled;
            const strokeLength = circ * ratio;
            const strokeOffset = circ - currentOffset;
            currentOffset += strokeLength;

            const isActive = this.activeFilterCategory === 'ALL' || this.activeFilterCategory === slice.category;
            const opacity = isActive ? '1' : '0.2';
            const strokeW = isActive ? '15' : '10';

            pathsHTML += `
                <circle 
                    cx="100" cy="100" r="${radius}"
                    fill="transparent"
                    stroke="${slice.color}"
                    stroke-width="${strokeW}"
                    stroke-dasharray="${strokeLength} ${circ}"
                    stroke-dashoffset="${strokeOffset}"
                    transform="rotate(-90 100 100)"
                    style="transition: all 0.5s ease; cursor:pointer; opacity: ${opacity};"
                    onclick="DashboardComponent.filterCategory('${slice.category}')"
                    onmouseenter="DashboardComponent.playChime('hover')"
                />
            `;
        });

        // Center overlay showing total filled percent of overall seats
        const overallPercent = Math.round((this.liveData.filledSeats / this.liveData.totalSeats) * 100);

        svgContainer.innerHTML = `
            ${pathsHTML}
            <circle cx="100" cy="100" r="${radius - 12}" fill="var(--bg-secondary)" />
            <text x="100" y="96" text-anchor="middle" font-size="18" font-weight="800" fill="var(--text-primary)" style="font-family:'Inter', sans-serif;">
                ${overallPercent}%
            </text>
            <text x="100" y="114" text-anchor="middle" font-size="10" font-weight="600" fill="var(--text-muted)" style="letter-spacing:0.5px; text-transform:uppercase; font-family:'Inter', sans-serif;">
                Seats Filled
            </text>
        `;
    },

    filterCategory(cat) {
        this.playChime('click');
        if (this.activeFilterCategory === cat) {
            this.activeFilterCategory = 'ALL';
        } else {
            this.activeFilterCategory = cat;
        }

        // Highlight selected buttons in dashboard
        document.querySelectorAll('.legend-chip-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.category === this.activeFilterCategory) {
                btn.classList.add('active');
            }
        });

        this.drawDonutChart();
        this.updateCategoryDetailPanel();
    },

    updateCategoryDetailPanel() {
        const detailPanel = document.getElementById('category-details-panel');
        if (!detailPanel) return;

        if (this.activeFilterCategory === 'ALL') {
            detailPanel.innerHTML = `
                <div class="all-categories-panel">
                    <p class="panel-desc">💡 <em>Click any slice on the Donut visualizer above or quota buttons to focus on specific category parameters and seat filling rates.</em></p>
                    <div class="category-bars-grid">
                        ${Object.entries(this.categoryData).map(([cat, data]) => {
                            const pct = Math.round((data.filled / data.total) * 100);
                            return `
                                <div class="category-row-bar">
                                    <div class="bar-header">
                                        <strong>${cat} (${data.label})</strong>
                                        <span>${pct}% filled (${data.filled.toLocaleString('en-IN')} / ${data.total.toLocaleString('en-IN')})</span>
                                    </div>
                                    <div class="bar-track">
                                        <div class="bar-fill" style="width: ${pct}%; background:${data.color};"></div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        } else {
            const cat = this.activeFilterCategory;
            const data = this.categoryData[cat];
            const pct = Math.round((data.filled / data.total) * 100);
            const remaining = data.total - data.filled;

            detailPanel.innerHTML = `
                <div class="single-category-panel animated fadeIn" style="border-left: 4px solid ${data.color};">
                    <div class="panel-top-row">
                        <h4>${data.label} Quota Status (${cat})</h4>
                        <span class="badge-pill" style="background:${data.color}20; color:${data.color};">${pct}% Occupied</span>
                    </div>
                    <div class="panel-details-grid">
                        <div class="p-detail-item">
                            <small>Total Quota Seats</small>
                            <h3>${data.total.toLocaleString('en-IN')}</h3>
                        </div>
                        <div class="p-detail-item">
                            <small>Seats Allocated</small>
                            <h3>${data.filled.toLocaleString('en-IN')}</h3>
                        </div>
                        <div class="p-detail-item">
                            <small>Seats Vacant</small>
                            <h3 style="color:#22c55e;">${remaining.toLocaleString('en-IN')}</h3>
                        </div>
                    </div>
                    <p class="quota-note">🛡️ Admission probabilities for **${cat}** candidates are actively computed based on these vacancies during live round iterations.</p>
                </div>
            `;
        }
    },

    // ─── Seat Probability Live Mini-Widget ────────────────────────────────────
    simulateProbability() {
        this.playChime('success');
        
        const rankInput = document.getElementById('mini-rank-input');
        const categorySelect = document.getElementById('mini-category-select');
        const examSelect = document.getElementById('mini-exam-select');

        const rank = parseInt(rankInput.value);
        if (isNaN(rank) || rank < 1) {
            alert('Please enter a valid rank.');
            return;
        }

        const exam = examSelect.value;
        const category = categorySelect.value;

        // Simple mock calculations based on standard benchmarks
        let probability = 100;

        if (exam === 'KCET') {
            if (rank < 2000) probability = 98;
            else if (rank < 8000) probability = 85;
            else if (rank < 25000) probability = 62;
            else if (rank < 60000) probability = 44;
            else probability = 20;
        } else if (exam === 'JEE') {
            if (rank < 1000) probability = 96;
            else if (rank < 5000) probability = 82;
            else if (rank < 15000) probability = 58;
            else if (rank < 40000) probability = 38;
            else probability = 15;
        } else { // NEET
            if (rank < 500) probability = 95;
            else if (rank < 3000) probability = 78;
            else if (rank < 10000) probability = 52;
            else if (rank < 30000) probability = 30;
            else probability = 10;
        }

        // Quota adjustments
        if (category === 'OBC') probability = Math.min(100, probability + 5);
        if (category === 'SC') probability = Math.min(100, probability + 12);
        if (category === 'ST') probability = Math.min(100, probability + 15);

        // Render circular dynamic progress widget
        const outcomeContainer = document.getElementById('mini-sim-outcome');
        if (!outcomeContainer) return;

        outcomeContainer.style.display = 'block';
        
        let strokeColor = '#ef4444';
        let feedbackText = '🔴 Dream (Low probability. Keep options wide.)';
        if (probability >= 80) {
            strokeColor = '#10a37f';
            feedbackText = '🟢 Safe (Highly likely to secure tier-1 seat!)';
        } else if (probability >= 45) {
            strokeColor = '#f59e0b';
            feedbackText = '🟡 Moderate (Good probability. Keep moderate backups.)';
        }

        outcomeContainer.innerHTML = `
            <div class="sim-outcome-card animate-zoom">
                <div class="sim-svg-wrapper">
                    <svg width="80" height="80" viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="16" fill="transparent" stroke="var(--border-color)" stroke-width="3" />
                        <circle class="circle-fill-anim" cx="18" cy="18" r="16" fill="transparent" 
                                stroke="${strokeColor}" stroke-width="3.5"
                                stroke-dasharray="${probability} 100"
                                transform="rotate(-90 18 18)" />
                        <text x="18" y="21" text-anchor="middle" font-size="8" font-weight="800" fill="var(--text-primary)">${probability}%</text>
                    </svg>
                </div>
                <div class="sim-feedback">
                    <strong>Predicted Probability</strong>
                    <p class="sim-verdict">${feedbackText}</p>
                    <small>For premium custom counseling ordering, use the sidebar's full dedicated predictors!</small>
                </div>
            </div>
        `;
    },

    getTimeRemaining(date) {
        const now = new Date();
        const diff = date - now;

        if (diff <= 0) return { expired: true, days: 0, hours: 0, minutes: 0 };

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        return { days, hours, minutes, expired: false };
    },

    renderDashboard() {
        let section = document.getElementById('dashboard-section');
        if (!section) {
            section = document.createElement('div');
            section.id = 'dashboard-section';
            section.className = 'dashboard-section';
            const mainContent = document.querySelector('.main-content');
            if (mainContent) mainContent.appendChild(section);
        }

        const nextEvent = this.importantDates[0];
        const timeRemaining = this.getTimeRemaining(nextEvent.date);

        section.innerHTML = `
            <!-- Glassmorphic Header -->
            <div class="dashboard-premium-header">
                <div class="head-left">
                    <span class="premium-tag">⚡ AI-Powered Real-Time Feed</span>
                    <h2>📊 Live Counselling Analytics</h2>
                </div>
                <div class="live-indicator-pill">
                    <span class="pulsing-circle"></span>
                    <span>LIVE CONNECTED</span>
                </div>
            </div>

            <!-- Dashboard Columns Layout -->
            <div class="dashboard-columns-grid">
                
                <!-- COLUMN LEFT: Primary Stats and Donut Visualizer -->
                <div class="column-left">
                    
                    <!-- Stats cards -->
                    <div class="stats-premium-grid">
                        <div class="premium-stat-card" onmouseenter="DashboardComponent.playChime('hover')">
                            <span class="icon-wrap">🎓</span>
                            <div>
                                <h3 class="counter-value" data-target="${this.liveData.totalSeats}">0</h3>
                                <small>Total Quota Seats</small>
                            </div>
                        </div>
                        <div class="premium-stat-card glowing-border" onmouseenter="DashboardComponent.playChime('hover')">
                            <span class="icon-wrap" style="background:#10a37f15; color:#10a37f;">✅</span>
                            <div>
                                <h3 id="filled-seats">112,450</h3>
                                <small>Seats Allotted</small>
                            </div>
                            <span class="live-flash-tag">↑ live</span>
                        </div>
                        <div class="premium-stat-card" onmouseenter="DashboardComponent.playChime('hover')">
                            <span class="icon-wrap" style="background:#3b82f615; color:#3b82f6;">👥</span>
                            <div>
                                <h3 id="online-users">1,420</h3>
                                <small>Active Candidates</small>
                            </div>
                        </div>
                        <div class="premium-stat-card" onmouseenter="DashboardComponent.playChime('hover')">
                            <span class="icon-wrap" style="background:#f59e0b15; color:#f59e0b;">🎯</span>
                            <div>
                                <h3 id="predictions-count">843</h3>
                                <small>Predictions Run Today</small>
                            </div>
                        </div>
                    </div>

                    <!-- Interactive Donut and Category Status -->
                    <div class="counselling-seats-section">
                        <h3>📊 Quota Seat Allocation Distribution</h3>
                        <p class="sect-subtitle">Visual seat filling rates mapped to candidate categories. Tap sections to filter.</p>
                        
                        <div class="donut-visualizer-row">
                            <div class="donut-svg-holder">
                                <svg id="interactive-donut-svg" width="200" height="200" viewBox="0 0 200 200"></svg>
                            </div>
                            
                            <div class="donut-legend-holder">
                                <button class="legend-chip-btn active" data-category="ALL" onclick="DashboardComponent.filterCategory('ALL')">
                                    <span class="lg-dot" style="background:#475569;"></span>
                                    <strong>ALL</strong>
                                    <span>Global Overview</span>
                                </button>
                                ${Object.entries(this.categoryData).map(([cat, data]) => `
                                    <button class="legend-chip-btn" data-category="${cat}" onclick="DashboardComponent.filterCategory('${cat}')">
                                        <span class="lg-dot" style="background:${data.color};"></span>
                                        <strong>${cat}</strong>
                                        <span>${data.label}</span>
                                    </button>
                                `).join('')}
                            </div>
                        </div>

                        <!-- Category Details Panel -->
                        <div class="category-details-panel" id="category-details-panel"></div>
                    </div>

                    <!-- Mini Admission Simulator Widget -->
                    <div class="mini-simulator-section">
                        <div class="widget-header">
                            <span class="badge-mini">🎯 Mini-Tool</span>
                            <h3>⚡ Seat Probability Quick-Calculator</h3>
                        </div>
                        <p class="widget-desc">Test your admission likelihood instantaneously. Calculates rank probability curves.</p>
                        
                        <div class="mini-sim-form">
                            <div class="sim-group">
                                <label>Exam</label>
                                <select id="mini-exam-select">
                                    <option value="KCET">KCET (KEA)</option>
                                    <option value="JEE">JEE Main / Adv</option>
                                    <option value="NEET">NEET UG</option>
                                </select>
                            </div>
                            <div class="sim-group">
                                <label>Your Rank</label>
                                <input type="number" id="mini-rank-input" placeholder="e.g. 5000" min="1" value="4500" />
                            </div>
                            <div class="sim-group">
                                <label>Category</label>
                                <select id="mini-category-select">
                                    <option value="GM">GM (General)</option>
                                    <option value="OBC">OBC</option>
                                    <option value="SC">SC</option>
                                    <option value="ST">ST</option>
                                </select>
                            </div>
                            <button class="sim-submit-btn" onclick="DashboardComponent.simulateProbability()">
                                🚀 Calculate Chance
                            </button>
                        </div>

                        <div id="mini-sim-outcome" style="display:none; margin-top: 1rem;"></div>
                    </div>

                </div>

                <!-- COLUMN RIGHT: Real-time Live Feed and Timelines -->
                <div class="column-right">
                    
                    <!-- Countdown Panel -->
                    <div class="dashboard-countdown-card">
                        <small>📅 UPCOMING EVENT DETECTED</small>
                        <h4>${nextEvent.event}</h4>
                        <div class="live-countdown-grid">
                            <div class="timer-box">
                                <span class="time-num" id="countdown-days">${timeRemaining.days}</span>
                                <small>Days</small>
                            </div>
                            <div class="timer-colon">:</div>
                            <div class="timer-box">
                                <span class="time-num" id="countdown-hours">${timeRemaining.hours}</span>
                                <small>Hours</small>
                            </div>
                            <div class="timer-colon">:</div>
                            <div class="timer-box">
                                <span class="time-num" id="countdown-mins">${timeRemaining.minutes}</span>
                                <small>Mins</small>
                            </div>
                        </div>
                    </div>

                    <!-- Live Activity Stream Feed -->
                    <div class="counselling-feed-card">
                        <div class="feed-header">
                            <span class="live-dot"></span>
                            <h4>🔥 Real-Time Candidate Simulation Stream</h4>
                        </div>
                        <p class="feed-desc">Simulated real-time updates representing seat allotment outcomes and fits.</p>
                        
                        <div class="activity-feed-container" id="activity-feed-container">
                            <!-- Live transaction bubbles pushed dynamically -->
                        </div>
                    </div>

                    <!-- Glowing Journey Timeline -->
                    <div class="timeline-glowing-card">
                        <h3>📅 Active Counselling Schedule</h3>
                        <div class="timeline-trail">
                            ${this.importantDates.map((item, idx) => {
                                const remaining = this.getTimeRemaining(item.date);
                                const statusClass = remaining.expired ? 'expired' : (idx === 0 ? 'active' : 'upcoming');
                                return `
                                    <div class="timeline-trail-item ${statusClass}">
                                        <div class="trail-dot"></div>
                                        <div class="trail-body">
                                            <h5>${item.event}</h5>
                                            <span class="trail-date">⏱️ ${item.date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</span>
                                            ${!remaining.expired ? `<span class="trail-tag">${remaining.days} days left</span>` : '<span class="trail-tag completed">Done</span>'}
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>

                    <!-- Fast Entry Counseling Portals -->
                    <div class="fast-portals-card">
                        <h3>🚀 Dedicated Prediction Portals</h3>
                        <div class="portal-buttons-grid">
                            <button class="portal-nav-btn kcet" onclick="DashboardComponent.goToPredictor()">
                                🎯 KCET Prediction Portal
                            </button>
                            <button class="portal-nav-btn jee" onclick="DashboardComponent.goToJEE()">
                                🎓 JEE Predictor Portal
                            </button>
                            <button class="portal-nav-btn neet" onclick="DashboardComponent.goToNEET()">
                                🩺 NEET Predictor Portal
                            </button>
                        </div>
                    </div>

            </div>

            <!-- Interactive Karnataka Education Hubs Map Visualizer -->
            <div class="karnataka-map-premium-section" onmouseenter="playChime('hover')">
                <div class="map-section-header">
                    <span class="badge-mini">🗺️ Interactive GIS Hubs</span>
                    <h3>🏛️ Karnataka Major Higher Education Hubs</h3>
                    <p class="widget-desc">Click or hover over active glowing hubs to examine regional seat densities, average packages, and top campus clusters.</p>
                </div>
                
                <div class="map-layout-grid">
                    <div class="map-visualizer-holder">
                        <!-- Elegant abstract SVG Map representation of Karnataka with hot-spots -->
                        <svg viewBox="0 0 400 500" class="karnataka-svg-map">
                            <!-- Karnataka Outline (Abstract minimal representation) -->
                            <path d="M 120 40 L 190 20 L 240 60 L 260 120 L 220 180 L 200 220 L 230 260 L 250 320 L 220 380 L 180 430 L 140 450 L 110 420 L 110 380 L 130 320 L 120 280 L 90 250 L 80 180 L 100 130 L 100 80 Z" 
                                  fill="rgba(16, 163, 127, 0.03)" stroke="var(--border-color)" stroke-width="2.5" />
                                  
                            <!-- Bangalore Pulse Pin -->
                            <g class="map-pin" onclick="DashboardComponent.showHubDetails('Bangalore')">
                                <circle cx="210" cy="390" r="16" class="pulse-ring-slow" fill="rgba(16, 163, 127, 0.25)" />
                                <circle cx="210" cy="390" r="6" fill="#10a37f" />
                                <text x="222" y="394" class="map-pin-label">Bangalore</text>
                            </g>
                            
                            <!-- Mysore Pulse Pin -->
                            <g class="map-pin" onclick="DashboardComponent.showHubDetails('Mysore')">
                                <circle cx="160" cy="420" r="16" class="pulse-ring-slow" fill="rgba(59, 130, 246, 0.25)" />
                                <circle cx="160" cy="420" r="6" fill="#3b82f6" />
                                <text x="172" y="424" class="map-pin-label">Mysore</text>
                            </g>
                            
                            <!-- Dharwad/Hubli Pulse Pin -->
                            <g class="map-pin" onclick="DashboardComponent.showHubDetails('Dharwad')">
                                <circle cx="120" cy="220" r="16" class="pulse-ring-slow" fill="rgba(139, 92, 246, 0.25)" />
                                <circle cx="120" cy="220" r="6" fill="#8b5cf6" />
                                <text x="132" y="224" class="map-pin-label">Dharwad/Hubli</text>
                            </g>
                            
                            <!-- Mangalore Pulse Pin -->
                            <g class="map-pin" onclick="DashboardComponent.showHubDetails('Mangalore')">
                                <circle cx="100" cy="340" r="16" class="pulse-ring-slow" fill="rgba(245, 158, 11, 0.25)" />
                                <circle cx="100" cy="340" r="6" fill="#f59e0b" />
                                <text x="112" y="344" class="map-pin-label">Mangalore</text>
                            </g>
                            
                            <!-- Belagavi Pulse Pin -->
                            <g class="map-pin" onclick="DashboardComponent.showHubDetails('Belagavi')">
                                <circle cx="100" cy="150" r="16" class="pulse-ring-slow" fill="rgba(236, 72, 153, 0.25)" />
                                <circle cx="100" cy="150" r="6" fill="#ec4899" />
                                <text x="112" y="154" class="map-pin-label">Belagavi</text>
                            </g>
                        </svg>
                    </div>
                    
                    <div class="map-details-card" id="map-hub-details-card">
                        <!-- Populated dynamically -->
                    </div>
                </div>
            </div>

            <!-- Footer timestamps -->
            <div class="dashboard-premium-footer">
                <span>🔄 Simulated Data Stream &bull; Connected to RAG College Knowledge Base</span>
                <span>Last updated: <strong id="last-updated">${this.liveData.lastUpdated.toLocaleTimeString('en-IN')}</strong></span>
            </div>
        `;

        this.updateCategoryDetailPanel();
        this.startCountdownTimer();
        setTimeout(() => this.showHubDetails('Bangalore'), 150);
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
        }, 60000);
    },

    goToPredictor() {
        this.playChime('click');
        document.querySelector('[data-feature="predictor"]')?.click();
    },
    goToJEE() {
        this.playChime('click');
        document.querySelector('[data-feature="jee"]')?.click();
    },
    goToNEET() {
        this.playChime('click');
        document.querySelector('[data-feature="neet"]')?.click();
    },

    hubData: {
        Bangalore: {
            title: 'Silicon Valley Hub (Bangalore)',
            colleges: '72+ Engineering & Medical Campuses',
            packages: '₹6.5 - ₹48.0 LPA (Average: ₹9.8 LPA)',
            cutoffRange: '100 - 45,000 KCET Rank',
            accommodation: '540+ Government & Private Hostels',
            popularCampuses: 'RVCE, PESU, BMSCE, MSRIT, BMCRI',
            description: 'The highest density of Tier-1 campuses in South India, offering supreme industry integration, startup incubators, and direct technical placements.',
            color: '#10a37f'
        },
        Mysore: {
            title: 'Heritage Academic Hub (Mysore)',
            colleges: '18+ Campuses',
            packages: '₹4.5 - ₹24.0 LPA (Average: ₹7.2 LPA)',
            cutoffRange: '500 - 80,000 KCET Rank',
            accommodation: '120+ Hostels',
            popularCampuses: 'SJCE, NIE Mysore, MMCRI, Vidyavardhaka',
            description: 'Known for peaceful academic environments, strong research focus, traditional manufacturing, and mechanical engineering excellence.',
            color: '#3b82f6'
        },
        Dharwad: {
            title: 'North Karnataka Knowledge Hub (Dharwad/Hubli)',
            colleges: '14+ Campuses',
            packages: '₹5.0 - ₹35.0 LPA (Average: ₹7.8 LPA)',
            cutoffRange: '1,200 - 95,000 KCET Rank',
            accommodation: '98+ Hostels',
            popularCampuses: 'IIT Dharwad, IIIT Dharwad, KLS GIT, BVBCET',
            description: 'North Karnataka’s apex learning cluster, combining central institutes like IIT and IIIT with historical KEA-affiliated campuses.',
            color: '#8b5cf6'
        },
        Mangalore: {
            title: 'Coastal Education Hub (Mangalore/Surathkal)',
            colleges: '22+ Campuses',
            packages: '₹5.5 - ₹52.0 LPA (Average: ₹9.2 LPA)',
            cutoffRange: '200 - 65,000 KCET Rank',
            accommodation: '150+ Hostels',
            popularCampuses: 'NITK Surathkal, KMC Mangalore, NMAMIT, MITE',
            description: 'Apex academic standards along the coastline. Home to NITK Surathkal, offering high-level marine research, heavy tech, and medical excellence.',
            color: '#f59e0b'
        },
        Belagavi: {
            title: 'Border Industrial Hub (Belagavi)',
            colleges: '12+ Campuses',
            packages: '₹4.0 - ₹18.0 LPA (Average: ₹6.0 LPA)',
            cutoffRange: '2,500 - 110,000 KCET Rank',
            accommodation: '85+ Hostels',
            popularCampuses: 'VTU Headquarters, KLS GIT, AIT Belagavi, BIMS',
            description: 'Home of Visvesvaraya Technological University (VTU) governing all technical colleges in Karnataka. High core-engineering industrial interface.',
            color: '#ec4899'
        }
    },

    showHubDetails(hubName) {
        const hub = this.hubData[hubName];
        if (!hub) return;
        
        const card = document.getElementById('map-hub-details-card');
        if (!card) return;
        
        // Soft chime feedback
        this.playChime('click');

        card.innerHTML = `
            <div class="hub-details-wrapper animated fadeIn" style="border-left: 4px solid ${hub.color};">
                <div class="hub-title-row">
                    <span class="hub-badge" style="background: ${hub.color}15; color: ${hub.color}">${hub.title}</span>
                </div>
                <p class="hub-desc">${hub.description}</p>
                
                <div class="hub-stats-grid">
                    <div class="hub-stat-item">
                        <small>Average Package</small>
                        <strong style="color: ${hub.color}">${hub.packages}</strong>
                    </div>
                    <div class="hub-stat-item">
                        <small>Cutoff Threshold</small>
                        <strong>${hub.cutoffRange}</strong>
                    </div>
                    <div class="hub-stat-item">
                        <small>Campuses</small>
                        <strong>${hub.colleges}</strong>
                    </div>
                    <div class="hub-stat-item">
                        <small>Safe Hostels</small>
                        <strong>${hub.accommodation}</strong>
                    </div>
                </div>
                
                <div class="hub-campuses">
                    <small>🌟 Elite Institutions:</small>
                    <div class="campus-tags" style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px;">
                        ${hub.popularCampuses.split(', ').map(c => `<span class="campus-tag-item" style="background:${hub.color}08; border:1px solid ${hub.color}20; color: ${hub.color}; font-weight: 700; font-size: 11px; padding: 4px 8px; border-radius: 6px;">${c}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    DashboardComponent.init();
});

window.DashboardComponent = DashboardComponent;
