# ==============================================================================
# InsightRural — Admin Dashboard Router
# ==============================================================================
# Endpoints: /admin/upload
# Migrated from app.py Flask endpoints (lines 2374-2497)
# ==============================================================================

import json
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from core.logging import get_logger
from core.config import settings

logger = get_logger("api.admin")
router = APIRouter()

UPLOAD_FOLDER = os.path.join(str(settings.BASE_DIR), "data", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "json", "csv"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/admin/upload")
async def admin_upload(file: UploadFile = File(...)):
    """
    Admin Upload Dashboard.
    Accepts files (PDF, JSON, CSV) and automatically processes them:
      - PDF  -> KEA cutoff parsing + RAG vector ingestion
      - JSON -> Loaded for review
      - CSV  -> Saved for manual review
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    if not _allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    from werkzeug.utils import secure_filename

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    processing_results = {"file": filename, "saved": True, "actions": []}
    ext = filename.rsplit(".", 1)[1].lower()

    # ── PDF Processing ────────────────────────────────────────────────────
    if ext == "pdf":
        try:
            import sys
            sys.path.insert(0, os.path.join(str(settings.BASE_DIR), "data_pipeline"))
            from pdf_parser import KEAPDFParser as PipelinePDFParser

            parser = PipelinePDFParser()
            df = parser.parse_pdf(file_path)
            record_count = len(df) if not df.empty else 0
            processing_results["actions"].append({
                "step": "kea_cutoff_parse",
                "status": "success" if record_count > 0 else "no_data",
                "records_extracted": record_count,
            })
        except ImportError:
            processing_results["actions"].append({
                "step": "kea_cutoff_parse",
                "status": "skipped",
                "detail": "PDF parser module not available",
            })
        except Exception as e:
            processing_results["actions"].append({
                "step": "kea_cutoff_parse",
                "status": "error",
                "detail": str(e),
            })

        # RAG ingestion
        try:
            from core.dependencies import get_rag_engine
            rag = get_rag_engine()
            rag.ingest_document(file_path, doc_type="counseling_rules")
            processing_results["actions"].append({
                "step": "rag_ingestion",
                "status": "success",
            })
        except Exception as e:
            processing_results["actions"].append({
                "step": "rag_ingestion",
                "status": "error",
                "detail": str(e),
            })

    # ── JSON Processing ───────────────────────────────────────────────────
    elif ext == "json":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                uploaded_data = json.load(f)
            record_count = len(uploaded_data) if isinstance(uploaded_data, list) else 1
            processing_results["actions"].append({
                "step": "json_load",
                "status": "success",
                "records_loaded": record_count,
                "detail": "Data loaded. Use /api/admin/apply-json to merge into live service.",
            })
        except json.JSONDecodeError as e:
            processing_results["actions"].append({
                "step": "json_load",
                "status": "error",
                "detail": f"Invalid JSON: {str(e)}",
            })

    # ── CSV Processing ────────────────────────────────────────────────────
    elif ext == "csv":
        processing_results["actions"].append({
            "step": "csv_saved",
            "status": "success",
            "detail": "CSV saved for review. Use /api/admin/apply-csv to import.",
        })

    return {
        "success": True,
        "message": f"File '{filename}' uploaded and processed.",
        "processing": processing_results,
    }
