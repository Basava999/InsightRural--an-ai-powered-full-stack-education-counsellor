from fpdf import FPDF
import os

class AnalysisReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_title("InsightRural Project Analysis Report")
        
    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(16, 163, 127)  # Primary green from project
        self.cell(0, 10, 'InsightRural', align='C', ln=True)
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Project Analysis & Deployment Report', align='C', ln=True)
        self.ln(10)
        self.set_draw_color(16, 163, 127)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, label):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102) # Dark Blue
        self.cell(0, 10, label, ln=True)
        self.ln(2)

    def chapter_subtitle(self, label):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, label, ln=True)
        
    def body_text(self, text, indent=False):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(20, 20, 20)
        if indent:
            self.set_x(20)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet_point(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(20, 20, 20)
        self.set_x(15)
        self.multi_cell(0, 6, chr(149) + " " + text)
        self.ln(1)

pdf = AnalysisReportPDF()
pdf.add_page()

# 1. Executive Summary
pdf.chapter_title("1. Executive Summary")
pdf.body_text("InsightRural is a sophisticated, AI-powered educational counseling platform specifically designed for Karnataka students (KEA/KCET). Unlike generic college predictors, it implements a high-fidelity simulation of the KEA Serial Dictatorship Algorithm, accounting for complex reservation categories.")
pdf.ln(2)
pdf.body_text("It features a Hybrid AI Architecture: combining deterministic algorithms for precise predictions with Generative AI (Llama-3 via Groq) for conversational counseling and document assistance.")
pdf.ln(5)

# 2. Technical Architecture
pdf.chapter_title("2. Technical Architecture")

pdf.chapter_subtitle("Frontend (Client-Side)")
pdf.bullet_point("Tech Stack: Vanilla HTML5, CSS3, JavaScript (ES6+).")
pdf.bullet_point("Design Pattern: Component-based architecture without a heavy framework.")
pdf.bullet_point("Key Files: state.js (Global State), predictor.js (KEA Logic), voice_counselor.js (Speech API).")
pdf.ln(3)

pdf.chapter_subtitle("Backend (Server-Side)")
pdf.bullet_point("Tech Stack: Python 3.10+, Flask.")
pdf.bullet_point("AI Engine: Groq Cloud API (Llama-3-70b) + RAG (ChromaDB + sentence-transformers).")
pdf.bullet_point("Predictor: KEA Algorithm simulation + scikit-learn for trend analysis.")
pdf.ln(5)

# 3. Feature Breakdown
pdf.chapter_title("3. Feature Breakdown")

pdf.chapter_subtitle("1. KEA College Predictor")
pdf.bullet_point("Accuracy: High. Implements exact KEA seat allotment rules.")
pdf.bullet_point("Quotas: Rural (15%), Kannada Medium (5%), HK Region (8%), Caste Categories.")
pdf.bullet_point("Analytics: Sparkline trends (2022-2024), Admission Probability, ROI Calculator.")
pdf.ln(3)

pdf.chapter_subtitle("2. Voice-First AI Counselor")
pdf.bullet_point("Full voice interaction (Speech-to-Text & Text-to-Speech).")
pdf.bullet_point("Multi-lingual support structure (English, Hindi, Kannada).")
pdf.bullet_point("Context-aware responses based on student profile.")
pdf.ln(3)

pdf.chapter_subtitle("3. Scholarship Finder & Auto-Writer")
pdf.bullet_point("Smart Match: Filters based on Income + Category.")
pdf.bullet_point("AI Writer: Generates personalized Statement of Purpose (SOP) essays.")
pdf.ln(3)

pdf.chapter_subtitle("4. Document & Report Engine")
pdf.bullet_point("Generates detailed PDF Counselling Strategy Reports.")
pdf.bullet_point("Dynamic document checklists based on claimed quotas.")
pdf.ln(5)

# 4. Code Quality & Status
pdf.chapter_title("4. Code Quality & Status")

pdf.chapter_subtitle("Strengths")
pdf.bullet_point("Modular Code: Clearly separated concerns (rag_engine.py vs ml_predictor.py).")
pdf.bullet_point("Robust Error Handling: Fallbacks exist for offline AI availability.")
pdf.bullet_point("Performance: Optimized lightweight Vector Search.")
pdf.ln(3)

pdf.chapter_subtitle("Weaknesses & Action Items")
pdf.bullet_point("Hardcoded URLs: state.js points to localhost. Must be fixed.")
pdf.bullet_point("Heavy Dependencies: torch/transformers are large for serverless.")
pdf.bullet_point("Security: Groq API Key hardcoded or needs environment variable setup.")
pdf.ln(5)

# 5. Deployment Recommendation
pdf.chapter_title("5. Deployment Recommendation")
pdf.body_text("A 'Hybrid Deployment' Strategy is recommended due to project size constraints:")
pdf.ln(3)

pdf.set_fill_color(240, 240, 240)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(40, 10, "Component", 1, 0, 'C', 1)
pdf.cell(50, 10, "Host", 1, 0, 'C', 1)
pdf.cell(90, 10, "Reason", 1, 1, 'C', 1)

pdf.set_font('Helvetica', '', 11)
pdf.cell(40, 10, "Frontend", 1, 0, 'C')
pdf.cell(50, 10, "Vercel", 1, 0, 'C')
pdf.cell(90, 10, "Free, Global CDN, Static Site Optimized", 1, 1, 'L')

pdf.cell(40, 10, "Backend", 1, 0, 'C')
pdf.cell(50, 10, "Render", 1, 0, 'C')
pdf.cell(90, 10, "Supports large Python/ML apps (Free Tier)", 1, 1, 'L')
pdf.ln(5)

pdf.chapter_subtitle("Next Steps")
pdf.bullet_point("1. Sign up for Vercel and Render.")
pdf.bullet_point("2. Obtain Groq API Key.")
pdf.bullet_point("3. Update code to fix hardcoded URLs.")
pdf.bullet_point("4. Deploy using the provided guides.")

output_path = os.path.join(os.path.dirname(__file__), "InsightRural_Analysis_Report.pdf")
pdf.output(output_path)
print(f"PDF generated at: {output_path}")
