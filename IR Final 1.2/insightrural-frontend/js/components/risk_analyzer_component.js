/**
 * ============================================================================
 * AI Student Success & Counseling Risk Analyzer — Premium Frontend Component
 * ============================================================================
 * Fully working, production-grade. 11 scoring dimensions with premium UI.
 * ============================================================================
 */
class RiskAnalyzerComponent {
    constructor() {
        this.container = null;
        this.isAnalyzing = false;
    }

    async activate() {
        this.container = document.getElementById('risk-analyzer-section');
        if (!this.container) return;
        this.render();
        this.setupEventListeners();
        this.prefillFromProfile();
    }

    prefillFromProfile() {
        if (typeof AppState === 'undefined') return;
        const p = AppState.getProfile();
        if (p.kcet_rank) this._setVal('risk-rank', p.kcet_rank);
        if (p.income) this._setVal('risk-income', p.income > 100 ? (p.income / 100000) : p.income);
        if (p.category) this._setVal('risk-category', p.category);
        if (p.branch) this._setVal('risk-branch', p.branch);
        if (p.location) this._setVal('risk-location', p.location);
    }

    _setVal(id, val) {
        const el = document.getElementById(id);
        if (el) el.value = val;
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="risk-analyzer-container">
                <!-- HERO -->
                <div class="risk-hero">
                    <div class="risk-hero-content">
                        <div class="risk-hero-badge">
                            <span>🧠</span> AI-Powered Deep Analysis
                        </div>
                        <h2>Student Success & Risk Analyzer</h2>
                        <p>Don't just predict colleges — predict your future. Discover hidden risks, ROI, career alignment, and regret probability before making life-changing decisions.</p>
                    </div>
                </div>

                <!-- MAIN GRID -->
                <div class="risk-main-grid">
                    <!-- LEFT: INPUT FORM -->
                    <div class="risk-form-card">
                        <div class="risk-form-title">Student Profile</div>
                        <div class="risk-form-subtitle">Fill in your details for personalized AI analysis</div>

                        <!-- Academic -->
                        <div class="risk-form-section">
                            <div class="risk-form-section-label">📚 Academic Profile</div>
                            <div class="risk-input-row">
                                <div class="risk-input-group">
                                    <label>Entrance Rank</label>
                                    <input type="number" id="risk-rank" placeholder="e.g. 15000" min="1">
                                </div>
                                <div class="risk-input-group">
                                    <label>PUC Marks (%)</label>
                                    <input type="number" id="risk-marks" placeholder="e.g. 85" min="0" max="100" step="0.1">
                                </div>
                            </div>
                            <div class="risk-input-row">
                                <div class="risk-input-group">
                                    <label>Category</label>
                                    <select id="risk-category">
                                        <option value="GM">General Merit (GM)</option>
                                        <option value="OBC">OBC</option>
                                        <option value="SC">SC</option>
                                        <option value="ST">ST</option>
                                        <option value="CAT1">Category-1</option>
                                        <option value="2A">2A</option>
                                        <option value="2B">2B</option>
                                        <option value="3A">3A</option>
                                        <option value="3B">3B</option>
                                    </select>
                                </div>
                                <div class="risk-input-group">
                                    <label>Gender</label>
                                    <select id="risk-gender">
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                        <option value="Other">Other</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Branch & Career -->
                        <div class="risk-form-section">
                            <div class="risk-form-section-label">🎯 Branch & Career</div>
                            <div class="risk-input-group">
                                <label>Target Branch</label>
                                <select id="risk-branch">
                                    <option value="CSE">Computer Science (CSE)</option>
                                    <option value="ISE">Information Science (ISE)</option>
                                    <option value="AIML">AI & Machine Learning</option>
                                    <option value="DS">Data Science</option>
                                    <option value="ECE">Electronics (ECE)</option>
                                    <option value="EEE">Electrical (EEE)</option>
                                    <option value="MECH">Mechanical</option>
                                    <option value="CIVIL">Civil</option>
                                    <option value="MBBS">Medicine (MBBS)</option>
                                    <option value="BDS">Dental (BDS)</option>
                                    <option value="BIOTECH">Biotechnology</option>
                                    <option value="MBA">MBA / Business</option>
                                </select>
                            </div>
                            <div class="risk-input-group">
                                <label>Core Interests</label>
                                <input type="text" id="risk-interests" placeholder="e.g. Coding, Robotics, Biology, AI">
                            </div>
                            <div class="risk-input-group">
                                <label>Skills</label>
                                <input type="text" id="risk-skills" placeholder="e.g. Python, Mathematics, Problem Solving">
                            </div>
                            <div class="risk-input-group">
                                <label>Career Goals</label>
                                <input type="text" id="risk-goals" placeholder="e.g. Software Engineer, Researcher, Doctor">
                            </div>
                        </div>

                        <!-- Financial -->
                        <div class="risk-form-section">
                            <div class="risk-form-section-label">💰 Financial Profile</div>
                            <div class="risk-input-row">
                                <div class="risk-input-group">
                                    <label>Family Income (₹ Lakhs/yr)</label>
                                    <input type="number" id="risk-income" placeholder="e.g. 5.5" step="0.1" min="0">
                                </div>
                                <div class="risk-input-group">
                                    <label>Budget (₹ Lakhs/yr)</label>
                                    <input type="number" id="risk-budget" placeholder="e.g. 2.0" step="0.1" min="0">
                                </div>
                            </div>
                            <div class="risk-input-row">
                                <div class="risk-input-group">
                                    <label>Annual Fees (₹)</label>
                                    <input type="number" id="risk-fees" placeholder="e.g. 150000" min="0" value="100000">
                                </div>
                                <div class="risk-input-group">
                                    <label>Hostel Fees (₹/yr)</label>
                                    <input type="number" id="risk-hostel-fees" placeholder="e.g. 70000" min="0" value="50000">
                                </div>
                            </div>
                            <div class="risk-checkbox-row">
                                <label class="risk-checkbox-item">
                                    <input type="checkbox" id="risk-hostel-req"> Hostel Required
                                </label>
                                <label class="risk-checkbox-item">
                                    <input type="checkbox" id="risk-loan-req"> Loan Required
                                </label>
                                <label class="risk-checkbox-item">
                                    <input type="checkbox" id="risk-scholarship"> Has Scholarship
                                </label>
                            </div>
                        </div>

                        <!-- Location -->
                        <div class="risk-form-section">
                            <div class="risk-form-section-label">📍 Preferences</div>
                            <div class="risk-input-group">
                                <label>Home Location</label>
                                <input type="text" id="risk-location" placeholder="e.g. Hubli, Gulbarga, Bangalore">
                            </div>
                            <div class="risk-input-group">
                                <label>College Tier</label>
                                <select id="risk-tier">
                                    <option value="1">Tier 1 (Top Colleges)</option>
                                    <option value="2" selected>Tier 2 (Good Colleges)</option>
                                    <option value="3">Tier 3 (Average Colleges)</option>
                                </select>
                            </div>
                        </div>

                        <button id="btn-analyze-risk" class="risk-analyze-btn">
                            🧠 Generate Full Risk Report
                        </button>
                    </div>

                    <!-- RIGHT: RESULTS -->
                    <div class="risk-results-area">
                        <!-- Empty State -->
                        <div id="risk-empty-state" class="risk-empty-state">
                            <div class="risk-empty-icon">🔬</div>
                            <h3>Awaiting Your Profile</h3>
                            <p>Fill in your details and click "Generate Full Risk Report" to discover hidden risks, ROI, and your true success probability.</p>
                        </div>

                        <!-- Results Container (hidden initially) -->
                        <div id="risk-results-container" style="display:none; flex-direction:column; gap:24px;">

                            <!-- Row 1: Score Cards -->
                            <div class="risk-score-grid" id="risk-score-grid"></div>

                            <!-- Row 2: Risk Radar -->
                            <div class="risk-radar-card risk-animate-in" style="animation-delay:0.2s">
                                <div class="risk-radar-title">⚠️ Multi-Dimensional Risk Radar</div>
                                <div class="risk-radar-grid" id="risk-radar-grid"></div>
                            </div>

                            <!-- Row 3: Detail Cards -->
                            <div class="risk-detail-grid" id="risk-detail-grid"></div>

                            <!-- Row 3.5: Advanced Analytics Chart -->
                            <div class="risk-chart-card risk-animate-in" style="animation-delay:0.48s; background: var(--bg-secondary); border-radius: 16px; padding: 24px; border: 1px solid var(--border-color); position: relative; overflow: hidden;">
                                <div class="risk-radar-title">📊 10-Year Career & Salary Projection (AI Forecast)</div>
                                <div style="position: relative; height: 300px; width: 100%; margin-top: 20px;">
                                    <canvas id="risk-projection-chart"></canvas>
                                </div>
                            </div>

                            <!-- Row 4: Regret Predictor -->
                            <div class="risk-regret-section risk-animate-in" style="animation-delay:0.5s" id="risk-regret-section"></div>

                            <!-- Row 5: AI Explanation -->
                            <div class="risk-ai-card risk-animate-in" style="animation-delay:0.6s" id="risk-ai-card"></div>

                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        if (!this.container) return;
        const btn = this.container.querySelector('#btn-analyze-risk');
        if (btn) {
            btn.addEventListener('click', () => this.analyzeRisk());
        }
    }

    async analyzeRisk() {
        if (this.isAnalyzing) return;
        this.isAnalyzing = true;

        const btn = document.getElementById('btn-analyze-risk');
        btn.disabled = true;
        btn.innerHTML = '<span class="risk-btn-spinner"></span> AI Analyzing 11 Dimensions...';

        try {
            const incomeLakhs = parseFloat(document.getElementById('risk-income').value || '5');
            const data = {
                rank: parseInt(document.getElementById('risk-rank').value || '50000'),
                category: document.getElementById('risk-category').value,
                gender: document.getElementById('risk-gender').value,
                income: incomeLakhs,
                marks: parseFloat(document.getElementById('risk-marks').value || '70'),
                branch: document.getElementById('risk-branch').value,
                interests: (document.getElementById('risk-interests').value || '').split(',').map(s => s.trim()).filter(Boolean),
                skills: (document.getElementById('risk-skills').value || '').split(',').map(s => s.trim()).filter(Boolean),
                career_goals: document.getElementById('risk-goals').value || '',
                budget: parseFloat(document.getElementById('risk-budget').value || '0') || null,
                fees: parseInt(document.getElementById('risk-fees').value || '100000'),
                hostel_fees: parseInt(document.getElementById('risk-hostel-fees').value || '50000'),
                hostel_required: document.getElementById('risk-hostel-req').checked,
                loan_required: document.getElementById('risk-loan-req').checked,
                has_scholarship: document.getElementById('risk-scholarship').checked,
                home_location: document.getElementById('risk-location').value || '',
                college_tier: parseInt(document.getElementById('risk-tier').value || '2'),
            };

            const headers = { 'Content-Type': 'application/json' };
            const token = localStorage.getItem('insightrural-token') || localStorage.getItem('token') || '';
            if (token) headers['Authorization'] = 'Bearer ' + token;

            const res = await fetch(`${API_BASE_URL}/api/analyze/risk`, {
                method: 'POST',
                headers,
                body: JSON.stringify(data)
            });

            const result = await res.json();

            if (result.success) {
                this.displayResults(result.risk_analysis, result.ai_explanation);
                if (window.AudioService) window.AudioService.play('success');
            } else {
                this._showError(result.error || 'Analysis failed');
            }
        } catch (e) {
            console.error('Risk Analyzer error:', e);
            this._showError('Failed to connect to AI server. Please ensure the backend is running.');
        } finally {
            this.isAnalyzing = false;
            btn.disabled = false;
            btn.innerHTML = '🧠 Generate Full Risk Report';
        }
    }

    _showError(msg) {
        alert('⚠️ ' + msg);
    }

    displayResults(report, aiExplanation) {
        document.getElementById('risk-empty-state').style.display = 'none';
        const container = document.getElementById('risk-results-container');
        container.style.display = 'flex';

        // Scroll to results
        setTimeout(() => {
            container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

        this._renderScoreCards(report);
        this._renderRiskRadar(report);
        this._renderDetailCards(report);
        this._renderCharts(report);
        this._renderRegretSection(report);
        this._renderAIExplanation(aiExplanation);
        this._renderPDFButton();
    }

    _renderPDFButton() {
        let btn = document.getElementById('btn-download-risk-pdf');
        if (!btn) {
            btn = document.createElement('button');
            btn.id = 'btn-download-risk-pdf';
            btn.className = 'risk-animate-in';
            btn.style = 'margin-top: 2rem; width: 100%; padding: 15px; font-size: 1.1rem; display: flex; justify-content: center; align-items: center; gap: 10px; background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3); transition: all 0.3s;';
            btn.innerHTML = '📄 Download Premium PDF Report';
            btn.style.animationDelay = '0.8s';
            
            btn.addEventListener('mouseenter', () => btn.style.transform = 'translateY(-2px)');
            btn.addEventListener('mouseleave', () => btn.style.transform = 'translateY(0)');
            btn.addEventListener('click', () => this.generatePDF());
            
            document.getElementById('risk-results-container').appendChild(btn);
        }
    }

    generatePDF() {
        const btn = document.getElementById('btn-download-risk-pdf');
        btn.innerHTML = '⏳ Generating PDF... Please wait';
        btn.disabled = true;

        if (!window.html2pdf) {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js';
            script.onload = () => this._executePDFGeneration(btn);
            document.head.appendChild(script);
        } else {
            this._executePDFGeneration(btn);
        }
    }

    _executePDFGeneration(btn) {
        const element = document.getElementById('risk-results-container');
        btn.style.display = 'none';

        const opt = {
            margin:       10,
            filename:     'InsightRural_Risk_Analyzer_Report.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true, backgroundColor: '#0a0a0f' },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        window.html2pdf().set(opt).from(element).save().then(() => {
            btn.style.display = 'flex';
            btn.innerHTML = '✅ PDF Downloaded Successfully';
            setTimeout(() => {
                btn.innerHTML = '📄 Download Premium PDF Report';
                btn.disabled = false;
            }, 3000);
            
            if (window.ProgressComponent) {
                ProgressComponent.unlockBadge('pdf_download');
                ProgressComponent.addXP(20);
            }
        }).catch(err => {
            console.error("PDF generation failed", err);
            btn.style.display = 'flex';
            btn.innerHTML = '❌ Failed to generate PDF';
            btn.disabled = false;
        });
    }

    // =========================================================================
    // SCORE CARDS (Top Row)
    // =========================================================================
    _renderScoreCards(r) {
        const grid = document.getElementById('risk-score-grid');
        const cards = [
            {
                label: 'Success Score',
                value: r.success_score,
                suffix: '',
                sublabel: 'Out of 100',
                colorClass: r.success_score >= 70 ? 'success' : r.success_score >= 45 ? 'warning' : 'danger',
                cardClass: r.success_score >= 70 ? 'card-success' : r.success_score >= 45 ? 'card-warning' : 'card-danger',
            },
            {
                label: 'Regret Probability',
                value: r.regret_probability,
                suffix: '%',
                sublabel: 'Likelihood of Regret',
                colorClass: r.regret_probability <= 25 ? 'success' : r.regret_probability <= 50 ? 'warning' : 'danger',
                cardClass: r.regret_probability <= 25 ? 'card-success' : r.regret_probability <= 50 ? 'card-warning' : 'card-danger',
            },
            {
                label: 'Branch Match',
                value: r.branch_compatibility_score,
                suffix: '%',
                sublabel: 'Compatibility',
                colorClass: r.branch_compatibility_score >= 70 ? 'info' : r.branch_compatibility_score >= 45 ? 'warning' : 'danger',
                cardClass: r.branch_compatibility_score >= 70 ? 'card-info' : r.branch_compatibility_score >= 45 ? 'card-warning' : 'card-danger',
            },
            {
                label: 'Career Alignment',
                value: r.career_alignment_score,
                suffix: '%',
                sublabel: 'Goal Fit',
                colorClass: 'purple',
                cardClass: 'card-purple',
            },
        ];

        grid.innerHTML = cards.map((c, i) => `
            <div class="risk-score-card ${c.cardClass} risk-animate-in" style="animation-delay:${i * 0.08}s">
                <div class="risk-score-label">${c.label}</div>
                <div class="risk-gauge-wrap">
                    ${this._renderGauge(c.value, c.colorClass)}
                </div>
                <div class="risk-score-sublabel">${c.sublabel}</div>
            </div>
        `).join('');

        // Animate gauge fills
        setTimeout(() => this._animateGauges(), 50);
    }

    _renderGauge(value, colorClass) {
        const circumference = 2 * Math.PI * 34; // radius = 34
        const offset = circumference - (value / 100) * circumference;
        const colorMap = {
            success: '#10b981', danger: '#ef4444', warning: '#f59e0b',
            info: '#3b82f6', purple: '#8b5cf6'
        };
        const color = colorMap[colorClass] || '#8b5cf6';

        return `
            <div class="risk-gauge">
                <svg viewBox="0 0 80 80">
                    <circle class="risk-gauge-track" cx="40" cy="40" r="34" />
                    <circle class="risk-gauge-fill" cx="40" cy="40" r="34"
                        stroke="${color}"
                        stroke-dasharray="${circumference}"
                        stroke-dashoffset="${circumference}"
                        data-target-offset="${offset}" />
                </svg>
                <span class="risk-gauge-text color-${colorClass}" data-target="${value}">0</span>
            </div>
        `;
    }

    _animateGauges() {
        // Animate SVG circle strokes
        document.querySelectorAll('.risk-gauge-fill').forEach(circle => {
            const target = parseFloat(circle.getAttribute('data-target-offset'));
            setTimeout(() => {
                circle.style.strokeDashoffset = target;
            }, 100);
        });

        // Animate numbers
        document.querySelectorAll('.risk-gauge-text').forEach(el => {
            const target = parseFloat(el.getAttribute('data-target'));
            this._countUp(el, 0, target, 1200);
        });
    }

    _countUp(el, start, end, duration) {
        let startTime = null;
        const step = (ts) => {
            if (!startTime) startTime = ts;
            const progress = Math.min((ts - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            const current = start + (end - start) * eased;
            el.textContent = current.toFixed(1);
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }

    // =========================================================================
    // RISK RADAR
    // =========================================================================
    _renderRiskRadar(r) {
        const grid = document.getElementById('risk-radar-grid');
        const items = [
            {
                name: 'Academic Risk',
                level: r.academic_risk,
                score: r.academic_risk_score,
                reason: r.academic_risk_reason,
            },
            {
                name: 'Financial Risk',
                level: r.financial_risk,
                score: r.financial_risk_score,
                reason: r.financial_risk_reason,
            },
            {
                name: 'Placement Risk',
                level: r.placement_risk,
                score: r.placement_risk_score,
                reason: r.placement_risk_reason,
            },
            {
                name: 'Counseling Risk',
                level: r.counseling_risk_score > 65 ? 'High' : r.counseling_risk_score > 35 ? 'Medium' : 'Low',
                score: r.counseling_risk_score,
                reason: `Overall counseling risk aggregated from all factors.`,
            },
        ];

        grid.innerHTML = items.map((item, i) => {
            const levelClass = item.level === 'High' ? 'high' : item.level === 'Medium' ? 'medium' : 'low';
            const barClass = `bar-${levelClass}`;
            return `
                <div class="risk-radar-item risk-animate-in" style="animation-delay:${0.3 + i * 0.08}s">
                    <div class="risk-radar-header">
                        <span class="risk-radar-name">${item.name}</span>
                        <span class="risk-level-badge level-${levelClass}">${item.level}</span>
                    </div>
                    <div class="risk-radar-bar">
                        <div class="risk-radar-bar-fill ${barClass}" data-width="${item.score}%"></div>
                    </div>
                    <div class="risk-radar-reason">${this._truncateReason(item.reason)}</div>
                </div>
            `;
        }).join('');

        // Animate bars
        setTimeout(() => {
            document.querySelectorAll('.risk-radar-bar-fill').forEach(bar => {
                bar.style.width = bar.getAttribute('data-width');
            });
        }, 200);
    }

    _truncateReason(reason) {
        if (!reason) return '';
        // Split multi-reason strings and show first meaningful one
        const parts = reason.split(' | ');
        if (parts.length > 2) return parts.slice(0, 2).join('. ') + '.';
        return parts.join('. ');
    }

    // =========================================================================
    // DETAIL CARDS
    // =========================================================================
    _renderDetailCards(r) {
        const grid = document.getElementById('risk-detail-grid');

        // ROI Card
        const roi = r.roi_details || {};
        const roiColor = r.college_roi_score >= 70 ? '#10b981' : r.college_roi_score >= 40 ? '#f59e0b' : '#ef4444';

        // Placement Details
        const place = r.placement_details || {};

        // Financial Details
        const fin = r.financial_details || {};

        grid.innerHTML = `
            <!-- ROI Dashboard -->
            <div class="risk-detail-card risk-animate-in" style="animation-delay:0.35s">
                <div class="risk-detail-header">
                    <div class="risk-detail-icon icon-roi">📈</div>
                    <div class="risk-detail-title">College ROI Score</div>
                </div>
                <div class="risk-detail-score" style="color:${roiColor}">${r.college_roi_score}/100</div>
                <div class="risk-detail-label">${r.roi_label || 'Medium ROI'}</div>
                <div class="risk-detail-stats">
                    <div class="risk-detail-stat">
                        <span>Expected Salary</span>
                        <span class="risk-detail-stat-value">₹${(roi.expected_salary_lpa || 0)} LPA</span>
                    </div>
                    <div class="risk-detail-stat">
                        <span>4-Year Education Cost</span>
                        <span class="risk-detail-stat-value">₹${this._formatINR(roi.total_education_cost || 0)}</span>
                    </div>
                    <div class="risk-detail-stat">
                        <span>ROI Ratio</span>
                        <span class="risk-detail-stat-value">${roi.roi_ratio || 0}x</span>
                    </div>
                    <div class="risk-detail-stat">
                        <span>Breakeven</span>
                        <span class="risk-detail-stat-value">${roi.breakeven_months || '—'} months</span>
                    </div>
                </div>
            </div>

            <!-- Scholarship Opportunity -->
            <div class="risk-detail-card risk-animate-in" style="animation-delay:0.4s">
                <div class="risk-detail-header">
                    <div class="risk-detail-icon icon-scholarship">🎓</div>
                    <div class="risk-detail-title">Scholarship Opportunity</div>
                </div>
                <div class="risk-detail-score" style="color:#f59e0b">${r.scholarship_opportunity_score}/100</div>
                <div class="risk-detail-label">${r.scholarship_reason || 'Standard eligibility'}</div>
                ${(r.eligible_scholarships && r.eligible_scholarships.length > 0) ? `
                    <div class="risk-scholarship-list">
                        ${r.eligible_scholarships.map(s => `<span class="risk-scholarship-badge">${s}</span>`).join('')}
                    </div>
                ` : ''}
            </div>

            <!-- Career Alignment -->
            <div class="risk-detail-card risk-animate-in" style="animation-delay:0.45s">
                <div class="risk-detail-header">
                    <div class="risk-detail-icon icon-career">🧭</div>
                    <div class="risk-detail-title">Career Alignment</div>
                </div>
                <div class="risk-detail-score" style="color:#3b82f6">${r.career_alignment_score}/100</div>
                <div class="risk-detail-label">${r.career_alignment_reason || 'Moderate alignment'}</div>
                ${(r.branch_mismatches && r.branch_mismatches.length > 0) ? `
                    <div style="margin-top:12px; padding:10px; background:rgba(239,68,68,0.06); border-radius:8px; border-left:3px solid #ef4444;">
                        <div style="font-size:0.78rem; font-weight:600; color:#dc2626; margin-bottom:4px;">⚠️ Mismatches Detected</div>
                        ${r.branch_mismatches.map(m => `<div style="font-size:0.75rem; color:var(--text-secondary); margin-bottom:2px;">${m}</div>`).join('')}
                    </div>
                ` : ''}
            </div>

            <!-- Placement Outlook -->
            <div class="risk-detail-card risk-animate-in" style="animation-delay:0.5s">
                <div class="risk-detail-header">
                    <div class="risk-detail-icon icon-placement">💼</div>
                    <div class="risk-detail-title">Placement Outlook</div>
                </div>
                <div class="risk-detail-score" style="color:#8b5cf6">${(100 - r.placement_risk_score).toFixed(0)}/100</div>
                <div class="risk-detail-label">Employability Index</div>
                <div class="risk-detail-stats">
                    <div class="risk-detail-stat">
                        <span>Salary Range</span>
                        <span class="risk-detail-stat-value">${place.salary_range || '—'}</span>
                    </div>
                    <div class="risk-detail-stat">
                        <span>Industry Demand</span>
                        <span class="risk-detail-stat-value">${(place.demand_percent || 0).toFixed(0)}%</span>
                    </div>
                    <div class="risk-detail-stat">
                        <span>Growth Trend</span>
                        <span class="risk-detail-stat-value">${place.growth_trend || '—'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    _formatINR(val) {
        if (!val) return '—';
        if (val >= 100000) return (val / 100000).toFixed(1) + 'L';
        if (val >= 1000) return (val / 1000).toFixed(0) + 'K';
        return val.toString();
    }

    // =========================================================================
    // REGRET PREDICTOR
    // =========================================================================
    _renderRegretSection(r) {
        const section = document.getElementById('risk-regret-section');
        const regret = r.regret_probability;
        const regretColor = regret <= 25 ? '#10b981' : regret <= 50 ? '#f59e0b' : '#ef4444';
        const reasons = r.regret_reasons || [];

        section.innerHTML = `
            <div class="risk-regret-header">
                <div>
                    <div class="risk-radar-title" style="margin-bottom:4px">🔮 Student Regret Predictor</div>
                    <div style="font-size:0.82rem; color:var(--text-muted)">Predicting the probability you may regret this decision after admission</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:2rem; font-weight:800; color:${regretColor}">${regret}%</div>
                    <div style="font-size:0.72rem; color:var(--text-muted)">Regret Probability</div>
                </div>
            </div>
            <div class="risk-regret-meter">
                <div class="risk-regret-fill" data-width="${regret}%" style="background:linear-gradient(90deg, ${regretColor}, ${regretColor}88);"></div>
            </div>
            <div class="risk-regret-reasons">
                ${reasons.map(reason => {
                    const dotColor = reason.includes('Low') || reason.includes('well-aligned') ? '#10b981' : '#ef4444';
                    return `
                        <div class="risk-regret-reason-item">
                            <div class="risk-regret-dot" style="background:${dotColor}"></div>
                            <span>${reason}</span>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        // Animate regret meter
        setTimeout(() => {
            const fill = section.querySelector('.risk-regret-fill');
            if (fill) fill.style.width = fill.getAttribute('data-width');
        }, 400);
    }

    // =========================================================================
    // ADVANCED AI CHARTS
    // =========================================================================
    _renderCharts(r) {
        if (!window.Chart) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = () => this._drawProjectionChart(r);
            document.head.appendChild(script);
        } else {
            this._drawProjectionChart(r);
        }
    }

    _drawProjectionChart(r) {
        const ctx = document.getElementById('risk-projection-chart');
        if (!ctx) return;
        
        if (window.riskChartInstance) {
            window.riskChartInstance.destroy();
        }

        const roi = r.roi_details || {};
        const startingSalary = parseFloat(roi.expected_salary_lpa || '5');
        const growthTrend = r.placement_details?.growth_trend || '';
        const growthRate = growthTrend.includes('High') ? 1.15 : 
                          (growthTrend.includes('Low') ? 1.05 : 1.10);
        
        const labels = Array.from({length: 10}, (_, i) => `Year ${i+1}`);
        const data = [];
        let currentSalary = startingSalary;
        
        for(let i=0; i<10; i++) {
            data.push(currentSalary.toFixed(1));
            currentSalary *= growthRate;
        }

        const context2d = ctx.getContext('2d');
        const gradient = context2d.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.4)'); // Purple
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

        window.riskChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Projected Salary (₹ Lakhs)',
                    data: data,
                    borderColor: '#8b5cf6',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#0a0a0f',
                    pointBorderColor: '#8b5cf6',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#e2e8f0',
                        borderColor: 'rgba(139, 92, 246, 0.3)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: (context) => `₹${context.parsed.y} LPA`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                        ticks: { color: 'rgba(255, 255, 255, 0.5)' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                        ticks: { 
                            color: 'rgba(255, 255, 255, 0.5)',
                            callback: (value) => '₹' + value + 'L'
                        },
                        beginAtZero: true
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'nearest',
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    // =========================================================================
    // AI EXPLANATION
    // =========================================================================
    _renderAIExplanation(text) {
        const card = document.getElementById('risk-ai-card');
        card.innerHTML = `
            <div class="risk-ai-header">
                <div class="risk-ai-avatar">🤖</div>
                <div class="risk-ai-meta">
                    <div class="risk-ai-name">InsightRural AI Counselor</div>
                    <div class="risk-ai-role">Elite AI Admission Strategist & Risk Analyst</div>
                </div>
            </div>
            <div class="risk-ai-body" id="risk-ai-text"></div>
        `;

        // Typewriter effect
        const textEl = document.getElementById('risk-ai-text');
        this._typeWriter(textEl, text, 12);
    }

    _typeWriter(el, text, speed) {
        let i = 0;
        el.classList.add('risk-typewriter');
        const type = () => {
            if (i < text.length) {
                // Add characters in chunks for performance
                const chunk = text.substring(i, Math.min(i + 3, text.length));
                el.textContent += chunk;
                i += 3;
                setTimeout(type, speed);
            } else {
                el.classList.remove('risk-typewriter');
            }
        };
        type();
    }
}
