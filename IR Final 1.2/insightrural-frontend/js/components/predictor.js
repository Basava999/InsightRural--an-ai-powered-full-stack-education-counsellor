// ==============================================================================
// College Predictor Component — KEA-Accurate Frontend
// ==============================================================================
// Mirrors KEA's KCET counselling process:
//   - OBC sub-categories (2A, 2B, 3A, 3B, Cat-1)
//   - KCET marks → rank calculator
//   - KEA Round predictions (Round 1 / Round 2 / Extended)
//   - Reservation benefit badges
//   - 3-year cutoff trend sparklines
// ==============================================================================
// API_BASE_URL is defined in state.js (loaded first)

const PredictorComponent = {
    isLoading: false,
    lastPredictionResult: null,
    lastFormData: null,
    compareList: [],        // colleges selected for comparison
    activeTab: 'predict',

    // KEA-accurate options
    branches: ['CSE', 'ECE', 'EEE', 'ME', 'CIVIL', 'ISE', 'AI', 'DS', 'CY', 'AERO'],
    locations: ['Bangalore', 'Mysore', 'Tumkur', 'Hubli', 'Belagavi', 'Dharwad', 'Hassan', 'Mandya', 'Bagalkot', 'Raichur'],

    // KEA categories with OBC sub-categories
    categories: [
        { value: 'GM', label: 'General Merit (GM)' },
        { value: '2A', label: 'OBC - Category 2A (15%)' },
        { value: '2B', label: 'OBC - Category 2B (4%)' },
        { value: '3A', label: 'OBC - Category 3A (4%)' },
        { value: '3B', label: 'OBC - Category 3B (5%)' },
        { value: 'CAT1', label: 'OBC - Category 1 (4%)' },
        { value: 'SC', label: 'Scheduled Caste (SC) - 15%' },
        { value: 'ST', label: 'Scheduled Tribe (ST) - 3%' },
    ],
    collegeTypes: ['Any', 'Government', 'Private'],

    // KEA counselling document checklist
    keaDocuments: [
        { id: 'kcet_scorecard', name: 'KCET Score Card', desc: 'Downloaded from KEA website', mandatory: true },
        { id: 'puc_marks', name: 'PUC/12th Marks Card', desc: 'Original + 2 copies', mandatory: true },
        { id: 'sslc_marks', name: 'SSLC Marks Card', desc: 'Original + 2 copies', mandatory: true },
        { id: 'aadhar', name: 'Aadhaar Card', desc: 'Original + copy', mandatory: true },
        { id: 'caste_cert', name: 'Caste/Income Certificate', desc: 'For SC/ST/OBC candidates', mandatory: false },
        { id: 'study_cert', name: 'Study Certificate (1-10)', desc: 'From school, stating Karnataka study', mandatory: true },
        { id: 'rural_cert', name: 'Rural Study Certificate', desc: 'For Rural quota - 1st to 10th std', mandatory: false },
        { id: 'kannada_cert', name: 'Kannada Medium Certificate', desc: 'For KM quota candidates', mandatory: false },
        { id: 'domicile', name: 'Domicile Certificate', desc: 'Karnataka domicile proof', mandatory: true },
        { id: 'photos', name: 'Passport Photos (8)', desc: 'Recent passport size', mandatory: true },
        { id: 'income_cert', name: 'Income Certificate', desc: 'For fee concession', mandatory: false },
        { id: 'hk_cert', name: 'HK Region Certificate', desc: 'For Art. 371(J) reservation', mandatory: false },
        { id: 'ews_cert', name: 'EWS Certificate', desc: 'Economically Weaker Section', mandatory: false },
        { id: 'pwd_cert', name: 'Disability Certificate (PwD)', desc: 'From competent authority', mandatory: false },
    ],

    init() {
        this.renderForm();
        this.setupTabs();
        this.animateHeroStats();
        this.createParticles();
        this.renderChecklist();
        this.renderSimulator();
        this.renderCompare();
        this.renderAnalytics();
    },

    setupEventListeners() {
        const form = document.getElementById('predictor-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handlePredict();
            });
        }

        const budgetSlider = document.getElementById('budget-slider');
        const budgetValue = document.getElementById('budget-value');
        if (budgetSlider && budgetValue) {
            budgetSlider.addEventListener('input', () => {
                budgetValue.textContent = `₹${parseInt(budgetSlider.value).toLocaleString('en-IN')}/year`;
            });
        }
    },

    renderForm() {
        const formContainer = document.getElementById('predictor-form-content');
        if (!formContainer) return;

        formContainer.innerHTML = `
            <div class="form-grid">
                <!-- KCET Rank -->
                <div class="form-group">
                    <label>KCET Rank <span class="required">*</span></label>
                    <input type="number" id="kcet-rank" placeholder="Enter your KCET rank" required min="1" max="250000">
                    <small style="color: var(--text-tertiary, #888); font-size: 11px;">Don't know your rank? Enter KCET marks below</small>
                </div>
                
                <!-- Category with OBC sub-categories -->
                <div class="form-group">
                    <label>Category <span class="required">*</span></label>
                    <select id="category" required>
                        <option value="">Select your KEA category</option>
                        <optgroup label="General">
                            <option value="GM">General Merit (GM)</option>
                        </optgroup>
                        <optgroup label="OBC Sub-Categories">
                            <option value="2A">Category 2A — 15% quota</option>
                            <option value="2B">Category 2B — 4% quota</option>
                            <option value="3A">Category 3A — 4% quota</option>
                            <option value="3B">Category 3B — 5% quota</option>
                            <option value="CAT1">Category 1 — 4% quota</option>
                        </optgroup>
                        <optgroup label="SC / ST">
                            <option value="SC">Scheduled Caste (SC) — 15%</option>
                            <option value="ST">Scheduled Tribe (ST) — 3%</option>
                        </optgroup>
                    </select>
                </div>
                
                <!-- KEA Reservation Quotas -->
                <div class="form-group" style="grid-column: 1 / -1; background: var(--bg-secondary, #f8f9fa); padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border-color, #e0e0e0);">
                    <label style="font-weight: 600; margin-bottom: 6px; display: block;">
                        🎫 Special Reservations <span style="font-weight: 400; font-size: 12px; color: var(--text-tertiary, #888);">(Select all applicable)</span>
                    </label>
                    <div class="checkbox-group" style="margin-top: 5px;">
                        <label class="checkbox-item">
                            <input type="checkbox" id="res-rural"> 🌾 Rural (1-10 Std) — 15% quota
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="res-kannada"> 🕉️ Kannada Medium — 5% quota
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" id="res-hk"> 🏛️ Hyderabad-Karnataka (Art. 371J) — 8% state quota
                        </label>
                    </div>
                </div>

                <!-- KCET Marks (Optional rank calculator) -->
                <div class="form-group" style="grid-column: 1 / -1; background: var(--bg-secondary, #f0f7ff); padding: 12px 14px; border-radius: 10px; border: 1px dashed var(--accent-blue, #3b82f6);">
                    <label style="font-weight: 600;">
                        📐 KCET Marks <span style="font-weight: 400; font-size: 12px; color: var(--text-tertiary, #888);">(Optional — auto-calculates rank)</span>
                    </label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 6px;">
                        <input type="number" id="kcet-phy" placeholder="Physics (/60)" min="0" max="60">
                        <input type="number" id="kcet-chem" placeholder="Chemistry (/60)" min="0" max="60">
                        <input type="number" id="kcet-math" placeholder="Maths (/60)" min="0" max="60">
                    </div>
                </div>

                <!-- PUC Marks -->
                <div class="form-group" style="grid-column: 1 / -1;">
                    <label>📚 PUC / 12th Marks <span style="font-weight: 400; font-size: 12px; color: var(--text-tertiary, #888);">(Optional — for KCET composite score + tie-breaking)</span></label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
                        <input type="number" id="puc-phy" placeholder="Physics (/100)" min="0" max="100">
                        <input type="number" id="puc-chem" placeholder="Chemistry (/100)" min="0" max="100">
                        <input type="number" id="puc-math" placeholder="Maths (/100)" min="0" max="100">
                    </div>
                    <small style="color: var(--text-tertiary, #888); font-size: 11px; margin-top: 4px; display: block;">KEA KCET Rank = 50% KCET marks + 50% PUC marks</small>
                </div>

                <!-- Preferred Branches -->
                <div class="form-group" style="grid-column: 1 / -1;">
                    <label>Preferred Branches <span class="required">*</span></label>
                    <div class="checkbox-group" id="branch-checkboxes">
                        ${this.branches.map(b => `
                            <label class="checkbox-item" data-branch="${b}">
                                <input type="checkbox" name="branches" value="${b}" ${['CSE', 'ECE', 'ISE'].includes(b) ? 'checked' : ''}>
                                ${b}
                            </label>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Preferred Locations -->
                <div class="form-group" style="grid-column: 1 / -1;">
                    <label>Preferred Locations <span style="font-weight: 400; font-size: 12px; color: var(--text-tertiary, #888);">(Leave empty for all Karnataka)</span></label>
                    <div class="checkbox-group" id="location-checkboxes">
                        ${this.locations.map(l => `
                            <label class="checkbox-item" data-location="${l}">
                                <input type="checkbox" name="locations" value="${l}">
                                ${l}
                            </label>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Budget -->
                <div class="form-group">
                    <label>Maximum Annual Budget</label>
                    <div class="budget-slider">
                        <input type="range" id="budget-slider" min="0" max="400000" step="10000" value="200000">
                        <div class="budget-value" id="budget-value">₹2,00,000/year</div>
                    </div>
                </div>
                
                <!-- College Type -->
                <div class="form-group">
                    <label>College Type Preference</label>
                    <select id="college-type">
                        ${this.collegeTypes.map(t => `<option value="${t}">${t}</option>`).join('')}
                    </select>
                </div>
                
                <!-- Submit Button -->
                <button type="submit" class="predict-btn" id="predict-btn" style="grid-column: 1 / -1;">
                    <span class="btn-text">🎯 Predict My Colleges (KEA Algorithm)</span>
                    <div class="spinner" style="display: none;"></div>
                </button>
            </div>
        `;

        this.setupCheckboxToggles();
        this.setupEventListeners();
    },

    setupCheckboxToggles() {
        document.querySelectorAll('.checkbox-item').forEach(item => {
            const checkbox = item.querySelector('input');
            if (checkbox && checkbox.checked) {
                item.classList.add('selected');
            }

            item.addEventListener('click', (e) => {
                if (!checkbox) return;
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                }
                item.classList.toggle('selected', checkbox.checked);
            });
        });
    },

    getFormData() {
        const rank = document.getElementById('kcet-rank')?.value;
        const category = document.getElementById('category')?.value;
        const budget = document.getElementById('budget-slider')?.value;
        const collegeType = document.getElementById('college-type')?.value;

        // KEA Reservations
        const reservations = {
            rural: document.getElementById('res-rural')?.checked || false,
            kannada: document.getElementById('res-kannada')?.checked || false,
            hk_region: document.getElementById('res-hk')?.checked || false
        };

        // PUC Marks
        const pucMarks = {
            physics: parseInt(document.getElementById('puc-phy')?.value) || 0,
            chemistry: parseInt(document.getElementById('puc-chem')?.value) || 0,
            maths: parseInt(document.getElementById('puc-math')?.value) || 0
        };

        // KCET Marks (for rank calculator)
        const kcetMarks = {
            physics: parseInt(document.getElementById('kcet-phy')?.value) || 0,
            chemistry: parseInt(document.getElementById('kcet-chem')?.value) || 0,
            maths: parseInt(document.getElementById('kcet-math')?.value) || 0
        };
        const hasKcetMarks = kcetMarks.physics > 0 || kcetMarks.chemistry > 0 || kcetMarks.maths > 0;

        const branches = [];
        document.querySelectorAll('input[name="branches"]:checked').forEach(cb => {
            branches.push(cb.value);
        });

        const locations = [];
        document.querySelectorAll('input[name="locations"]:checked').forEach(cb => {
            locations.push(cb.value);
        });

        return {
            kcet_rank: parseInt(rank),
            category: category,
            preferred_branches: branches.length > 0 ? branches : ['CSE', 'ECE', 'ISE'],
            preferred_locations: locations.length > 0 ? locations : null,
            budget: parseInt(budget) || null,
            college_type_pref: collegeType !== 'Any' ? collegeType : null,
            reservations: reservations,
            puc_marks: pucMarks,
            kcet_marks: hasKcetMarks ? kcetMarks : null,
            top_n: 15
        };
    },

    async handlePredict() {
        if (this.isLoading) return;

        const formData = this.getFormData();

        // Validate
        if (!formData.kcet_rank || formData.kcet_rank < 1) {
            alert('Please enter a valid KCET rank');
            return;
        }
        if (!formData.category) {
            alert('Please select your category');
            return;
        }

        this.setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/predict/college`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                this.lastPredictionResult = result;
                this.lastFormData = formData;
                this.renderResults(result);
                this.launchConfetti();
                // Refresh other tabs with new data
                if (this.activeTab === 'analytics') this.renderAnalytics();
            } else {
                alert('Prediction failed: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Prediction error:', error);
            alert('Failed to connect to prediction server. Make sure the backend is running.');
        } finally {
            this.setLoading(false);
        }
    },

    setLoading(loading) {
        this.isLoading = loading;
        const btn = document.getElementById('predict-btn');
        const btnText = btn?.querySelector('.btn-text');
        const spinner = btn?.querySelector('.spinner');

        if (btn) {
            btn.disabled = loading;
            if (btnText) btnText.style.display = loading ? 'none' : 'inline';
            if (spinner) spinner.style.display = loading ? 'block' : 'none';
        }
    },

    // Download PDF Report
    async downloadReport() {
        if (!this.lastPredictionResult || !this.lastFormData) {
            alert('Please generate a prediction first');
            return;
        }

        const downloadBtn = document.getElementById('download-report-btn');
        if (downloadBtn) {
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '⏳ Generating PDF...';
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/report/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prediction_result: this.lastPredictionResult,
                    student_profile: this.lastFormData
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to generate report');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `InsightRural_KEA_Report_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showNotification('📄 Report downloaded successfully!');
        } catch (error) {
            console.error('PDF generation error:', error);
            alert('Failed to generate PDF report: ' + error.message);
        } finally {
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '📄 Download PDF Report';
            }
        }
    },

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'predictor-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #10a37f, #1e90ff);
            color: white;
            padding: 12px 24px;
            border-radius: 50px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 20px rgba(16, 163, 127, 0.3);
            z-index: 1000;
            animation: slideUp 0.3s ease;
        `;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(-50%) translateY(-10px)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    renderResults(result) {
        const resultsContainer = document.getElementById('prediction-results');
        if (!resultsContainer) return;

        const predictions = result.predictions || [];
        const guidance = result.counselling_guidance || {};
        const keaInfo = result.kea_info || {};
        const summary = guidance.summary || {};

        if (predictions.length === 0) {
            resultsContainer.innerHTML = `
                <div class="no-results-state">
                    <div class="no-results-icon">🔍</div>
                    <h3>No colleges matched your criteria</h3>
                    <p>Try increasing your budget, expanding preferred branches, or selecting "Any" for college type. Consider adding more locations.</p>
                </div>
            `;
            resultsContainer.classList.add('active');
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
            return;
        }

        // Top Match Spotlight
        const topMatch = predictions[0];
        const matchMeterHTML = topMatch ? `
            <div class="match-meter-spotlight">
                <div class="meter-content">
                    <div class="meter-info">
                        <h3>✨ Best Match Found!</h3>
                        <p>${topMatch.college_name} — ${topMatch.branch}</p>
                        <div class="match-score-badge">${topMatch.match_index}% Match</div>
                        <div style="margin-top: 6px;">
                            <span class="kea-round-badge ${this.getRoundClass(topMatch.predicted_round)}">${topMatch.predicted_round}</span>
                        </div>
                    </div>
                    <div class="meter-visual">
                        <svg viewBox="0 0 100 100">
                            <circle class="meter-bg" cx="50" cy="50" r="45"></circle>
                            <circle class="meter-fill" cx="50" cy="50" r="45" style="stroke-dashoffset: ${283 - (283 * topMatch.match_index / 100)}"></circle>
                        </svg>
                        <div class="meter-text">${topMatch.match_index}%</div>
                    </div>
                </div>
            </div>
        ` : '';

        // Summary counts
        const safeCount = predictions.filter(p => ['Safe', 'Very Safe'].includes(p.category)).length;
        const moderateCount = predictions.filter(p => ['Moderate', 'Good Chance'].includes(p.category)).length;
        const reachCount = predictions.filter(p => ['Reach', 'Long Shot', 'Very Unlikely'].includes(p.category)).length;

        // KEA info banner
        const keaBanner = `
            <div style="background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(16,163,127,0.08)); border: 1px solid rgba(59,130,246,0.2); border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; font-size: 13px;">
                <strong>🏛️ KEA Algorithm:</strong> ${keaInfo.algorithm || 'Serial Dictatorship'}
                &nbsp;|&nbsp; <strong>Category:</strong> ${result.student_profile?.category || '—'}
                &nbsp;|&nbsp; <strong>Quota:</strong> ${keaInfo.quota_percentage || '—'}
                &nbsp;|&nbsp; <strong>Checked:</strong> ${result.total_colleges_checked || '—'} colleges
                &nbsp;|&nbsp; <strong>Eligible:</strong> ${result.total_eligible || '—'} options
            </div>
        `;

        resultsContainer.innerHTML = `
            <!-- Results Header -->
            <div class="results-header">
                <h3>🎓 KEA Prediction Results</h3>
                <div class="results-actions">
                    <button id="download-report-btn" class="download-btn" onclick="PredictorComponent.downloadReport()">
                        📄 Download PDF Report
                    </button>
                </div>
            </div>
            
            ${keaBanner}
            ${this.renderWhatIfSlider(this.lastFormData?.kcet_rank || 10000)}
            ${matchMeterHTML}

            <!-- Summary Badges -->
            <div class="results-summary">
                <span class="summary-badge safe">${safeCount} Safe</span>
                <span class="summary-badge moderate">${moderateCount} Moderate</span>
                <span class="summary-badge reach">${reachCount} Reach</span>
            </div>
            
            <!-- Rank Analysis -->
            <div class="guidance-section" style="margin-bottom: 1.5rem; margin-top: 1rem;">
                <p><strong>📊 Analysis:</strong> ${guidance.rank_analysis || 'Good options available'}</p>
                <p><strong>📋 Strategy:</strong> ${guidance.strategy || 'Mix safe and aspirational choices'}</p>
            </div>
            
            <!-- Prediction Cards -->
            <div class="prediction-cards">
                ${predictions.map((pred, idx) => this.renderPredictionCard(pred, idx + 1)).join('')}
            </div>
        `;

        // Add remaining sections
        this.renderRemainingSections(resultsContainer, result);

        resultsContainer.classList.add('active');
        resultsContainer.scrollIntoView({ behavior: 'smooth' });

        // Setup What-If slider live update
        const whatIfSlider = document.getElementById('what-if-slider');
        if (whatIfSlider) {
            whatIfSlider.addEventListener('input', () => {
                const val = parseInt(whatIfSlider.value).toLocaleString('en-IN');
                const display = document.getElementById('what-if-value');
                if (display) display.innerHTML = `Rank: <strong>${val}</strong>`;
            });
        }
    },

    getRoundClass(round) {
        if (!round) return '';
        if (round.includes('Guaranteed') || round.includes('Round 1')) return 'round-1';
        if (round.includes('Round 2')) return 'round-2';
        return 'round-ext';
    },

    renderRemainingSections(container, result) {
        const optionSequence = result.option_entry_sequence || [];
        const guidance = result.counselling_guidance || {};
        const dates = guidance.important_dates || {};

        const extraHTML = `
            <!-- Option Entry Sequence -->
            ${optionSequence.length > 0 ? `
                <div class="option-entry-section">
                    <h3>📝 KEA Option Entry Sequence (Recommended)</h3>
                    <p style="font-size: 13px; color: var(--text-secondary, #666); margin-bottom: 12px;">
                        In KEA, you can ONLY move UP your preference list in later rounds. Order by true preference!
                    </p>
                    <div class="option-list">
                        ${optionSequence.map(opt => `
                            <div class="option-item ${opt.strategy || opt.category.toLowerCase()}">
                                <div class="option-priority">${opt.priority}</div>
                                <div class="option-info">
                                    <strong>${opt.college} — ${opt.branch}</strong>
                                    <small>${opt.reason}</small>
                                    <small style="color: var(--text-tertiary, #888);">${opt.probability} | ${opt.round}</small>
                                </div>
                                <span class="category-badge ${opt.category.toLowerCase().replace(' ', '-')}">${opt.category}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <!-- KEA Important Dates -->
            ${Object.keys(dates).length > 0 ? `
                <div class="guidance-section" style="margin-top: 1.5rem;">
                    <h3>📅 KEA Counselling Timeline</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; font-size: 13px;">
                        ${Object.entries(dates).map(([key, val]) => `
                            <div style="padding: 6px 10px; background: var(--bg-secondary, #f5f5f5); border-radius: 8px;">
                                <strong>${key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:</strong><br>
                                <span style="color: var(--text-secondary, #666);">${val}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Guidance Tips -->
            ${guidance.tips ? `
                <div class="guidance-section">
                    <h3>💡 KEA Counselling Tips</h3>
                    <ul class="guidance-tips">
                        ${guidance.tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        container.insertAdjacentHTML('beforeend', extraHTML);
    },

    renderPredictionCard(pred, rank) {
        const categoryClass = this.getCategoryClass(pred.category);
        const feeDisplay = pred.annual_fee ? `₹${pred.annual_fee.toLocaleString('en-IN')}` : 'Free';
        const mapLink = pred.map_link || `https://maps.google.com/?q=${pred.location}+Karnataka`;

        const sparklineHTML = this.renderSparkline(pred.historical_cutoffs);

        // Reservation Benefit Badges
        const reservationBadges = (pred.reservation_benefits || []).map(b =>
            `<span class="benefit-badge reservation" title="${b}">🌾 ${b}</span>`
        ).join('');

        const pucBadge = pred.is_puc_boosted
            ? `<span class="benefit-badge puc" title="Chance boosted by PUC marks">⚡ PUC Boost</span>` : '';

        // KEA Round Badge
        const roundBadge = pred.predicted_round
            ? `<span class="kea-round-badge ${this.getRoundClass(pred.predicted_round)}">${pred.predicted_round}</span>` : '';

        // Startup Metrics
        const trendBadge = `<span class="startup-badge trend ${pred.trend?.includes('Trending') ? 'hot' : ''}">${pred.trend || 'Stable'}</span>`;
        const roiBadge = `<span class="startup-badge roi">${pred.roi_label || 'N/A'}</span>`;
        const naacBadge = pred.naac_grade && pred.naac_grade !== 'N/A'
            ? `<span class="startup-badge naac">NAAC ${pred.naac_grade}</span>` : '';

        // Cutoff Display
        const cutoffDisplay = pred.is_reservation_benefit
            ? `<span class="cutoff-benefit" title="Original: ${pred.original_cutoff}">🎫 Adjusted Cutoff: ${pred.cutoff_rank} <small>(↑ benefit)</small></span>`
            : `<span>🎫 Cutoff: ${pred.cutoff_rank}</span>`;

        // 4-year cost
        const fourYearCost = pred.four_year_cost
            ? `<small style="color: var(--text-tertiary, #888);">(₹${pred.four_year_cost.toLocaleString('en-IN')} for 4 yrs)</small>` : '';

        return `
            <div class="prediction-card">
                <div class="prediction-rank">${rank}</div>
                <div class="prediction-info">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px; flex-wrap: wrap; gap: 4px;">
                        <h4 style="margin: 0;">${pred.college_name}</h4>
                        <div class="badges-row" style="display: flex; flex-wrap: wrap; gap: 4px;">
                            ${roundBadge}
                            ${naacBadge}
                            ${trendBadge}
                            ${roiBadge}
                        </div>
                    </div>
                    <span class="branch">${pred.branch}</span>
                    <div class="details">
                        <span>📍 <a href="${mapLink}" target="_blank" style="color: inherit; text-decoration: underline;">${pred.location}</a></span>
                        <span>💰 ${feeDisplay}/yr ${fourYearCost}</span>
                        ${cutoffDisplay}
                        <span>🏢 ${pred.college_type?.replace(/_/g, ' ') || 'Private'}</span>
                    </div>
                    ${reservationBadges || pucBadge ? `
                        <div class="badges-row" style="margin-top: 4px; display: flex; flex-wrap: wrap; gap: 4px;">
                            ${reservationBadges}
                            ${pucBadge}
                        </div>
                    ` : ''}
                </div>
                <!-- Sparkline Section -->
                <div class="sparkline-container" title="5-Year Cutoff Trend (2020-2024)">
                    <div class="sparkline-label">5-Yr Trend</div>
                    ${sparklineHTML}
                </div>
                <div class="prediction-meta">
                    <div class="match-score-mini">${pred.match_index}% Match</div>
                    <div class="probability-bar">
                        <div class="probability-fill ${categoryClass}" style="width: ${pred.probability}%;"></div>
                    </div>
                    <div class="probability-text">${pred.probability}%</div>
                    <span class="category-badge ${categoryClass}">${pred.category}</span>
                </div>
                <!-- 5-Year Cutoff Section -->
                ${this.renderCutoffSection(pred)}
            </div>
        `;
    },

    getCategoryClass(category) {
        if (!category) return 'moderate';
        const lower = category.toLowerCase();
        if (lower.includes('safe')) return 'safe';
        if (lower.includes('good')) return 'safe';
        if (lower.includes('moderate')) return 'moderate';
        if (lower.includes('reach')) return 'reach';
        if (lower.includes('long') || lower.includes('unlikely')) return 'reach';
        return 'moderate';
    },

    renderSparkline(history) {
        const years = ['2020', '2021', '2022', '2023', '2024'];
        if (!history) return '<div class="no-trend">N/A</div>';
        const points = years.map(y => history[y] || 0).filter(v => v > 0);
        if (points.length < 2) return '<div class="no-trend">Stable</div>';
        const max = Math.max(...points);
        const min = Math.min(...points);
        const range = max - min || 1;
        const w = 12; // x spacing per year
        const normalized = points.map(p => 38 - ((p - min) / range * 30));
        const pathData = normalized.map((p, i) => `${i === 0 ? 'M' : 'L'} ${i * w} ${p}`).join(' ');
        const isImproving = points[points.length - 1] < points[0]; // lower rank = better
        const color = isImproving ? '#22c55e' : '#ef4444';
        const yearLabels = years.filter((y, i) => points[i] > 0);
        return `<svg class="sparkline-svg" width="60" height="44" viewBox="0 0 ${(yearLabels.length - 1) * w} 44">
            <path d="${pathData}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            ${normalized.map((p, i) => `<circle cx="${i * w}" cy="${p}" r="2.5" fill="${color}"/>`).join('')}
        </svg>`;
    },

    renderCutoffSection(pred) {
        const trends = pred.cutoff_trends || {};
        const branch = pred.branch || 'CSE';
        const years = ['2020', '2021', '2022', '2023', '2024'];
        const hasData = Object.keys(trends).some(y => trends[y]?.[branch]);
        if (!hasData) return '';
        const cardId = `cutoff-${pred.college_name?.replace(/\s+/g, '_')}_${branch}`.replace(/[^a-zA-Z0-9_]/g, '');
        const rows = years.filter(y => trends[y]?.[branch]).map(y => {
            const c = trends[y][branch];
            return `<tr>
              <td><strong>${y}</strong></td>
              <td>${(c.GM || '-').toLocaleString?.() ?? c.GM}</td>
              <td>${(c.OBC || '-').toLocaleString?.() ?? c.OBC}</td>
              <td>${(c.SC || '-').toLocaleString?.() ?? c.SC}</td>
              <td>${(c.ST || '-').toLocaleString?.() ?? c.ST}</td>
            </tr>`;
        }).join('');
        return `
        <div class="cutoff-section">
            <button class="cutoff-toggle" onclick="this.parentElement.classList.toggle('expanded')" title="View 5-year KCET cutoffs">
                📊 5-Year Cutoffs (${branch})
                <span class="cutoff-arrow">▼</span>
            </button>
            <div class="cutoff-table-wrap">
                <table class="cutoff-table">
                    <thead><tr>
                        <th>Year</th><th>GM</th><th>OBC</th><th>SC</th><th>ST</th>
                    </tr></thead>
                    <tbody>${rows}</tbody>
                </table>
                <p class="cutoff-note">*Lower rank = better. Source: KEA KCET Allotment Data 2020-2024</p>
            </div>
        </div>`;
    },

    // ====== HERO STATS COUNTER ANIMATION ======
    animateHeroStats() {
        const nums = document.querySelectorAll('.stat-num');
        nums.forEach(el => {
            const target = parseInt(el.dataset.target);
            const duration = 2000;
            const start = performance.now();
            const animate = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const ease = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.floor(target * ease).toLocaleString('en-IN');
                if (progress < 1) requestAnimationFrame(animate);
            };
            requestAnimationFrame(animate);
        });
    },

    // ====== FLOATING PARTICLES ======
    createParticles() {
        const container = document.getElementById('hero-particles');
        if (!container) return;
        for (let i = 0; i < 20; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            p.style.cssText = `left:${Math.random() * 100}%;top:${Math.random() * 100}%;animation-delay:${Math.random() * 5}s;animation-duration:${3 + Math.random() * 4}s;width:${3 + Math.random() * 5}px;height:${3 + Math.random() * 5}px;`;
            container.appendChild(p);
        }
    },

    // ====== TAB NAVIGATION ======
    setupTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                this.activeTab = tab;
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.predictor-tab-content').forEach(tc => tc.classList.remove('active'));
                const target = document.getElementById(`tab-${tab}`);
                if (target) { target.classList.add('active'); target.style.animation = 'fadeInUp 0.4s ease'; }
                if (tab === 'analytics' && this.lastPredictionResult) this.renderAnalytics();
                if (tab === 'compare') this.renderCompare();
            });
        });
    },

    // ====== CONFETTI CELEBRATION ======
    launchConfetti() {
        const colors = ['#667eea', '#764ba2', '#22c55e', '#eab308', '#ef4444', '#3b82f6'];
        const container = document.createElement('div');
        container.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;overflow:hidden;';
        document.body.appendChild(container);
        for (let i = 0; i < 80; i++) {
            const piece = document.createElement('div');
            const color = colors[Math.floor(Math.random() * colors.length)];
            const size = 6 + Math.random() * 8;
            const left = Math.random() * 100;
            const delay = Math.random() * 0.5;
            const rotation = Math.random() * 360;
            piece.style.cssText = `position:absolute;top:-20px;left:${left}%;width:${size}px;height:${size * 0.6}px;background:${color};border-radius:2px;animation:confettiFall ${2 + Math.random() * 2}s ease-in ${delay}s forwards;transform:rotate(${rotation}deg);`;
            container.appendChild(piece);
        }
        setTimeout(() => container.remove(), 5000);
    },

    // ====== WHAT-IF RANK SLIDER ======
    renderWhatIfSlider(currentRank) {
        return `
        <div class="what-if-section">
            <h3>🎚 What-If Rank Analyzer</h3>
            <p style="font-size:13px;color:var(--text-secondary);">Drag the slider to see how predictions change at different ranks</p>
            <div class="what-if-slider-wrap">
                <span class="what-if-label">1</span>
                <input type="range" id="what-if-slider" min="1" max="200000" value="${currentRank}" class="what-if-range">
                <span class="what-if-label">2,00,000</span>
            </div>
            <div class="what-if-display">
                <span>Current: <strong>${currentRank.toLocaleString('en-IN')}</strong></span>
                <span id="what-if-value">Rank: <strong>${currentRank.toLocaleString('en-IN')}</strong></span>
                <button class="what-if-go" onclick="PredictorComponent.whatIfPredict()">Re-predict</button>
            </div>
        </div>`;
    },

    whatIfPredict() {
        const slider = document.getElementById('what-if-slider');
        if (!slider || !this.lastFormData) return;
        const newRank = parseInt(slider.value);
        document.getElementById('kcet-rank').value = newRank;
        this.handlePredict();
    },

    // ====== ANALYTICS DASHBOARD ======
    renderAnalytics() {
        const container = document.getElementById('analytics-dashboard');
        if (!container) return;
        const preds = this.lastPredictionResult?.predictions || [];
        if (preds.length === 0) {
            container.innerHTML = `<div class="empty-tab"><div class="empty-icon">📊</div><h3>Analytics Dashboard</h3><p>Run a prediction first to see analytics charts, branch distribution, fee comparison, and cutoff trend analysis.</p></div>`;
            return;
        }
        // Category distribution
        const safeCount = preds.filter(p => ['Safe', 'Very Safe', 'Good Chance'].includes(p.category)).length;
        const modCount = preds.filter(p => p.category === 'Moderate').length;
        const reachCount = preds.filter(p => ['Reach', 'Long Shot', 'Very Unlikely'].includes(p.category)).length;
        const total = preds.length;
        // Branch distribution
        const branchMap = {};
        preds.forEach(p => { branchMap[p.branch] = (branchMap[p.branch] || 0) + 1; });
        // Fee analysis
        const fees = preds.map(p => p.annual_fee || 0).filter(f => f > 0);
        const avgFee = fees.length > 0 ? Math.round(fees.reduce((a, b) => a + b, 0) / fees.length) : 0;
        const minFee = fees.length > 0 ? Math.min(...fees) : 0;
        const maxFee = fees.length > 0 ? Math.max(...fees) : 0;
        // Avg probability
        const avgProb = Math.round(preds.reduce((a, p) => a + (p.probability || 0), 0) / total);

        container.innerHTML = `
        <div class="analytics-grid">
            <div class="analytics-card glass">
                <h4>Admission Probability</h4>
                <div class="donut-chart">${this.renderDonut(safeCount, modCount, reachCount, total)}</div>
                <div class="donut-legend">
                    <span class="legend-item"><span class="legend-dot safe"></span>Safe: ${safeCount}</span>
                    <span class="legend-item"><span class="legend-dot moderate"></span>Moderate: ${modCount}</span>
                    <span class="legend-item"><span class="legend-dot reach"></span>Reach: ${reachCount}</span>
                </div>
            </div>
            <div class="analytics-card glass">
                <h4>Branch Distribution</h4>
                <div class="bar-chart">${Object.entries(branchMap).map(([b, c]) => `
                    <div class="bar-row"><span class="bar-label">${b}</span><div class="bar-track"><div class="bar-fill" style="width:${(c / total) * 100}%"></div></div><span class="bar-count">${c}</span></div>
                `).join('')}</div>
            </div>
            <div class="analytics-card glass">
                <h4>Fee Analysis</h4>
                <div class="fee-stats">
                    <div class="fee-stat"><span class="fee-icon">💚</span><span class="fee-label">Lowest</span><span class="fee-val">${minFee > 0 ? '₹' + minFee.toLocaleString('en-IN') : 'Free'}</span></div>
                    <div class="fee-stat"><span class="fee-icon">💛</span><span class="fee-label">Average</span><span class="fee-val">₹${avgFee.toLocaleString('en-IN')}</span></div>
                    <div class="fee-stat"><span class="fee-icon">❤️</span><span class="fee-label">Highest</span><span class="fee-val">₹${maxFee.toLocaleString('en-IN')}</span></div>
                </div>
            </div>
            <div class="analytics-card glass">
                <h4>Key Metrics</h4>
                <div class="key-metrics">
                    <div class="metric"><span class="metric-num">${total}</span><span class="metric-label">Options Found</span></div>
                    <div class="metric"><span class="metric-num">${avgProb}%</span><span class="metric-label">Avg. Probability</span></div>
                    <div class="metric"><span class="metric-num">${safeCount}</span><span class="metric-label">Safe Choices</span></div>
                    <div class="metric"><span class="metric-num">${Object.keys(branchMap).length}</span><span class="metric-label">Branches</span></div>
                </div>
            </div>
        </div>`;
    },

    renderDonut(safe, mod, reach, total) {
        if (total === 0) return '<p>No data</p>';
        const r = 50, cx = 60, cy = 60, circ = 2 * Math.PI * r;
        const s1 = (safe / total) * circ, s2 = (mod / total) * circ, s3 = (reach / total) * circ;
        return `<svg viewBox="0 0 120 120" width="140" height="140">
            <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#22c55e" stroke-width="14" stroke-dasharray="${s1} ${circ - s1}" stroke-dashoffset="0" transform="rotate(-90 ${cx} ${cy})" />
            <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#eab308" stroke-width="14" stroke-dasharray="${s2} ${circ - s2}" stroke-dashoffset="${-s1}" transform="rotate(-90 ${cx} ${cy})" />
            <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#ef4444" stroke-width="14" stroke-dasharray="${s3} ${circ - s3}" stroke-dashoffset="${-(s1 + s2)}" transform="rotate(-90 ${cx} ${cy})" />
            <text x="${cx}" y="${cy - 5}" text-anchor="middle" font-size="18" font-weight="800" fill="var(--text-primary, #333)">${total}</text>
            <text x="${cx}" y="${cy + 12}" text-anchor="middle" font-size="9" fill="var(--text-secondary, #888)">options</text>
        </svg>`;
    },

    // ====== COLLEGE COMPARISON ======
    renderCompare() {
        const container = document.getElementById('compare-container');
        if (!container) return;
        const preds = this.lastPredictionResult?.predictions || [];
        if (preds.length === 0) {
            container.innerHTML = `<div class="empty-tab"><div class="empty-icon">⚖️</div><h3>College Comparison</h3><p>Run a prediction first, then select colleges to compare side-by-side (fees, cutoffs, placement, NAAC grade).</p></div>`;
            return;
        }
        const selected = this.compareList.length > 0 ? preds.filter((_, i) => this.compareList.includes(i)) : preds.slice(0, 3);
        container.innerHTML = `
        <div class="compare-header">
            <h3>⚖️ Side-by-Side Comparison</h3>
            <p style="font-size:13px;color:var(--text-secondary);">Select up to 4 colleges to compare</p>
        </div>
        <div class="compare-selector">
            ${preds.map((p, i) => `<label class="compare-chip ${this.compareList.includes(i) ? 'selected' : ''}">
                <input type="checkbox" ${this.compareList.includes(i) ? 'checked' : ''} onchange="PredictorComponent.toggleCompare(${i})"> ${p.college_name} - ${p.branch}
            </label>`).join('')}
        </div>
        <div class="compare-table-wrap">
            <table class="compare-table">
                <thead><tr><th>Metric</th>${selected.map(s => `<th>${s.college_name}<br><small>${s.branch}</small></th>`).join('')}</tr></thead>
                <tbody>
                    <tr><td>Probability</td>${selected.map(s => `<td><strong>${s.probability}%</strong></td>`).join('')}</tr>
                    <tr><td>Category</td>${selected.map(s => `<td><span class="category-badge ${this.getCategoryClass(s.category)}">${s.category}</span></td>`).join('')}</tr>
                    <tr><td>Cutoff Rank</td>${selected.map(s => `<td>${s.cutoff_rank?.toLocaleString('en-IN') || '-'}</td>`).join('')}</tr>
                    <tr><td>Annual Fee</td>${selected.map(s => `<td>${s.annual_fee ? '₹' + s.annual_fee.toLocaleString('en-IN') : 'Free'}</td>`).join('')}</tr>
                    <tr><td>4-Year Cost</td>${selected.map(s => `<td>${s.four_year_cost ? '₹' + s.four_year_cost.toLocaleString('en-IN') : '-'}</td>`).join('')}</tr>
                    <tr><td>KEA Round</td>${selected.map(s => `<td><span class="kea-round-badge ${this.getRoundClass(s.predicted_round)}">${s.predicted_round || '-'}</span></td>`).join('')}</tr>
                    <tr><td>College Type</td>${selected.map(s => `<td>${s.college_type?.replace(/_/g, ' ') || '-'}</td>`).join('')}</tr>
                    <tr><td>Location</td>${selected.map(s => `<td>${s.location || '-'}</td>`).join('')}</tr>
                    <tr><td>NAAC Grade</td>${selected.map(s => `<td>${s.naac_grade || 'N/A'}</td>`).join('')}</tr>
                    <tr><td>Match Score</td>${selected.map(s => `<td><strong>${s.match_index}%</strong></td>`).join('')}</tr>
                </tbody>
            </table>
        </div>`;
    },

    toggleCompare(idx) {
        const pos = this.compareList.indexOf(idx);
        if (pos >= 0) { this.compareList.splice(pos, 1); }
        else if (this.compareList.length < 4) { this.compareList.push(idx); }
        this.renderCompare();
    },

    // ====== ROUND SIMULATOR ======
    renderSimulator() {
        const container = document.getElementById('simulator-container');
        if (!container) return;
        container.innerHTML = `
        <div class="simulator-content">
            <div class="sim-header">
                <h3>🔄 KEA Allotment Round Simulator</h3>
                <p>Experience how KEA allocates seats across 3 rounds. Enter your rank and watch the simulation!</p>
            </div>
            <div class="sim-controls">
                <input type="number" id="sim-rank" placeholder="Enter KCET rank" min="1" max="250000" value="${this.lastFormData?.kcet_rank || ''}">
                <button class="sim-start-btn" onclick="PredictorComponent.runSimulation()">▶ Start Simulation</button>
            </div>
            <div class="sim-timeline" id="sim-timeline">
                <div class="sim-round" id="sim-r1"><div class="sim-round-header"><span class="sim-dot pending"></span><strong>Round 1</strong><small>First allotment</small></div><div class="sim-round-body">Waiting...</div></div>
                <div class="sim-connector"></div>
                <div class="sim-round" id="sim-r2"><div class="sim-round-header"><span class="sim-dot pending"></span><strong>Round 2</strong><small>Upgradation round</small></div><div class="sim-round-body">Waiting...</div></div>
                <div class="sim-connector"></div>
                <div class="sim-round" id="sim-r3"><div class="sim-round-header"><span class="sim-dot pending"></span><strong>Extended Round</strong><small>Final chance</small></div><div class="sim-round-body">Waiting...</div></div>
            </div>
            <div class="sim-info">
                <h4>How KEA Rounds Work</h4>
                <ul>
                    <li><strong>Round 1:</strong> Initial allotment based on rank + preference order. You can accept, reject, or seek upgrade.</li>
                    <li><strong>Round 2:</strong> Only upward movement allowed. Seats vacated by rejects are redistributed.</li>
                    <li><strong>Extended Round:</strong> Remaining seats offered. Last chance to grab a seat.</li>
                    <li><strong>Important:</strong> Once you accept in Round 2, you cannot participate in Extended Round.</li>
                </ul>
            </div>
        </div>`;
    },

    async runSimulation() {
        const rank = parseInt(document.getElementById('sim-rank')?.value);
        if (!rank || rank < 1) { alert('Enter a valid rank'); return; }
        const rounds = ['sim-r1', 'sim-r2', 'sim-r3'];
        const roundNames = ['Round 1 (Guaranteed)', 'Round 2 (Likely)', 'Extended Round'];
        const preds = this.lastPredictionResult?.predictions || [];
        // Reset
        rounds.forEach(id => { const el = document.getElementById(id); if (el) { el.querySelector('.sim-dot').className = 'sim-dot pending'; el.querySelector('.sim-round-body').innerHTML = 'Processing...'; } });
        // Simulate each round with delay
        for (let r = 0; r < 3; r++) {
            await new Promise(resolve => setTimeout(resolve, 1200));
            const el = document.getElementById(rounds[r]);
            if (!el) continue;
            const roundPreds = preds.filter(p => p.predicted_round?.includes(roundNames[r].split(' ')[0]) || (r === 0 && p.predicted_round?.includes('Guaranteed')));
            el.querySelector('.sim-dot').className = `sim-dot ${roundPreds.length > 0 ? 'success' : 'empty'}`;
            el.querySelector('.sim-round-body').innerHTML = roundPreds.length > 0
                ? roundPreds.slice(0, 5).map(p => `<div class="sim-allotment"><strong>${p.college_name}</strong> - ${p.branch} <span class="category-badge ${this.getCategoryClass(p.category)}">${p.probability}%</span></div>`).join('') + (roundPreds.length > 5 ? `<small>+${roundPreds.length - 5} more options</small>` : '')
                : `<div class="sim-empty">No new allotments in this round for rank ${rank.toLocaleString('en-IN')}</div>`;
        }
        if (preds.length > 0) this.launchConfetti();
    },

    // ====== DOCUMENT CHECKLIST ======
    renderChecklist() {
        const container = document.getElementById('checklist-container');
        if (!container) return;
        const saved = JSON.parse(localStorage.getItem('kea_checklist') || '{}');
        const mandatoryDocs = this.keaDocuments.filter(d => d.mandatory);
        const optionalDocs = this.keaDocuments.filter(d => !d.mandatory);
        const checkedCount = Object.values(saved).filter(v => v).length;
        const totalMandatory = mandatoryDocs.length;
        const mandatoryChecked = mandatoryDocs.filter(d => saved[d.id]).length;
        const progress = Math.round((checkedCount / this.keaDocuments.length) * 100);

        container.innerHTML = `
        <div class="checklist-content">
            <div class="checklist-header">
                <h3>📋 KEA Counselling Document Checklist</h3>
                <p>Track your document preparation. Progress is saved automatically.</p>
            </div>
            <div class="checklist-progress">
                <div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:${progress}%"></div></div>
                <span class="progress-text">${checkedCount}/${this.keaDocuments.length} documents ready (${progress}%)</span>
                ${mandatoryChecked < totalMandatory ? `<span class="progress-warn">⚠️ ${totalMandatory - mandatoryChecked} mandatory docs pending!</span>` : `<span class="progress-ok">✅ All mandatory documents ready!</span>`}
            </div>
            <div class="checklist-section">
                <h4>🔴 Mandatory Documents</h4>
                ${mandatoryDocs.map(d => `
                <label class="checklist-item ${saved[d.id] ? 'checked' : ''}" onclick="PredictorComponent.toggleDoc('${d.id}')">
                    <div class="check-box ${saved[d.id] ? 'checked' : ''}"><svg viewBox="0 0 24 24" width="16" height="16"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="currentColor"/></svg></div>
                    <div class="check-info"><strong>${d.name}</strong><small>${d.desc}</small></div>
                    <span class="mandatory-tag">Required</span>
                </label>`).join('')}
            </div>
            <div class="checklist-section">
                <h4>🟡 Optional / Category-Specific</h4>
                ${optionalDocs.map(d => `
                <label class="checklist-item ${saved[d.id] ? 'checked' : ''}" onclick="PredictorComponent.toggleDoc('${d.id}')">
                    <div class="check-box ${saved[d.id] ? 'checked' : ''}"><svg viewBox="0 0 24 24" width="16" height="16"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" fill="currentColor"/></svg></div>
                    <div class="check-info"><strong>${d.name}</strong><small>${d.desc}</small></div>
                    <span class="optional-tag">If applicable</span>
                </label>`).join('')}
            </div>
        </div>`;
    },

    toggleDoc(docId) {
        const saved = JSON.parse(localStorage.getItem('kea_checklist') || '{}');
        saved[docId] = !saved[docId];
        localStorage.setItem('kea_checklist', JSON.stringify(saved));
        this.renderChecklist();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('predictor-section')) {
        PredictorComponent.init();
    }
});

// Confetti CSS injection
const confettiStyle = document.createElement('style');
confettiStyle.textContent = `@keyframes confettiFall{0%{transform:translateY(-10px) rotate(0deg);opacity:1}100%{transform:translateY(100vh) rotate(720deg);opacity:0}}`;
document.head.appendChild(confettiStyle);

window.PredictorComponent = PredictorComponent;

