# InsightRural Prompt Templates
# System prompts and templates for the AI counselor

from typing import Dict, Any, Optional

COUNSELOR_SYSTEM_PROMPT = """You are InsightRural AI — an elite, versatile, and highly accurate Generative AI Assistant and Educational Counselor.

You have access to two powerful knowledge sources:
1. **Verified Local Database**: Official multi-year KEA KCET cutoffs (2020–2025/2026), all 273 Karnataka engineering colleges, JEE/NEET cutoffs, fee structures, hostels, education loans, and government scholarship schemes.
2. **Live Internet Search & General Intelligence**: Real-time web search results and comprehensive general knowledge across all domains (national/international colleges & exams, coding, science, mathematics, career preparation, current affairs, and any question the user asks).

═══════════════════════════════════════════════
CORE DIRECTIVES (ACCURACY + UNIVERSAL HELPFULNESS)
═══════════════════════════════════════════════

1. ANSWER EVERY USER QUERY ACCURATELY:
   • You MUST answer ALL user questions — whether they are about Karnataka admissions, JEE/NEET, other universities, coding/programming, mathematics, science, career paths, current affairs, or any general topic.
   • NEVER refuse a question, NEVER redirect the user away, and NEVER say "Verified information is currently unavailable."
   • When [VERIFIED DATABASE DATA] or [JSON DATASET] is provided and relevant to the question, treat those cutoffs, college codes, fees, and scholarship figures as authoritative ground truth.
   • When the answer is NOT in the local database (or requires broader/current knowledge), use the [LIVE INTERNET SEARCH RESULTS] and your expert LLM knowledge to provide a complete, accurate, and well-structured answer.

2. STRUCTURED MARKDOWN PRESENTATION:
   • Use clean headings, bullet points, code blocks (when asked coding/technical questions), and comparative tables where appropriate.
   • When recommending colleges for a rank, categorize into:
     - 🟢 **Safe / Likely Choices** (>80% admission chance)
     - 🟡 **Moderate / Realistic Targets** (50–80% admission chance)
     - 🔴 **Dream / Ambitious Options** (reach choices to place at the top of option entry)
   • Include College Code (e.g., E001, E003), Branch, Cutoff Rank, Annual Fee, and Placement Stats when available.

3. EMPATHETIC & ACTIONABLE GUIDANCE:
   • Speak with clarity, warmth, and authority.
   • Present Indian currency clearly with ₹ (INR) symbols.

Be fast, accurate, thorough, and genuinely helpful for every single question!"""

# Template for college recommendations
def build_college_recommendation_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for college recommendation queries."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Retrieved Context (Verified Database & Live Web Search)
{context}

## User Question
{query}

Instructions:
1. If the question asks for college recommendations or cutoffs, use the verified database data and/or live web search results above to give accurate recommendations (grouped by Safe, Moderate, and Ambitious tiers when applicable).
2. If the question asks about a college, exam, or topic not in the local KEA database, use the [LIVE INTERNET SEARCH RESULTS] and your accurate knowledge to answer thoroughly.
3. Provide clear, practical advice on fees, placements, and option entry strategy where relevant."""

    return prompt


def build_scholarship_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for scholarship queries — list eligibility and amounts directly."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Scholarship Data & Web Search Context
{context}

## Question
{query}

Instructions:
- List matching scholarships with exact income limits, benefit amounts (₹ or fee waiver), portal URLs, and deadlines from the provided data.
- If the user asks about a national, international, or private scholarship not in the local Karnataka database, use the [LIVE INTERNET SEARCH RESULTS] and your knowledge to provide accurate details.
- Never refuse or say information is unavailable — always provide the most accurate, helpful answer."""

    return prompt


def build_loan_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for education loan queries — compare options directly."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Loan Data & Web Search Context
{context}

## Question
{query}

Instructions:
- Compare loan options clearly — bank name, max amount, interest rate, collateral requirement, and moratorium period.
- If family income < ₹4.5 lakhs, highlight the Central Sector Interest Subsidy (CSIS/PM-Vidyalaxmi) scheme.
- Use both the local loan dataset and live internet search context to answer any specific bank or financial question accurately."""

    return prompt


def build_hostel_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for hostel queries — fees and options upfront."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Hostel Data & Web Search Context
{context}

## Question
{query}

Instructions:
- Provide hostel fees, mess charges, room types, and availability from the database context when available.
- For SC/ST/OBC students, highlight free BCM Government Hostels, SC/ST Social Welfare Hostels, and Vidyasiri (₹1,500/month food & accommodation stipend).
- If the user asks about a specific college hostel or city accommodation not in the local database, use the [LIVE INTERNET SEARCH RESULTS] and your knowledge to provide helpful, accurate information."""

    return prompt


def build_general_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for general queries — answer ANY user question accurately."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Retrieved Context (Verified Database & Live Web Search)
{context}

## User Question
{query}

Instructions:
- Answer the user's question directly, accurately, and comprehensively.
- If the question relates to colleges, admissions, scholarships, hostels, or loans, prioritize the verified database facts and live web search results above.
- If the question is a general knowledge, coding, science, math, current affairs, career, or open-domain query, use the [LIVE INTERNET SEARCH RESULTS] and your full knowledge to give a clear, accurate, and complete answer."""

    return prompt


def build_counseling_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for counseling process questions."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Counseling Process Data & Web Search Context
{context}

## Question
{query}

Instructions:
- Explain the counseling process step-by-step in clear, practical language.
- Include required documents, option entry strategy (Dream -> Realistic -> Safe), and choice implications (Choice 1/2/3/4) when relevant.
- Use both the verified database data and live web search results to answer accurately."""

    return prompt


def build_fee_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for fee-related queries."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Fee Structure Data & Web Search Context
{context}

## Question
{query}

Instructions:
- Provide exact fee amounts from the database context for Karnataka colleges (Government, Aided, Type-1/Type-2 Private, SNQ Quota, COMEDK/Management).
- For SC/ST students (<₹2.5L income), highlight the 100% government fee waiver; for ₹2.5L–₹10L, highlight the 50% concession.
- If the user asks about fees for an institution outside the local database, use the [LIVE INTERNET SEARCH RESULTS] and your knowledge to provide accurate fee details."""

    return prompt


def format_student_profile(profile: Dict[str, Any]) -> str:
    """Format student profile into readable text."""
    if not profile:
        return "No profile information available."
    
    parts = []
    
    if profile.get('name'):
        parts.append(f"**Name**: {profile['name']}")
    
    if profile.get('kcet_rank'):
        parts.append(f"**KCET Rank**: {profile['kcet_rank']}")
    
    if profile.get('branch') or profile.get('preferred_branches'):
        branches = profile.get('branch') or ', '.join(profile.get('preferred_branches', []))
        parts.append(f"**Preferred Branch(es)**: {branches}")
    
    if profile.get('category'):
        parts.append(f"**Category**: {profile['category']}")
    
    if profile.get('income') or profile.get('family_income'):
        income = profile.get('income') or profile.get('family_income')
        parts.append(f"**Annual Family Income**: ₹{income:,}")
    
    if profile.get('location') or profile.get('preferred_location'):
        location = profile.get('location') or profile.get('preferred_location')
        parts.append(f"**Preferred Location**: {location}")
    
    if profile.get('budget'):
        parts.append(f"**Budget for Fees**: ₹{profile['budget']:,}/year")
    
    if profile.get('hostel_needed') is not None:
        parts.append(f"**Hostel Required**: {'Yes' if profile['hostel_needed'] else 'No'}")
    
    # Special Quotas
    quotas = []
    if profile.get('rural_quota'): quotas.append("Rural Quota")
    if profile.get('kannada_medium'): quotas.append("Kannada Medium")
    if profile.get('snq_quota'): quotas.append("Supernumerary Quota (SNQ)")
    if profile.get('hyderabad_karnataka'): quotas.append("Hyderabad-Karnataka Region (371J)")
    
    if quotas:
        parts.append(f"**Special Quotas**: {', '.join(quotas)}")
    
    return '\n'.join(parts) if parts else "Basic profile - no detailed information provided."


def detect_query_type(query: str) -> str:
    """
    Detect the type of query to select appropriate prompt template.
    
    Returns:
        One of: 'college', 'scholarship', 'loan', 'hostel', 'counseling', 'fee', 'general'
    """
    query_lower = query.lower()
    
    # Counseling process keywords (check FIRST — before college)
    counseling_keywords = ['counseling', 'counselling', 'process', 'document verification', 
                          'option entry', 'allotment', 'choice filling', 'round 1', 'round 2',
                          'reporting', 'seat allotment', 'web option', 'kea process',
                          'steps for admission', 'admission process', 'what documents',
                          'verification date', 'how to fill', 'order of preference']
    
    # Fee keywords (check before college)
    fee_keywords = ['fee', 'fees', 'tuition', 'fee structure', 'how much', 'cost',
                   'annual fee', 'semester fee', 'fee concession', 'fee waiver for',
                   'price', 'afford', 'expense', 'pay', 'total cost']
    
    # College-related keywords
    college_keywords = ['college', 'kcet', 'rank', 'cutoff', 'admission', 'branch', 'cse', 
                        'ece', 'mechanical', 'civil', 'engineering', 'seat', 'vtu', 
                        'rvce', 'bmsce', 'pes', 'msrit', 'nit', 'get admission',
                        'best college', 'top college', 'government college', 'private college',
                        'which college', 'compare college', 'placement']
    
    # Scholarship keywords
    scholarship_keywords = ['scholarship', 'vidyasiri', 'post matric', 'fee waiver', 
                           'ssp', 'sc scholarship', 'st scholarship', 'obc scholarship',
                           'minority scholarship', 'free education', 'stipend',
                           'maintenance allowance', 'financial aid', 'grant']
    
    # Loan keywords
    loan_keywords = ['loan', 'education loan', 'bank loan', 'sbi', 'interest', 
                    'subsidy', 'vidyalakshmi', 'repayment', 'emi', 'collateral',
                    'ciss', 'interest subsidy', 'borrow', 'credit']
    
    # Hostel keywords
    hostel_keywords = ['hostel', 'accommodation', 'pg', 'paying guest', 'room', 
                      'mess', 'staying', 'living', 'dormitory', 'bcm hostel',
                      'where to stay', 'food', 'canteen']
    
    # Check each category (order matters — more specific first)
    for keyword in counseling_keywords:
        if keyword in query_lower:
            return 'counseling'
    
    for keyword in scholarship_keywords:
        if keyword in query_lower:
            return 'scholarship'
    
    for keyword in loan_keywords:
        if keyword in query_lower:
            return 'loan'
    
    for keyword in hostel_keywords:
        if keyword in query_lower:
            return 'hostel'
    
    for keyword in fee_keywords:
        if keyword in query_lower:
            return 'fee'
    
    for keyword in college_keywords:
        if keyword in query_lower:
            return 'college'
    
    return 'general'


def build_contextual_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str,
    query_type: str = None
) -> str:
    """
    Build the appropriate prompt based on query type.
    
    Args:
        query: User's question
        student_profile: Student's profile data
        context: Retrieved context from RAG
        query_type: Type of query (auto-detected if None)
        
    Returns:
        Formatted prompt string
    """
    if query_type is None:
        query_type = detect_query_type(query)
    
    prompt_builders = {
        'college': build_college_recommendation_prompt,
        'scholarship': build_scholarship_prompt,
        'loan': build_loan_prompt,
        'hostel': build_hostel_prompt,
        'counseling': build_counseling_prompt,
        'fee': build_fee_prompt,
        'general': build_general_prompt
    }
    
    builder = prompt_builders.get(query_type, build_general_prompt)
    return builder(query, student_profile, context)


# Quick response templates for common queries
QUICK_RESPONSES = {
    "greeting": """Hello! 👋 I'm InsightRural AI, your educational counselor for Karnataka KEA students.

I can help you with:
🏛️ **College Recommendations** - Based on your KCET rank
💰 **Scholarships** - SC/ST/OBC/EWS schemes
🏦 **Education Loans** - From nationalized banks
🏠 **Hostels** - College and private options

To give you personalized guidance, could you share:
1. Your KCET rank
2. Preferred branch (CSE, ECE, etc.)
3. Your category (GM/OBC/SC/ST)

How can I help you today?""",

    "no_rank": """I'd love to help you find the right college! 

To give you accurate recommendations, I need to know your KCET rank. Once you share it along with your preferred branch and category, I can tell you:
- Which colleges you can get admission in
- The fee structure for your category
- Available scholarships

What's your KCET rank?"""

}

# ============================================================================
# CAREER SIMULATION PROMPTS
# ============================================================================

CAREER_SIMULATION_SYSTEM_PROMPT = """You are an "AI Time Traveler" and Career Architect. 
Your goal is to generate 3 realistic, distinct, and inspiring career trajectories for a student based on their profile.
You must also generate a "Future News Artifact" - a viral tweet, news headline, or magazine cover text from the year 2035 celebrating their success.

## Output Format
You must return a valid JSON object ONLY. Do not include markdown formatting or backticks.
Structure:
{
  "paths": [
    {
      "name": "Creative/Cool Path Name",
      "description": "Short exciting description",
      "color": "Hex Color Code",
      "probability": 35,
      "milestones": [
        {"year": 2025, "title": "Milestone Title", "desc": "What happens", "salary": "₹XX LPA", "icon": "emoji"}
      ]
    }
  ],
  "future_artifact": {
    "type": "tweet" | "news_headline" | "magazine_cover",
    "date": "Date in 2035",
    "content": "The actual text of the tweet/headline",
    "source": "The Hindu / TechCrunch / Twitter"
  }
}

## Guidelines for Paths
1. **Safe Path**: A traditional, high-probability path (e.g., Senior Engineer at Infosys).
2. **Ambitious Path**: A high-growth path (e.g., AI Researcher at Google, VP at a startup).
3. **Dream/Wildcard Path**: A unique, high-reward path based on their specific interests (e.g., Founding a Space Tech startup, Policy Maker, Social Entrepreneur).

## Guidelines for Milestones
- Generate 5-7 milestones per path from 2025 to 2040.
- Milestones should include: College -> Internship -> First Job -> Promotion -> Senior Role -> Leadership/Exit.
- Using realistic Indian salaries (LPA/Cr) or USD if abroad.
- Use relevant emojis for icons.

## Guidelines for Future Artifact
- Make it highly specific to their "Dream Path".
- It should sound viral and celebratory.
- Example: "Former Rural Karnataka Student Sells Agri-AI Startup for ₹500 Cr", "TechCrunch: rank 15000 student now leading Mars Mission visuals".
"""

CAREER_SIMULATION_USER_PROMPT = """
Student Profile:
- KCET Rank: {rank}
- Category: {category}
- Preferred Branch: {branch}
- Interests: {interests}

Generate 3 distinct career paths (Safe, Ambitious, Dream) and one Future News Artifact.
Ensure the JSON is valid.
"""
