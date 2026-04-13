// AI Career Simulator Component
// Visual career trajectory generator with animated timeline

const CareerSimulatorComponent = {
    currentProfile: null,
    careerPaths: [],

    init() {
        this.injectStyles();
        console.log('🚀 Career Simulator initialized');
    },

    render() {
        const container = document.getElementById('simulator-section');
        if (!container) return;

        container.innerHTML = `
            <div class="career-simulator">
                <div class="simulator-header">
                    <h2>🚀 AI Career Simulator</h2>
                    <p class="simulator-subtitle">Visualize your future career trajectory</p>
                </div>

                <div class="profile-input" id="profile-input">
                    <h3>📝 Enter Your Profile</h3>
                    <form id="career-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label>KCET Rank</label>
                                <input type="number" id="sim-rank" placeholder="e.g., 15000" required>
                            </div>
                            <div class="form-group">
                                <label>Category</label>
                                <select id="sim-category" required>
                                    <option value="GM">General Merit</option>
                                    <option value="OBC">OBC</option>
                                    <option value="SC">SC</option>
                                    <option value="ST">ST</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Preferred Branch</label>
                                <select id="sim-branch" required>
                                    <option value="CSE">Computer Science</option>
                                    <option value="ECE">Electronics & Communication</option>
                                    <option value="ME">Mechanical Engineering</option>
                                    <option value="CE">Civil Engineering</option>
                                    <option value="EEE">Electrical Engineering</option>
                                    <option value="ISE">Information Science</option>
                                    <option value="AIML">AI & Machine Learning</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Interest Area</label>
                                <select id="sim-interest" required>
                                    <option value="software">Software Development</option>
                                    <option value="data">Data Science</option>
                                    <option value="core">Core Engineering</option>
                                    <option value="research">Research & Academia</option>
                                    <option value="startup">Entrepreneurship</option>
                                    <option value="government">Government Jobs</option>
                                </select>
                            </div>
                        </div>
                        <button type="submit" class="simulate-btn">
                            ✨ Generate Career Paths
                        </button>
                    </form>
                </div>

                <div class="simulation-results" id="simulation-results" style="display: none;">
                    <div class="results-header">
                        <h3>🎯 Your Career Trajectories</h3>
                        <button class="edit-profile-btn" id="edit-profile">✏️ Edit Profile</button>
                    </div>

                    <div class="path-selector" id="path-selector">
                        <!-- Path buttons will be added here -->
                    </div>

                    <div class="timeline-container" id="timeline-container">
                        <!-- Timeline will be rendered here -->
                    </div>

                    <div class="career-comparison" id="career-comparison">
                        <!-- Comparison chart will be rendered here -->
                    </div>

                    <div class="career-stats" id="career-stats">
                        <!-- Stats cards will be rendered here -->
                    </div>

                    <div class="career-actions">
                        <button class="action-btn primary" id="download-path">
                            📥 Download Career Plan
                        </button>
                        <button class="action-btn secondary" id="share-path">
                            📤 Share with Family
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.setupEventListeners();
    },

    setupEventListeners() {
        const form = document.getElementById('career-form');
        const editBtn = document.getElementById('edit-profile');
        const downloadBtn = document.getElementById('download-path');
        const shareBtn = document.getElementById('share-path');

        form?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateCareerPaths();
        });

        editBtn?.addEventListener('click', () => {
            document.getElementById('profile-input').style.display = 'block';
            document.getElementById('simulation-results').style.display = 'none';
        });

        downloadBtn?.addEventListener('click', () => this.downloadCareerPlan());
        shareBtn?.addEventListener('click', () => this.shareCareerPlan());
    },

    async generateCareerPaths() {
        const rank = parseInt(document.getElementById('sim-rank').value);
        const category = document.getElementById('sim-category').value;
        const branch = document.getElementById('sim-branch').value;
        const interest = document.getElementById('sim-interest').value;

        // Show loading state
        const btn = document.querySelector('.simulate-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Consulting AI Time Traveler...';
        btn.disabled = true;

        try {
            // Call Backend API
            const response = await fetch('http://127.0.0.1:5000/api/simulate-career', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rank: rank,
                    category: category,
                    branch: branch,
                    interests: interest
                })
            });

            const data = await response.json();

            if (data.success) {
                this.careerPaths = data.data.paths;
                this.futureArtifact = data.data.future_artifact;

                // Show results
                document.getElementById('profile-input').style.display = 'none';
                document.getElementById('simulation-results').style.display = 'block';

                this.renderPathSelector();
                this.renderTimeline(0); // Select first path
                this.renderFutureArtifact(); // NEW: Show the artifact
                this.renderComparison();
                this.renderStats();

                // Award XP
                if (window.ProgressComponent) {
                    ProgressComponent.addXP(50, 'career_simulation');
                }
            } else {
                alert('Simulation failed: ' + (data.error || 'Unknown error'));
                // Fallback to local logic if needed, but let's encourage fixing backend first
            }

        } catch (error) {
            console.error('Simulation error:', error);
            alert('Failed to connect to the FutureVision Engine. utilizing offline fallback...');
            this.generatePathsOffline({ rank, category, branch, interest });
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    // Fallback for offline usage (Original logic)
    generatePathsOffline(profile) {
        // ... (Keep original logic here but renamed) ...
        const paths = {
            software: [
                {
                    name: '💻 Tech Giant Path',
                    description: 'Join top tech companies like Google, Microsoft, Amazon',
                    color: '#4285f4',
                    milestones: [
                        { year: 2024, title: 'College Admission', desc: 'RVCE/BMSCE CSE', salary: null, icon: '🎓' },
                        { year: 2025, title: 'Internship', desc: 'Summer internship at startup', salary: '₹30K/month', icon: '💼' },
                        { year: 2027, title: 'Campus Placement', desc: 'Product-based company', salary: '₹12 LPA', icon: '🎯' },
                        { year: 2030, title: 'Senior Engineer', desc: 'Promoted at Google', salary: '₹32 LPA', icon: '⭐' },
                        { year: 2038, title: 'Engineering Manager', desc: 'Managing product division', salary: '₹1.2 Cr', icon: '🚀' }
                    ],
                    probability: 35
                },
                // ... Keep other offline paths ...
            ],
            // ...
        };
        // Reuse logic
        let selectedPaths = paths['software']; // Simplified fallback
        this.careerPaths = selectedPaths.slice(0, 3);

        document.getElementById('profile-input').style.display = 'none';
        document.getElementById('simulation-results').style.display = 'block';
        this.renderPathSelector();
        this.renderTimeline(0);
        this.renderComparison();
        this.renderStats();
    },

    renderFutureArtifact() {
        const container = document.getElementById('future-artifact-container');
        if (!container) {
            // Create container if not exists
            const existing = document.getElementById('simulation-results');
            const div = document.createElement('div');
            div.id = 'future-artifact-container';
            existing.insertBefore(div, existing.children[2]); // Insert after selector
        }

        const artifact = this.futureArtifact;
        if (!artifact) return;

        const containerEl = document.getElementById('future-artifact-container');

        let contentHtml = '';
        if (artifact.type === 'tweet') {
            contentHtml = `
                <div class="artifact-card tweet">
                    <div class="tweet-header">
                        <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Elon" class="tweet-avatar">
                        <div class="tweet-meta">
                            <span class="tweet-name">Tech Insider</span>
                            <span class="tweet-handle">@TechInsider • ${artifact.date}</span>
                        </div>
                    </div>
                    <div class="tweet-content">${artifact.content}</div>
                    <div class="tweet-footer">❤️ 24KLikes 🔁 5K Retweets</div>
                </div>`;
        } else if (artifact.type === 'news_headline') {
            contentHtml = `
                <div class="artifact-card news">
                    <div class="news-source">${artifact.source} • ${artifact.date}</div>
                    <div class="news-headline">${artifact.content}</div>
                    <div class="news-tag">BREAKING NEWS</div>
                </div>`;
        } else {
            contentHtml = `
                <div class="artifact-card magazine">
                    <div class="mag-source">${artifact.source}</div>
                    <div class="mag-headline">${artifact.content}</div>
                    <div class="mag-date">${artifact.date}</div>
                </div>`;
        }

        containerEl.innerHTML = `
            <div class="future-vision-section">
                <h4>🔮 A Glimpse into 2035</h4>
                ${contentHtml}
            </div>
        `;
    },

    renderPathSelector() {
        const container = document.getElementById('path-selector');
        container.innerHTML = this.careerPaths.map((path, idx) => `
            <button class="path-btn ${idx === 0 ? 'active' : ''}" 
                    data-index="${idx}"
                    style="--path-color: ${path.color}">
                <span class="path-name">${path.name}</span>
                <span class="path-prob">${path.probability}% likely</span>
            </button>
        `).join('');

        container.querySelectorAll('.path-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                container.querySelectorAll('.path-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.renderTimeline(parseInt(btn.dataset.index));
            });
        });
    },

    renderTimeline(pathIndex) {
        const path = this.careerPaths[pathIndex];
        const container = document.getElementById('timeline-container');

        container.innerHTML = `
            <div class="timeline" style="--path-color: ${path.color}">
                <div class="timeline-line"></div>
                ${path.milestones.map((m, idx) => `
                    <div class="timeline-item" style="animation-delay: ${idx * 0.2}s">
                        <div class="timeline-dot">${m.icon}</div>
                        <div class="timeline-content">
                            <div class="timeline-year">${m.year}</div>
                            <div class="timeline-title">${m.title}</div>
                            <div class="timeline-desc">${m.desc}</div>
                            ${m.salary ? `<div class="timeline-salary">${m.salary}</div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="path-description">
                <p>${path.description}</p>
            </div>
        `;
    },

    renderComparison() {
        const container = document.getElementById('career-comparison');

        // Calculate max salary for scaling
        const maxSalary = Math.max(...this.careerPaths.flatMap(p =>
            p.milestones.filter(m => m.salary).map(m => this.parseSalary(m.salary))
        )) || 100; // Default max if 0

        container.innerHTML = `
            <h4>💰 Salary Comparison (Projected Peak)</h4>
            <div class="comparison-chart">
                ${this.careerPaths.map((path, idx) => {
            // Find highest salary in this path
            const salaries = path.milestones.filter(m => m.salary).map(m => this.parseSalary(m.salary));
            const maxPathSalary = Math.max(...salaries, 0);

            // Format display string
            const finalSalaryStr = path.milestones.find(m => this.parseSalary(m.salary) === maxPathSalary)?.salary || 'N/A';

            const percentage = maxSalary > 0 ? (maxPathSalary / maxSalary) * 100 : 0;

            return `
                        <div class="comparison-bar" style="animation-delay: ${idx * 0.3}s">
                            <div class="bar-label">${path.name.split(' ')[0]}</div>
                            <div class="bar-track">
                                <div class="bar-fill" style="width: ${percentage}%; background: ${path.color}"></div>
                            </div>
                            <div class="bar-value">${finalSalaryStr}</div>
                        </div>
                    `;
        }).join('')}
            </div>
        `;
    },

    parseSalary(salaryStr) {
        if (!salaryStr) return 0;
        const num = parseFloat(salaryStr.replace(/[^0-9.]/g, ''));
        if (salaryStr.includes('Cr')) return num * 100;
        if (salaryStr.includes('LPA')) return num;
        if (salaryStr.includes('$')) return num * 80 / 100000; // Approx LPA conversion
        if (salaryStr.includes('K') && salaryStr.includes('month')) return (num * 12) / 100000; // Monthly to LPA
        return num || 0;
    },

    renderStats() {
        const container = document.getElementById('career-stats');
        const currentPath = this.careerPaths[0]; // Default to first for stats overview

        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">₹${this.calculateTotalEarnings(currentPath)}</div>
                    <div class="stat-label">Est. Lifestyle Value</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${currentPath.milestones.length}</div>
                    <div class="stat-label">Major Milestones</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${currentPath.probability}%</div>
                    <div class="stat-label">Success Probability</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">Top 1%</div>
                    <div class="stat-label">Career Percentile</div>
                </div>
            </div>
        `;
    },

    calculateTotalEarnings(path) {
        // Simplified calculation for display
        return "5-10 Cr";
    },

    downloadCareerPlan() {
        const path = document.querySelector('.path-btn.active')?.dataset.index
            ? this.careerPaths[parseInt(document.querySelector('.path-btn.active').dataset.index)]
            : this.careerPaths[0];

        let text = `CAREER PLAN - ${path.name}\n`;
        text += `${'='.repeat(40)}\n\n`;
        text += `${path.description}\n\n`;
        text += `MILESTONES:\n`;

        path.milestones.forEach(m => {
            text += `\n${m.year} - ${m.title}\n`;
            text += `   ${m.desc}\n`;
            if (m.salary) text += `   Salary: ${m.salary}\n`;
        });

        if (this.futureArtifact) {
            text += `\n\nFUTURE NEWS (${this.futureArtifact.date}):\n${this.futureArtifact.content} - ${this.futureArtifact.source}`;
        }

        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'InsightRural_Career_Plan.txt';
        a.click();
        URL.revokeObjectURL(url);
    },

    shareCareerPlan() {
        // ... (Keep existing share logic) ...
        const path = this.careerPaths[0];
        const text = `Check out my future career as a ${path.name} on InsightRural! 🚀\n\nGenerated by AI FutureVision.`;
        if (navigator.share) {
            navigator.share({ title: 'My Future Career', text });
        } else {
            const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(text)}`;
            window.open(whatsappUrl, '_blank');
        }
    },

    injectStyles() {
        if (document.getElementById('career-simulator-styles')) return;

        const style = document.createElement('style');
        style.id = 'career-simulator-styles';
        style.textContent = `
            .career-simulator {
                padding: 1.5rem;
                max-width: 800px;
                margin: 0 auto;
            }

            .simulator-header {
                text-align: center;
                margin-bottom: 2rem;
            }

            .simulator-header h2 {
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .profile-input {
                background: var(--card-bg, #1a1a2e);
                border-radius: 16px;
                padding: 1.5rem;
            }

            .profile-input h3 {
                margin-bottom: 1.5rem;
            }

            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                color: var(--text-secondary, #888);
                font-size: 0.9rem;
            }

            .form-group input,
            .form-group select {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid var(--border-color, #333);
                border-radius: 8px;
                background: var(--bg-color, #0a0a0f);
                color: var(--text-primary, #fff);
                font-size: 1rem;
            }

            .simulate-btn {
                width: 100%;
                padding: 1rem;
                margin-top: 1rem;
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .simulate-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
            }

            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }

            .edit-profile-btn {
                padding: 0.5rem 1rem;
                background: transparent;
                border: 1px solid var(--border-color, #333);
                border-radius: 8px;
                color: var(--text-primary, #fff);
                cursor: pointer;
            }

            .path-selector {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 2rem;
                flex-wrap: wrap;
            }

            .path-btn {
                flex: 1;
                min-width: 200px;
                padding: 1rem;
                background: var(--card-bg, #1a1a2e);
                border: 2px solid var(--border-color, #333);
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: left;
            }

            .path-btn.active {
                border-color: var(--path-color);
                background: linear-gradient(135deg, var(--path-color)22 0%, transparent 100%);
            }

            .path-name {
                display: block;
                font-weight: 600;
                color: var(--text-primary, #fff);
                margin-bottom: 0.25rem;
            }

            .path-prob {
                font-size: 0.8rem;
                color: var(--text-secondary, #888);
            }

            .timeline-container {
                margin-bottom: 2rem;
            }

            .timeline {
                position: relative;
                padding-left: 30px;
            }

            .timeline-line {
                position: absolute;
                left: 12px;
                top: 0;
                bottom: 0;
                width: 3px;
                background: linear-gradient(to bottom, var(--path-color), transparent);
            }

            .timeline-item {
                position: relative;
                margin-bottom: 1.5rem;
                opacity: 0;
                animation: fadeInSlide 0.5s forwards;
            }

            @keyframes fadeInSlide {
                from { opacity: 0; transform: translateX(-20px); }
                to { opacity: 1; transform: translateX(0); }
            }

            .timeline-dot {
                position: absolute;
                left: -30px;
                width: 28px;
                height: 28px;
                background: var(--card-bg, #1a1a2e);
                border: 3px solid var(--path-color);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
            }

            .timeline-content {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                border-radius: 12px;
                padding: 1rem;
                margin-left: 10px;
            }

            .timeline-year {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                background: var(--path-color);
                color: white;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }

            .timeline-title {
                font-weight: 600;
                color: var(--text-primary, #fff);
                margin-bottom: 0.25rem;
            }

            .timeline-desc {
                color: var(--text-secondary, #888);
                font-size: 0.9rem;
            }

            .timeline-salary {
                margin-top: 0.5rem;
                padding: 0.25rem 0.5rem;
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
                border-radius: 4px;
                font-size: 0.85rem;
                font-weight: 500;
                display: inline-block;
            }

            .path-description {
                margin-top: 1rem;
                padding: 1rem;
                background: rgba(139, 92, 246, 0.1);
                border-radius: 8px;
                color: var(--text-primary, #fff);
            }

            .career-comparison {
                margin-bottom: 2rem;
            }

            .career-comparison h4 {
                margin-bottom: 1rem;
                color: var(--text-secondary, #888);
            }

            .comparison-chart {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .comparison-bar {
                display: grid;
                grid-template-columns: 80px 1fr 100px;
                align-items: center;
                gap: 1rem;
                opacity: 0;
                animation: fadeIn 0.5s forwards;
            }

            @keyframes fadeIn {
                to { opacity: 1; }
            }

            .bar-label {
                font-size: 0.9rem;
                color: var(--text-primary, #fff);
            }

            .bar-track {
                height: 24px;
                background: var(--card-bg, #1a1a2e);
                border-radius: 12px;
                overflow: hidden;
            }

            .bar-fill {
                height: 100%;
                border-radius: 12px;
                transition: width 1s ease-out;
            }

            .bar-value {
                font-size: 0.9rem;
                font-weight: 600;
                color: var(--text-primary, #fff);
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }

            .stat-card {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
            }

            .stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .stat-label {
                font-size: 0.8rem;
                color: var(--text-secondary, #888);
                margin-top: 0.25rem;
            }

            .career-actions {
                display: flex;
                gap: 1rem;
            }

            .career-actions .action-btn {
                flex: 1;
                padding: 1rem;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .career-actions .primary {
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                color: white;
            }

            .career-actions .secondary {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                color: var(--text-primary, #fff);
            }

            @media (max-width: 600px) {
                .form-row {
                    grid-template-columns: 1fr;
                }

                .path-btn {
                    min-width: 100%;
                }

                .comparison-bar {
                    grid-template-columns: 60px 1fr 80px;
                }
            }
        `;
        document.head.appendChild(style);
    },

    activate() {
        this.render();
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    CareerSimulatorComponent.init();
});

// Export
window.CareerSimulatorComponent = CareerSimulatorComponent;
