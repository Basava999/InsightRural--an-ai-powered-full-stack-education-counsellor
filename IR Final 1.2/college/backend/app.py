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
from models import College, FeeStructure

# AI modules for chat functionality
try:
    from rag_engine import get_rag_engine, RAGEngine
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

# Trigger Reload: Updated at 2026-01-29 - Counseling Suite v2
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
        
    except Exception as e:
        print(f"âŒ ERROR in get_colleges: {str(e)}")
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

# Store for student profiles (in production, use database)
student_profiles = {}

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
        profile      = data.get("profile", {})
        session_id   = data.get("session_id", "default")
        chat_history = data.get("history", [])

        if not user_message:
            return jsonify({"response": "Please enter a message.", "error": True}), 400

        # Persist student profile for session
        if profile:
            student_profiles[session_id] = profile
        else:
            profile = student_profiles.get(session_id, {})

        orchestrator = get_llm_service()
        response = orchestrator.generate_response(
            query=user_message,
            chat_history=chat_history[-12:],
            session_id=session_id,
            session_profile=profile if profile else None,
        )

        return jsonify({"response": response, "session_id": session_id})

    except Exception as e:
        print(f"[ERROR] /api/chat: {e}")
        import traceback; print(traceback.format_exc())
        return jsonify({"response": "Sorry, something went wrong. Please try again.", "error": True}), 500


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
    profile      = data.get("profile", {})
    session_id   = data.get("session_id", "default")
    chat_history = data.get("history", [])

    if profile:
        student_profiles[session_id] = profile
    else:
        profile = student_profiles.get(session_id, {})

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

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
    """
    try:
        data = request.json
        rank = int(data.get("kcet_rank", 0))
        branch = data.get("branch", "CSE")
        category = data.get("category", "GM")
        
        if rank <= 0:
            return jsonify({"error": "Please provide a valid KCET rank"}), 400
        
        if AI_MODULES_AVAILABLE:
            rag_engine = get_rag_engine()
            colleges = rag_engine.get_colleges_by_rank(rank, branch, category)
        else:
            # Fallback to JSON file
            import os
            data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'kea_colleges_complete.json')
            with open(data_file, 'r', encoding='utf-8') as f:
                all_colleges = json.load(f)
            
            colleges = []
            for college in all_colleges:
                cutoffs = college.get('cutoff_2024', {})
                branch_cutoff = cutoffs.get(branch, {})
                if isinstance(branch_cutoff, dict):
                    cat_cutoff = branch_cutoff.get(category, branch_cutoff.get('GM', float('inf')))
                    if rank <= cat_cutoff:
                        colleges.append({
                            "college": college['name'],
                            "location": college['location'],
                            "type": college['type'],
                            "cutoff": cat_cutoff,
                            "fee": college.get('annual_fee', {}),
                            "branch": branch
                        })
            colleges.sort(key=lambda x: x['cutoff'])
        
        return jsonify({
            "rank": rank,
            "branch": branch,
            "category": category,
            "total_matches": len(colleges),
            "colleges": colleges[:20]  # Top 20
        })
        
    except Exception as e:
        print(f"âŒ ERROR in recommend_colleges: {str(e)}")
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
        
        if AI_MODULES_AVAILABLE:
            rag_engine = get_rag_engine()
            scholarships = rag_engine.get_eligible_scholarships(category, income)
        else:
            # Fallback to JSON file
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
                    if category_lower in ['sc', 'st'] and (category_lower in str(sch_categories) or 'sc' in str(sch_categories)):
                        scholarships.append(sch)
                    elif 'obc' in category_lower and 'category' in str(sch_categories):
                        scholarships.append(sch)
        
        return jsonify({
            "category": category,
            "income": income,
            "total_matches": len(scholarships),
            "scholarships": scholarships
        })
        
    except Exception as e:
        print(f"âŒ ERROR in recommend_scholarships: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile", methods=["POST", "GET"])
def manage_profile():
    """Store or retrieve student profile."""
    session_id = request.args.get("session_id", "default")
    
    if request.method == "POST":
        profile = request.json
        student_profiles[session_id] = profile
        return jsonify({"status": "saved", "profile": profile})
    else:
        profile = student_profiles.get(session_id, {})
        return jsonify(profile)


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
        
        # Make prediction
        result = predictor.predict(
            kcet_rank=int(data['kcet_rank']),
            category=data['category'].upper(),
            preferred_branches=data.get('preferred_branches', ['CSE', 'ECE', 'ISE']),
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

@app.route('/api/simulate-career', methods=['POST'])
def simulate_career():
    """
    Generative AI Career Simulator.
    Accepts: { "rank": 5000, "category": "2A", "branch": "CSE", "interests": "Robotics, AI" }
    Returns: JSON with 3 career paths + Future Artifact
    """
    if not AI_MODULES_AVAILABLE:
        return jsonify({"error": "AI modules not available"}), 503
        
    data = request.json
    rank = data.get('rank')
    category = data.get('category')
    branch = data.get('branch')
    interests = data.get('interests', 'Technology, Engineering')
    
    if not all([rank, category, branch]):
        return jsonify({"error": "Missing required fields"}), 400
        
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
                "success": False,
                "error": "Failed to generate valid simulation data. Please try again."
            }), 500
            
    except Exception as e:
        print(f"[ERROR] in simulate_career: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


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
            except:
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
            except:
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
        income = int(data.get("income", 500000))
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
    
    app.run(host="127.0.0.1", port=5000, debug=True)
