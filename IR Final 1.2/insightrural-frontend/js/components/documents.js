// Smart Document Vault Component
// Document tracking and verification checklist

const DocumentsComponent = {
    isActive: false,

    // Document categories by student category
    documentsByCategory: {
        common: [
            { id: 'aadhaar', name: 'Aadhaar Card (Student)', required: true, icon: '🪪' },
            { id: 'aadhaar_parent', name: 'Aadhaar Card (Parent)', required: true, icon: '🪪' },
            { id: 'sslc', name: 'SSLC Marks Card', required: true, icon: '📄' },
            { id: 'puc', name: 'PUC/12th Marks Card', required: true, icon: '📄' },
            { id: 'kcet_scorecard', name: 'KCET Score Card', required: true, icon: '🎯' },
            { id: 'kcet_admission', name: 'KCET Admission Ticket', required: true, icon: '🎫' },
            { id: 'passport_photo', name: 'Passport Size Photos (10)', required: true, icon: '📸' },
            { id: 'bank_passbook', name: 'Bank Passbook (Aadhaar Linked)', required: true, icon: '🏦' },
            { id: 'study_cert', name: 'Study Certificate (Class 1-10)', required: true, icon: '📜' },
            { id: 'transfer_cert', name: 'Transfer Certificate (TC)', required: true, icon: '📋' }
        ],
        SC: [
            { id: 'caste_cert', name: 'Caste Certificate (SC)', required: true, icon: '📑' },
            { id: 'income_cert', name: 'Income Certificate (< 2.5 Lakhs)', required: true, icon: '💰' },
            { id: 'kutumba_id', name: 'Kutumba/Family ID', required: true, icon: '👨‍👩‍👧' }
        ],
        ST: [
            { id: 'tribe_cert', name: 'Tribe Certificate (ST)', required: true, icon: '📑' },
            { id: 'income_cert', name: 'Income Certificate (< 2.5 Lakhs)', required: true, icon: '💰' },
            { id: 'kutumba_id', name: 'Kutumba/Family ID', required: true, icon: '👨‍👩‍👧' }
        ],
        OBC: [
            { id: 'caste_cert', name: 'Caste Certificate (2A/2B/3A/3B)', required: true, icon: '📑' },
            { id: 'income_cert', name: 'Income Certificate', required: true, icon: '💰' },
            { id: 'ncl_cert', name: 'Non-Creamy Layer Certificate', required: true, icon: '📄' }
        ],
        GM: [
            { id: 'income_cert', name: 'Income Certificate (if needed)', required: false, icon: '💰' },
            { id: 'ews_cert', name: 'EWS Certificate (if applicable)', required: false, icon: '📄' }
        ]
    },

    // User's document status
    userDocuments: {},
    userCategory: 'GM',

    init() {
        this.loadProgress();
        this.setupEventListeners();
        console.log('📁 Documents component initialized');
    },

    setupEventListeners() {
        document.addEventListener('featureChange', (e) => {
            if (e.detail === 'documents') {
                this.activate();
            } else {
                this.deactivate();
            }
        });
    },

    activate() {
        this.isActive = true;
        this.render();
    },

    deactivate() {
        this.isActive = false;
    },

    loadProgress() {
        try {
            const saved = localStorage.getItem('insightrural_documents');
            if (saved) {
                const data = JSON.parse(saved);
                this.userDocuments = data.documents || {};
                this.userCategory = data.category || 'GM';
            }
        } catch (e) {
            console.log('No saved document progress');
        }
    },

    saveProgress() {
        try {
            localStorage.setItem('insightrural_documents', JSON.stringify({
                documents: this.userDocuments,
                category: this.userCategory
            }));
        } catch (e) {
            console.log('Could not save progress');
        }
    },

    getRequiredDocuments() {
        const common = this.documentsByCategory.common;
        const categoryDocs = this.documentsByCategory[this.userCategory] || [];
        return [...common, ...categoryDocs];
    },

    getProgress() {
        const docs = this.getRequiredDocuments();
        const completed = docs.filter(d => this.userDocuments[d.id]).length;
        return {
            completed,
            total: docs.length,
            percentage: Math.round((completed / docs.length) * 100)
        };
    },

    toggleDocument(docId) {
        this.userDocuments[docId] = !this.userDocuments[docId];
        this.saveProgress();
        this.updateDisplay();

        // Update gamification
        if (window.ProgressComponent) {
            ProgressComponent.addXP(this.userDocuments[docId] ? 10 : -10);

            // Check for badge
            const progress = this.getProgress();
            if (progress.completed === progress.total) {
                ProgressComponent.unlockBadge('document_master');
            }
        }
    },

    selectCategory(category) {
        this.userCategory = category;
        this.saveProgress();
        this.render();
    },

    updateDisplay() {
        const progress = this.getProgress();

        // Update progress ring
        const ring = document.querySelector('.progress-ring-fill');
        if (ring) {
            const circumference = 2 * Math.PI * 45;
            const offset = circumference - (progress.percentage / 100) * circumference;
            ring.style.strokeDashoffset = offset;
        }

        // Update counter
        const counter = document.getElementById('doc-progress-text');
        if (counter) {
            counter.textContent = `${progress.completed}/${progress.total}`;
        }

        // Update percentage
        const percent = document.getElementById('doc-progress-percent');
        if (percent) {
            percent.textContent = `${progress.percentage}%`;
        }

        // Update checkboxes
        document.querySelectorAll('.doc-checkbox').forEach(cb => {
            const docId = cb.dataset.docId;
            cb.checked = this.userDocuments[docId] || false;
            cb.closest('.doc-item').classList.toggle('completed', cb.checked);
        });
    },

    render() {
        let section = document.getElementById('documents-section');

        if (!section) {
            section = document.createElement('div');
            section.id = 'documents-section';
            section.className = 'documents-section';

            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.appendChild(section);
            }
        }

        const progress = this.getProgress();
        const docs = this.getRequiredDocuments();

        section.innerHTML = `
            <div class="documents-header">
                <h2>📁 Smart Document Vault</h2>
                <p>Track and organize your admission documents</p>
            </div>
            
            <!-- Category Selector -->
            <div class="category-selector">
                <span>Your Category:</span>
                <div class="category-buttons">
                    ${['GM', 'OBC', 'SC', 'ST'].map(cat => `
                        <button class="cat-btn ${this.userCategory === cat ? 'active' : ''}" 
                                onclick="DocumentsComponent.selectCategory('${cat}')">
                            ${cat}
                        </button>
                    `).join('')}
                </div>
            </div>
            
            <!-- Progress Ring -->
            <div class="doc-progress-container">
                <div class="progress-ring-container">
                    <svg class="progress-ring" width="120" height="120">
                        <circle class="progress-ring-bg" cx="60" cy="60" r="45" />
                        <circle class="progress-ring-fill" cx="60" cy="60" r="45"
                                style="stroke-dasharray: 283; stroke-dashoffset: ${283 - (progress.percentage / 100) * 283}" />
                    </svg>
                    <div class="progress-ring-text">
                        <span id="doc-progress-text">${progress.completed}/${progress.total}</span>
                        <small>Documents</small>
                    </div>
                </div>
                <div class="progress-status">
                    <span class="progress-percent" id="doc-progress-percent">${progress.percentage}%</span>
                    <span class="progress-label">Ready for Counselling</span>
                    ${progress.percentage === 100 ? '<span class="all-done">✅ All documents ready!</span>' : ''}
                </div>
            </div>
            
            <!-- Document List -->
            <div class="doc-list">
                <h3>📋 Required Documents for ${this.userCategory}</h3>
                
                ${docs.map(doc => `
                    <div class="doc-item ${this.userDocuments[doc.id] ? 'completed' : ''}" 
                         onclick="DocumentsComponent.toggleDocument('${doc.id}')">
                        <div class="doc-icon">${doc.icon}</div>
                        <div class="doc-info">
                            <span class="doc-name">${doc.name}</span>
                            ${doc.required ? '<span class="required-badge">Required</span>' : '<span class="optional-badge">Optional</span>'}
                        </div>
                        <input type="checkbox" class="doc-checkbox" data-doc-id="${doc.id}"
                               ${this.userDocuments[doc.id] ? 'checked' : ''} 
                               onclick="event.stopPropagation()">
                        <div class="doc-check-mark">✓</div>
                    </div>
                `).join('')}
            </div>
            
            <!-- Tips -->
            <div class="doc-tips">
                <h3>💡 Document Tips</h3>
                <ul>
                    <li>Keep <strong>original + 2 photocopies</strong> of all documents</li>
                    <li>All documents should be <strong>self-attested</strong></li>
                    <li>Caste/Income certificates must be recent (within 6 months)</li>
                    <li>Bank account must be <strong>Aadhaar-linked</strong> for scholarships</li>
                    <li>Carry documents in a <strong>waterproof folder</strong></li>
                </ul>
            </div>
            
            <!-- Share -->
            <div class="doc-actions">
                <button class="action-btn primary" onclick="DocumentsComponent.shareList()">
                    📤 Share Checklist
                </button>
                <button class="action-btn secondary" onclick="DocumentsComponent.downloadPDF()">
                    📄 Download PDF
                </button>
            </div>
        `;

        this.addDocumentStyles();
    },

    shareList() {
        const progress = this.getProgress();
        const text = `📁 InsightRural Document Checklist\n\n${progress.completed}/${progress.total} documents ready (${progress.percentage}%)\n\nGet your checklist at insightrural.com`;

        if (navigator.share) {
            navigator.share({ title: 'Document Checklist', text });
        } else {
            navigator.clipboard.writeText(text);
            alert('Checklist copied to clipboard!');
        }
    },

    downloadPDF() {
        alert('📄 PDF generation coming soon!');
    },

    addDocumentStyles() {
        if (document.getElementById('documents-styles')) return;

        const style = document.createElement('style');
        style.id = 'documents-styles';
        style.textContent = `
            .documents-section {
                display: none;
                padding: 2rem;
                max-width: 800px;
                margin: 0 auto;
            }
            
            .documents-section.active {
                display: block;
            }
            
            .documents-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .documents-header h2 {
                font-size: 1.8rem;
                background: linear-gradient(135deg, #1e90ff 0%, #6366f1 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .documents-header p {
                color: var(--text-secondary);
            }
            
            .category-selector {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                margin-bottom: 2rem;
                flex-wrap: wrap;
            }
            
            .category-buttons {
                display: flex;
                gap: 0.5rem;
            }
            
            .cat-btn {
                padding: 0.5rem 1.5rem;
                border: 2px solid var(--border-color);
                background: var(--bg-secondary);
                color: var(--text-primary);
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .cat-btn.active {
                background: linear-gradient(135deg, #1e90ff 0%, #6366f1 100%);
                border-color: transparent;
                color: white;
            }
            
            .doc-progress-container {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 2rem;
                margin-bottom: 2rem;
                padding: 2rem;
                background: var(--bg-secondary);
                border-radius: 20px;
                border: 1px solid var(--border-color);
            }
            
            .progress-ring-container {
                position: relative;
                width: 120px;
                height: 120px;
            }
            
            .progress-ring {
                transform: rotate(-90deg);
            }
            
            .progress-ring-bg {
                fill: none;
                stroke: var(--bg-tertiary);
                stroke-width: 8;
            }
            
            .progress-ring-fill {
                fill: none;
                stroke: url(#gradient);
                stroke-width: 8;
                stroke-linecap: round;
                transition: stroke-dashoffset 0.5s ease;
            }
            
            .progress-ring-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
            }
            
            .progress-ring-text span {
                font-size: 1.5rem;
                font-weight: 700;
            }
            
            .progress-ring-text small {
                display: block;
                font-size: 0.75rem;
                color: var(--text-secondary);
            }
            
            .progress-status {
                text-align: center;
            }
            
            .progress-percent {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                display: block;
            }
            
            .progress-label {
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .all-done {
                display: block;
                color: #22c55e;
                font-weight: 600;
                margin-top: 0.5rem;
            }
            
            .doc-list {
                margin-bottom: 2rem;
            }
            
            .doc-list h3 {
                margin-bottom: 1rem;
                font-size: 1.1rem;
            }
            
            .doc-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem;
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                margin-bottom: 0.75rem;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .doc-item:hover {
                border-color: #1e90ff;
            }
            
            .doc-item.completed {
                background: rgba(34, 197, 94, 0.1);
                border-color: rgba(34, 197, 94, 0.3);
            }
            
            .doc-icon {
                font-size: 1.5rem;
            }
            
            .doc-info {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }
            
            .doc-name {
                font-weight: 500;
            }
            
            .required-badge {
                font-size: 0.7rem;
                color: #ef4444;
                text-transform: uppercase;
            }
            
            .optional-badge {
                font-size: 0.7rem;
                color: var(--text-secondary);
            }
            
            .doc-checkbox {
                display: none;
            }
            
            .doc-check-mark {
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background: var(--bg-tertiary);
                display: flex;
                align-items: center;
                justify-content: center;
                color: transparent;
                transition: all 0.3s;
            }
            
            .doc-item.completed .doc-check-mark {
                background: #22c55e;
                color: white;
            }
            
            .doc-tips {
                background: linear-gradient(135deg, rgba(30, 144, 255, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
                border: 1px solid rgba(30, 144, 255, 0.2);
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .doc-tips h3 {
                margin-bottom: 1rem;
                color: #1e90ff;
            }
            
            .doc-tips ul {
                list-style: none;
                padding: 0;
            }
            
            .doc-tips li {
                padding: 0.5rem 0;
                padding-left: 1.5rem;
                position: relative;
                color: var(--text-secondary);
            }
            
            .doc-tips li::before {
                content: "•";
                position: absolute;
                left: 0;
                color: #1e90ff;
            }
            
            .doc-actions {
                display: flex;
                gap: 1rem;
                justify-content: center;
            }
        `;
        document.head.appendChild(style);
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    DocumentsComponent.init();
});

window.DocumentsComponent = DocumentsComponent;
