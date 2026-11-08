class NeetCounselingComponent {
    constructor() {
        this.container = null;
        this.activeTab = 'predict';
    }

    async activate() {
        this.container = document.getElementById('neet-section');
        if(!this.container) return;
        this.render();
        this.setupEventListeners();
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="counseling-container fade-in" style="padding:20px; max-width:1200px; margin:auto;">
                <div class="suite-header" style="margin-bottom:20px;">
                    <h2>NEET Counseling Hub (MBBS/BDS/AYUSH)</h2>
                    <div class="suite-tabs" style="display:flex; gap:10px; margin-top:10px;">
                        <button class="tab-btn ${this.activeTab === 'predict' ? 'active' : ''}" data-tab="predict">🎯 Predict Seat</button>
                        <button class="tab-btn ${this.activeTab === 'colleges' ? 'active' : ''}" data-tab="colleges">🏥 Medical Colleges</button>
                    </div>
                </div>

                <div class="suite-content">
                    <!-- PREDICT TAB -->
                    <div id="neet-tab-predict" class="${this.activeTab === 'predict' ? '' : 'hidden'}">
                        <div class="generator-layout" style="display:grid; grid-template-columns: 1fr 2fr; gap:20px;">
                            <div class="generator-form card" style="background:var(--bg-secondary); color:var(--text-primary); padding:20px; border-radius:12px; border:1px solid var(--border-color); box-shadow:0 4px 6px rgba(0,0,0,0.05);">
                                <h3>NEET Predictor</h3>
                                <div class="form-group" style="margin-bottom:15px;">
                                    <label style="display:block; margin-bottom:5px;">NEET All India Rank</label>
                                    <input type="number" id="neet-rank" placeholder="e.g. 25000" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary);">
                                </div>
                                <div class="form-group" style="margin-bottom:15px;">
                                    <label style="display:block; margin-bottom:5px;">NEET Score (Optional)</label>
                                    <input type="number" id="neet-score" placeholder="e.g. 620" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary);">
                                </div>
                                <div class="form-group" style="margin-bottom:15px;">
                                    <label style="display:block; margin-bottom:5px;">Category</label>
                                    <select id="neet-category" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary);">
                                        <option value="OPEN">OPEN (General)</option>
                                        <option value="OBC-NCL">OBC-NCL</option>
                                        <option value="SC">SC</option>
                                        <option value="ST">ST</option>
                                        <option value="EWS">EWS</option>
                                    </select>
                                </div>
                                <div class="form-group" style="margin-bottom:15px;">
                                    <label style="display:block; margin-bottom:5px;">State Domicile</label>
                                    <input type="text" id="neet-state" placeholder="e.g. Karnataka" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary);">
                                </div>
                                <button id="neet-btn-predict" class="btn-primary" style="width:100%; padding:12px; background:#10a37f; color:white; border:none; border-radius:6px; cursor:pointer;">Generate Predictions</button>
                            </div>
                            
                            <div class="results-column">
                                <h3>Predicted Options</h3>
                                <div id="neet-prediction-results" style="display:flex; flex-direction:column; gap:15px; margin-top:15px;">
                                    <div style="color:var(--text-secondary);">Enter your ranks and click generate to see predictions.</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- COLLEGES TAB -->
                    <div id="neet-tab-colleges" class="${this.activeTab === 'colleges' ? '' : 'hidden'}">
                        <div style="margin-bottom:20px; display:flex; gap:10px;">
                            <input type="text" id="neet-search" placeholder="Search colleges..." style="padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary); flex:1;">
                            <select id="neet-filter-type" style="padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary);">
                                <option value="">All Types</option>
                                <option value="Government">Government</option>
                                <option value="Private">Private</option>
                                <option value="Deemed">Deemed</option>
                                <option value="Dental">Dental</option>
                                <option value="AYUSH">AYUSH</option>
                            </select>
                            <button id="neet-btn-search" style="padding:10px 20px; background:#10a37f; color:white; border:none; border-radius:6px; cursor:pointer;">Search</button>
                        </div>
                        <div id="neet-colleges-list" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(300px, 1fr)); gap:20px;">
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        if (!this.container) return;

        const tabs = this.container.querySelectorAll('.tab-btn');
        tabs.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.getAttribute('data-tab');
                this.activeTab = tab;
                this.render();
                this.setupEventListeners();
                if(tab === 'colleges') this.fetchColleges();
            });
        });

        const predictBtn = this.container.querySelector('#neet-btn-predict');
        if (predictBtn) {
            predictBtn.addEventListener('click', () => this.generatePrediction());
        }

        const searchBtn = this.container.querySelector('#neet-btn-search');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.fetchColleges());
        }
    }

    async generatePrediction() {
        const btn = document.getElementById('neet-btn-predict');
        const resultsDiv = document.getElementById('neet-prediction-results');
        btn.disabled = true;
        btn.innerText = "Analyzing...";

        try {
            const data = {
                neet_rank: document.getElementById('neet-rank').value,
                neet_score: document.getElementById('neet-score').value,
                category: document.getElementById('neet-category').value,
                state: document.getElementById('neet-state').value,
                top_n: 10
            };

            const res = await fetch(`${API_BASE_URL}/api/neet/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await res.json();
            
            if (result.success) {
                resultsDiv.innerHTML = result.predictions.map(p => `
                    <div style="background:var(--bg-secondary); color:var(--text-primary); border-radius:8px; padding:15px; border:1px solid var(--border-color); box-shadow:0 2px 5px rgba(0,0,0,0.05); border-left:4px solid ${this.getColor(p.admission_chance)}">
                        <div style="display:flex; justify-content:space-between;">
                            <h4 style="margin:0; font-size:16px; color:var(--text-primary);">${p.college}</h4>
                            <span style="background:${this.getColor(p.admission_chance)}20; color:${this.getColor(p.admission_chance)}; padding:4px 8px; border-radius:12px; font-size:12px; font-weight:bold;">${p.admission_chance}</span>
                        </div>
                        <p style="margin:5px 0; color:var(--text-secondary); font-size:14px;">${p.course} &bull; ${p.track} &bull; ${p.quota} Quota</p>
                        <div style="display:flex; justify-content:space-between; font-size:13px; color:var(--text-secondary); margin-top:10px;">
                            <span>Expected Cutoff: <b>${p.predicted_cutoff}</b></span>
                            <span>Probability: <b>${Math.round(p.probability)}%</b></span>
                        </div>
                    </div>
                `).join('');
            } else {
                resultsDiv.innerHTML = `<div style="color:#ef4444;">${result.error || 'Error fetching predictions.'}</div>`;
            }
        } catch (e) {
            console.error("NEET predict error", e);
            resultsDiv.innerHTML = `<div style="color:#ef4444;">Failed to connect to server.</div>`;
        } finally {
            btn.disabled = false;
            btn.innerText = "Generate Predictions";
        }
    }

    async fetchColleges() {
        const listDiv = document.getElementById('neet-colleges-list');
        const search = document.getElementById('neet-search').value;
        const type = document.getElementById('neet-filter-type').value;

        listDiv.innerHTML = "Loading...";

        try {
            const res = await fetch(`${API_BASE_URL}/api/neet/colleges?search=${encodeURIComponent(search)}&type=${encodeURIComponent(type)}`);
            const data = await res.json();
            
            if (data.success && data.colleges.length > 0) {
                listDiv.innerHTML = data.colleges.map(c => `
                    <div style="background:var(--bg-secondary); color:var(--text-primary); border-radius:8px; padding:15px; border:1px solid var(--border-color);">
                        <span style="font-size:11px; font-weight:bold; color:#10a37f; text-transform:uppercase;">${c.type}</span>
                        <h4 style="margin:5px 0; color:var(--text-primary);">${c.name}</h4>
                        <p style="margin:0; font-size:13px; color:var(--text-secondary);">${c.state}</p>
                    </div>
                `).join('');
            } else {
                listDiv.innerHTML = "No colleges found.";
            }
        } catch(e) {
            console.error("Fetch colleges error", e);
            listDiv.innerHTML = "Error loading colleges.";
        }
    }

    getColor(tier) {
        if (tier.includes("Safe")) return "#10a37f";
        if (tier.includes("Moderate")) return "#f59e0b";
        return "#ef4444";
    }
}

window.NeetComponent = window.NeetComponent || new NeetCounselingComponent();
