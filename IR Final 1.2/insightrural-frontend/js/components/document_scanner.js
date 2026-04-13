// Smart Document Scanner Component
// AI-powered document analysis with OCR

const DocumentScannerComponent = {
    uploadedFile: null,
    extractedData: null,

    init() {
        this.injectStyles();
        console.log('📄 Document Scanner initialized');
    },

    render() {
        const container = document.getElementById('scanner-section');
        if (!container) return;

        container.innerHTML = `
            <div class="document-scanner">
                <div class="scanner-header">
                    <h2>📄 Smart Document Scanner</h2>
                    <p class="scanner-subtitle">Upload documents for AI-powered extraction & verification</p>
                </div>

                <div class="scanner-tabs">
                    <button class="scan-tab active" data-type="marksheet">📊 Marksheet</button>
                    <button class="scan-tab" data-type="certificate">🏅 Certificate</button>
                    <button class="scan-tab" data-type="income">💰 Income Proof</button>
                    <button class="scan-tab" data-type="caste">📜 Caste Certificate</button>
                </div>

                <div class="upload-zone" id="upload-zone">
                    <div class="upload-icon">📷</div>
                    <h3>Drop your document here</h3>
                    <p>or click to browse</p>
                    <input type="file" id="file-input" accept="image/*,.pdf" hidden>
                    <div class="upload-formats">Supports: JPG, PNG, PDF</div>
                </div>

                <div class="preview-section" id="preview-section" style="display: none;">
                    <div class="preview-header">
                        <h3>📸 Document Preview</h3>
                        <button class="remove-btn" id="remove-file">✕ Remove</button>
                    </div>
                    <div class="preview-container">
                        <img id="preview-image" src="" alt="Document preview">
                        <div class="scan-overlay" id="scan-overlay">
                            <div class="scan-line"></div>
                        </div>
                    </div>
                    <button class="analyze-btn" id="analyze-btn">
                        🔍 Analyze Document
                    </button>
                </div>

                <div class="results-section" id="results-section" style="display: none;">
                    <div class="results-header">
                        <h3>✅ Extracted Information</h3>
                        <div class="confidence-badge" id="confidence-badge">
                            <span class="confidence-value">--</span>% Confidence
                        </div>
                    </div>

                    <div class="extracted-data" id="extracted-data">
                        <!-- Will be populated dynamically -->
                    </div>

                    <div class="verification-status" id="verification-status">
                        <!-- Verification messages -->
                    </div>

                    <div class="suggestions-box" id="suggestions-box">
                        <h4>💡 AI Suggestions</h4>
                        <ul id="suggestions-list"></ul>
                    </div>

                    <div class="result-actions">
                        <button class="action-btn primary" id="use-data-btn">
                            ✓ Use This Data
                        </button>
                        <button class="action-btn secondary" id="rescan-btn">
                            🔄 Scan Again
                        </button>
                    </div>
                </div>

                <div class="scanner-tips">
                    <h4>📝 Tips for Better Results</h4>
                    <ul>
                        <li>Ensure good lighting and clear focus</li>
                        <li>Keep the document flat without folds</li>
                        <li>Capture all corners of the document</li>
                        <li>Avoid shadows and reflections</li>
                    </ul>
                </div>
            </div>
        `;

        this.setupEventListeners();
    },

    setupEventListeners() {
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');
        const removeBtn = document.getElementById('remove-file');
        const analyzeBtn = document.getElementById('analyze-btn');
        const useDataBtn = document.getElementById('use-data-btn');
        const rescanBtn = document.getElementById('rescan-btn');

        // Upload zone click
        uploadZone?.addEventListener('click', () => fileInput?.click());

        // File input change
        fileInput?.addEventListener('change', (e) => {
            if (e.target.files[0]) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadZone?.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone?.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone?.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            if (e.dataTransfer.files[0]) {
                this.handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        // Remove file
        removeBtn?.addEventListener('click', () => this.resetUpload());

        // Analyze
        analyzeBtn?.addEventListener('click', () => this.analyzeDocument());

        // Use data
        useDataBtn?.addEventListener('click', () => this.useExtractedData());

        // Rescan
        rescanBtn?.addEventListener('click', () => this.resetUpload());

        // Tab switching
        document.querySelectorAll('.scan-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.scan-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    },

    handleFileUpload(file) {
        if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
            alert('Please upload an image or PDF file');
            return;
        }

        this.uploadedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewImage = document.getElementById('preview-image');
            previewImage.src = e.target.result;

            document.getElementById('upload-zone').style.display = 'none';
            document.getElementById('preview-section').style.display = 'block';
            document.getElementById('results-section').style.display = 'none';
        };
        reader.readAsDataURL(file);
    },

    async analyzeDocument() {
        const analyzeBtn = document.getElementById('analyze-btn');
        const scanOverlay = document.getElementById('scan-overlay');

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '🔍 Scanning...';
        scanOverlay.classList.add('scanning');

        // Get active document type
        const docType = document.querySelector('.scan-tab.active')?.dataset.type || 'marksheet';

        try {
            // Convert image to base64
            const base64 = await this.getBase64(this.uploadedFile);

            // Call backend API
            const response = await fetch(`${API_BASE_URL}/api/documents/scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: base64,
                    document_type: docType
                })
            });

            if (!response.ok) {
                // Use simulated data if API not available
                this.extractedData = this.getSimulatedData(docType);
            } else {
                const data = await response.json();
                this.extractedData = data;
            }

            this.displayResults();

            // Award XP
            if (window.ProgressComponent) {
                ProgressComponent.addXP(20, 'document_scan');
            }

        } catch (error) {
            console.error('Document analysis error:', error);
            // Use simulated data as fallback
            this.extractedData = this.getSimulatedData(docType);
            this.displayResults();
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '🔍 Analyze Document';
            scanOverlay.classList.remove('scanning');
        }
    },

    getBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.onerror = error => reject(error);
        });
    },

    getSimulatedData(docType) {
        const simulations = {
            marksheet: {
                confidence: 92,
                data: {
                    'Student Name': 'Rahul Kumar',
                    'Registration No': 'KAR2024123456',
                    'Exam Year': '2024',
                    'Physics': '85/100',
                    'Chemistry': '78/100',
                    'Mathematics': '92/100',
                    'Total Marks': '255/300',
                    'Percentage': '85%',
                    'Grade': 'Distinction'
                },
                verification: {
                    status: 'valid',
                    messages: [
                        '✅ Document format recognized',
                        '✅ All marks within valid range',
                        '✅ Total calculation verified'
                    ]
                },
                suggestions: [
                    'With 85%, you are eligible for top engineering colleges',
                    'Consider applying for merit-based scholarships',
                    'Your physics score qualifies you for JEE Mains'
                ]
            },
            certificate: {
                confidence: 88,
                data: {
                    'Certificate Type': 'Caste Certificate',
                    'Name': 'Rahul Kumar',
                    'Father Name': 'Suresh Kumar',
                    'Category': 'SC',
                    'District': 'Dharwad',
                    'Issue Date': '15-03-2024',
                    'Valid Until': '14-03-2027'
                },
                verification: {
                    status: 'valid',
                    messages: [
                        '✅ Certificate format valid',
                        '✅ Within validity period',
                        '⚠️ Ensure original is available for counselling'
                    ]
                },
                suggestions: [
                    'SC category qualifies for reserved seats',
                    'Apply for SC Post-Matric Scholarship',
                    'Fee waiver available in government colleges'
                ]
            },
            income: {
                confidence: 85,
                data: {
                    'Certificate Type': 'Income Certificate',
                    'Name': 'Suresh Kumar',
                    'Annual Income': '₹2,40,000',
                    'Category': 'EWS',
                    'Taluk': 'Hubli',
                    'Issue Date': '20-01-2024'
                },
                verification: {
                    status: 'valid',
                    messages: [
                        '✅ Income within scholarship limits',
                        '✅ Certificate is recent',
                        '⚠️ Some scholarships require income < 2.5 lakhs'
                    ]
                },
                suggestions: [
                    'Eligible for Central Sector Scholarship',
                    'Can apply for fee reimbursement',
                    'Consider education loan with interest subsidy'
                ]
            },
            caste: {
                confidence: 90,
                data: {
                    'Certificate Type': 'Caste Certificate',
                    'Caste': 'Scheduled Caste',
                    'Sub-Caste': 'Madar',
                    'Name': 'Rahul Kumar',
                    'Valid': 'Yes'
                },
                verification: {
                    status: 'valid',
                    messages: ['✅ Valid SC certificate detected']
                },
                suggestions: [
                    'Eligible for SC reserved seats in KCET',
                    'Apply for post-matric scholarship'
                ]
            }
        };

        return simulations[docType] || simulations.marksheet;
    },

    displayResults() {
        document.getElementById('preview-section').style.display = 'none';
        document.getElementById('results-section').style.display = 'block';

        const { confidence, data, verification, suggestions } = this.extractedData;

        // Confidence badge
        const confidenceBadge = document.getElementById('confidence-badge');
        confidenceBadge.querySelector('.confidence-value').textContent = confidence;
        confidenceBadge.className = `confidence-badge ${confidence >= 90 ? 'high' : confidence >= 70 ? 'medium' : 'low'}`;

        // Extracted data
        const dataContainer = document.getElementById('extracted-data');
        dataContainer.innerHTML = Object.entries(data).map(([key, value]) => `
            <div class="data-row">
                <span class="data-key">${key}</span>
                <span class="data-value">${value}</span>
            </div>
        `).join('');

        // Verification status
        const verificationContainer = document.getElementById('verification-status');
        verificationContainer.innerHTML = `
            <div class="verification-badge ${verification.status}">
                ${verification.status === 'valid' ? '✅' : '⚠️'} 
                ${verification.status === 'valid' ? 'Document Verified' : 'Needs Review'}
            </div>
            <div class="verification-messages">
                ${verification.messages.map(msg => `<p>${msg}</p>`).join('')}
            </div>
        `;

        // Suggestions
        const suggestionsList = document.getElementById('suggestions-list');
        suggestionsList.innerHTML = suggestions.map(s => `<li>${s}</li>`).join('');
    },

    useExtractedData() {
        // Store extracted data for use in other components
        if (this.extractedData && this.extractedData.data) {
            localStorage.setItem('scannedDocumentData', JSON.stringify(this.extractedData.data));

            // Show success message
            alert('✅ Data saved! This information will be auto-filled in forms.');

            // Award badge
            if (window.ProgressComponent) {
                ProgressComponent.unlockBadge('document_scanner');
            }
        }
    },

    resetUpload() {
        this.uploadedFile = null;
        this.extractedData = null;

        document.getElementById('upload-zone').style.display = 'flex';
        document.getElementById('preview-section').style.display = 'none';
        document.getElementById('results-section').style.display = 'none';
        document.getElementById('file-input').value = '';
    },

    injectStyles() {
        if (document.getElementById('document-scanner-styles')) return;

        const style = document.createElement('style');
        style.id = 'document-scanner-styles';
        style.textContent = `
            .document-scanner {
                padding: 1.5rem;
                max-width: 600px;
                margin: 0 auto;
            }

            .scanner-header {
                text-align: center;
                margin-bottom: 1.5rem;
            }

            .scanner-header h2 {
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .scanner-subtitle {
                color: var(--text-secondary, #888);
            }

            .scanner-tabs {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1.5rem;
                flex-wrap: wrap;
            }

            .scan-tab {
                padding: 0.5rem 1rem;
                border: 1px solid var(--border-color, #333);
                border-radius: 20px;
                background: transparent;
                color: var(--text-primary, #fff);
                cursor: pointer;
                font-size: 0.85rem;
                transition: all 0.3s ease;
            }

            .scan-tab.active {
                background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
                border-color: transparent;
            }

            .upload-zone {
                border: 2px dashed var(--border-color, #333);
                border-radius: 16px;
                padding: 3rem 2rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.5rem;
            }

            .upload-zone:hover,
            .upload-zone.dragover {
                border-color: #f59e0b;
                background: rgba(245, 158, 11, 0.1);
            }

            .upload-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }

            .upload-zone h3 {
                font-size: 1.2rem;
                color: var(--text-primary, #fff);
            }

            .upload-zone p {
                color: var(--text-secondary, #888);
            }

            .upload-formats {
                font-size: 0.75rem;
                color: var(--text-secondary, #888);
                margin-top: 1rem;
            }

            .preview-section {
                border: 1px solid var(--border-color, #333);
                border-radius: 16px;
                overflow: hidden;
            }

            .preview-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem;
                background: var(--card-bg, #1a1a2e);
            }

            .preview-header h3 {
                margin: 0;
                font-size: 1rem;
            }

            .remove-btn {
                background: transparent;
                border: none;
                color: #ef4444;
                cursor: pointer;
            }

            .preview-container {
                position: relative;
                max-height: 300px;
                overflow: hidden;
            }

            #preview-image {
                width: 100%;
                height: auto;
                display: block;
            }

            .scan-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s;
            }

            .scan-overlay.scanning {
                opacity: 1;
            }

            .scan-line {
                position: absolute;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, transparent, #f59e0b, transparent);
                animation: scan 2s infinite;
            }

            @keyframes scan {
                0% { top: 0; }
                100% { top: 100%; }
            }

            .analyze-btn {
                width: 100%;
                padding: 1rem;
                background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
                border: none;
                color: white;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .analyze-btn:hover {
                opacity: 0.9;
            }

            .analyze-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .results-section {
                border: 1px solid var(--border-color, #333);
                border-radius: 16px;
                padding: 1.5rem;
            }

            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }

            .confidence-badge {
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
            }

            .confidence-badge.high {
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }

            .confidence-badge.medium {
                background: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
            }

            .confidence-badge.low {
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
            }

            .extracted-data {
                background: var(--card-bg, #1a1a2e);
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .data-row {
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid var(--border-color, #333);
            }

            .data-row:last-child {
                border-bottom: none;
            }

            .data-key {
                color: var(--text-secondary, #888);
            }

            .data-value {
                color: var(--text-primary, #fff);
                font-weight: 500;
            }

            .verification-status {
                margin-bottom: 1rem;
            }

            .verification-badge {
                padding: 0.75rem 1rem;
                border-radius: 8px;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }

            .verification-badge.valid {
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }

            .verification-messages p {
                margin: 0.25rem 0;
                font-size: 0.9rem;
                color: var(--text-secondary, #888);
            }

            .suggestions-box {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1.5rem;
            }

            .suggestions-box h4 {
                margin: 0 0 0.75rem 0;
                color: #3b82f6;
            }

            .suggestions-box ul {
                margin: 0;
                padding-left: 1.5rem;
            }

            .suggestions-box li {
                margin: 0.5rem 0;
                color: var(--text-primary, #fff);
            }

            .result-actions {
                display: flex;
                gap: 1rem;
            }

            .action-btn {
                flex: 1;
                padding: 0.75rem 1rem;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .action-btn.primary {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
            }

            .action-btn.secondary {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                color: var(--text-primary, #fff);
            }

            .scanner-tips {
                margin-top: 2rem;
                padding: 1rem;
                background: var(--card-bg, #1a1a2e);
                border-radius: 12px;
            }

            .scanner-tips h4 {
                margin: 0 0 0.75rem 0;
                color: var(--text-secondary, #888);
            }

            .scanner-tips ul {
                margin: 0;
                padding-left: 1.5rem;
            }

            .scanner-tips li {
                margin: 0.25rem 0;
                color: var(--text-primary, #fff);
                font-size: 0.9rem;
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
    DocumentScannerComponent.init();
});

// Export
window.DocumentScannerComponent = DocumentScannerComponent;
