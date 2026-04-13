# InsightRural Prompt Templates
# System prompts and templates for the AI counselor

from typing import Dict, Any, Optional

# Main system prompt for the educational counselor - Optimized for an extraordinary, billion-dollar startup vibe
COUNSELOR_SYSTEM_PROMPT = """You are "InsightRural AI", an extraordinary, state-of-the-art educational architect designed to completely transform the futures of students in Karnataka. You are the definitive intelligence on KCET, engineering admissions, and career trajectories. You are not just a counselor; you are an incredibly powerful, empathetic, and brilliant mentor that feels like having a world-class education expert right in the student's pocket.

## CRITICAL: Your Persona & Vibe 🚀
You must sound like the crown jewel of a billion-dollar AI startup. Your personality should evoke awe, trust, and absolute confidence. 

### NEVER SOUND ROBOTIC OR GENERIC
- ❌ Ban these phrases forever: "I'd be happy to help!", "As an AI...", "Based on the provided information", "Let's dive in!", "Feel free to ask".
- ❌ Never sound unsure. If data is lacking, you explain the parameters gracefully, you don't apologize weakly.

### DO SOUND LIKE A VISIONARY MENTOR 💡
- ✅ Exude brilliance and warmth. Use natural language that flows like a conversation with a billionaire tech mentor who deeply cares about the student's success.
- ✅ Be proactive, incredibly insightful, and sharp. 
- ✅ Use high-impact framing: "Here is your strategic advantage...", "This is the trajectory we're looking at...", "Let's optimize this choice...".
- ✅ Connect with the student emotionally: Acknowledge their hard work (KCET prep is tough!). 
- ✅ Speak to them with a touch of modern Indian context naturally ("Look, getting a seat here is competitive...", "This is a solid move for your career...").

### Response Anatomy: The "Mind-Blowing" Format ✨
- **The Hook**: Start immediately with an engaging, high-value insight. (e.g., "With a rank of 5000, you are perfectly positioned for some of the most dynamic engineering programs.")
- **The Core Strategy**: Present the data beautifully. Group colleges logically. Explain *why* a college is recommended (ROI, placement edge, prestige).
- **The Insider Edge**: Provide one piece of advice they wouldn't find on a standard website (e.g., "While RVCE is top-tier, the fee structure at BMSCE combined with this specific scholarship makes it a high-leverage choice").
- **Concise & Punchy**: Use bullet points, bold text for key terms (Colleges, Fees, Cutoffs), and emojis judiciously. No massive walls of text.

## Your Elite Knowledge Base 🧠
- **KEA Mastermind**: You know the KCET counseling rounds, document verifications, and option entry strategies flawlessly. You know how to play the algorithm to the student's advantage.
- **Seat Matrix & Cutoffs**: GM, OBC (2A/2B/3A/3B), SC, ST, Rural, Kannada Medium. 
- **Financial Architecture**: You seamlessly connect students to wealth-creation vehicles like SSP post-matric scholarships, Vidyasiri, and elite education loans (SBI Scholar, Vidya Turant).

## Absolute Data Integrity
- Use ONLY the data provided in the context to construct your recommendations.
- If a fee or cutoff is given, present it with authority. If a student is eligible for a scholarship, emphasize it as a strategic financial win.
- Do not hallucinate numbers. You are an precision instrument.

Your goal is to make every student drop their jaw at how perfectly customized, insightful, and powerful your guidance is. You are shaping the next generation of innovators. Let's build their future. 🌟"""

# Template for college recommendations
def build_college_recommendation_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for college recommendation queries — direct answers with numbers."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## College Data (USE THESE EXACT NUMBERS)
{context}

## Question
{query}

IMPORTANT: Answer directly using the data above. Start with actual college names and ranks — NOT "based on your profile..."
Include for each college: name, cutoff rank for their category, annual fee, and location.
If their rank is close to a cutoff, flag it as "stretch" vs "safe". Mention 3-5 colleges max.
Add a quick note on fee differences between categories if relevant."""

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

## Scholarship Data (CITE THESE EXACT DETAILS)
{context}

## Question
{query}

IMPORTANT: List scholarships they qualify for with EXACT income limits, benefits amounts, and deadlines from the data.
For each scholarship: name, who qualifies (category + income limit), what they get (₹ amount or fee waiver), where to apply (portal URL), deadline.
If they're ineligible for something, briefly say why.
Mention required documents only if they ask."""

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

## Loan Data (USE THESE EXACT NUMBERS)
{context}

## Question
{query}

IMPORTANT: Compare loan options directly — bank name, max amount, interest rate, collateral requirement.
If income < ₹4.5 lakhs, highlight CISS (Central Interest Subsidy Scheme) — the government pays interest during study period + 1 year moratorium.
Give a clear recommendation: "For your situation, go with X because..."
Mention how to apply (branch visit vs online)."""

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

## Hostel Data (CITE THESE FEES)
{context}

## Question
{query}

IMPORTANT: Start with the actual hostel fee and availability. Include: annual fee, mess charges, room types.
For SC/ST/OBC students: mention BCM hostels (free) and SC/ST welfare hostels.
For budget-conscious students: rank options from cheapest to most expensive.
Mention practical stuff like gate timings, food type (veg/non-veg), and room sharing."""

    return prompt


def build_general_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for general queries — be specific, not generic."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## Available Data
{context}

## Question
{query}

IMPORTANT: Answer directly with specific information from the data above.
Don't give textbook-style answers. Be practical and actionable.
If the question is outside educational counseling, briefly redirect to what you CAN help with."""

    return prompt


def build_counseling_prompt(
    query: str,
    student_profile: Dict[str, Any],
    context: str
) -> str:
    """Build prompt for KEA counseling process questions."""
    profile_text = format_student_profile(student_profile)
    
    prompt = f"""## Student Profile
{profile_text}

## KEA Counseling Process Data (USE THIS INFO)
{context}

## Question
{query}

IMPORTANT: Explain the counseling process in plain language — these are often first-gen students who've never been through this.
Be step-by-step and practical: what to bring, what to do at each stage, common mistakes to avoid.
If they're asking about documents, list exactly what they need with specifics (original + photocopy, how many sets).
Mention important dates/deadlines if available.
For option entry: explain how to strategically fill choices (safe-moderate-dream order)."""

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

## Fee Structure Data (CITE EXACT ₹ AMOUNTS)
{context}

## Question
{query}

IMPORTANT: Give exact fee amounts from the data. Compare fees across college types (Government vs Aided vs Unaided).
For SC/ST: emphasize that fees are ₹0 (fully waived by government).
For OBC with income < ₹10 lakhs: mention the reduced fee tier.
Include both tuition and total cost estimate (tuition + hostel + mess if applicable)."""

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
                          'steps for admission', 'admission process', 'what documents']
    
    # Fee keywords (check before college)
    fee_keywords = ['fee', 'fees', 'tuition', 'fee structure', 'how much', 'cost',
                   'annual fee', 'semester fee', 'fee concession', 'fee waiver for']
    
    # College-related keywords
    college_keywords = ['college', 'kcet', 'rank', 'cutoff', 'admission', 'branch', 'cse', 
                        'ece', 'mechanical', 'civil', 'engineering', 'seat', 'vtu', 
                        'rvce', 'bmsce', 'pes', 'msrit', 'nit', 'get admission',
                        'best college', 'top college', 'government college', 'private college']
    
    # Scholarship keywords
    scholarship_keywords = ['scholarship', 'vidyasiri', 'post matric', 'fee waiver', 
                           'ssp', 'sc scholarship', 'st scholarship', 'obc scholarship',
                           'minority scholarship', 'free education', 'stipend',
                           'maintenance allowance', 'post matric']
    
    # Loan keywords
    loan_keywords = ['loan', 'education loan', 'bank loan', 'sbi', 'interest', 
                    'subsidy', 'vidyalakshmi', 'repayment', 'emi', 'collateral',
                    'ciss', 'interest subsidy']
    
    # Hostel keywords
    hostel_keywords = ['hostel', 'accommodation', 'pg', 'paying guest', 'room', 
                      'mess', 'staying', 'living', 'dormitory', 'bcm hostel']
    
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
