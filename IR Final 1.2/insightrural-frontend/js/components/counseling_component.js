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
                                <button class="btn-secondary" onclick="window.CounselingSuiteComponent.copyToClipboard()">📋 Copy List</button>
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
                    onchange="window.CounselingSuiteComponent.toggleDoc('${doc.id}')">
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
            .counseling-container { max-width: 1100px; margin: 0 auto; padding: 1.5rem; animation: counselingFadeIn 0.5s ease; }
            @keyframes counselingFadeIn {
                from { opacity: 0; transform: translateY(15px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .suite-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }
            .suite-header h2 { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, var(--primary-color, #10a37f) 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .suite-tabs { display: flex; gap: 0.5rem; background: var(--bg-primary); padding: 6px; border-radius: 12px; border: 1px solid var(--border-color); }
            .tab-btn { padding: 10px 20px; border: none; background: transparent; cursor: pointer; border-radius: 8px; font-weight: 600; color: var(--text-secondary); transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }
            .tab-btn:hover { color: var(--text-primary); background: rgba(16, 163, 127, 0.05); }
            .tab-btn.active { background: var(--bg-secondary); color: var(--primary-color, #10a37f); box-shadow: var(--shadow-sm); border: 1px solid var(--border-color); }
            
            .guide-layout { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; }
            .process-step { display: flex; gap: 1.25rem; background: var(--bg-secondary); padding: 1.25rem; border-radius: 16px; margin-bottom: 1.25rem; border: 1px solid var(--border-color); transition: all 0.3s ease; }
            .process-step:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: var(--primary-color); }
            .step-icon { font-size: 1.8rem; background: rgba(16, 163, 127, 0.08); width: 54px; height: 54px; display: flex; align-items: center; justify-content: center; border-radius: 14px; flex-shrink: 0; box-shadow: inset 0 0 10px rgba(16, 163, 127, 0.05); }
            .step-content h4 { margin: 0 0 6px 0; color: var(--text-primary); font-size: 1.1rem; font-weight: 700; }
            .step-content p { margin: 0; color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; }
            
            .checklist-box { background: var(--bg-secondary); padding: 1.5rem; border-radius: 18px; border: 1px solid var(--border-color); margin-bottom: 1.5rem; }
            .checklist-item { display: flex; gap: 12px; margin-bottom: 1rem; align-items: flex-start; transition: all 0.2s ease; }
            .checklist-item:hover { transform: translateX(2px); }
            .checklist-item input { margin-top: 6px; width: 16px; height: 16px; accent-color: var(--primary-color); }
            .doc-name { display: block; font-weight: 600; color: var(--text-primary); font-size: 0.95rem; }
            .doc-detail { font-size: 0.82rem; color: var(--text-muted); display: block; margin-top: 2px; }
            .req { color: var(--danger, #ef4444); font-weight: bold; margin-left: 2px; }
            
            .faq-box { background: var(--bg-secondary); padding: 1.5rem; border-radius: 18px; border: 1px solid var(--border-color); }
            .faq-box h3 { font-size: 1.15rem; font-weight: 800; color: var(--text-primary); margin-bottom: 1rem; }
            .faq-item { margin-bottom: 1.25rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); }
            .faq-item:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
            .faq-item strong { color: var(--text-primary); font-size: 0.92rem; display: block; margin-bottom: 4px; }
            .faq-item p { margin: 0; color: var(--text-secondary); font-size: 0.88rem; line-height: 1.5; }
            
            .generator-layout { display: grid; grid-template-columns: 320px 1fr; gap: 2rem; }
            .card { background: var(--bg-secondary); padding: 1.75rem; border-radius: 18px; border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); }
            .generator-form h3 { font-size: 1.2rem; font-weight: 800; color: var(--text-primary); margin-bottom: 0.5rem; }
            .generator-form p { color: var(--text-secondary); font-size: 0.88rem; margin-bottom: 1.5rem; line-height: 1.4; }
            .form-group { margin-bottom: 1.25rem; }
            .form-group label { display: block; font-size: 0.88rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
            .form-group input, .form-group select { width: 100%; padding: 10px 14px; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-input, var(--bg-primary)); color: var(--text-primary); font-family: inherit; font-size: 0.92rem; transition: all 0.2s; }
            .form-group input:focus, .form-group select:focus { border-color: var(--primary-color); outline: none; box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1); }
            
            .checkbox-group { display: flex; flex-direction: column; gap: 8px; max-height: 180px; overflow-y: auto; padding: 4px; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-input, var(--bg-primary)); }
            .checkbox-group label { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; font-weight: 500; color: var(--text-primary); cursor: pointer; padding: 4px 8px; border-radius: 6px; transition: background 0.15s; }
            .checkbox-group label:hover { background: var(--bg-hover); }
            .checkbox-group input { width: 15px; height: 15px; accent-color: var(--primary-color); }
            
            .generator-results { background: var(--bg-secondary); padding: 1.75rem; border-radius: 18px; border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); display: flex; flex-direction: column; height: 100%; }
            .results-header { display: flex; gap: 0.75rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
            .stat-badge { padding: 6px 14px; border-radius: 50px; font-size: 0.85rem; font-weight: 700; background: var(--bg-primary); border: 1px solid var(--border-color); }
            .stat-badge.safe { border-color: rgba(34, 197, 94, 0.25); background: rgba(34, 197, 94, 0.05); color: #22c55e; }
            .stat-badge.realistic { border-color: rgba(245, 158, 11, 0.25); background: rgba(245, 158, 11, 0.05); color: #f59e0b; }
            .stat-badge.ambitious { border-color: rgba(239, 68, 68, 0.25); background: rgba(239, 68, 68, 0.05); color: #ef4444; }
            
            .options-list { max-height: 480px; overflow-y: auto; background: var(--bg-input, var(--bg-primary)); border-radius: 14px; border: 1px solid var(--border-color); margin-bottom: 1.25rem; }
            .option-row { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border-color); gap: 1.25rem; transition: all 0.2s ease; }
            .option-row:hover { background: var(--bg-hover); }
            .option-row:last-child { border-bottom: none; }
            .opt-rank { font-weight: 800; color: var(--text-muted); width: 32px; font-size: 1rem; }
            .opt-info { flex: 1; }
            .opt-info strong { color: var(--text-primary); font-size: 0.95rem; display: block; }
            .opt-branch { display: block; font-size: 0.82rem; color: var(--text-secondary); margin-top: 2px; }
            .opt-chance { font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.3px; }
            
            .tag-safe { background: rgba(34, 197, 94, 0.12); color: #22c55e; }
            .tag-realistic { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }
            .tag-ambitious, .tag-dream { background: rgba(239, 68, 68, 0.12); color: #ef4444; }
            
            .btn-primary { padding: 12px 24px; border-radius: 12px; font-family: inherit; font-size: 0.95rem; font-weight: 700; width: 100%; border: none; cursor: pointer; background: linear-gradient(135deg, var(--primary-color, #10a37f), #0d9488); color: white; box-shadow: 0 4px 15px rgba(16, 163, 127, 0.2); transition: all 0.25s; }
            .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(16, 163, 127, 0.3); }
            .btn-primary:disabled { background: var(--border-color); color: var(--text-muted); cursor: not-allowed; transform: none; box-shadow: none; }
            
            .btn-secondary { padding: 10px 20px; border-radius: 10px; font-family: inherit; font-size: 0.9rem; font-weight: 600; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-secondary); color: var(--text-primary); transition: all 0.2s; align-self: flex-start; }
            .btn-secondary:hover { border-color: var(--primary-color); color: var(--primary-color); }
            
            @media (max-width: 768px) {
                .guide-layout, .generator-layout { grid-template-columns: 1fr; }
            }
        `;
        document.head.appendChild(style);
    }
}

window.CounselingSuiteComponent = new CounselingSuite();
