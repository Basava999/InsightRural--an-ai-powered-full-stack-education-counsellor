// Sidebar Component
const SidebarComponent = {
    init() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.themeToggle = document.getElementById('theme-toggle');

        this.profileBtn = document.getElementById('profile-btn');

        this.isOpen = false;
        this.setupEventListeners();
        this.setupClickOutside();
    },

    setupEventListeners() {
        // Sidebar toggle button
        this.sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleSidebar();
        });

        // Theme toggle
        this.themeToggle.addEventListener('click', () => {
            AppState.toggleTheme();
        });



        // Profile button
        this.profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showProfileModal();
        });


        // Navigation items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const feature = item.dataset.feature;

                // Update active state
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');

                // 🔹 COLLEGES - External link
                if (feature === "colleges") {
                    window.location.href = "../college/frontend/index.html";
                    return;
                }

                // 🔹 PREDICTOR SECTION
                if (feature === "predictor") {
                    this.showSection('predictor');
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 DASHBOARD SECTION
                if (feature === "dashboard") {
                    this.showSection('dashboard');
                    if (window.DashboardComponent) {
                        DashboardComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 DOCUMENTS SECTION
                if (feature === "documents") {
                    this.showSection('documents');
                    if (window.DocumentsComponent) {
                        DocumentsComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 CAREER COUNSELOR - Use chat with career context
                if (feature === "career") {
                    this.showSection('career');
                    if (window.innerWidth <= 768) this.hideSidebar();
                    // Dispatch event for career assessment
                    document.dispatchEvent(new CustomEvent('featureChange', { detail: 'career' }));
                    return;
                }

                // 🔹 VOICE COUNSELOR
                if (feature === "voice") {
                    this.showSection('voice');
                    if (window.VoiceCounselorComponent) {
                        VoiceCounselorComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 SCHOLARSHIPS AI AUTO-PILOT
                if (feature === "scholarships") {
                    this.showSection('scholarships');
                    if (window.ScholarshipComponent) {
                        ScholarshipComponent.init();
                    } else if (window.ScholarshipsComponent) {
                        ScholarshipsComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 HOSTELS EXPLORER
                if (feature === "hostels") {
                    this.showSection('hostels');
                    if (window.HostelExplorer) {
                        HostelExplorer.init();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 COUNSELING SUITE
                if (feature === "counseling") {
                    this.showSection('counseling');
                    if (window.CounselingSuiteComponent) {
                        CounselingSuiteComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 DOCUMENT SCANNER
                if (feature === "scanner") {
                    this.showSection('scanner');
                    if (window.DocumentScannerComponent) {
                        DocumentScannerComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 CAREER SIMULATOR
                if (feature === "simulator") {
                    this.showSection('simulator');
                    if (window.CareerSimulatorComponent) {
                        CareerSimulatorComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // 🔹 VIDEO AVATAR
                if (feature === "avatar") {
                    this.showSection('avatar');
                    if (window.VideoAvatarComponent) {
                        VideoAvatarComponent.activate();
                    }
                    if (window.innerWidth <= 768) this.hideSidebar();
                    return;
                }

                // Default: Hide all sections and show chat
                this.showSection('chat');

                if (feature) {
                    AppState.setFeature(feature);
                    if (window.innerWidth <= 768) {
                        this.hideSidebar();
                    }
                }
            });
        });
    },



    showProfileModal() {
        if (window.ModalComponent) {
            ModalComponent.showModal('profile-modal');
        }
    },

    showSection(sectionName) {
        // Hide all sections
        const chatContainer = document.querySelector('.chat-container');
        const predictorSection = document.getElementById('predictor-section');

        if (chatContainer) chatContainer.style.display = 'none';
        if (predictorSection) predictorSection.classList.remove('active');

        // Hide ALL feature sections (unified approach)
        ['dashboard', 'documents', 'career', 'voice', 'scanner', 'simulator', 'avatar', 'scholarships', 'hostels', 'counseling'].forEach(id => {
            const el = document.getElementById(`${id}-section`);
            if (el) {
                el.style.display = 'none';
                el.classList.remove('active');
            }
        });

        // Show requested section
        switch (sectionName) {
            case 'chat':
                if (chatContainer) chatContainer.style.display = '';
                break;
            case 'predictor':
                if (predictorSection) {
                    predictorSection.classList.add('active');
                    if (window.PredictorComponent) {
                        window.PredictorComponent.renderForm();
                    }
                }
                break;
            case 'dashboard': {
                const el = document.getElementById('dashboard-section');
                if (el) { el.style.display = 'block'; el.classList.add('active'); }
                break;
            }
            case 'documents': {
                const el = document.getElementById('documents-section');
                if (el) { el.style.display = 'block'; el.classList.add('active'); }
                break;
            }
            case 'career':
                this.showCareerSection();
                break;
            default: {
                // voice, scanner, simulator, avatar, scholarships, counseling
                const el = document.getElementById(`${sectionName}-section`);
                if (el) { el.style.display = 'block'; el.classList.add('active'); }
                break;
            }
        }

        // Dispatch feature change event
        document.dispatchEvent(new CustomEvent('featureChange', { detail: sectionName }));
    },

    showCareerSection() {
        // Use existing career section from HTML
        let careerSection = document.getElementById('career-section');

        if (careerSection) {
            careerSection.style.display = 'block';
            careerSection.classList.add('active');
            this.renderCareerAssessment(careerSection);
        }
    },

    renderCareerAssessment(container) {
        container.innerHTML = `
            <div class="career-header">
                <h2>🧭 AI Career Counselor</h2>
                <p>Discover your ideal engineering branch based on your interests</p>
            </div>
            
            <div class="career-assessment">
                <div class="assessment-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="career-progress" style="width: 0%"></div>
                    </div>
                    <span id="question-counter">Question 1 of 5</span>
                </div>
                
                <div id="question-container">
                    <!-- Questions will be rendered here -->
                </div>
                
                <div id="career-results" style="display: none;">
                    <!-- Results will be shown here -->
                </div>
            </div>
        `;

        this.addCareerStyles();
        this.initCareerAssessment();
    },

    careerQuestions: [
        {
            id: 1,
            question: "What do you enjoy doing in your free time?",
            options: [
                { text: "Coding or using computers", branches: ["CSE", "ISE", "AIML"] },
                { text: "Building or fixing things", branches: ["MECH", "ECE", "EEE"] },
                { text: "Reading about science/nature", branches: ["BIOTECH", "CHEM"] },
                { text: "Planning and organizing", branches: ["CIVIL", "ISE"] }
            ]
        },
        {
            id: 2,
            question: "Which subject interests you the most?",
            options: [
                { text: "Mathematics & Logic", branches: ["CSE", "AIML", "DS"] },
                { text: "Physics & Mechanics", branches: ["MECH", "ECE", "EEE"] },
                { text: "Chemistry & Biology", branches: ["BIOTECH", "CHEM"] },
                { text: "Design & Creativity", branches: ["CIVIL", "MECH"] }
            ]
        },
        {
            id: 3,
            question: "How do you prefer to work?",
            options: [
                { text: "Independently on a computer", branches: ["CSE", "ISE", "DS"] },
                { text: "In a team building things", branches: ["MECH", "CIVIL", "ECE"] },
                { text: "Research and experimentation", branches: ["BIOTECH", "AIML", "CHEM"] },
                { text: "Mix of desk and field work", branches: ["EEE", "CIVIL"] }
            ]
        },
        {
            id: 4,
            question: "What kind of problems do you like solving?",
            options: [
                { text: "Puzzles and logical challenges", branches: ["CSE", "AIML", "DS"] },
                { text: "How things work/break", branches: ["MECH", "ECE", "EEE"] },
                { text: "Environmental/health issues", branches: ["BIOTECH", "CHEM", "CIVIL"] },
                { text: "Data and patterns", branches: ["DS", "ISE"] }
            ]
        },
        {
            id: 5,
            question: "What's most important to you in a career?",
            options: [
                { text: "High salary and growth", branches: ["CSE", "AIML", "DS"] },
                { text: "Stability and job security", branches: ["EEE", "CIVIL", "MECH"] },
                { text: "Making a difference", branches: ["BIOTECH", "CIVIL", "CHEM"] },
                { text: "Innovation and creativity", branches: ["CSE", "AIML", "ECE"] }
            ]
        }
    ],

    branchProfiles: {
        CSE: { name: "Computer Science & Engineering", icon: "💻", salary: "8-25 LPA", growth: "Very High" },
        ISE: { name: "Information Science", icon: "🖥️", salary: "7-20 LPA", growth: "High" },
        ECE: { name: "Electronics & Communication", icon: "📡", salary: "6-18 LPA", growth: "High" },
        EEE: { name: "Electrical & Electronics", icon: "⚡", salary: "6-15 LPA", growth: "Moderate" },
        MECH: { name: "Mechanical Engineering", icon: "⚙️", salary: "5-15 LPA", growth: "Moderate" },
        CIVIL: { name: "Civil Engineering", icon: "🏗️", salary: "4-12 LPA", growth: "Moderate" },
        AIML: { name: "AI & Machine Learning", icon: "🤖", salary: "10-30 LPA", growth: "Very High" },
        DS: { name: "Data Science", icon: "📊", salary: "8-25 LPA", growth: "Very High" },
        BIOTECH: { name: "Biotechnology", icon: "🧬", salary: "4-12 LPA", growth: "Moderate" },
        CHEM: { name: "Chemical Engineering", icon: "🧪", salary: "5-14 LPA", growth: "Moderate" }
    },

    currentQuestion: 0,
    userResponses: [],
    branchScores: {},

    initCareerAssessment() {
        this.currentQuestion = 0;
        this.userResponses = [];
        this.branchScores = {};
        this.renderQuestion();
    },

    renderQuestion() {
        const container = document.getElementById('question-container');
        const resultsContainer = document.getElementById('career-results');

        if (this.currentQuestion >= this.careerQuestions.length) {
            container.style.display = 'none';
            resultsContainer.style.display = 'block';
            this.showCareerResults();
            return;
        }

        container.style.display = 'block';
        resultsContainer.style.display = 'none';

        const q = this.careerQuestions[this.currentQuestion];
        const progressPercent = ((this.currentQuestion) / this.careerQuestions.length) * 100;

        document.getElementById('career-progress').style.width = `${progressPercent}%`;
        document.getElementById('question-counter').textContent = `Question ${this.currentQuestion + 1} of ${this.careerQuestions.length}`;

        container.innerHTML = `
            <div class="question-card">
                <h3>${q.question}</h3>
                <div class="options-grid">
                    ${q.options.map((opt, idx) => `
                        <button class="option-btn" onclick="SidebarComponent.selectOption(${idx})">
                            ${opt.text}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    },

    selectOption(optionIndex) {
        const q = this.careerQuestions[this.currentQuestion];
        const selectedOption = q.options[optionIndex];

        // Add scores for branches
        selectedOption.branches.forEach(branch => {
            this.branchScores[branch] = (this.branchScores[branch] || 0) + 2;
        });

        this.userResponses.push({ question_id: q.id, option_index: optionIndex });
        this.currentQuestion++;
        this.renderQuestion();

        // Add XP
        if (window.ProgressComponent) {
            ProgressComponent.addXP(5);
        }
    },

    showCareerResults() {
        const resultsContainer = document.getElementById('career-results');

        // Calculate top matches
        const matches = Object.entries(this.branchScores)
            .map(([code, score]) => ({
                code,
                ...this.branchProfiles[code],
                score,
                matchPercent: Math.min(100, Math.round((score / 10) * 100) + 20)
            }))
            .sort((a, b) => b.score - a.score)
            .slice(0, 5);

        document.getElementById('career-progress').style.width = '100%';
        document.getElementById('question-counter').textContent = 'Assessment Complete!';

        resultsContainer.innerHTML = `
            <div class="results-card">
                <div class="results-header">
                    <h3>🎉 Your Career Matches</h3>
                    <p>Based on your interests and aptitudes</p>
                </div>
                
                <div class="match-list">
                    ${matches.map((m, idx) => `
                        <div class="match-item ${idx === 0 ? 'top-match' : ''}">
                            <div class="match-rank">${idx + 1}</div>
                            <div class="match-icon">${m.icon}</div>
                            <div class="match-info">
                                <strong>${m.name}</strong>
                                <div class="match-stats">
                                    <span>💰 ${m.salary}</span>
                                    <span>📈 ${m.growth} Growth</span>
                                </div>
                            </div>
                            <div class="match-percent ${idx === 0 ? 'high' : ''}">${m.matchPercent}%</div>
                        </div>
                    `).join('')}
                </div>

                <div class="results-actions">
                    <button class="action-btn primary" onclick="SidebarComponent.goToPredictorWithBranch('${matches[0]?.code}')">
                        🎯 Predict Colleges for ${matches[0]?.code}
                    </button>
                    <button class="action-btn secondary" onclick="SidebarComponent.initCareerAssessment()">
                        🔄 Retake Assessment
                    </button>
                </div>
            </div>
        `;

        // Unlock badge
        if (window.ProgressComponent) {
            ProgressComponent.addXP(30);
        }
    },

    goToPredictorWithBranch(branchCode) {
        this.showSection('predictor');
        // Pre-select the branch in predictor if possible
        setTimeout(() => {
            const checkbox = document.querySelector(`input[value="${branchCode}"]`);
            if (checkbox) checkbox.checked = true;
        }, 100);
    },

    addCareerStyles() {
        if (document.getElementById('career-styles')) return;

        const style = document.createElement('style');
        style.id = 'career-styles';
        style.textContent = `
            .career-section {
                display: none;
                padding: 2rem;
                max-width: 700px;
                margin: 0 auto;
            }
            
            .career-section.active {
                display: block;
            }
            
            .career-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .career-header h2 {
                font-size: 1.8rem;
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .assessment-progress {
                margin-bottom: 2rem;
            }
            
            .assessment-progress .progress-bar {
                height: 8px;
                background: var(--bg-tertiary);
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 0.5rem;
            }
            
            .assessment-progress .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
                transition: width 0.3s ease;
            }
            
            #question-counter {
                font-size: 0.85rem;
                color: var(--text-secondary);
            }
            
            .question-card {
                background: var(--bg-secondary);
                border-radius: 20px;
                padding: 2rem;
                text-align: center;
            }
            
            .question-card h3 {
                font-size: 1.3rem;
                margin-bottom: 1.5rem;
            }
            
            .options-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
            }
            
            .option-btn {
                padding: 1.5rem 1rem;
                background: var(--bg-primary);
                border: 2px solid var(--border-color);
                border-radius: 12px;
                color: var(--text-primary);
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .option-btn:hover {
                border-color: #8b5cf6;
                background: rgba(139, 92, 246, 0.1);
                transform: translateY(-2px);
            }
            
            .results-card {
                background: var(--bg-secondary);
                border-radius: 20px;
                padding: 2rem;
            }
            
            .results-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .match-list {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .match-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem;
                background: var(--bg-primary);
                border-radius: 12px;
                border: 1px solid var(--border-color);
            }
            
            .match-item.top-match {
                border-color: #8b5cf6;
                background: rgba(139, 92, 246, 0.1);
            }
            
            .match-rank {
                width: 32px;
                height: 32px;
                background: var(--bg-tertiary);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
            }
            
            .match-item.top-match .match-rank {
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                color: white;
            }
            
            .match-icon {
                font-size: 2rem;
            }
            
            .match-info {
                flex: 1;
            }
            
            .match-stats {
                display: flex;
                gap: 1rem;
                font-size: 0.8rem;
                color: var(--text-secondary);
                margin-top: 0.25rem;
            }
            
            .match-percent {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text-secondary);
            }
            
            .match-percent.high {
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .results-actions {
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
            
            @media (max-width: 600px) {
                .options-grid {
                    grid-template-columns: 1fr;
                }
                
                .results-actions {
                    flex-direction: column;
                }
            }
            
            /* Badge styles for sidebar */
            .nav-badge.live {
                background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
                animation: pulse-badge 2s infinite;
            }
            
            .nav-badge.ai {
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            }
            
            @keyframes pulse-badge {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        `;
        document.head.appendChild(style);
    },

    showPredictorSection() {
        const chatContainer = document.querySelector('.chat-container');
        const predictorSection = document.getElementById('predictor-section');

        if (chatContainer) chatContainer.style.display = 'none';
        if (predictorSection) {
            predictorSection.classList.add('active');
            // Initialize predictor form if not already done
            if (window.PredictorComponent) {
                window.PredictorComponent.renderForm();
            }
        }

        // Update nav active state
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.getElementById('predictor-nav')?.classList.add('active');
    },

    hidePredictorSection() {
        const chatContainer = document.querySelector('.chat-container');
        const predictorSection = document.getElementById('predictor-section');

        if (chatContainer) chatContainer.style.display = '';
        if (predictorSection) predictorSection.classList.remove('active');

        // Update nav active state
        document.getElementById('predictor-nav')?.classList.remove('active');
    },

    setupClickOutside() {
        document.addEventListener('click', (e) => {
            if (this.isOpen &&
                !this.sidebar.contains(e.target) &&
                !this.sidebarToggle.contains(e.target)) {
                this.hideSidebar();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.hideSidebar();
            }
        });
    },

    toggleSidebar() {
        if (this.isOpen) {
            this.hideSidebar();
        } else {
            this.showSidebar();
        }
    },

    showSidebar() {
        this.sidebar.classList.add('active');
        this.isOpen = true;
        if (window.innerWidth <= 768) {
            document.body.style.overflow = 'hidden';
        }
    },

    hideSidebar() {
        this.sidebar.classList.remove('active');
        this.isOpen = false;
        document.body.style.overflow = '';
    }
};
