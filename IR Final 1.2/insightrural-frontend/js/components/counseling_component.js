/**
 * KEA Counseling Suite Component
 * Tab 1: Process Guide (Wizard)
 * Tab 2: Smart Option Generator (AI)
 */

class CounselingSuite {
    constructor() {
        this.container = null;
        this.activeTab = 'guide'; // 'guide' or 'generate'
        this.guideData = null;
    }

    async activate() {
        this.container = document.getElementById('counseling-section');
        if (!this.guideData) await this.fetchGuideData();
        this.render();
        this.setupEventListeners();
    }

    async fetchGuideData() {
        try {
            const res = await fetch(`${API_BASE_URL}/api/counseling/guide`);
            this.guideData = await res.json();
            console.log("Guide Data Loaded:", this.guideData);
        } catch (e) {
            console.error("Failed to load guide:", e);
        }
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="counseling-container fade-in">
                <div class="suite-header">
                    <h2>🏛️ KEA Counseling Suite</h2>
                    <div class="suite-tabs">
                        <button class="tab-btn ${this.activeTab === 'guide' ? 'active' : ''}" data-tab="guide">
                            📘 Process Guide
                        </button>
                        <button class="tab-btn ${this.activeTab === 'generate' ? 'active' : ''}" data-tab="generate">
                            ✨ Smart Option Generator
                        </button>
                    </div>
                </div>

                <div class="suite-content">
                    <!-- GUIDE TAB -->
                    <div id="tab-guide" class="${this.activeTab === 'guide' ? '' : 'hidden'}">
                        <div class="guide-layout">
                            <div class="steps-column">
                                <h3>📝 Step-by-Step Process</h3>
                                <div class="step-list">
                                    ${this.renderSteps()}
                                </div>
                            </div>
                            <div class="checklist-column">
                                <h3>✅ Document Checklist</h3>
                                <div class="checklist-box">
                                    ${this.renderChecklist()}
                                </div>
                                <div class="faq-box">
                                    <h3>❓ FAQ</h3>
                                    ${this.renderFAQ()}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- GENERATOR TAB -->
                    <div id="tab-generate" class="${this.activeTab === 'generate' ? '' : 'hidden'}">
                        <div class="generator-layout">
                            <div class="generator-form card">
                                <h3>🤖 AI Option Entry Generator</h3>
                                <p>Enter your details to generate a scientifically sorted priority list.</p>
                                
                                <div class="form-group">
                                    <label>KCET Rank</label>
                                    <input type="number" id="gen-rank" placeholder="e.g. 15000">
                                </div>
                                
                                <div class="form-group">
                                    <label>Category</label>
                                    <select id="gen-category">
                                        <option value="GM">General Merit (GM)</option>
                                        <option value="OBC">OBC (2A/2B/3A/3B)</option>
                                        <option value="SC">SC</option>
                                        <option value="ST">ST</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label>Preferred Branches</label>
                                    <div class="checkbox-group">
                                        <label><input type="checkbox" value="CSE" checked> CSE</label>
                                        <label><input type="checkbox" value="ISE" checked> ISE</label>
                                        <label><input type="checkbox" value="ECE" checked> ECE</label>
                                        <label><input type="checkbox" value="AI"> AI & DS</label>
                                        <label><input type="checkbox" value="ME"> Mech</label>
                                        <label><input type="checkbox" value="CIVIL"> Civil</label>
                                    </div>
                                </div>
                                
                                <button class="btn-primary" id="btn-generate-options">
                                    Generate Priority List 🚀
                                </button>
                            </div>
                            
                            <div class="generator-results hidden" id="gen-results">
                                <div class="results-header">
                                    <div class="stat-badge safe">🟢 Safe: <span id="count-safe">0</span></div>
                                    <div class="stat-badge realistic">🟡 Realistic: <span id="count-realistic">0</span></div>
                                    <div class="stat-badge ambitious">🔴 Ambitious: <span id="count-ambitious">0</span></div>
                                </div>
                                <div class="options-list" id="options-list-container">
                                    <!-- Options injected here -->
                                </div>
                                <button class="btn-secondary" onclick="window.CounselingSuite.copyToClipboard()">📋 Copy List</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.addStyles();
    }

    renderSteps() {
        if (!this.guideData) return '<p>Loading...</p>';
        return this.guideData.engineering.steps.map(step => `
            <div class="process-step">
                <div class="step-icon">${step.icon}</div>
                <div class="step-content">
                    <h4>${step.id}. ${step.title}</h4>
                    <p>${step.description}</p>
                </div>
            </div>
        `).join('');
    }

    renderChecklist() {
        if (!this.guideData) return '';
        // Load saved state
        const saved = JSON.parse(localStorage.getItem('kea_docs') || '{}');

        return this.guideData.documents.map(doc => `
            <div class="checklist-item">
                <input type="checkbox" id="${doc.id}" 
                    ${saved[doc.id] ? 'checked' : ''} 
                    onchange="window.CounselingSuite.toggleDoc('${doc.id}')">
                <label for="${doc.id}">
                    <span class="doc-name">${doc.name} ${doc.required ? '<span class="req">*</span>' : ''}</span>
                    <span class="doc-detail">${doc.details}</span>
                </label>
            </div>
        `).join('');
    }

    renderFAQ() {
        if (!this.guideData) return '';
        return this.guideData.faq.map(f => `
            <div class="faq-item">
                <strong>Q: ${f.q}</strong>
                <p>A: ${f.a}</p>
            </div>
        `).join('');
    }

    toggleDoc(id) {
        const saved = JSON.parse(localStorage.getItem('kea_docs') || '{}');
        saved[id] = !saved[id];
        localStorage.setItem('kea_docs', JSON.stringify(saved));
    }

    setupEventListeners() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.activeTab = e.target.dataset.tab;
                this.render();
                this.setupEventListeners(); // Re-attach after re-render
            });
        });

        const genBtn = document.getElementById('btn-generate-options');
        if (genBtn) {
            genBtn.addEventListener('click', () => this.generateOptions());
        }
    }

    async generateOptions() {
        const rank = document.getElementById('gen-rank').value;
        const category = document.getElementById('gen-category').value;
        const branches = Array.from(document.querySelectorAll('.checkbox-group input:checked')).map(cb => cb.value);

        if (!rank) { alert("Please enter your rank"); return; }

        const btn = document.getElementById('btn-generate-options');
        btn.textContent = "Analyzing 50+ Colleges...";
        btn.disabled = true;

        try {
            const res = await fetch(`${API_BASE_URL}/api/counseling/generate-options`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rank, category, branches })
            });

            const data = await res.json();

            document.getElementById('gen-results').classList.remove('hidden');
            document.getElementById('count-safe').textContent = data.summary.safe_count;
            document.getElementById('count-realistic').textContent = data.summary.realistic_count;
            document.getElementById('count-ambitious').textContent = data.summary.ambitious_count;

            const listContainer = document.getElementById('options-list-container');
            listContainer.innerHTML = data.options.map((opt, idx) => `
                <div class="option-row ${opt.type}">
                    <div class="opt-rank">#${idx + 1}</div>
                    <div class="opt-info">
                        <strong>${opt.college_name}</strong>
                        <span class="opt-branch">${opt.branch} | Cutoff: ${opt.cutoff}</span>
                    </div>
                    <div class="opt-chance tag-${opt.type}">${opt.chance}</div>
                </div>
            `).join('');

        } catch (error) {
            alert("Error generating options: " + error.message);
        } finally {
            btn.textContent = "Generate Priority List 🚀";
            btn.disabled = false;
        }
    }

    copyToClipboard() {
        const text = Array.from(document.querySelectorAll('.option-row')).map(row => {
            return row.innerText.replace(/\n/g, ' ');
        }).join('\n');
        navigator.clipboard.writeText(text);
        alert("List copied to clipboard!");
    }

    addStyles() {
        if (document.getElementById('counseling-css')) return;
        const style = document.createElement('style');
        style.id = 'counseling-css';
        style.textContent = `
            .counseling-container { max-width: 1000px; margin: 0 auto; padding: 1rem; }
            .suite-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }
            .suite-tabs { display: flex; gap: 1rem; background: #f3f4f6; padding: 5px; border-radius: 8px; }
            .tab-btn { padding: 10px 20px; border: none; background: transparent; cursor: pointer; border-radius: 6px; font-weight: 500; color: #6b7280; transition: all 0.2s; }
            .tab-btn.active { background: white; color: var(--primary-color); shadow: 0 1px 3px rgba(0,0,0,0.1); }
            
            .guide-layout { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; }
            .process-step { display: flex; gap: 1rem; background: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #e5e7eb; }
            .step-icon { font-size: 2rem; background: #f0fdf4; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }
            .step-content h4 { margin: 0 0 5px 0; color: #1f2937; }
            .step-content p { margin: 0; color: #6b7280; font-size: 0.9rem; }
            
            .checklist-box { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb; }
            .checklist-item { display: flex; gap: 10px; margin-bottom: 1rem; align-items: flex-start; }
            .checklist-item input { margin-top: 5px; }
            .doc-name { display: block; font-weight: 600; color: #374151; }
            .doc-detail { font-size: 0.85rem; color: #9ca3af; }
            .req { color: red; }
            
            .generator-layout { display: grid; grid-template-columns: 300px 1fr; gap: 2rem; }
            .card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb; }
            .form-group { margin-bottom: 1rem; }
            .checkbox-group { display: flex; flex-direction: column; gap: 5px; }
            
            .results-header { display: flex; gap: 1rem; margin-bottom: 1rem; }
            .stat-badge { padding: 5px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; background: white; border: 1px solid #e5e7eb; }
            
            .options-list { max-height: 500px; overflow-y: auto; background: white; border-radius: 8px; border: 1px solid #e5e7eb; }
            .option-row { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #f3f4f6; gap: 1rem; }
            .option-row:last-child { border-bottom: none; }
            .opt-rank { font-weight: bold; color: #9ca3af; width: 40px; }
            .opt-info { flex: 1; }
            .opt-branch { display: block; font-size: 0.85rem; color: #6b7280; }
            
            .tag-safe { background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
            .tag-realistic { background: #fef9c3; color: #854d0e; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
            .tag-ambitious, .tag-dream { background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
            
            @media (max-width: 768px) {
                .guide-layout, .generator-layout { grid-template-columns: 1fr; }
            }
        `;
        document.head.appendChild(style);
    }
}

window.CounselingSuiteComponent = new CounselingSuite();
