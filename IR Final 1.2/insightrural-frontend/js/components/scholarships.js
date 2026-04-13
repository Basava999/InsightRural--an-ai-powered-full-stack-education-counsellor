// =============================================================
// Enhanced Scholarship Component - Loads ALL scholarships from API
// Features: Category filters, search, AI match score, auto-apply
// =============================================================

const ScholarshipComponent = {
    allScholarships: [],
    filteredScholarships: [],
    activeFilter: 'all',
    searchQuery: '',
    isLoading: false,

    async init() {
        this.container = document.getElementById('scholarships-section');
        if (!this.container) return;
        this.renderSkeleton();
        await this.loadScholarships();
    },

    renderSkeleton() {
        this.container.innerHTML = `
            <div class="scholarships-page">
                <div class="scholarships-header">
                    <div class="scholarships-hero">
                        <div class="hero-icon">💰</div>
                        <h2>Scholarship Finder</h2>
                        <p>AI-powered scholarship matching for Karnataka students</p>
                    </div>
                    <div class="scholarships-search">
                        <div class="search-input-wrap">
                            <span class="search-icon">🔍</span>
                            <input type="text" id="scholarship-search" placeholder="Search scholarships by name, category, or department..." />
                        </div>
                    </div>
                    <div class="scholarship-filters" id="scholarship-filters">
                        <button class="filter-chip active" data-filter="all">All</button>
                        <button class="filter-chip" data-filter="sc">SC</button>
                        <button class="filter-chip" data-filter="st">ST</button>
                        <button class="filter-chip" data-filter="obc">OBC</button>
                        <button class="filter-chip" data-filter="minority">Minority</button>
                        <button class="filter-chip" data-filter="general">General / Merit</button>
                        <button class="filter-chip" data-filter="girls">Girls Only</button>
                    </div>
                </div>
                <div class="scholarships-grid" id="scholarships-grid">
                    ${this.renderLoadingCards()}
                </div>
                <div class="smart-match-banner" id="smart-match-banner" style="display:none;">
                    <div class="match-icon">🤖</div>
                    <div class="match-text">
                        <strong>AI Smart Match</strong>
                        <p>Based on your profile, you're eligible for <span id="match-count">0</span> scholarships!</p>
                    </div>
                    <button class="btn-primary btn-sm" id="btn-show-matches">Show My Matches</button>
                </div>
            </div>
        `;
        this.setupEventListeners();
    },

    renderLoadingCards() {
        return Array(6).fill('').map(() => `
            <div class="scholarship-card skeleton">
                <div class="skeleton-line w60"></div>
                <div class="skeleton-line w80"></div>
                <div class="skeleton-line w40"></div>
            </div>
        `).join('');
    },

    setupEventListeners() {
        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                this.activeFilter = e.target.dataset.filter;
                this.applyFilters();
            });
        });

        // Search
        const searchInput = document.getElementById('scholarship-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value.toLowerCase();
                this.applyFilters();
            });
        }

        // Smart match button
        const matchBtn = document.getElementById('btn-show-matches');
        if (matchBtn) {
            matchBtn.addEventListener('click', () => {
                this.activeFilter = 'matched';
                document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                this.applyFilters();
            });
        }
    },

    async loadScholarships() {
        this.isLoading = true;
        try {
            const response = await fetch(`${API_BASE_URL}/api/scholarships/list`);
            const data = await response.json();
            this.allScholarships = data.scholarships || [];

            // Mark matched scholarships
            await this.checkSmartMatch();

            this.applyFilters();
        } catch (error) {
            console.error('Failed to load scholarships:', error);
            this.allScholarships = this.getFallbackScholarships();
            this.applyFilters();
        }
        this.isLoading = false;
    },

    async checkSmartMatch() {
        const profile = (typeof AppState !== 'undefined' && AppState.getProfile()) || {};
        if (!profile.category) return;

        try {
            const resp = await fetch(`${API_BASE_URL}/api/smart-match`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    category: profile.category || '',
                    income: profile.income || profile.finance || 500000,
                    gender: profile.gender || '',
                    location: profile.location || ''
                })
            });
            const matchData = await resp.json();

            if (matchData.scholarships && matchData.scholarships.total > 0) {
                const matchedNames = matchData.scholarships.items.map(s => (s.name || '').toLowerCase());
                this.allScholarships.forEach(sch => {
                    sch._matched = matchedNames.includes((sch.name || '').toLowerCase());
                });

                const banner = document.getElementById('smart-match-banner');
                if (banner) {
                    document.getElementById('match-count').textContent = matchData.scholarships.total;
                    banner.style.display = 'flex';
                }
            }
        } catch (e) {
            console.log('Smart match not available:', e);
        }
    },

    applyFilters() {
        let filtered = [...this.allScholarships];

        // Category filter
        if (this.activeFilter === 'matched') {
            filtered = filtered.filter(s => s._matched);
        } else if (this.activeFilter !== 'all') {
            filtered = filtered.filter(s => {
                const cats = JSON.stringify(s.eligibility?.category || s.category || '').toLowerCase();
                const name = (s.name || '').toLowerCase();
                const dept = (s.department || '').toLowerCase();

                switch (this.activeFilter) {
                    case 'sc': return cats.includes('sc') || name.includes('sc ');
                    case 'st': return cats.includes('st') || name.includes('st ');
                    case 'obc': return cats.includes('obc') || cats.includes('category') || cats.includes('2a') || cats.includes('3a') || cats.includes('3b');
                    case 'minority': return cats.includes('minority') || name.includes('minority') || dept.includes('minority');
                    case 'general': return cats.includes('all') || cats.includes('general') || cats.includes('merit');
                    case 'girls': return (s.eligibility?.gender || '').toLowerCase().includes('female') || name.includes('girls') || name.includes('girl');
                    default: return true;
                }
            });
        }

        // Search filter
        if (this.searchQuery) {
            filtered = filtered.filter(s => {
                const searchable = `${s.name} ${s.department} ${s.category} ${JSON.stringify(s.eligibility || {})} ${JSON.stringify(s.benefits || {})}`.toLowerCase();
                return searchable.includes(this.searchQuery);
            });
        }

        this.filteredScholarships = filtered;
        this.renderScholarships();
    },

    renderScholarships() {
        const grid = document.getElementById('scholarships-grid');
        if (!grid) return;

        if (this.filteredScholarships.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <h3>No scholarships found</h3>
                    <p>Try adjusting your filters or search query</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.filteredScholarships.map((sch, i) => this.renderCard(sch, i)).join('');

        // Attach event listeners
        grid.querySelectorAll('.btn-auto-apply').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const name = e.target.closest('.scholarship-card').dataset.name;
                if (typeof ScholarshipWriterComponent !== 'undefined') {
                    ScholarshipWriterComponent.open(name);
                } else if (typeof window.ScholarshipWriterComponent !== 'undefined') {
                    window.ScholarshipWriterComponent.open(name);
                }
            });
        });

        grid.querySelectorAll('.btn-details-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const card = e.target.closest('.scholarship-card');
                const details = card.querySelector('.scholarship-details');
                details.classList.toggle('hidden');
                e.target.textContent = details.classList.contains('hidden') ? 'View Details' : 'Hide Details';
            });
        });
    },

    renderCard(sch, index) {
        const elig = sch.eligibility || {};
        const benefits = sch.benefits || {};
        const incomeLimitRaw = elig.income_limit || elig.income_max || 'N/A';
        const incomeLimit = typeof incomeLimitRaw === 'number' ? `₹${incomeLimitRaw.toLocaleString('en-IN')}` : incomeLimitRaw;
        const deadline = sch.deadline || sch.application_deadline || 'Check portal';
        const portal = sch.application_portal || sch.portal || '#';
        const docs = sch.documents_required || sch.documents || [];
        const isMatched = sch._matched;

        // Determine category badge color
        const catStr = JSON.stringify(elig.category || sch.category || 'General').toLowerCase();
        let badgeClass = 'badge-general';
        if (catStr.includes('sc')) badgeClass = 'badge-sc';
        else if (catStr.includes('st')) badgeClass = 'badge-st';
        else if (catStr.includes('obc') || catStr.includes('category')) badgeClass = 'badge-obc';
        else if (catStr.includes('minority')) badgeClass = 'badge-minority';

        // Benefits text
        let benefitsList = '';
        if (typeof benefits === 'string') {
            benefitsList = benefits;
        } else if (Array.isArray(benefits)) {
            benefitsList = benefits.join(', ');
        } else {
            benefitsList = Object.entries(benefits).map(([k, v]) => `${k}: ${v}`).join(', ');
        }

        return `
            <div class="scholarship-card ${isMatched ? 'matched' : ''}" data-name="${sch.name}" style="animation-delay: ${index * 0.05}s">
                ${isMatched ? '<div class="match-badge">🤖 AI Match</div>' : ''}
                <div class="card-header">
                    <h3 class="scholarship-name">${sch.name || 'Scholarship'}</h3>
                    <span class="category-badge ${badgeClass}">${elig.category || sch.category || 'General'}</span>
                </div>
                <div class="card-meta">
                    <span class="meta-item">🏛️ ${sch.department || 'Karnataka Govt'}</span>
                    <span class="meta-item">💰 Income: ${incomeLimit}</span>
                    <span class="meta-item">📅 ${deadline}</span>
                </div>
                <div class="card-benefits">
                    <strong>Benefits:</strong> ${benefitsList || 'Full fee reimbursement'}
                </div>
                <div class="scholarship-details hidden">
                    <div class="detail-section">
                        <h4>📋 Eligibility</h4>
                        <ul>
                            ${elig.marks ? `<li>Min Marks: ${elig.marks}%</li>` : ''}
                            ${elig.domicile ? `<li>Domicile: ${elig.domicile}</li>` : ''}
                            ${elig.education ? `<li>Education: ${elig.education}</li>` : ''}
                            <li>Income Limit: ${incomeLimit}</li>
                        </ul>
                    </div>
                    ${docs.length > 0 ? `
                    <div class="detail-section">
                        <h4>📄 Required Documents</h4>
                        <ul>${docs.map(d => `<li>${d}</li>`).join('')}</ul>
                    </div>
                    ` : ''}
                    ${portal !== '#' ? `
                    <div class="detail-section">
                        <h4>🌐 Application Portal</h4>
                        <a href="${portal.startsWith('http') ? portal : 'https://' + portal}" target="_blank" class="portal-link">${portal}</a>
                    </div>
                    ` : ''}
                </div>
                <div class="card-actions">
                    <button class="btn-secondary btn-sm btn-details-toggle">View Details</button>
                    <button class="btn-primary btn-sm btn-auto-apply">
                        <span>✨</span> AI Auto-Apply
                    </button>
                </div>
            </div>
        `;
    },

    getFallbackScholarships() {
        return [
            {
                name: "Post-Matric Scholarship for SC Students",
                department: "Social Welfare Department",
                category: "SC",
                eligibility: { category: ["SC"], income_limit: 250000, marks: 40, domicile: "Karnataka" },
                benefits: { fee_reimbursement: "Full", maintenance: "₹1,200/month (hosteller)" },
                deadline: "January 15, 2026",
                application_portal: "ssp.postmatric.karnataka.gov.in",
                documents_required: ["Caste Certificate", "Income Certificate", "Previous Marks Card", "Aadhaar Card", "Bank Passbook"]
            },
            {
                name: "Post-Matric Scholarship for ST Students",
                department: "Tribal Welfare Department",
                category: "ST",
                eligibility: { category: ["ST"], income_limit: 250000, marks: 40, domicile: "Karnataka" },
                benefits: { fee_reimbursement: "Full", maintenance: "₹1,200/month" },
                deadline: "February 15, 2026",
                application_portal: "ssp.postmatric.karnataka.gov.in",
                documents_required: ["Tribe Certificate", "Income Certificate", "Marks Card", "Aadhaar"]
            },
            {
                name: "Vidyasiri Scholarship (OBC)",
                department: "Backward Classes Welfare",
                category: "OBC",
                eligibility: { category: ["OBC (2A/2B/3A/3B)"], income_limit: 250000, domicile: "Karnataka" },
                benefits: { fee_reimbursement: "Partial", maintenance: "₹1,500/month" },
                deadline: "December 31, 2025",
                application_portal: "ssp.postmatric.karnataka.gov.in",
                documents_required: ["Caste Certificate", "Income Certificate", "Marks Card"]
            },
            {
                name: "Chief Minister's Fee Concession for EWS",
                department: "Higher Education Department",
                category: "General (EWS)",
                eligibility: { category: ["All Categories (EWS)"], income_limit: 100000, domicile: "Karnataka" },
                benefits: { fee_reimbursement: "100% (Govt colleges)" },
                deadline: "Ongoing",
                application_portal: "ssp.postmatric.karnataka.gov.in",
                documents_required: ["Income Certificate", "Domicile proof", "Marks Card", "Admission letter"]
            }
        ];
    }
};

// Auto-initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ScholarshipComponent.init());
} else {
    ScholarshipComponent.init();
}
