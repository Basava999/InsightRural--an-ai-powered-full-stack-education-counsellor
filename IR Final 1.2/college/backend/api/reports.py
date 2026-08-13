# ==============================================================================
# InsightRural — Reports Router
# ==============================================================================
# Endpoints: /report/generate, /report/status
# Migrated from app.py Flask endpoints (lines 1573-1637)
# ==============================================================================

from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse
from typing import Dict, Any

from core.logging import get_logger
from core.exceptions import ServiceUnavailableError

logger = get_logger("api.reports")
router = APIRouter()


@router.post("/report/generate")
async def generate_report(data: Dict[str, Any]):
    """
    Generate a PDF report from prediction results.
    Returns: PDF file download.
    """
    try:
        from pdf_generator import generate_college_report
    except ImportError:
        raise ServiceUnavailableError(
            "PDF Generator", {"detail": "Install fpdf2: pip install fpdf2"}
        )

    if not data.get("prediction_result"):
        raise HTTPException(status_code=400, detail="prediction_result is required")
    if not data.get("student_profile"):
        raise HTTPException(status_code=400, detail="student_profile is required")

    try:
        pdf_bytes = generate_college_report(
            prediction_result=data["prediction_result"],
            student_profile=data["student_profile"],
        )

        filename = f"InsightRural_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as e:
        logger.error("PDF generation error: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@router.get("/report/status")
async def report_status():
    """Check PDF generator availability."""
    try:
        from pdf_generator import generate_college_report  # noqa: F401
        return {"pdf_available": True}
    except ImportError:
        return {"pdf_available": False}
