import os
from fpdf import FPDF
from llm_service import get_llm_service

# Ensure output directory exists
PDF_DIR = os.path.join(os.path.dirname(__file__), 'static', 'applications')
os.makedirs(PDF_DIR, exist_ok=True)

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(0, 10, 'Scholarship Application', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_scholarship_essay(student_data, scholarship_name, reason):
    """
    Generates a persuasive scholarship essay using the LLM.
    """
    try:
        llm = get_llm_service()
        
        prompt = f"""
        You are a professional educational counselor helping a student write a scholarship application essay.
        
        Student Profile:
        - Name: {student_data.get('name', 'Student')}
        - Education: {student_data.get('education', 'Engineering Student')}
        - Family Income: {student_data.get('income', 'Low Income')}
        - Academic Performance: {student_data.get('marks', 'Excellent')}
        - Location: {student_data.get('location', 'Rural Karnataka')}
        
        Scholarship: {scholarship_name}
        Personal Reason: {reason}
        
        Task:
        Write a highly persuasive, empathetic, and professional Statement of Purpose (SOP) / Application Letter for this scholarship.
        
        Guidelines:
        - Tone: Formal, humble, yet confident.
        - Structure: Introduction, Financial Need explanation, Academic Achievements, Future Goals, Conclusion.
        - length: Around 250-300 words.
        - NO placeholders like [Name]. Use the provided name or "I".
        - Do not include subject lines or addresses, just the body of the essay.
        """
        
        # Use the existing chat method or a completion method if available. 
        # Assuming get_response works for single prompts.
        response = llm.generate(prompt)
        return response
        
    except Exception as e:
        print(f"Error generating essay: {e}")
        return "I am writing to express my sincere interest in this scholarship..."

def create_application_pdf(student_data, essay_text, filename="application.pdf"):
    """
    Generates a PDF file with the application letter.
    """
    try:
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Student Details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Name: {student_data.get('name')}", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Application No: {student_data.get('id', student_data.get('application_no', 'N/A'))}", 0, 1)
        pdf.cell(0, 8, f"Date: {student_data.get('date', 'Today')}", 0, 1)
        pdf.ln(10)
        
        # Content
        pdf.set_font('Arial', '', 12)
        
        # Sanitize text for latin-1 encoding (FPDF limitation)
        # Replace common unicode chars
        text = essay_text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        text = text.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.multi_cell(0, 8, text)
        
        # Signature area
        pdf.ln(20)
        pdf.cell(0, 10, "Sincerely,", 0, 1)
        pdf.ln(10)
        pdf.cell(0, 10, f"____________________", 0, 1)
        pdf.cell(0, 10,f"{student_data.get('name')}", 0, 1)
        
        filepath = os.path.join(PDF_DIR, filename)
        pdf.output(filepath)
        return filepath, f"/static/applications/{filename}"
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None, None
