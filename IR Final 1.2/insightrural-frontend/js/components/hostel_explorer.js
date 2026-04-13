// =============================================================
// Hostel Explorer Component
// Full hostel browser with filters, maps, how-to-apply, AI auto-apply
// =============================================================

const HostelExplorer = {
    allHostels: [],
    filteredHostels: [],
    activeFilter: 'all',
    searchQuery: '',
    compareList: [],
    isLoading: false,

    async init() {
        this.container = document.getElementById('hostels-section');
        if (!this.container) return;
        this.render();
        await this.loadHostels();
    },

    render() {
        this.container.innerHTML = `
            <div class="hostel-page">
                <div class="hostel-hero">
                    <div class="hero-icon-hostel">🏠</div>
                    <h2>Hostel Explorer</h2>
                    <p>Find the perfect accommodation — college hostels, government hostels & PGs</p>
                </div>

                <div class="hostel-controls">
                    <div class="hostel-search-wrap">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="hostel-search" placeholder="Search by hostel name, college, or location..." />
                    </div>
                    <div class="hostel-filters" id="hostel-filters">
                        <button class="filter-chip active" data-filter="all">All</button>
                        <button class="filter-chip" data-filter="college">🏛️ College</button>
                        <button class="filter-chip" data-filter="bcm">BCM</button>
                        <button class="filter-chip" data-filter="sc/st">SC/ST</button>
                        <button class="filter-chip" data-filter="minority">Minority</button>
                        <button class="filter-chip" data-filter="government">Government</button>
                    </div>
                </div>

                <div class="hostel-stats" id="hostel-stats"></div>
                
                <div class="hostel-grid" id="hostel-grid">
                    ${this.renderLoadingCards()}
                </div>

                <!-- Compare Panel -->
                <div class="compare-panel hidden" id="compare-panel">
                    <div class="compare-header">
                        <h3>⚖️ Compare Hostels (<span id="compare-count">0</span>/3)</h3>
                        <button class="btn-primary btn-sm" id="btn-compare-now">Compare Now</button>
                        <button class="btn-secondary btn-sm" id="btn-clear-compare">Clear</button>
                    </div>
                    <div class="compare-items" id="compare-items"></div>
                </div>

                <!-- Compare Modal -->
                <div class="modal hidden" id="compare-modal">
                    <div class="modal-overlay"></div>
                    <div class="modal-container compare-modal-container">
                        <div class="modal-header">
                            <h2>⚖️ Hostel Comparison</h2>
                            <button class="close-modal" id="close-compare-modal">×</button>
                        </div>
                        <div class="modal-body" id="compare-modal-body"></div>
                    </div>
                </div>

                <!-- How to Apply Modal -->
                <div class="modal hidden" id="hostel-apply-modal">
                    <div class="modal-overlay"></div>
                    <div class="modal-container hostel-apply-container">
                        <div class="modal-header">
                            <h2>📝 How to Apply</h2>
                            <button class="close-modal" id="close-apply-modal">×</button>
                        </div>
                        <div class="modal-body" id="apply-modal-body"></div>
                    </div>
                </div>

                <!-- AI Auto-Apply Modal -->
                <div class="modal hidden" id="hostel-ai-apply-modal">
                    <div class="modal-overlay"></div>
                    <div class="modal-container hostel-ai-apply-container">
                        <div class="modal-header">
                            <h2>✨ AI Hostel Application Generator</h2>
                            <button class="close-modal" id="close-ai-apply-modal">×</button>
                        </div>
                        <div class="modal-body">
                            <div id="ai-apply-step-1" class="ai-apply-step">
                                <div class="hostel-target-info">
                                    <h3 id="ai-target-hostel-name"></h3>
                                    <p>Let AI write your hostel application letter instantly</p>
                                </div>
                                <div class="form-group">
                                    <label>Why do you need hostel accommodation?</label>
                                    <textarea id="hostel-reason" placeholder="E.g., My home is 200km from the college. I come from a farming family and cannot afford daily commute..."></textarea>
                                </div>
                                <div class="form-group">
                                    <label>Which college are you admitted to?</label>
                                    <input type="text" id="hostel-college-input" placeholder="E.g., BMSCE, RVCE, SIT Tumkur..." />
                                </div>
                                <button class="btn-primary btn-block" id="btn-generate-hostel-app">
                                    ⚡ Generate Application Letter
                                </button>
                            </div>
                            <div id="ai-apply-step-2" class="ai-apply-step hidden">
                                <div class="application-output" id="hostel-app-output" contenteditable="true"></div>
                                <div class="ai-apply-actions">
                                    <button class="btn-secondary" id="btn-regenerate-hostel-app">🔄 Regenerate</button>
                                    <button class="btn-primary" id="btn-copy-hostel-app">📋 Copy to Clipboard</button>
                                </div>
                            </div>
                            <div id="ai-apply-loading" class="loading-overlay hidden">
                                <div class="spinner"></div>
                                <p>AI is drafting your application...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.setupEventListeners();
    },

    renderLoadingCards() {
        return Array(6).fill('').map(() => `
            <div class="hostel-card skeleton">
                <div class="skeleton-line w60"></div>
                <div class="skeleton-line w80"></div>
                <div class="skeleton-line w40"></div>
            </div>
        `).join('');
    },

    setupEventListeners() {
        // Filters
        document.querySelectorAll('#hostel-filters .filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                document.querySelectorAll('#hostel-filters .filter-chip').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                this.activeFilter = e.target.dataset.filter;
                this.applyFilters();
            });
        });

        // Search
        const searchInput = document.getElementById('hostel-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.applyFilters();
            });
        }

        // Compare panel buttons
        document.getElementById('btn-compare-now')?.addEventListener('click', () => this.showComparison());
        document.getElementById('btn-clear-compare')?.addEventListener('click', () => this.clearCompare());
        document.getElementById('close-compare-modal')?.addEventListener('click', () => {
            document.getElementById('compare-modal').classList.add('hidden');
        });

        // Apply modal close
        document.getElementById('close-apply-modal')?.addEventListener('click', () => {
            document.getElementById('hostel-apply-modal').classList.add('hidden');
        });

        // AI apply modal
        document.getElementById('close-ai-apply-modal')?.addEventListener('click', () => {
            document.getElementById('hostel-ai-apply-modal').classList.add('hidden');
        });
        document.getElementById('btn-generate-hostel-app')?.addEventListener('click', () => this.generateHostelApplication());
        document.getElementById('btn-regenerate-hostel-app')?.addEventListener('click', () => {
            document.getElementById('ai-apply-step-2').classList.add('hidden');
            document.getElementById('ai-apply-step-1').classList.remove('hidden');
        });
        document.getElementById('btn-copy-hostel-app')?.addEventListener('click', () => {
            const text = document.getElementById('hostel-app-output').innerText;
            navigator.clipboard.writeText(text).then(() => {
                const btn = document.getElementById('btn-copy-hostel-app');
                btn.textContent = '✅ Copied!';
                setTimeout(() => btn.textContent = '📋 Copy to Clipboard', 2000);
            });
        });

        // Modal overlay clicks
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', () => {
                overlay.closest('.modal').classList.add('hidden');
            });
        });
    },

    async loadHostels() {
        this.isLoading = true;
        try {
            const response = await fetch(`${API_BASE_URL}/api/hostels`);
            const data = await response.json();
            this.allHostels = data.hostels || [];
            this.applyFilters();
            this.renderStats();
        } catch (error) {
            console.error('Failed to load hostels:', error);
            this.allHostels = this.getFallbackHostels();
            this.applyFilters();
        }
        this.isLoading = false;
    },

    renderStats() {
        const stats = document.getElementById('hostel-stats');
        if (!stats) return;
        const college = this.allHostels.filter(h => (h.type || '').toLowerCase().includes('college')).length;
        const govt = this.allHostels.filter(h => !(h.type || '').toLowerCase().includes('college')).length;
        stats.innerHTML = `
            <div class="stat-chip"><strong>${this.allHostels.length}</strong> Total Hostels</div>
            <div class="stat-chip"><strong>${college}</strong> College Hostels</div>
            <div class="stat-chip"><strong>${govt}</strong> Government Hostels</div>
        `;
    },

    applyFilters() {
        let filtered = [...this.allHostels];

        if (this.activeFilter !== 'all') {
            filtered = filtered.filter(h => {
                const type = (h.type || '').toLowerCase();
                const name = (h.name || '').toLowerCase();
                switch (this.activeFilter) {
                    case 'college': return type.includes('college') || type.includes('affiliated');
                    case 'bcm': return type.includes('bcm') || name.includes('bcm');
                    case 'sc/st': return type.includes('sc') || type.includes('st') || name.includes('sc/st');
                    case 'minority': return type.includes('minority') || name.includes('minority');
                    case 'government': return type.includes('government') || type.includes('bcm') || type.includes('sc') || type.includes('minority');
                    default: return true;
                }
            });
        }

        if (this.searchQuery) {
            filtered = filtered.filter(h => {
                const searchable = `${h.name} ${h.location} ${h.city} ${h.type} ${h.college || ''}`.toLowerCase();
                return searchable.includes(this.searchQuery);
            });
        }

        this.filteredHostels = filtered;
        this.renderHostels();
    },

    renderHostels() {
        const grid = document.getElementById('hostel-grid');
        if (!grid) return;

        if (this.filteredHostels.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🏠</div>
                    <h3>No hostels found</h3>
                    <p>Try adjusting your filters or search</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.filteredHostels.map((h, i) => this.renderCard(h, i)).join('');

        // Event listeners for cards
        grid.querySelectorAll('.btn-how-to-apply').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.target.closest('.hostel-card').dataset.index;
                this.showHowToApply(this.filteredHostels[idx]);
            });
        });

        grid.querySelectorAll('.btn-ai-apply-hostel').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.target.closest('.hostel-card').dataset.index;
                this.openAIApply(this.filteredHostels[idx]);
            });
        });

        grid.querySelectorAll('.btn-compare-add').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.target.closest('.hostel-card').dataset.index;
                this.addToCompare(this.filteredHostels[idx]);
            });
        });

        grid.querySelectorAll('.btn-map-hostel').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.target.closest('.hostel-card').dataset.index;
                const hostel = this.filteredHostels[idx];
                const loc = hostel.location || hostel.city || hostel.name;
                window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(loc + ' hostel Karnataka')}`, '_blank');
            });
        });
    },

    renderCard(hostel, index) {
        const type = (hostel.type || 'College').toLowerCase();
        let typeIcon = '🏛️';
        let typeClass = 'type-college';
        if (type.includes('bcm')) { typeIcon = '🏢'; typeClass = 'type-bcm'; }
        else if (type.includes('sc') || type.includes('st')) { typeIcon = '🏛️'; typeClass = 'type-scst'; }
        else if (type.includes('minority')) { typeIcon = '🕌'; typeClass = 'type-minority'; }
        else if (type.includes('government')) { typeIcon = '🏛️'; typeClass = 'type-govt'; }

        const fac = hostel.facilities || {};
        const fees = hostel.fees || hostel.fee || {};
        let feeText = 'Contact for details';
        if (typeof fees === 'string') {
            feeText = fees;
        } else if (typeof fees === 'number') {
            feeText = `₹${fees.toLocaleString('en-IN')}/year`;
        } else if (fees.annual) {
            feeText = `₹${fees.annual.toLocaleString('en-IN')}/year`;
        } else if (fees.hostel_fee) {
            feeText = `₹${fees.hostel_fee.toLocaleString('en-IN')}/year`;
        }

        const capacity = hostel.capacity || 'N/A';
        const location = hostel.location || hostel.city || 'Karnataka';

        // Amenities chips
        const amenities = [];
        if (fac.wifi) amenities.push('📶 WiFi');
        if (fac.mess) amenities.push('🍽️ Mess');
        if (fac.library) amenities.push('📚 Library');
        if (fac.gym) amenities.push('💪 Gym');
        if (fac.laundry) amenities.push('👕 Laundry');
        if (fac.hot_water) amenities.push('🚿 Hot Water');
        if (fac.boys_hostel) amenities.push('👦 Boys');
        if (fac.girls_hostel) amenities.push('👧 Girls');

        const isGovt = type.includes('bcm') || type.includes('sc') || type.includes('minority') || type.includes('government');

        return `
            <div class="hostel-card" data-index="${index}" style="animation-delay: ${index * 0.05}s">
                <div class="hostel-card-header ${typeClass}">
                    <span class="hostel-type-badge">${typeIcon} ${hostel.type || 'College Hostel'}</span>
                    ${isGovt ? '<span class="free-badge">🆓 Free / Subsidized</span>' : ''}
                </div>
                <div class="hostel-card-body">
                    <h3 class="hostel-name">${hostel.name || 'Hostel'}</h3>
                    <div class="hostel-meta">
                        <span>📍 ${location}</span>
                        <span>👥 Capacity: ${capacity}</span>
                        <span>💰 ${feeText}</span>
                    </div>
                    ${amenities.length > 0 ? `
                    <div class="amenities-row">
                        ${amenities.map(a => `<span class="amenity-chip">${a}</span>`).join('')}
                    </div>
                    ` : ''}
                    ${hostel.eligibility ? `
                    <div class="eligibility-info">
                        <strong>Eligibility:</strong> ${typeof hostel.eligibility === 'string' ? hostel.eligibility : JSON.stringify(hostel.eligibility).replace(/[{}"]/g, '').replace(/,/g, ', ')}
                    </div>
                    ` : ''}
                </div>
                <div class="hostel-card-actions">
                    <button class="btn-secondary btn-sm btn-map-hostel" title="View on Map">📍 Map</button>
                    <button class="btn-secondary btn-sm btn-compare-add" title="Add to Compare">⚖️ Compare</button>
                    <button class="btn-secondary btn-sm btn-how-to-apply">📋 How to Apply</button>
                    <button class="btn-primary btn-sm btn-ai-apply-hostel">✨ AI Apply</button>
                </div>
            </div>
        `;
    },

    showHowToApply(hostel) {
        const modal = document.getElementById('hostel-apply-modal');
        const body = document.getElementById('apply-modal-body');
        const type = (hostel.type || '').toLowerCase();

        let steps = '';
        let appProcess = hostel.application_process || hostel.how_to_apply || null;

        if (appProcess) {
            if (Array.isArray(appProcess)) {
                steps = appProcess.map((step, i) => `<div class="apply-step"><span class="step-num">${i + 1}</span><p>${step}</p></div>`).join('');
            } else {
                steps = `<div class="apply-step"><p>${appProcess}</p></div>`;
            }
        } else if (type.includes('bcm')) {
            steps = `
                <div class="apply-step"><span class="step-num">1</span><p>Visit the BCM Hostel Office or the District Social Welfare Officer's office</p></div>
                <div class="apply-step"><span class="step-num">2</span><p>Collect the application form (or download from bcwd.karnataka.gov.in)</p></div>
                <div class="apply-step"><span class="step-num">3</span><p>Fill in personal details, college admission proof, and category details</p></div>
                <div class="apply-step"><span class="step-num">4</span><p>Attach: Caste Certificate, Income Certificate, College Admission Letter, Aadhaar, 2 Passport Photos</p></div>
                <div class="apply-step"><span class="step-num">5</span><p>Submit to the Hostel Warden before the academic year starts (usually July-August)</p></div>
                <div class="apply-step"><span class="step-num">6</span><p>Admission is on first-come, first-served basis. Apply early!</p></div>
            `;
        } else if (type.includes('sc') || type.includes('st')) {
            steps = `
                <div class="apply-step"><span class="step-num">1</span><p>Visit the Social Welfare Department or District SC/ST Hostel Office</p></div>
                <div class="apply-step"><span class="step-num">2</span><p>Obtain the hostel admission application form</p></div>
                <div class="apply-step"><span class="step-num">3</span><p>Required Documents: Caste Certificate (SC/ST), Income Certificate (< ₹2.5 Lakhs), College Admission Letter, Previous Marks Card, Aadhaar Card, 3 Passport Photos</p></div>
                <div class="apply-step"><span class="step-num">4</span><p>Submit the completed form to the Hostel Superintendent</p></div>
                <div class="apply-step"><span class="step-num">5</span><p>Admission is usually free with free meals. Apply before July each year.</p></div>
            `;
        } else if (type.includes('minority')) {
            steps = `
                <div class="apply-step"><span class="step-num">1</span><p>Apply through the Minority Welfare Department portal or visit the district office</p></div>
                <div class="apply-step"><span class="step-num">2</span><p>Required: Minority Community Certificate, Income Certificate, College admission proof</p></div>
                <div class="apply-step"><span class="step-num">3</span><p>Submit application with all documents before the deadline (usually August)</p></div>
                <div class="apply-step"><span class="step-num">4</span><p>Admission based on merit and income criteria</p></div>
            `;
        } else {
            steps = `
                <div class="apply-step"><span class="step-num">1</span><p>Get admitted to the college first through KEA counseling</p></div>
                <div class="apply-step"><span class="step-num">2</span><p>Apply for hostel during admission itself — most colleges have a hostel form in the admission kit</p></div>
                <div class="apply-step"><span class="step-num">3</span><p>Submit the hostel application with: College admission receipt, Parent details, Medical certificate, 2 Passport photos</p></div>
                <div class="apply-step"><span class="step-num">4</span><p>Pay the hostel fee (usually annual) along with mess advance</p></div>
                <div class="apply-step"><span class="step-num">5</span><p>💡 Tip: Apply early! College hostels fill up fast, especially for girls' hostels.</p></div>
            `;
        }

        body.innerHTML = `
            <div class="apply-guide">
                <div class="apply-guide-header">
                    <h3>${hostel.name}</h3>
                    <span class="type-tag">${hostel.type || 'College Hostel'}</span>
                </div>
                <div class="apply-steps">
                    ${steps}
                </div>
                ${hostel.contact ? `
                <div class="contact-info">
                    <h4>📞 Contact</h4>
                    <p>${typeof hostel.contact === 'string' ? hostel.contact : JSON.stringify(hostel.contact).replace(/[{}"]/g, '').replace(/,/g, '<br>')}</p>
                </div>
                ` : ''}
                <div class="apply-guide-footer">
                    <button class="btn-primary" onclick="HostelExplorer.openAIApply(HostelExplorer.filteredHostels.find(h => h.name === '${(hostel.name || '').replace(/'/g, "\\'")}'))">
                        ✨ Generate Application with AI
                    </button>
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
    },

    openAIApply(hostel) {
        this.currentApplyHostel = hostel;
        document.getElementById('ai-target-hostel-name').textContent = hostel.name;
        document.getElementById('ai-apply-step-1').classList.remove('hidden');
        document.getElementById('ai-apply-step-2').classList.add('hidden');
        document.getElementById('hostel-ai-apply-modal').classList.remove('hidden');
        document.getElementById('hostel-apply-modal').classList.add('hidden');
    },

    async generateHostelApplication() {
        const reason = document.getElementById('hostel-reason').value;
        const college = document.getElementById('hostel-college-input').value;
        if (!reason) {
            alert('Please tell us why you need hostel accommodation.');
            return;
        }

        const loader = document.getElementById('ai-apply-loading');
        loader.classList.remove('hidden');

        const profile = (typeof AppState !== 'undefined' && AppState.getProfile()) || {};
        const studentData = {
            name: profile.name || 'Student',
            category: profile.category || '',
            kcet_rank: profile.kcet_rank || profile.rank || '',
            income: profile.income || profile.finance || '',
            location: profile.location || 'Karnataka',
            college: college || profile.college || ''
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/hostels/apply`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_data: studentData,
                    hostel_name: this.currentApplyHostel?.name || 'Government Hostel',
                    reason: reason
                })
            });

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            document.getElementById('hostel-app-output').innerText = data.application;
            document.getElementById('ai-apply-step-1').classList.add('hidden');
            document.getElementById('ai-apply-step-2').classList.remove('hidden');
        } catch (error) {
            alert('Failed to generate application: ' + error.message);
        } finally {
            loader.classList.add('hidden');
        }
    },

    addToCompare(hostel) {
        if (this.compareList.length >= 3) {
            alert('You can compare up to 3 hostels at a time.');
            return;
        }
        if (this.compareList.find(h => h.name === hostel.name)) {
            alert('This hostel is already in your compare list.');
            return;
        }

        this.compareList.push(hostel);
        this.updateComparePanel();
    },

    updateComparePanel() {
        const panel = document.getElementById('compare-panel');
        const items = document.getElementById('compare-items');
        const count = document.getElementById('compare-count');

        if (this.compareList.length > 0) {
            panel.classList.remove('hidden');
            count.textContent = this.compareList.length;
            items.innerHTML = this.compareList.map(h => `
                <div class="compare-item">
                    <span>${h.name}</span>
                    <button class="btn-xs" onclick="HostelExplorer.removeFromCompare('${(h.name || '').replace(/'/g, "\\'")}')">×</button>
                </div>
            `).join('');
        } else {
            panel.classList.add('hidden');
        }
    },

    removeFromCompare(name) {
        this.compareList = this.compareList.filter(h => h.name !== name);
        this.updateComparePanel();
    },

    clearCompare() {
        this.compareList = [];
        this.updateComparePanel();
    },

    showComparison() {
        if (this.compareList.length < 2) {
            alert('Please add at least 2 hostels to compare.');
            return;
        }

        const body = document.getElementById('compare-modal-body');
        const headers = this.compareList.map(h => `<th>${h.name}</th>`).join('');

        const getVal = (hostel, path) => {
            const fees = hostel.fees || hostel.fee || {};
            const fac = hostel.facilities || {};
            switch (path) {
                case 'type': return hostel.type || 'N/A';
                case 'location': return hostel.location || hostel.city || 'N/A';
                case 'capacity': return hostel.capacity || 'N/A';
                case 'fees':
                    if (typeof fees === 'string') return fees;
                    if (typeof fees === 'number') return `₹${fees.toLocaleString('en-IN')}`;
                    if (fees.annual) return `₹${fees.annual.toLocaleString('en-IN')}/yr`;
                    if (fees.hostel_fee) return `₹${fees.hostel_fee.toLocaleString('en-IN')}/yr`;
                    return 'Contact';
                case 'wifi': return fac.wifi ? '✅' : '❌';
                case 'mess': return fac.mess ? '✅' : '❌';
                case 'boys': return fac.boys_hostel ? '✅' : '❌';
                case 'girls': return fac.girls_hostel ? '✅' : '❌';
                default: return 'N/A';
            }
        };

        const rows = [
            { label: 'Type', key: 'type' },
            { label: 'Location', key: 'location' },
            { label: 'Capacity', key: 'capacity' },
            { label: 'Fees', key: 'fees' },
            { label: 'WiFi', key: 'wifi' },
            { label: 'Mess', key: 'mess' },
            { label: 'Boys Hostel', key: 'boys' },
            { label: 'Girls Hostel', key: 'girls' }
        ];

        body.innerHTML = `
            <table class="compare-table">
                <thead><tr><th>Feature</th>${headers}</tr></thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td><strong>${row.label}</strong></td>
                            ${this.compareList.map(h => `<td>${getVal(h, row.key)}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        document.getElementById('compare-modal').classList.remove('hidden');
    },

    getFallbackHostels() {
        return [
            {
                name: "RVCE Hostel",
                type: "College Hostel",
                location: "Bangalore",
                capacity: 800,
                fees: { annual: 45000, mess: "₹4,500/month" },
                facilities: { wifi: true, mess: true, library: true, boys_hostel: true, girls_hostel: true },
                how_to_apply: ["Apply during college admission", "Submit hostel form with admission kit", "Pay hostel + mess fees"]
            },
            {
                name: "BCM Hostel - Bangalore",
                type: "BCM Government Hostel",
                location: "Bangalore",
                capacity: 200,
                fees: "Free",
                facilities: { mess: true, boys_hostel: true },
                eligibility: "OBC Category students with income < ₹2.5 Lakhs",
                how_to_apply: ["Visit BCM Hostel office", "Submit caste + income certificate", "Apply before July"]
            }
        ];
    }
};

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => HostelExplorer.init());
} else {
    HostelExplorer.init();
}
