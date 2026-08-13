from flask import Flask, jsonify, request, abort, Response, stream_with_context
from flask_cors import CORS
from sqlalchemy import or_, func
import json
import traceback
import os

# Load environment variables from .env file (for permanent API key storage)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded .env file")
except ImportError:
    print("[!] python-dotenv not installed. Run: pip install python-dotenv")

from db import SessionLocal, engine, Base
from db_models import College, FeeStructure, User
from werkzeug.security import generate_password_hash, check_password_hash
import hmac
import hashlib
import base64
import time
from functools import wraps

# Secret key for signing custom JWT tokens
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    import warnings
    warnings.warn("JWT_SECRET_KEY env var not set. Using local development key.", UserWarning)
    SECRET_KEY = "insightrural_secret_viva_2026_key"


# AI modules for chat functionality
try:
    from rag_engine import get_rag_engine, StrictRAGEngine
    from llm_service import get_llm_service, MultiLLMOrchestrator
    AI_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI modules not fully loaded: {e}")
    AI_MODULES_AVAILABLE = False

# ML Predictor module
try:
    from ml_predictor import get_predictor, CollegePredictor
    ML_PREDICTOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML Predictor not available: {e}")
    ML_PREDICTOR_AVAILABLE = False

# PDF Report Generator
try:
    from pdf_generator import generate_college_report
    PDF_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PDF Generator not available: {e}")
    PDF_GENERATOR_AVAILABLE = False

# WhatsApp Bot
try:
    from whatsapp_bot import get_whatsapp_bot, WhatsAppBot
    WHATSAPP_BOT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: WhatsApp Bot not available: {e}")
    WHATSAPP_BOT_AVAILABLE = False

# Document Scanner
try:
    from document_scanner import scan_document
    DOCUMENT_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Document Scanner not available: {e}")
    DOCUMENT_SCANNER_AVAILABLE = False

# Scholarship Auto-Pilot
try:
    from scholarship_service import generate_scholarship_essay, create_application_pdf
    SCHOLARSHIP_AI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Scholarship AI not available: {e}")
    SCHOLARSHIP_AI_AVAILABLE = False

# Counseling Suite Service
try:
    from counseling_service import get_counseling_guide, generate_option_entry_list
    COUNSELING_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Counseling Service not available: {e}")
    COUNSELING_SERVICE_AVAILABLE = False

# Unified JEE / NEET Admission Counseling Services
try:
    from admission_probability import calculate_admission_probability
    from admissions_service import (
        answer_admission_query,
        build_neet_counseling_plan,
        compare_colleges as compare_colleges_service,
        compare_jee_options,
        generate_career_roadmap,
        get_jee_cutoffs,
        get_neet_cutoffs,
        predict_jee,
        predict_neet,
    )
    ADMISSIONS_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Admissions Service not available: {e}")
    ADMISSIONS_SERVICE_AVAILABLE = False

# Risk Analyzer Engine
try:
    from risk_analyzer import analyze_risk, generate_ai_explanation
    RISK_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Risk Analyzer not available: {e}")
    RISK_ANALYZER_AVAILABLE = False

# JSON-First Data Service (Priority 1)
try:
    from json_data_service import get_json_data_service
    JSON_DATA_SERVICE_AVAILABLE = True
    print("[OK] JSON Data Service loaded for API endpoints")
except ImportError as e:
    print(f"Warning: JSON Data Service not available: {e}")
    JSON_DATA_SERVICE_AVAILABLE = False

# Recommendation Service Orchestrator
try:
    from services.recommendation_service import RecommendationService
    from models.schemas import PredictRequest
    from pydantic import ValidationError
    RECOMMENDATION_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Recommendation Service not available: {e}")
    RECOMMENDATION_SERVICE_AVAILABLE = False

# KEA Seat Allotment Simulation Engine
try:
    from kea_allotment_engine import get_kea_engine
    KEA_ENGINE_AVAILABLE = True
    print("[OK] KEA Allotment Engine loaded for API endpoints")
except ImportError as e:
    print(f"Warning: KEA Allotment Engine not available: {e}")
    KEA_ENGINE_AVAILABLE = False

# Trigger Reload: Updated at 2026-01-29 - Counseling Suite v2
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup Flask-Limiter for API rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
# Custom HMAC-SHA256 JWT implementation (pyjwt independent)
def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def b64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def generate_token(user_id: int, expires_in: int = 86400 * 7) -> str:
    """Generate a custom JWT token signed with HMAC-SHA256."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + expires_in
    }
    header_b64 = b64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = b64url_encode(json.dumps(payload).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    signature_b64 = b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_token(token: str):
    """Decode and verify custom JWT token. Returns user_id if valid, else None."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        expected_sig_b64 = b64url_encode(expected_sig)
        if not hmac.compare_digest(signature_b64.encode('utf-8'), expected_sig_b64.encode('utf-8')):
            return None
        payload = json.loads(b64url_decode(payload_b64).decode('utf-8'))
        if payload.get("exp", 0) < time.time():
            return None
        return payload.get("user_id")
    except Exception:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"success": False, "error": "Authentication token is missing"}), 401
        user_id = decode_token(token)
        if not user_id:
            return jsonify({"success": False, "error": "Invalid or expired token"}), 401
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated

Base.metadata.create_all(bind=engine)


def college_to_dict(col):
    return {
        "college_id": col.id,
        "name": col.name,
        "type": col.type,
        "location": col.location,
        "affiliation": col.affiliation,
        "hostel_available": bool(col.hostel_available),
        "branches": col.branches or [],
        "fee_category": col.fee_category,
        "cutoff_data": col.cutoff_data or {}
    }
def fee_to_dict(fee):
    if not fee:
        return None
    return {
        "category": fee.category,
        "gm_and_others_above_income_limit": fee.gm_and_others_above_income_limit,
        "snq_quota": fee.snq_quota,
        "sc_st_concession": fee.sc_st_concession,
        "cat1_upto_2_5_lakhs": fee.cat1_upto_2_5_lakhs,
        "others_upto_10_lakhs": fee.others_upto_10_lakhs,
        "cat1_above_2_5_lakhs": fee.cat1_above_2_5_lakhs
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route("/api/auth/signup", methods=["POST"])
def auth_signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    profile = data.get("profile") or {}
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400
        
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            return jsonify({"success": False, "error": "An account with this email already exists"}), 400
            
        password_hash = generate_password_hash(password)
        new_user = User(
            email=email,
            password_hash=password_hash,
            profile=profile
        )
        session.add(new_user)
        session.commit()
        
        token = generate_token(new_user.id)
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "profile": new_user.profile or {}
            }
        }), 201
    except Exception as e:
        session.rollback()
        print(f"[ERROR] /api/auth/signup: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        session.close()

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400
        
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
            
        token = generate_token(user.id)
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "profile": user.profile or {}
            }
        })
    except Exception as e:
        print(f"[ERROR] /api/auth/login: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        session.close()

@app.route("/api/auth/me", methods=["GET"])
@token_required
def auth_me():
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == request.user_id).first()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
            
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "profile": user.profile or {}
            }
        })
    finally:
        session.close()

@app.route("/api/colleges", methods=["GET"])

def get_colleges():
    session = SessionLocal()
    try:
        print("\n=== GET /api/colleges ===")
        
        # Get query parameters
        q = (request.args.get("q") or "").strip().lower()
        branch = (request.args.get("branch") or "").strip()
        location_filter = (request.args.get("location") or "").strip()
        type_filter = (request.args.get("type") or "").strip()
        page = int(request.args.get("page", 1))
        limit = min(int(request.args.get("limit", 12)), 100)
        
        print(f"Query params: q='{q}', branch='{branch}', loc='{location_filter}', type='{type_filter}'")
        
        # Fetch ALL colleges (small dataset ~230 items, safe to load in memory)
        all_colleges = session.query(College).all()
        
        # Apply Filters in Python for maximum flexibility
        filtered_colleges = []
        
        for col in all_colleges:
            # 1. Search Query (Smart Fuzzy Match)
            if q:
                # Normalize text: remove dots, spaces, special chars
                def normalize(text):
                    return "".join(e for e in str(text).lower() if e.isalnum())
                
                norm_q = normalize(q)
                norm_name = normalize(col.name)
                norm_loc = normalize(col.location)
                
                # Check for match in name, location, or abbreviation
                # Also allow direct substring match (e.g. "Engineer" in "Engineering")
                if (q in col.name.lower()) or \
                   (norm_q in norm_name) or \
                   (q in col.location.lower() if col.location else False) or \
                   (col.affiliation and q in col.affiliation.lower()):
                    pass # Match found
                else:
                    continue # Skip this college
            
            # 2. Branch Filter
            if branch and branch != "":
                if not col.branches or branch not in col.branches:
                    continue
            
            # 3. Location Filter
            if location_filter and location_filter != "":
                if not col.location or location_filter.lower() not in col.location.lower():
                    continue
            
            # 4. Type Filter
            if type_filter and type_filter != "":
                if not col.type or type_filter.lower() != col.type.lower():
                    continue
            
            filtered_colleges.append(col)
            
        # Get total count
        total = len(filtered_colleges)
        print(f"Total colleges after filter: {total}")
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_cols = filtered_colleges[start:end]
        
        results = [college_to_dict(c) for c in paginated_cols]
        print(f"Returning {len(results)} colleges for page {page}")
        
        response_data = {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "items": results
        }
        
        print("Response data prepared successfully")
        return jsonify(response_data)
        
    except ValidationError as ve:
        return jsonify({"error": "Validation Error", "details": ve.errors()}), 400
    except Exception as e:
        print(f"â Œ ERROR in get_colleges: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "total": 0,
            "page": 1,
            "limit": 12,
            "pages": 0,
            "items": []
        }), 500
    finally:
        session.close()

@app.route("/api/colleges/<cid>", methods=["GET"])
def get_college(cid):
    session = SessionLocal()
    try:
        print(f"\n=== GET /api/colleges/{cid} ===")
        
        col = session.query(College).filter(College.id == cid).first()
        if not col:
            print(f"College not found: {cid}")
            return jsonify({"error": "College not found"}), 404
        
        result = college_to_dict(col)
        
        # Get fee details if fee_category exists
        if col.fee_category:
            fee = session.query(FeeStructure).filter(FeeStructure.category == col.fee_category).first()
            if fee:
                result["fee_details"] = fee_to_dict(fee)
        
        print(f"Returning college: {col.name}")
        return jsonify(result)
        
    except Exception as e:
        print(f"âŒ ERROR in get_college: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/api/fees/<path:category>", methods=["GET"])
def get_fee(category):
    session = SessionLocal()
    try:
        print(f"\n=== GET /api/fees/{category} ===")
        
        fee = session.query(FeeStructure).filter(FeeStructure.category == category).first()
        if not fee:
            print(f"Fee category not found: {category}")
            return jsonify({"error": "Fee category not found"}), 404
        
        print(f"Returning fee for category: {category}")
        return jsonify(fee_to_dict(fee))
        
    except Exception as e:
        print(f"âŒ ERROR in get_fee: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/api/branches", methods=["GET"])
def get_branches():
    session = SessionLocal()
    try:
        print("\n=== GET /api/branches ===")
        
        # Get all colleges
        colleges = session.query(College).all()
        branches_set = set()
        
        for college in colleges:
            if college.branches:
                for branch in college.branches:
                    if branch:  # Skip empty strings
                        branches_set.add(branch)
        
        branches_list = sorted(list(branches_set))
        print(f"Found {len(branches_list)} unique branches")
        return jsonify(branches_list)
        
    except Exception as e:
        print(f"âŒ ERROR in get_branches: {str(e)}")
        print(traceback.format_exc())
        # Return empty list instead of fallback to avoid confusion
        return jsonify([]), 500
    finally:
        session.close()

@app.route("/api/locations", methods=["GET"])
def get_locations():
    session = SessionLocal()
    try:
        print("\n=== GET /api/locations ===")
        
        locations = session.query(func.distinct(College.location)).filter(
            College.location.isnot(None)
        ).order_by(College.location).all()
        
        # Extract location strings from results
        location_list = [loc[0] for loc in locations if loc[0]]
        print(f"Found {len(location_list)} unique locations")
        return jsonify(location_list)
        
    except Exception as e:
        print(f"âŒ ERROR in get_locations: {str(e)}")
        print(traceback.format_exc())
        # Return empty list instead of fallback to avoid confusion
        return jsonify([]), 500
    finally:
        session.close()

@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    session = SessionLocal()
    try:
        print("\n=== GET /api/statistics ===")
        
        total_colleges = session.query(func.count(College.id)).scalar() or 0
        print(f"Total colleges: {total_colleges}")
        
        total_locations = session.query(func.count(func.distinct(College.location))).scalar() or 0
        print(f"Total locations: {total_locations}")
        
        # Count unique branches
        colleges = session.query(College).all()
        branches_set = set()
        for college in colleges:
            if college.branches:
                for branch in college.branches:
                    if branch:  # Skip empty strings
                        branches_set.add(branch)
        total_branches = len(branches_set)
        print(f"Total branches: {total_branches}")
        
        return jsonify({
            "total_colleges": total_colleges,
            "total_locations": total_locations,
            "total_branches": total_branches
        })
        
    except Exception as e:
        print(f"âŒ ERROR in get_statistics: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "total_colleges": 0,
            "total_locations": 0,
            "total_branches": 0
        }), 500
    finally:
        session.close()

@app.route("/api/search/suggestions", methods=["GET"])
def get_suggestions():
    session = None
    try:
        q = (request.args.get("q") or "").strip()
        if len(q) < 2:
            return jsonify([])
        
        print(f"\n=== GET /api/search/suggestions?q={q} ===")
        
        session = SessionLocal()
        results = session.query(College.name, College.location).filter(
            College.name.ilike(f"%{q}%")
        ).limit(5).all()
        
        suggestions = [{"name": r[0], "location": r[1] or ""} for r in results]
        print(f"Found {len(suggestions)} suggestions for '{q}'")
        return jsonify(suggestions)
        
    except Exception as e:
        print(f"âŒ ERROR in get_suggestions: {str(e)}")
        return jsonify([])
    finally:
        if session is not None:
            session.close()

@app.route("/api/health", methods=["GET"])
def health_check():
    session = SessionLocal()
    try:
        # Test database connection
        college_count = session.query(func.count(College.id)).scalar() or 0
        fee_count = session.query(func.count(FeeStructure.category)).scalar() or 0
        
        return jsonify({
            "status": "healthy",
            "message": "API is running",
            "database": {
                "colleges": college_count,
                "fee_structures": fee_count
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": str(e),
            "database": "connection failed"
        }), 500
    finally:
        session.close()

@app.route("/api/debug", methods=["GET"])
def debug_info():
    """Debug endpoint to check database content"""
    session = SessionLocal()
    try:
        # Get sample data
        sample_colleges = session.query(College).limit(5).all()
        sample_fees = session.query(FeeStructure).limit(5).all()
        
        return jsonify({
            "sample_colleges": [college_to_dict(c) for c in sample_colleges],
            "sample_fees": [fee_to_dict(f) for f in sample_fees],
            "total_colleges": session.query(func.count(College.id)).scalar(),
            "total_fees": session.query(func.count(FeeStructure.category)).scalar()
        })
    finally:
        session.close()


# ============================================================================
# AI CHAT ENDPOINTS
# ============================================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main AI chat endpoint (non-streaming).
    Uses MultiLLMOrchestrator: Sarvam AI + Llama 3 + DeepSeek R1 + Mixtral.
    """
    if not AI_MODULES_AVAILABLE:
        return jsonify({"response": "AI modules unavailable.", "error": True}), 500

    try:
        data        = request.json or {}
        user_message = data.get("message", "").strip()
        session_id   = data.get("session_id", "default")
        chat_history = data.get("history", [])
        language     = data.get("language", "en-IN")

        if not user_message:
            return jsonify({"response": "Please enter a message.", "error": True}), 400

        if language == "kn-IN":
            user_message += " [CRITICAL INSTRUCTION: You MUST reply entirely in Kannada script.]"
        elif language == "hi-IN":
            user_message += " [CRITICAL INSTRUCTION: You MUST reply entirely in Hindi script.]"

        # Retrieve student profile from authenticated user in SQLite
        profile = data.get("profile", {})
        db_session = None
        try:
            db_session = SessionLocal()
            user_id = getattr(request, "user_id", None)
            if user_id:
                user = db_session.query(User).filter(User.id == user_id).first()
                if user and user.profile:
                    profile = user.profile
        except Exception:
            pass
        finally:
            if db_session:
                db_session.close()

        orchestrator = get_llm_service()
        response = orchestrator.generate_response(
            query=user_message,
            chat_history=chat_history[-12:],
            session_id=session_id,
            session_profile=profile if profile else None,
        )

        return jsonify({"response": response, "session_id": session_id})

    except Exception as e:
        err_msg = traceback.format_exc()
        print(f"[ERROR] /api/chat: {err_msg}")
        return jsonify({"response": "I'm having a small issue right now. Please try again!", "error": True}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    """
    Streaming AI chat endpoint — SSE token stream.
    Pipeline: profile fetch → ChromaDB RAG → LLaMA 3 (Ollama local) → token stream.
    Fallback: RAG-only response if Ollama is offline.
    """
    if not AI_MODULES_AVAILABLE:
        return jsonify({"error": "AI modules unavailable"}), 500

    data         = request.json or {}
    user_message = data.get("message", "").strip()
    session_id   = data.get("session_id", "default")
    chat_history = data.get("history", [])
    language     = data.get("language", "en-IN")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if language == "kn-IN":
        user_message += " [CRITICAL INSTRUCTION: You MUST reply entirely in Kannada script.]"
    elif language == "hi-IN":
        user_message += " [CRITICAL INSTRUCTION: You MUST reply entirely in Hindi script.]"

    # Retrieve student profile from authenticated user in SQLite
    profile = data.get("profile", {})
    db_session = None
    try:
        db_session = SessionLocal()
        user_id = getattr(request, "user_id", None)
        if user_id:
            user = db_session.query(User).filter(User.id == user_id).first()
            if user and user.profile:
                profile = user.profile
    except Exception:
        pass
    finally:
        if db_session:
            db_session.close()

    def generate():
        try:
            counselor = get_llm_service()

            for token in counselor.stream_response(
                query=user_message,
                chat_history=chat_history[-12:],
                session_id=session_id,
                session_profile=profile if profile else None,
            ):
                yield f"data: {json.dumps({'chunk': token})}\n\n"

            yield f"data: {json.dumps({'done': True, 'model': 'LLaMA 3 (Ollama)'})}\n\n"

        except Exception as e:
            print(f"[ERROR] /api/chat/stream generate(): {e}")
            import traceback; print(traceback.format_exc())
            yield f"data: {json.dumps({'chunk': 'I ran into a small issue. Please try again!'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":   "no-cache",
            "Connection":      "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/api/recommend/colleges", methods=["POST"])
def recommend_colleges():
    """
    Get college recommendations based on student profile.
    Accepts: { "kcet_rank": 5000, "branch": "CSE", "category": "OBC" }
    Legacy endpoint mapped to new RecommendationService.
    """
    if not RECOMMENDATION_SERVICE_AVAILABLE or not JSON_DATA_SERVICE_AVAILABLE:
        return jsonify({"error": "Recommendation Service not available"}), 500
        
    try:
        data = request.json or {}
        rank = int(data.get("kcet_rank", 0))
        branch = data.get("branch", "CSE")
        category = data.get("category", "GM")
        
        if rank <= 0:
            return jsonify({"error": "Please provide a valid KCET rank"}), 400
            
        json_svc = get_json_data_service()
        rec_svc = RecommendationService(json_svc)
        
        req = PredictRequest(
            kcet_rank=rank,
            preferred_branches=[branch],
            category=category
        )
        
        response = rec_svc.recommend(req.to_student_profile())
        
        # Flatten safe/moderate/ambitious for legacy response format
        colleges = []
        for c in response.safe + response.moderate + response.ambitious:
            colleges.append({
                "college": c.college_name,
                "location": c.location,
                "type": c.college_type,
                "cutoff": c.cutoff_rank,
                "fee": {"gm": c.annual_fee}, # approximated for legacy format
                "branch": c.branch
            })
            
        colleges.sort(key=lambda x: x['cutoff'])
        
        return jsonify({
            "rank": rank,
            "branch": branch,
            "category": category,
            "total_matches": len(colleges),
            "colleges": colleges[:20]  # Top 20
        })
        
    except ValidationError as ve:
        return jsonify({"error": "Validation Error", "details": ve.errors()}), 400
    except Exception as e:
        print(f"â Œ ERROR in recommend_colleges: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommend/scholarships", methods=["POST"])
def recommend_scholarships():
    """
    Get scholarship recommendations based on student profile.
    Accepts: { "category": "SC", "income": 200000 }
    """
    try:
        data = request.json
        category = data.get("category", "General")
        income = int(data.get("income", 500000))
        
        # Always use the JSON fallback for rules-based recommendation
        import os
        data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'scholarships.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            all_scholarships = json.load(f)
        
        scholarships = []
        category_lower = category.lower()
        for sch in all_scholarships:
            eligibility = sch.get('eligibility', {})
            income_limit = eligibility.get('income_limit', float('inf'))
            sch_categories = [c.lower() for c in eligibility.get('category', [])]
            
            if income <= income_limit:
                # Check if 'all categories' scholarship
                if 'all categories' in sch_categories or 'all' in sch_categories:
                    scholarships.append(sch)
                elif category_lower in ['sc', 'st'] and (category_lower in sch_categories or 'sc/st' in sch_categories):
                    scholarships.append(sch)
                elif 'obc' in category_lower and ('obc' in sch_categories or '2a' in sch_categories or '3a' in sch_categories or '3b' in sch_categories):
                    scholarships.append(sch)
                elif category_lower in ['gm', 'general', 'ews'] and ('general' in sch_categories or 'gm' in sch_categories or 'ews' in sch_categories or 'all categories' in sch_categories):
                    scholarships.append(sch)
        
        return jsonify({
            "category": category,
            "income": income,
            "total_matches": len(scholarships),
            "scholarships": scholarships
        })
        
    except Exception as e:
        print(f"â Œ ERROR in recommend_scholarships: {str(e)}")
        print(f"❌ ERROR in recommend_scholarships: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# JSON-FIRST DATA ENDPOINTS (Priority 1 — exact database values)
# ============================================================================

@app.route("/api/v2/recommend/colleges", methods=["POST"])
def recommend_colleges_v2():
    """
    Enhanced college recommendations using RecommendationService Pipeline.
    Returns SAFE / MODERATE / AMBITIOUS classifications with exact cutoff data.
    Accepts: { "kcet_rank": 5000, "branch": "CSE", "category": "OBC",
               "location": "Bengaluru", "hostel_needed": true, "budget": 120000 }
    """
    if not RECOMMENDATION_SERVICE_AVAILABLE or not JSON_DATA_SERVICE_AVAILABLE:
        return jsonify({"error": "Recommendation Service not available"}), 500

    try:
        data = request.json or {}
        rank = int(data.get("kcet_rank", 0))
        branch = data.get("branch", "CSE")
        category = data.get("category", "GM")
        location = data.get("location")
        hostel_needed = data.get("hostel_needed", False)
        budget = data.get("budget")

        if rank <= 0:
            return jsonify({"error": "Please provide a valid KCET rank"}), 400

        json_svc = get_json_data_service()
        rec_svc = RecommendationService(json_svc)
        
        req = PredictRequest(
            kcet_rank=rank,
            preferred_branches=[branch] if branch else ["CSE"],
            category=category,
            preferred_locations=[location] if location else None,
            hostel_required=hostel_needed,
            budget=int(budget) if budget else None,
        )
        
        response = rec_svc.recommend(req.to_student_profile())
        
        # Convert Pydantic models back to dict for jsonify
        safe_list = [c.model_dump() for c in response.safe]
        moderate_list = [c.model_dump() for c in response.moderate]
        ambitious_list = [c.model_dump() for c in response.ambitious]

        return jsonify({
            "rank": rank,
            "branch": branch,
            "category": category,
            "location": location,
            "total_matches": len(safe_list) + len(moderate_list) + len(ambitious_list),
            "safe": safe_list,
            "moderate": moderate_list,
            "ambitious": ambitious_list,
            "counselling_guidance": response.counselling_guidance,
            "confidence": response.confidence
        })

    except Exception as e:
        print(f"❌ ERROR in recommend_colleges_v2: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v2/hostel", methods=["POST"])
def get_hostel_v2():
    """
    Get hostel information from verified JSON database.
    Accepts: { "college": "RVCE", "location": "Bangalore", "category": "SC" }
    """
    if not JSON_DATA_SERVICE_AVAILABLE:
        return jsonify({"error": "JSON Data Service not available"}), 500

    try:
        data = request.json or {}
        svc = get_json_data_service()
        info = svc.get_hostel_info(
            college_name=data.get("college"),
            location=data.get("location"),
            category=data.get("category"),
        )
        if not info:
            return jsonify({
                "message": "Verified hostel information is not currently available for this query.",
                "hostels": [],
            })
        return jsonify({"info": info, "source": "Structured JSON Database"})

    except Exception as e:
        print(f"❌ ERROR in get_hostel_v2: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v2/scholarships", methods=["POST"])
def get_scholarships_v2():
    """
    Get verified scholarships from JSON database.
    Accepts: { "category": "SC", "income": 200000, "gender": "Female" }
    """
    if not JSON_DATA_SERVICE_AVAILABLE:
        return jsonify({"error": "JSON Data Service not available"}), 500

    try:
        data = request.json or {}
        svc = get_json_data_service()
        info = svc.get_scholarships(
            category=data.get("category"),
            income=int(data.get("income")) if data.get("income") else None,
            gender=data.get("gender"),
        )
        if not info:
            return jsonify({
                "message": "No matching scholarships found for this profile.",
                "scholarships": [],
            })
        return jsonify({"info": info, "source": "Structured JSON Database"})

    except Exception as e:
        print(f"❌ ERROR in get_scholarships_v2: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v2/cutoff-trends", methods=["POST"])
def get_cutoff_trends_v2():
    """
    Get multi-year cutoff trends for a specific college.
    Accepts: { "college": "RVCE", "branch": "CSE", "category": "GM" }
    """
    if not JSON_DATA_SERVICE_AVAILABLE:
        return jsonify({"error": "JSON Data Service not available"}), 500

    try:
        data = request.json or {}
        college = data.get("college", "")
        branch = data.get("branch", "CSE")
        category = data.get("category", "GM")

        if not college:
            return jsonify({"error": "College name is required"}), 400

        svc = get_json_data_service()
        info = svc.get_cutoff_trends(college, branch, category)
        if not info:
            return jsonify({
                "message": "Cutoff trend data not available for this college.",
            })
        return jsonify({"info": info, "source": "Structured JSON Database"})

    except Exception as e:
        print(f"ERROR in get_cutoff_trends_v2: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# KEA SEAT ALLOTMENT SIMULATION (ML + Rules Engine)
# ============================================================================

@app.route("/api/v2/simulate", methods=["POST"])
def kea_simulate():
    """
    Full KEA seat allotment simulation.
    Uses ML models + rule-based engine to predict colleges.
    Returns SAFE / MODERATE / AMBITIOUS with confidence scores.
    
    Accepts: {
        "kcet_rank": 5000,
        "category": "OBC",
        "gender": "Male",
        "branch_preference": ["CSE", "ISE", "ECE"],
        "district_preference": ["Bengaluru Urban"],
        "rural_quota": false,
        "kannada_medium": false,
        "snq": false,
        "371j_status": false,
        "minority_status": false,
        "annual_income": 400000,
        "hostel_required": false,
        "budget": 120000,
        "top_n": 15
    }
    """
    if not KEA_ENGINE_AVAILABLE:
        return jsonify({"error": "KEA Allotment Engine not available"}), 500

    try:
        data = request.json or {}
        rank = int(data.get("kcet_rank", 0))
        if rank <= 0:
            return jsonify({"error": "Please provide a valid KCET rank"}), 400

        engine = get_kea_engine()
        result = engine.simulate(
            rank=rank,
            category=data.get("category", "GM"),
            gender=data.get("gender", "Male"),
            branch_preference=data.get("branch_preference", ["CSE", "ISE", "ECE"]),
            district_preference=data.get("district_preference"),
            college_preference=data.get("college_preference"),
            rural_quota=data.get("rural_quota", False),
            kannada_medium=data.get("kannada_medium", False),
            snq=data.get("snq", False),
            special_reservation=data.get("special_reservation"),
            hk_371j=data.get("371j_status", False),
            minority_status=data.get("minority_status", False),
            annual_income=int(data.get("annual_income", 0)),
            hostel_required=data.get("hostel_required", False),
            budget=int(data.get("budget", 0)) if data.get("budget") else 0,
            top_n=int(data.get("top_n", 15)),
        )

        return jsonify(result)

    except Exception as e:
        print(f"ERROR in kea_simulate: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/v2/ml-info", methods=["GET"])
def ml_info():
    """Get information about the trained ML models."""
    if not KEA_ENGINE_AVAILABLE:
        return jsonify({"error": "KEA Engine not available"}), 500

    try:
        engine = get_kea_engine()
        return jsonify({
            "ml_model": engine.ml_engine.best_model_name or "Rule-based",
            "is_trained": engine.ml_engine.is_trained,
            "model_comparison": engine.ml_engine.metrics,
            "total_colleges": len(engine.colleges),
            "feature_names": engine.ml_engine.feature_names,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/profile", methods=["POST", "GET"])
@token_required
def manage_profile():
    """Store or retrieve student profile in database."""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == request.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if request.method == "POST":
            profile = request.json or {}
            user.profile = profile
            session.commit()
            return jsonify({"status": "saved", "profile": profile})
        else:
            return jsonify(user.profile or {})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()



@app.route("/api/ai/status", methods=["GET"])
def ai_status():
    """Check AI system status (Ollama + ChromaDB RAG)."""
    status = {
        "ai_modules_available": AI_MODULES_AVAILABLE,
        "ollama_connected":     False,
        "ollama_model":         "llama3",
        "rag_indexed":          False,
        "pipeline":             "local-ollama-llama3-chromadb-rag",
    }

    if AI_MODULES_AVAILABLE:
        try:
            counselor = get_llm_service()
            detail = counselor.get_status()
            status["ollama_connected"] = detail.get("ollama", {}).get("available", False)
            status["ollama_model"]     = detail.get("ollama", {}).get("model", "llama3")
            status["rag_indexed"]      = detail.get("rag_engine", {}).get("available", False)
        except Exception:
            pass

    return jsonify(status)


# ============================================================================
# UNIFIED ADMISSION COUNSELING ENDPOINTS (JEE + NEET)
# ============================================================================

@app.route("/api/admission-probability", methods=["POST"])
def admission_probability_endpoint():
    """Calculate rank-vs-cutoff admission probability from 0 to 100."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    data = request.get_json(silent=True) or {}
    rank = data.get("rank")
    previous_cutoff = data.get("previous_cutoff") or data.get("cutoff")
    category = data.get("category", "OPEN")

    if data.get("colleges"):
        results = []
        for college in data.get("colleges", []):
            cutoff = college.get("cutoff") or college.get("previous_cutoff")
            probability = calculate_admission_probability(rank, cutoff, category)
            results.append({
                "college": college.get("college") or college.get("name"),
                "branch": college.get("branch") or college.get("course"),
                "previous_cutoff": cutoff,
                **probability,
            })
        return jsonify({"success": True, "results": results})

    if not rank or not previous_cutoff:
        return jsonify({"success": False, "error": "rank and previous_cutoff are required"}), 400

    return jsonify({
        "success": True,
        "rank": rank,
        "previous_cutoff": previous_cutoff,
        "category": category,
        **calculate_admission_probability(rank, previous_cutoff, category),
    })


@app.route("/api/jee/predict", methods=["POST"])
def jee_predict_endpoint():
    """Predict IIT, NIT, IIIT, and GFTI options from JEE ranks."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        if not data.get("jee_main_rank") and not data.get("jee_advanced_rank"):
            return jsonify({"success": False, "error": "Provide JEE Main rank or JEE Advanced rank"}), 400
        return jsonify(predict_jee(data))
    except Exception as e:
        print(f"JEE prediction error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jee/compare", methods=["POST"])
def jee_compare_endpoint():
    """Compare JEE options or named colleges."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        return jsonify(compare_jee_options(data))
    except Exception as e:
        print(f"JEE compare error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/jee/cutoffs", methods=["GET"])
def jee_cutoffs_endpoint():
    """Return JEE cutoff rows with optional filters."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        return jsonify(get_jee_cutoffs(request.args.to_dict()))
    except Exception as e:
        print(f"JEE cutoffs error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/neet/predict", methods=["POST"])
def neet_predict_endpoint():
    """Predict AIQ, state, government, private, dental, and AYUSH options."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        if not data.get("neet_rank"):
            return jsonify({"success": False, "error": "NEET rank is required"}), 400
        return jsonify(predict_neet(data))
    except Exception as e:
        print(f"NEET prediction error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/neet/cutoffs", methods=["POST"])
def neet_cutoffs_endpoint():
    """Return NEET cutoff rows with optional filters."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        return jsonify(get_neet_cutoffs(data))
    except Exception as e:
        print(f"NEET cutoffs error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/neet/counseling", methods=["POST"])
def neet_counseling_endpoint():
    """Generate a NEET counseling plan with choice buckets and documents."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        if not data.get("neet_rank"):
            return jsonify({"success": False, "error": "NEET rank is required"}), 400
        return jsonify(build_neet_counseling_plan(data))
    except Exception as e:
        print(f"NEET counseling error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/compare", methods=["POST"])
def unified_compare_endpoint():
    """Compare fees, placement, hostel, location, average and highest package."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        return jsonify(compare_colleges_service(data))
    except Exception as e:
        print(f"Unified compare error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/career/roadmap", methods=["POST"])
def career_roadmap_endpoint():
    """Generate a deterministic 5-year roadmap and opportunity summary."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        return jsonify(generate_career_roadmap(data))
    except Exception as e:
        print(f"Career roadmap error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admission-counselor", methods=["POST"])
def admission_counselor_endpoint():
    """RAG-style admission counselor for JEE/NEET questions."""
    if not ADMISSIONS_SERVICE_AVAILABLE:
        return jsonify({"success": False, "error": "Admissions service unavailable"}), 503

    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        if not message:
            return jsonify({"success": False, "error": "message is required"}), 400

        llm = get_llm_service() if AI_MODULES_AVAILABLE else None
        return jsonify(answer_admission_query(message, data.get("profile", {}), llm=llm))
    except Exception as e:
        print(f"Admission counselor error: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# ML COLLEGE PREDICTION ENDPOINT
# ============================================

@app.route('/api/predict/college', methods=['POST'])
def predict_college():
    """
    ML-based college prediction.
    """
    if not ML_PREDICTOR_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "ML Predictor not available. Install scikit-learn."
        }), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'kcet_rank' not in data or 'category' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields: kcet_rank, category"
            }), 400

        # Get predictor instance
        predictor = get_predictor()
        
        # Determine branches (handle single branch fallback)
        branches = data.get('preferred_branches')
        if not branches and data.get('branch'):
            branches = [data.get('branch')]
        if not branches:
            branches = ['CSE', 'ECE', 'ISE']

        # Make prediction
        result = predictor.predict(
            kcet_rank=int(data['kcet_rank']),
            category=data['category'].upper(),
            preferred_branches=branches,
            preferred_locations=data.get('preferred_locations'),
            budget=data.get('budget'),
            college_type_pref=data.get('college_type_pref'),
            reservations=data.get('reservations'),
            puc_marks=data.get('puc_marks'),
            kcet_marks=data.get('kcet_marks'),
            top_n=data.get('top_n', 15)
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERROR in predict_college: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500


# ============================================================================
# GEN AI CAREER SIMULATOR ENDPOINT
# ============================================================================

def _career_simulation_fallback(rank, category, branch, interests):
    roadmap = generate_career_roadmap({
        "branch": branch,
        "interests": interests,
    }) if ADMISSIONS_SERVICE_AVAILABLE else {}

    branch_label = str(branch or "CSE").upper()
    interest_label = str(interests or "technology").title()

    return {
        "paths": [
            {
                "name": "Placement Track",
                "description": f"Build strong fundamentals in {branch_label}, complete internships, and target campus placements.",
                "color": "#2563eb",
                "probability": 72,
                "milestones": [
                    {"year": 2026, "title": "Admission", "desc": f"Join {branch_label} and finish bridge courses", "salary": None, "icon": "1"},
                    {"year": 2027, "title": "Skill Build", "desc": "Projects, coding/core labs, communication practice", "salary": None, "icon": "2"},
                    {"year": 2028, "title": "Internship", "desc": "Summer internship or hospital/industry exposure", "salary": "Rs. 15K-35K/month", "icon": "3"},
                    {"year": 2029, "title": "Campus Placement", "desc": "Target product/service/core companies", "salary": roadmap.get("expected_salary", "6-12 LPA"), "icon": "4"},
                    {"year": 2030, "title": "Growth", "desc": "Specialize and move to higher-impact roles", "salary": "12-24 LPA", "icon": "5"}
                ]
            },
            {
                "name": "Higher Studies Track",
                "description": "Prepare for GATE/GRE/NEET PG/CAT depending on your course and build a research profile.",
                "color": "#059669",
                "probability": 58,
                "milestones": [
                    {"year": 2026, "title": "Foundation", "desc": "Maintain CGPA and identify target exams", "salary": None, "icon": "1"},
                    {"year": 2027, "title": "Research Start", "desc": "Mini-projects, papers, open-source or clinical audits", "salary": None, "icon": "2"},
                    {"year": 2028, "title": "Exam Prep", "desc": "Structured test preparation and mentorship", "salary": None, "icon": "3"},
                    {"year": 2029, "title": "Admission", "desc": "M.Tech/MS/MD/MBA pathway", "salary": None, "icon": "4"},
                    {"year": 2030, "title": "Specialist Role", "desc": "Research, specialist, or leadership track", "salary": "10-22 LPA", "icon": "5"}
                ]
            },
            {
                "name": "Startup Track",
                "description": f"Use your {interest_label} interest to solve a student, rural, health, or industry problem.",
                "color": "#f97316",
                "probability": 36,
                "milestones": [
                    {"year": 2026, "title": "Problem Discovery", "desc": "Talk to users and validate one real pain point", "salary": None, "icon": "1"},
                    {"year": 2027, "title": "Prototype", "desc": "Build MVP with a small student team", "salary": None, "icon": "2"},
                    {"year": 2028, "title": "Pilot", "desc": "Run pilots through campus/incubation cells", "salary": None, "icon": "3"},
                    {"year": 2029, "title": "Funding/Revenue", "desc": "Apply for grants or earn first revenue", "salary": "Variable", "icon": "4"},
                    {"year": 2030, "title": "Scale", "desc": "Convert project into company or strong portfolio", "salary": "Variable", "icon": "5"}
                ]
            }
        ],
        "future_artifact": {
            "type": "news_headline",
            "date": "2030",
            "source": "InsightRural FutureVision",
            "content": f"Student with rank {rank} turns {branch_label} roadmap into a high-impact {interest_label} career."
        },
        "roadmap": roadmap
    }


@app.route('/api/simulate-career', methods=['POST'])
def simulate_career():
    """
    Generative AI Career Simulator.
    Accepts: { "rank": 5000, "category": "2A", "branch": "CSE", "interests": "Robotics, AI" }
    Returns: JSON with 3 career paths + Future Artifact
    """
    data = request.get_json(silent=True) or {}
    rank = data.get('rank')
    category = data.get('category')
    branch = data.get('branch')
    interests = data.get('interests', 'Technology, Engineering')
    
    if not all([rank, category, branch]):
        return jsonify({"error": "Missing required fields"}), 400

    if not AI_MODULES_AVAILABLE:
        return jsonify({
            "success": True,
            "data": _career_simulation_fallback(rank, category, branch, interests),
            "mode": "deterministic-fallback"
        })
        
    try:
        from prompt_templates import CAREER_SIMULATION_SYSTEM_PROMPT, CAREER_SIMULATION_USER_PROMPT
        
        user_prompt = CAREER_SIMULATION_USER_PROMPT.format(
            rank=rank,
            category=category,
            branch=branch,
            interests=interests
        )
        
        print(f"\n=== CAREER SIMULATION ===")
        print(f"Generating paths for Rank {rank}, {branch}...")
        
        llm_service = get_llm_service()
        # Force JSON mode by appending requirement to system prompt if model supports, 
        # or just relying on the prompt instructions.
        response_text = llm_service.generate(
            prompt=user_prompt,
            system_prompt=CAREER_SIMULATION_SYSTEM_PROMPT,
            temperature=0.8, # Higher creativity for "Dream" paths
            max_tokens=2000
        )
        
        # Clean response to ensure valid JSON (sometimes LLMs add text before/after)
        response_text = response_text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            
        try:
            result = json.loads(response_text)
            return jsonify({
                "success": True,
                "data": result
            })
        except json.JSONDecodeError:
            print(f"[!] Invalid JSON from LLM: {response_text[:100]}...")
            return jsonify({
                "success": True,
                "data": _career_simulation_fallback(rank, category, branch, interests),
                "mode": "deterministic-fallback",
                "warning": "LLM returned invalid JSON, so a fallback simulation was used."
            })
            
    except Exception as e:
        print(f"[ERROR] in simulate_career: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": True,
            "data": _career_simulation_fallback(rank, category, branch, interests),
            "mode": "deterministic-fallback",
            "warning": str(e)
        })


@app.route('/api/predict/status', methods=['GET'])
def predict_status():
    """Check ML predictor status."""
    return jsonify({
        "ml_available": ML_PREDICTOR_AVAILABLE,
        "model_loaded": ML_PREDICTOR_AVAILABLE,
        "version": "KEA_UPGRADE_V1"
    })




# ============================================
# PDF REPORT GENERATION ENDPOINT
# ============================================

@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """
    Generate a PDF report from prediction results.
    
    Request body:
    {
        "prediction_result": {...},  # Result from predict endpoint
        "student_profile": {...}     # Student's profile
    }
    
    Returns: PDF file download
    """
    if not PDF_GENERATOR_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "PDF Generator not available. Install fpdf2: pip install fpdf2"
        }), 503
    
    try:
        data = request.get_json()
        
        if not data.get('prediction_result'):
            return jsonify({"success": False, "error": "prediction_result is required"}), 400
        
        if not data.get('student_profile'):
            return jsonify({"success": False, "error": "student_profile is required"}), 400
        
        # Generate PDF
        pdf_bytes = generate_college_report(
            prediction_result=data['prediction_result'],
            student_profile=data['student_profile']
        )
        
        # Return as downloadable file
        from datetime import datetime
        filename = f"InsightRural_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': len(pdf_bytes)
            }
        )
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/report/status', methods=['GET'])
def report_status():
    """Check PDF generator status."""
    return jsonify({
        "pdf_available": PDF_GENERATOR_AVAILABLE
    })


# ============================================
# WHATSAPP BOT ENDPOINTS
# ============================================

@app.route('/api/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    WhatsApp webhook for Twilio.
    Receives incoming messages and returns TwiML responses.
    
    Configure this URL in your Twilio Console:
    https://your-domain.com/api/whatsapp/webhook
    """
    if not WHATSAPP_BOT_AVAILABLE:
        return "WhatsApp Bot not available", 503
    
    try:
        # Get message from Twilio
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        print(f"\n=== WhatsApp Message ===")
        print(f"From: {from_number}")
        print(f"Message: {incoming_msg}")
        
        # Get bot instance with predictor if available
        predictor = None
        if ML_PREDICTOR_AVAILABLE:
            try:
                predictor = get_predictor()
            except Exception:
                pass
        
        bot = get_whatsapp_bot(predictor)
        
        # Process message and get response
        response_text = bot.process_message(incoming_msg, from_number)
        
        # Return TwiML response
        twiml = bot.create_twiml_response(response_text)
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
        traceback.print_exc()
        return "Error processing message", 500


@app.route('/api/whatsapp/test', methods=['POST'])
def whatsapp_test():
    """
    Test WhatsApp bot without Twilio.
    Accepts: { "message": "your message here" }
    Returns: { "response": "bot response" }
    """
    if not WHATSAPP_BOT_AVAILABLE:
        return jsonify({"error": "WhatsApp Bot not available"}), 503
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get bot with predictor
        predictor = None
        if ML_PREDICTOR_AVAILABLE:
            try:
                predictor = get_predictor()
            except Exception:
                pass
        
        bot = get_whatsapp_bot(predictor)
        response = bot.process_message(message)
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents/scan", methods=["POST"])
def scan_document_endpoint():
    """
    Endpoint for smart document scanning.
    Accepts base64 image and document type.
    """
    if not DOCUMENT_SCANNER_AVAILABLE:
        return jsonify({"error": "Document scanner not available"}), 500
    
    try:
        data = request.json
        image = data.get("image")
        doc_type = data.get("document_type", "marksheet")
        
        if not image:
            return jsonify({"error": "No image provided"}), 400
            
        result = scan_document(image, doc_type)
        return jsonify(result)
        
    except Exception as e:
        print(f"âŒ ERROR in document scan: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/counseling/guide", methods=["GET"])
def get_counseling_guide_endpoint():
    """Get static counseling process guide."""
    if not COUNSELING_SERVICE_AVAILABLE:
        return jsonify({"error": "Counseling service unavailable"}), 503
    return jsonify(get_counseling_guide())

@app.route("/api/counseling/generate-options", methods=["POST"])
def generate_options_endpoint():
    """
    Generate smart option entry list.
    Accepts: { "rank": 5000, "category": "2A", "branches": ["CSE"] }
    """
    if not COUNSELING_SERVICE_AVAILABLE:
        return jsonify({"error": "Counseling service unavailable"}), 503
        
    try:
        data = request.json
        rank = data.get("rank")
        category = data.get("category", "GM")
        branches = data.get("branches", ["CSE"])
        
        if not rank:
            return jsonify({"error": "Rank is required"}), 400
            
        result = generate_option_entry_list(rank, category, branches)
        return jsonify(result)
        
    except Exception as e:
        print(f"Option Gen Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/scholarships/generate-essay", methods=["POST"])
def generate_essay_endpoint():
    """
    Generate scholarship essay using LLM.
    Accepts: { "student_data": {...}, "scholarship": "Name", "reason": "Reason" }
    """
    if not SCHOLARSHIP_AI_AVAILABLE:
        return jsonify({"error": "Scholarship AI unavailable"}), 503
    
    try:
        data = request.json
        essay = generate_scholarship_essay(
            data.get("student_data", {}),
            data.get("scholarship", "Scholarship"),
            data.get("reason", "")
        )
        return jsonify({"essay": essay})
    except Exception as e:
        print(f"Essay Generation Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/scholarships/download-pdf", methods=["POST"])
def download_scholarship_pdf():
    """
    Generate PDF for scholarship application.
    Accepts: { "student_data": {...}, "essay": "text" }
    """
    if not SCHOLARSHIP_AI_AVAILABLE:
        return jsonify({"error": "Scholarship AI unavailable"}), 503
        
    try:
        data = request.json
        filepath, url = create_application_pdf(
            data.get("student_data", {}),
            data.get("essay", "")
        )
        if not filepath:
            return jsonify({"error": "PDF generation failed"}), 500

        # Return full URL so frontend can open the PDF directly
        base_url = request.host_url.rstrip("/")
        full_url = f"{base_url}{url}"
        return jsonify({"url": full_url, "path": url})
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/whatsapp/status", methods=["GET"])
def whatsapp_status():
    """Check WhatsApp bot status."""
    return jsonify({
        "whatsapp_available": WHATSAPP_BOT_AVAILABLE,
        "twilio_configured": bool(os.environ.get('TWILIO_ACCOUNT_SID'))
    })


# ============================================
# HOSTEL & SCHOLARSHIP DATA ENDPOINTS
# ============================================

@app.route("/api/hostels", methods=["GET"])
def get_hostels():
    """
    Get all hostels with optional filters.
    Query params: location, type, gender, category
    """
    try:
        data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'hostels.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            all_hostels = json.load(f)
        
        # Apply filters
        location = request.args.get('location', '').strip().lower()
        hostel_type = request.args.get('type', '').strip().lower()
        gender = request.args.get('gender', '').strip().lower()
        category = request.args.get('category', '').strip().lower()
        
        filtered = all_hostels
        
        if location:
            filtered = [h for h in filtered if h.get('location', '').lower() == location]
        
        if hostel_type:
            filtered = [h for h in filtered if hostel_type in h.get('type', '').lower()]
        
        if gender:
            if gender == 'boys':
                filtered = [h for h in filtered if h.get('facilities', {}).get('boys_hostel', False)]
            elif gender == 'girls':
                filtered = [h for h in filtered if h.get('facilities', {}).get('girls_hostel', False)]
        
        if category:
            filtered = [h for h in filtered if category.upper() in str(h.get('category', []))]
        
        return jsonify({
            "total": len(filtered),
            "hostels": filtered
        })
        
    except Exception as e:
        print(f"ERROR in get_hostels: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e), "total": 0, "hostels": []}), 500


@app.route("/api/scholarships/list", methods=["GET"])
def get_scholarships_list():
    """
    Get all scholarships from JSON data with optional category filter.
    Query params: category
    """
    try:
        data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'scholarships.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            all_scholarships = json.load(f)
        
        # Apply category filter
        category = request.args.get('category', '').strip()
        
        if category:
            filtered = []
            for sch in all_scholarships:
                sch_cats = sch.get('eligibility', {}).get('category', [])
                cat_str = str(sch_cats).lower()
                if category.lower() in cat_str or category.lower() in sch.get('category', '').lower():
                    filtered.append(sch)
            all_scholarships = filtered
        
        return jsonify({
            "total": len(all_scholarships),
            "scholarships": all_scholarships
        })
        
    except Exception as e:
        print(f"ERROR in get_scholarships_list: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e), "total": 0, "scholarships": []}), 500


@app.route("/api/hostels/apply", methods=["POST"])
def hostel_apply():
    """
    Generate AI hostel application letter.
    Accepts: { "student_data": {...}, "hostel_name": "...", "reason": "..." }
    """
    if not AI_MODULES_AVAILABLE:
        return jsonify({"error": "AI modules not available"}), 503
    
    try:
        data = request.json
        student_data = data.get("student_data", {})
        hostel_name = data.get("hostel_name", "Government Hostel")
        reason = data.get("reason", "")
        
        llm = get_llm_service()
        
        prompt = f"""
        You are a professional educational counselor helping a student write a hostel admission application.
        
        Student Profile:
        - Name: {student_data.get('name', 'Student')}
        - Category: {student_data.get('category', 'Not specified')}
        - KCET Rank: {student_data.get('kcet_rank', 'Not specified')}
        - Family Income: {student_data.get('income', 'Not specified')}
        - Location: {student_data.get('location', 'Karnataka')}
        - College: {student_data.get('college', 'Not specified')}
        
        Hostel: {hostel_name}
        Personal Reason: {reason}
        
        Task:
        Write a formal, compelling hostel admission application letter addressed to the Hostel Warden / Department Head.
        
        Guidelines:
        - Tone: Formal, humble, and sincere.
        - Structure: Subject line, salutation, introduction, need for hostel, family background, academic commitment, conclusion.
        - Length: Around 200-250 words.
        - NO placeholders like [Name]. Use the provided name or "I".
        - Include the student's category and financial situation if relevant.
        - Mention the specific hostel name.
        """
        
        response = llm.generate(prompt)
        return jsonify({"application": response})
        
    except Exception as e:
        print(f"Hostel Application Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/smart-match", methods=["POST"])
def smart_match():
    """
    Auto-match student profile to eligible scholarships and hostels.
    Accepts: { "category": "SC", "income": 200000, "gender": "male", "location": "Bangalore" }
    """
    try:
        data = request.json
        category = data.get("category", "").upper()
        raw_income = data.get("income", 500000)
        # Handle text labels like "Low", "Medium", "High" from frontend
        income_map = {"low": 200000, "medium": 500000, "high": 1000000}
        if isinstance(raw_income, str) and raw_income.lower() in income_map:
            income = income_map[raw_income.lower()]
        else:
            try:
                income = int(raw_income)
            except (ValueError, TypeError):
                income = 500000
        gender = data.get("gender", "").lower()
        location = data.get("location", "").lower()
        
        # Load scholarships
        sch_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'scholarships.json')
        with open(sch_file, 'r', encoding='utf-8') as f:
            all_scholarships = json.load(f)
        
        # Load hostels
        host_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'hostels.json')
        with open(host_file, 'r', encoding='utf-8') as f:
            all_hostels = json.load(f)
        
        # Match scholarships
        eligible_scholarships = []
        for sch in all_scholarships:
            elig = sch.get('eligibility', {})
            income_limit = elig.get('income_limit', elig.get('income_max', float('inf')))
            sch_categories = str(elig.get('category', [])).lower()
            
            # Check income
            if income <= income_limit:
                # Check category
                cat_match = False
                if 'all categories' in sch_categories:
                    cat_match = True
                elif category.lower() in sch_categories:
                    cat_match = True
                elif category in ['SC', 'ST'] and ('sc' in sch_categories or 'st' in sch_categories):
                    cat_match = True
                elif 'obc' in category.lower() and ('category' in sch_categories or 'obc' in sch_categories):
                    cat_match = True
                
                # Check gender
                gender_req = elig.get('gender', '').lower()
                if gender_req and gender_req != gender:
                    cat_match = False
                
                if cat_match:
                    eligible_scholarships.append(sch)
        
        # Match hostels
        eligible_hostels = []
        for hostel in all_hostels:
            hostel_cats = str(hostel.get('category', [])).lower()
            
            # BCM/SC-ST hostels - check category
            if 'bcm' in hostel.get('type', '').lower() or 'sc/st' in hostel.get('type', '').lower() or 'minority' in hostel.get('type', '').lower():
                cat_match = False
                if category in ['SC', 'ST'] and ('sc' in hostel_cats or 'st' in hostel_cats):
                    cat_match = True
                elif 'obc' in category.lower() and 'obc' in hostel_cats:
                    cat_match = True
                elif 'category' in hostel_cats:
                    cat_match = True
                
                if cat_match:
                    # Check gender
                    fac = hostel.get('facilities', {})
                    if gender == 'male' and fac.get('boys_hostel', False):
                        eligible_hostels.append(hostel)
                    elif gender == 'female' and fac.get('girls_hostel', False):
                        eligible_hostels.append(hostel)
                    elif not gender:
                        eligible_hostels.append(hostel)
            else:
                # College hostels - always eligible
                eligible_hostels.append(hostel)
        
        return jsonify({
            "scholarships": {
                "total": len(eligible_scholarships),
                "items": eligible_scholarships
            },
            "hostels": {
                "total": len(eligible_hostels),
                "items": eligible_hostels
            }
        })
        
    except Exception as e:
        print(f"Smart Match Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
# ==============================================================================
# JEE COUNSELING MODULE ENDPOINTS
# ==============================================================================

@app.route('/api/jee/colleges', methods=['GET'])
def jee_colleges_list():
    from db_models import JeeCollege
    db = SessionLocal()
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        institute_type = request.args.get('institute_type', '').strip()
        state = request.args.get('state', '').strip()
        search = request.args.get('search', '').strip()
        
        query = db.query(JeeCollege)
        if institute_type:
            query = query.filter(JeeCollege.institute_type == institute_type)
        if state:
            query = query.filter(JeeCollege.state == state)
        if search:
            query = query.filter(JeeCollege.name.ilike(f'%{search}%'))
            
        total = query.count()
        colleges = query.offset((page - 1) * limit).limit(limit).all()
        
        result = []
        for c in colleges:
            result.append({
                "id": c.id,
                "name": c.name,
                "institute_type": c.institute_type,
                "location": c.location,
                "state": c.state,
                "fees": c.fees,
                "hostel": c.hostel,
                "placement_stats": c.placement_stats
            })
            
        return jsonify({
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "colleges": result
        })
    finally:
        db.close()

@app.route('/api/jee/college/<college_id>', methods=['GET'])
def jee_college_detail(college_id):
    from db_models import JeeCollege, JeeCutoff
    db = SessionLocal()
    try:
        college = db.query(JeeCollege).filter(JeeCollege.id == college_id).first()
        if not college:
            return jsonify({"success": False, "error": "College not found"}), 404
            
        cutoffs = db.query(JeeCutoff).filter(JeeCutoff.college_id == college_id).all()
        cutoff_list = []
        for c in cutoffs:
            cutoff_list.append({
                "branch": c.branch,
                "category": c.category,
                "quota": c.quota,
                "gender": c.gender,
                "opening_rank": c.opening_rank,
                "closing_rank": c.closing_rank,
                "year": c.year,
                "round": c.round
            })
            
        return jsonify({
            "success": True,
            "college": {
                "id": college.id,
                "name": college.name,
                "institute_type": college.institute_type,
                "location": college.location,
                "state": college.state,
                "fees": college.fees,
                "hostel": college.hostel,
                "placement_stats": college.placement_stats,
                "seat_matrix": college.seat_matrix
            },
            "cutoffs": cutoff_list
        })
    finally:
        db.close()

# NOTE: /api/jee/predict and /api/jee/compare are already defined above
# (jee_predict_endpoint and jee_compare_endpoint) — removed duplicates to prevent override

@app.route('/api/jee/statistics', methods=['GET'])
def jee_statistics_api():
    from db_models import JeeCollege, JeeCutoff
    db = SessionLocal()
    try:
        total_colleges = db.query(JeeCollege).count()
        types = db.query(JeeCollege.institute_type, func.count(JeeCollege.id)).group_by(JeeCollege.institute_type).all()
        type_counts = {t[0]: t[1] for t in types}
        return jsonify({
            "success": True,
            "total_colleges": total_colleges,
            "institute_types": type_counts
        })
    finally:
        db.close()

# ==============================================================================
# NEET COUNSELING MODULE ENDPOINTS
# ==============================================================================

@app.route('/api/neet/colleges', methods=['GET'])
def neet_colleges_list():
    from db_models import NeetCollege
    db = SessionLocal()
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        track_type = request.args.get('type', '').strip()
        state = request.args.get('state', '').strip()
        search = request.args.get('search', '').strip()
        
        query = db.query(NeetCollege)
        if track_type:
            query = query.filter(NeetCollege.type == track_type)
        if state:
            query = query.filter(NeetCollege.state == state)
        if search:
            query = query.filter(NeetCollege.name.ilike(f'%{search}%'))
            
        total = query.count()
        colleges = query.offset((page - 1) * limit).limit(limit).all()
        
        result = []
        for c in colleges:
            result.append({
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "state": c.state,
                "fees": c.fees,
                "hostel": c.hostel
            })
            
        return jsonify({
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "colleges": result
        })
    finally:
        db.close()

@app.route('/api/neet/college/<college_id>', methods=['GET'])
def neet_college_detail(college_id):
    from db_models import NeetCollege, NeetCutoff
    db = SessionLocal()
    try:
        college = db.query(NeetCollege).filter(NeetCollege.id == college_id).first()
        if not college:
            return jsonify({"success": False, "error": "College not found"}), 404
            
        cutoffs = db.query(NeetCutoff).filter(NeetCutoff.college_id == college_id).all()
        cutoff_list = []
        for c in cutoffs:
            cutoff_list.append({
                "course": c.course,
                "category": c.category,
                "quota": c.quota,
                "gender": c.gender,
                "opening_rank": c.opening_rank,
                "closing_rank": c.closing_rank,
                "year": c.year,
                "round": c.round
            })
            
        return jsonify({
            "success": True,
            "college": {
                "id": college.id,
                "name": college.name,
                "type": college.type,
                "state": college.state,
                "fees": college.fees,
                "hostel": college.hostel,
                "seat_matrix": college.seat_matrix
            },
            "cutoffs": cutoff_list
        })
    finally:
        db.close()

# NOTE: /api/neet/predict is already defined above (neet_predict_endpoint) — removed duplicate
# /api/neet/compare uses the unified compare endpoint

@app.route('/api/neet/statistics', methods=['GET'])
def neet_statistics_api():
    from db_models import NeetCollege
    db = SessionLocal()
    try:
        total_colleges = db.query(NeetCollege).count()
        types = db.query(NeetCollege.type, func.count(NeetCollege.id)).group_by(NeetCollege.type).all()
        type_counts = {t[0]: t[1] for t in types}
        return jsonify({
            "success": True,
            "total_colleges": total_colleges,
            "college_types": type_counts
        })
    finally:
        db.close()


# NOTE: /api/chat/stream is already defined above (chat_stream function at line 659)
# Removed duplicate that used different JSON keys ({content} vs {chunk}) which broke frontend


# ============================================================================
# AI STUDENT SUCCESS & COUNSELING RISK ANALYZER
# ============================================================================

@app.route("/api/analyze/risk", methods=["POST"])
def analyze_risk_endpoint():
    """
    AI Student Success & Counseling Risk Analyzer.
    Accepts full student profile and returns 11-dimensional risk analysis.
    """
    try:
        data = request.get_json(silent=True) or {}

        if not RISK_ANALYZER_AVAILABLE:
            return jsonify({"success": False, "error": "Risk Analyzer engine not available"}), 503

        # Run full analysis pipeline
        risk_analysis = analyze_risk(data)

        # Generate AI explanation
        ai_explanation = generate_ai_explanation(data, risk_analysis)

        # Save to database
        db_session = None
        try:
            db_session = SessionLocal()
            from db_models import StudentRiskProfile

            # Normalize inputs for DB
            interests = data.get("interests", "")
            if isinstance(interests, list):
                interests = ", ".join(interests)
            skills = data.get("skills", "")
            if isinstance(skills, list):
                skills = ", ".join(skills)
            preferred_branches = data.get("branch", "")

            income_raw = float(data.get("income", 0))
            income_lakhs = income_raw / 100000 if income_raw > 100 else income_raw

            risk_profile = StudentRiskProfile(
                exam=data.get("exam", "KCET"),
                rank=int(data.get("rank", 0)) if data.get("rank") else None,
                category=data.get("category", "GM"),
                income_lakhs=income_lakhs,
                interests=interests,
                career_goals=data.get("career_goals", ""),
                preferred_branches=preferred_branches,
                preferred_colleges=", ".join(data.get("preferred_colleges", [])) if isinstance(data.get("preferred_colleges"), list) else data.get("preferred_colleges", ""),
                success_score=risk_analysis["success_score"],
                academic_risk=risk_analysis["academic_risk"],
                financial_risk=risk_analysis["financial_risk"],
                placement_risk=risk_analysis["placement_risk"],
                regret_probability=risk_analysis["regret_probability"],
                branch_compatibility_score=risk_analysis["branch_compatibility_score"],
                roi_score=risk_analysis["roi_label"],
                ai_explanation=ai_explanation
            )
            db_session.add(risk_profile)
            db_session.commit()
        except Exception as db_err:
            print(f"[WARN] Could not save risk profile: {db_err}")
            if db_session:
                db_session.rollback()
        finally:
            if db_session:
                db_session.close()

        return jsonify({
            "success": True,
            "risk_analysis": risk_analysis,
            "ai_explanation": ai_explanation
        })

    except Exception as e:
        err_msg = traceback.format_exc()
        print(f"[ERROR] /api/analyze/risk: {err_msg}")
        return jsonify({"success": False, "error": "Risk analysis encountered an issue. Please try again."}), 500

# ============================================================================
# ADMIN DASHBOARD ENDPOINTS
# ============================================================================
import os
import sys
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'json', 'csv'}

# Import the existing KEA PDF parser from data_pipeline
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data_pipeline'))
    from pdf_parser import KEAPDFParser as PipelinePDFParser
    PDF_PARSER_AVAILABLE = True
except ImportError:
    PDF_PARSER_AVAILABLE = False
    print("[!] data_pipeline/pdf_parser.py not available for admin uploads")

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/admin/upload", methods=["POST"])
def admin_upload_endpoint():
    """
    Admin Upload Dashboard endpoint.
    Accepts files (PDF, JSON, CSV) and automatically processes them:
      - PDF  → KEA cutoff parsing + RAG vector ingestion
      - JSON → Merge into json_data_service college data
      - CSV  → Saved for manual review
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    processing_results = {"file": filename, "saved": True, "actions": []}
    ext = filename.rsplit('.', 1)[1].lower()

    # ── PDF Processing ────────────────────────────────────────────────────
    if ext == 'pdf':
        # 1) Structured cutoff parsing via existing data_pipeline parser
        if PDF_PARSER_AVAILABLE:
            try:
                parser = PipelinePDFParser()
                df = parser.parse_pdf(file_path)
                record_count = len(df) if not df.empty else 0
                processing_results["actions"].append({
                    "step": "kea_cutoff_parse",
                    "status": "success" if record_count > 0 else "no_data",
                    "records_extracted": record_count,
                })
            except Exception as e:
                processing_results["actions"].append({
                    "step": "kea_cutoff_parse",
                    "status": "error",
                    "detail": str(e),
                })
        else:
            processing_results["actions"].append({
                "step": "kea_cutoff_parse",
                "status": "skipped",
                "detail": "PDF parser module not available",
            })

        # 2) RAG vector ingestion for AI chat retrieval
        if AI_MODULES_AVAILABLE:
            try:
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
    elif ext == 'json':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
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
    elif ext == 'csv':
        processing_results["actions"].append({
            "step": "csv_saved",
            "status": "success",
            "detail": "CSV saved for review. Use /api/admin/apply-csv to import.",
        })

    return jsonify({
        "success": True,
        "message": f"File '{filename}' uploaded and processed.",
        "processing": processing_results,
    })

if __name__ == "__main__":
    print("\n" + "="*50)
    print("[*] Starting InsightRural AI Counselor API")
    print("="*50)
    
    # Initialize RAG engine if available
    if AI_MODULES_AVAILABLE:
        try:
            print("\n[*] Initializing RAG Engine...")
            rag_engine = get_rag_engine()
            results = rag_engine.index_all()
            print(f"[OK] Indexed: {results}")
        except Exception as e:
            print(f"[!] RAG initialization warning: {e}")
    
    print(f"\n[*] API available at: http://127.0.0.1:5000")
    print("\n[*] Available endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/colleges            - Get colleges with filters")
    print("  GET  /api/branches            - Get all branches")
    print("  GET  /api/locations           - Get all locations")
    print("  GET  /api/statistics          - Get statistics")
    print("  POST /api/chat                - AI chat endpoint")
    print("  POST /api/chat/stream         - Streaming AI chat")
    print("  POST /api/recommend/colleges  - College recommendations")
    print("  POST /api/recommend/scholarships - Scholarship recommendations")
    print("  GET  /api/ai/status           - AI system status")
    print("\n" + "="*50)
    
    print("  POST /api/predict/college     - ML College Prediction")
    print("  POST /api/documents/scan      - Smart Document Scanner")
    print("  POST /api/report/generate     - Generate PDF Report")
    print("  GET  /api/report/status       - PDF Generator Status")
    
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
