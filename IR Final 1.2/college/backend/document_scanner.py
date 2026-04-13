import base64
import random
import time

def scan_document(image_base64: str, doc_type: str = "marksheet"):
    """
    Simulate document scanning and OCR extraction.
    In a production environment, this would use Tesseract or a Vision LLM.
    """
    # Simulate processing delay
    time.sleep(1.5)
    
    # Return simulated data based on document type
    # This matches the frontend simulation to ensure consistency
    if doc_type == "marksheet":
        return {
            "confidence": random.randint(90, 99),
            "data": {
                "Student Name": "Rahul Kumar",
                "Registration No": f"KAR{random.randint(2024000000, 2024999999)}",
                "Exam Year": "2024",
                "Physics": f"{random.randint(70, 95)}/100",
                "Chemistry": f"{random.randint(70, 95)}/100",
                "Mathematics": f"{random.randint(75, 100)}/100",
                "Total Marks": "265/300",
                "Percentage": "88.33%",
                "Result": "DISTINCTION"
            },
            "verification": {
                "status": "valid",
                "messages": [
                    "✅ Document format recognized (PUC-II Marksheet)",
                    "✅ Board watermark detected",
                    "✅ Marks sum verified correctly"
                ]
            },
            "suggestions": [
                "Your PCM score (88.33%) is excellent for engineering!",
                "You are eligible for top colleges like RVCE and BMSCE through KCET.",
                "Consider applying for the 'Pratibha Puraskar' scholarship."
            ]
        }
    
    elif doc_type == "caste":
        return {
            "confidence": random.randint(85, 95),
            "data": {
                "Certificate Type": "Caste Certificate",
                "Category": "Scheduled Caste (SC)",
                "Sub-Caste": "Adi Karnataka",
                "RD Number": f"RD{random.randint(1000000, 9999999)}",
                "Applicant Name": "Rahul Kumar",
                "Validity": "Valid for Life"
            },
            "verification": {
                "status": "valid",
                "messages": [
                    "✅ Digital signature verified",
                    "✅ RD Number format matches Nadakacheri database",
                    "✅ Issued by Tahsildar, Bangalore North"
                ]
            },
            "suggestions": [
                "You are eligible for 15% reserved seats in KCET.",
                "Apply for SSP Post-Matric Scholarship (100% fee waiver).",
                "Use this RD Number for your KCET application."
            ]
        }
        
    elif doc_type == "income":
        income = random.choice(["1,50,000", "2,40,000", "95,000"])
        return {
            "confidence": random.randint(85, 95),
            "data": {
                "Certificate Type": "Income Certificate",
                "Annual Income": f"₹{income}",
                "Category": "CAT-1",
                "RD Number": f"RD{random.randint(1000000, 9999999)}",
                "Family Size": "4 Members",
                "Issue Date": "15-Jan-2024"
            },
            "verification": {
                "status": "valid",
                "messages": [
                    "✅ Income is within EWS/Reservation limits",
                    "✅ Certificate is valid (issued within 5 years)",
                    "✅ QR Code scanned successfully"
                ]
            },
            "suggestions": [
                "Income < 2.5 Lakhs qualifies for full fee reimbursement.",
                "Eligible for Vidyasiri (Food & Accommodation) scheme.",
                "You can claim Supernumerary Quota (SNQ) seats."
            ]
        }

    return {
        "error": "Unknown document type",
        "confidence": 0
    }
