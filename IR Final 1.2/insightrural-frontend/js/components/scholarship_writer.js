/**
 * AI Scholarship Auto-Pilot Component
 * Handles essay generation and PDF application creation
 */

class ScholarshipWriter {
    constructor() {
        this.activeScholarship = null;
        this.renderModal();
        this.setupEventListeners();
    }

    renderModal() {
        // Create modal HTML
        const modal = document.createElement('div');
        modal.className = 'modal hidden';
        modal.id = 'scholarship-writer-modal';

        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-container writer-modal">
                <div class="modal-header">
                    <h2><span class="icon">✨</span> AI Scholarship Auto-Pilot</h2>
                    <button class="close-modal" id="close-writer-modal">×</button>
                </div>
                
                <div class="modal-body">
                    <div id="writer-step-1" class="writer-step">
                        <div class="scholarship-summary">
                            <h3 id="target-scholarship-name">Scholarship Name</h3>
                            <p>Let AI write your winning application essay instantly.</p>
                        </div>
                        
                        <div class="form-group">
                            <label>Why do you need this satisfied?</label>
                            <textarea id="writer-reason" placeholder="E.g., I am a first-generation learner from a farming family..."></textarea>
                        </div>
                        
                        <button class="btn-primary btn-block" id="btn-generate-essay">
                            <span class="icon">⚡</span> Auto-Generate Application
                        </button>
                    </div>

                    <div id="writer-step-2" class="writer-step hidden">
                        <div class="typing-container">
                            <div id="essay-output" class="essay-content" contenteditable="true"></div>
                            <div class="typing-cursor"></div>
                        </div>
                        
                        <div class="writer-actions">
                            <button class="btn-secondary" id="btn-regenerate">Regenerate</button>
                            <button class="btn-primary" id="btn-download-pdf">
                                <span class="icon">📄</span> Download Official PDF
                            </button>
                        </div>
                    </div>
                    
                    <div id="writer-step-3" class="writer-step hidden">
                        <div class="success-message">
                            <div class="check-animation">✓</div>
                            <h3>Application Ready!</h3>
                            <p>Your PDF application has been downloaded.</p>
                            <button class="btn-secondary" id="btn-writer-close">Close</button>
                        </div>
                    </div>
                    
                    <div id="writer-loading" class="loading-overlay hidden">
                        <div class="spinner"></div>
                        <p>AI is drafting your story...</p>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add basic styles
        const style = document.createElement('style');
        style.textContent = `
            .writer-modal { max-width: 600px; width: 90%; }
            .writer-step { padding: 1rem; }
            .scholarship-summary { background: #f0fdf4; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; }
            .scholarship-summary h3 { color: #166534; margin-bottom: 0.5rem; }
            .essay-content { 
                min-height: 300px; 
                max-height: 400px; 
                overflow-y: auto; 
                background: #f9fafb; 
                padding: 1.5rem; 
                border-radius: 8px; 
                font-family: 'Times New Roman', serif; 
                font-size: 1.1rem; 
                line-height: 1.6;
                white-space: pre-wrap;
                border: 1px solid #e5e7eb;
            }
            .writer-actions { display: flex; gap: 1rem; margin-top: 1.5rem; justify-content: flex-end; }
            .check-animation { font-size: 4rem; color: #22c55e; margin-bottom: 1rem; }
            .success-message { text-align: center; padding: 2rem; }
        `;
        document.head.appendChild(style);

        this.modal = modal;
    }

    setupEventListeners() {
        document.getElementById('close-writer-modal').addEventListener('click', () => this.close());
        document.getElementById('btn-writer-close').addEventListener('click', () => this.close());

        this.modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) this.close();
        });

        document.getElementById('btn-generate-essay').addEventListener('click', () => this.generateEssay());
        document.getElementById('btn-download-pdf').addEventListener('click', () => this.downloadPDF());
        document.getElementById('btn-regenerate').addEventListener('click', () => {
            this.showStep(1);
            this.generateEssay();
        });
    }

    open(scholarshipName) {
        this.activeScholarship = scholarshipName;
        document.getElementById('target-scholarship-name').textContent = scholarshipName;
        this.modal.classList.remove('hidden');
        this.showStep(1);
    }

    close() {
        this.modal.classList.add('hidden');
    }

    showStep(step) {
        document.querySelectorAll('.writer-step').forEach(el => el.classList.add('hidden'));
        document.getElementById(`writer-step-${step}`).classList.remove('hidden');
    }

    setLoading(isLoading) {
        const loader = document.getElementById('writer-loading');
        if (isLoading) loader.classList.remove('hidden');
        else loader.classList.add('hidden');
    }

    async generateEssay() {
        const reason = document.getElementById('writer-reason').value;
        if (!reason) {
            alert("Please tell us little bit about why you need this.");
            return;
        }

        this.setLoading(true);

        // Get user profile from AppState, fallback to sensible defaults
        const profile = (typeof AppState !== 'undefined' && AppState.getProfile()) || {};
        const studentData = {
            name: profile.name || "Student",
            education: profile.education || "12th Standard",
            income: profile.finance || "Not specified",
            marks: profile.marks || "Not specified",
            location: profile.location || "Karnataka"
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/scholarships/generate-essay`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_data: studentData,
                    scholarship: this.activeScholarship,
                    reason: reason
                })
            });

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            this.currentEssay = data.essay;
            this.typewriterEffect(data.essay);
            this.showStep(2);

        } catch (error) {
            alert("Failed to generate essay: " + error.message);
        } finally {
            this.setLoading(false);
        }
    }

    typewriterEffect(text) {
        const container = document.getElementById('essay-output');
        container.textContent = '';
        let i = 0;
        const speed = 10; // ms per char

        function type() {
            if (i < text.length) {
                container.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        type();
    }

    async downloadPDF() {
        this.setLoading(true);
        try {
            const profile = (typeof AppState !== 'undefined' && AppState.getProfile()) || {};
            const studentData = {
                name: profile.name || "Student",
                id: profile.id || "N/A",
                date: new Date().toLocaleDateString()
            };

            const response = await fetch(`${API_BASE_URL}/api/scholarships/download-pdf`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_data: studentData,
                    essay: document.getElementById('essay-output').innerText // Get edited text
                })
            });

            const data = await response.json();
            if (data.error) throw new Error(data.error);

            // Backend returns full URL in data.url, use path for safety
            const link = document.createElement('a');
            link.href = data.url.startsWith('http') ? data.url : `${API_BASE_URL}${data.url}`;
            link.download = "Scholarship_Application.pdf";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            this.showStep(3);

        } catch (error) {
            alert("PDF Generation Failed: " + error.message);
        } finally {
            this.setLoading(false);
        }
    }
}

// Initialize
window.ScholarshipWriterComponent = new ScholarshipWriter();
