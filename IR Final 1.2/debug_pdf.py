import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'college', 'backend'))

from scholarship_service import create_application_pdf

def test_pdf():
    print("Testing PDF Generation...")
    student_data = {
        "name": "Debug Student",
        "id": "DBG001",
        "date": "29-01-2026"
    }
    essay = "This is a test essay to debug PDF generation. It contains clean text."
    
    try:
        path, url = create_application_pdf(student_data, essay, "debug.pdf")
        if path:
            print(f"[OK] Success! Path: {path}")
            print(f"URL: {url}")
        else:
            print("[FAIL] Failed (returned None)")
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf()
