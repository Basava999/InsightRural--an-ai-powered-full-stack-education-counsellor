"""
AI Career Counselor Engine
Matches student interests and aptitudes to engineering branches
"""

import json
from typing import Dict, List, Optional

class CareerEngine:
    """Matches student aptitudes to engineering branches and careers."""
    
    # Career profiles with associated traits
    CAREER_PROFILES = {
        "CSE": {
            "name": "Computer Science & Engineering",
            "traits": ["problem_solving", "technology", "logic", "creativity", "independent"],
            "interests": ["coding", "computers", "gaming", "apps", "internet"],
            "careers": ["Software Engineer", "Data Scientist", "AI/ML Engineer", "Web Developer", "Product Manager"],
            "avg_salary": "8-25 LPA",
            "growth": "Very High",
            "description": "Build software, apps, and AI systems that power the modern world"
        },
        "ISE": {
            "name": "Information Science & Engineering",
            "traits": ["analytical", "technology", "data", "systematic", "communication"],
            "interests": ["data", "systems", "organizing", "technology", "business"],
            "careers": ["System Analyst", "Database Admin", "IT Consultant", "Business Analyst"],
            "avg_salary": "7-20 LPA",
            "growth": "High"
        },
        "ECE": {
            "name": "Electronics & Communication",
            "traits": ["technical", "hardware", "physics", "analytical", "innovative"],
            "interests": ["electronics", "circuits", "mobile", "telecom", "signals"],
            "careers": ["Hardware Engineer", "VLSI Designer", "Telecom Engineer", "Embedded Systems"],
            "avg_salary": "6-18 LPA",
            "growth": "High"
        },
        "EEE": {
            "name": "Electrical & Electronics",
            "traits": ["physics", "power", "systematic", "practical", "safety"],
            "interests": ["electricity", "power", "motors", "renewable", "grids"],
            "careers": ["Power Engineer", "Control Systems", "Electrical Designer", "Energy Consultant"],
            "avg_salary": "6-15 LPA",
            "growth": "Moderate"
        },
        "MECH": {
            "name": "Mechanical Engineering",
            "traits": ["practical", "physics", "design", "hands_on", "systematic"],
            "interests": ["machines", "automotive", "manufacturing", "design", "physics"],
            "careers": ["Design Engineer", "Production Manager", "Automotive Engineer", "R&D Engineer"],
            "avg_salary": "5-15 LPA",
            "growth": "Moderate"
        },
        "CIVIL": {
            "name": "Civil Engineering",
            "traits": ["planning", "spatial", "environment", "leadership", "practical"],
            "interests": ["buildings", "construction", "infrastructure", "environment", "planning"],
            "careers": ["Structural Engineer", "Construction Manager", "Town Planner", "Site Engineer"],
            "avg_salary": "4-12 LPA",
            "growth": "Moderate"
        },
        "AIML": {
            "name": "AI & Machine Learning",
            "traits": ["math", "problem_solving", "research", "creativity", "analytical"],
            "interests": ["ai", "math", "research", "automation", "future"],
            "careers": ["ML Engineer", "AI Researcher", "NLP Engineer", "Computer Vision Engineer"],
            "avg_salary": "10-30 LPA",
            "growth": "Very High"
        },
        "DS": {
            "name": "Data Science",
            "traits": ["math", "analytical", "business", "communication", "curiosity"],
            "interests": ["statistics", "patterns", "data", "insights", "business"],
            "careers": ["Data Scientist", "Data Analyst", "Business Intelligence", "Analytics Manager"],
            "avg_salary": "8-25 LPA",
            "growth": "Very High"
        },
        "BIOTECH": {
            "name": "Biotechnology",
            "traits": ["biology", "research", "chemistry", "patience", "detail"],
            "interests": ["biology", "medicine", "research", "environment", "genetics"],
            "careers": ["Biotech Researcher", "Pharma Scientist", "Quality Analyst", "Research Associate"],
            "avg_salary": "4-12 LPA",
            "growth": "Moderate"
        },
        "CHEM": {
            "name": "Chemical Engineering",
            "traits": ["chemistry", "process", "analytical", "safety", "systematic"],
            "interests": ["chemistry", "processes", "manufacturing", "environment", "pharma"],
            "careers": ["Process Engineer", "Pharma Engineer", "Chemical Analyst", "Safety Engineer"],
            "avg_salary": "5-14 LPA",
            "growth": "Moderate"
        }
    }
    
    # Assessment questions
    ASSESSMENT_QUESTIONS = [
        {
            "id": 1,
            "question": "What do you enjoy doing in your free time?",
            "options": [
                {"text": "Coding or using computers", "traits": ["technology", "logic"], "branches": ["CSE", "ISE", "AIML"]},
                {"text": "Building or fixing things", "traits": ["practical", "hands_on"], "branches": ["MECH", "ECE", "EEE"]},
                {"text": "Reading about science/nature", "traits": ["research", "curiosity"], "branches": ["BIOTECH", "CHEM"]},
                {"text": "Planning and organizing", "traits": ["planning", "systematic"], "branches": ["CIVIL", "ISE"]}
            ]
        },
        {
            "id": 2,
            "question": "Which subject do you find most interesting?",
            "options": [
                {"text": "Mathematics & Logic", "traits": ["math", "logic"], "branches": ["CSE", "AIML", "DS"]},
                {"text": "Physics & Mechanics", "traits": ["physics", "practical"], "branches": ["MECH", "ECE", "EEE"]},
                {"text": "Chemistry & Biology", "traits": ["chemistry", "biology"], "branches": ["BIOTECH", "CHEM"]},
                {"text": "Design & Creativity", "traits": ["creativity", "design"], "branches": ["CIVIL", "MECH"]}
            ]
        },
        {
            "id": 3,
            "question": "How do you prefer to work?",
            "options": [
                {"text": "Independently on a computer", "traits": ["independent", "technology"], "branches": ["CSE", "ISE", "DS"]},
                {"text": "In a team building things", "traits": ["teamwork", "practical"], "branches": ["MECH", "CIVIL", "ECE"]},
                {"text": "Research and experimentation", "traits": ["research", "analytical"], "branches": ["BIOTECH", "AIML", "CHEM"]},
                {"text": "Mix of desk and field work", "traits": ["versatile"], "branches": ["EEE", "CIVIL"]}
            ]
        },
        {
            "id": 4,
            "question": "What kind of problems do you like solving?",
            "options": [
                {"text": "Puzzles and logical challenges", "traits": ["problem_solving", "logic"], "branches": ["CSE", "AIML", "DS"]},
                {"text": "How things work/break", "traits": ["practical", "analytical"], "branches": ["MECH", "ECE", "EEE"]},
                {"text": "Environmental/health issues", "traits": ["environment", "biology"], "branches": ["BIOTECH", "CHEM", "CIVIL"]},
                {"text": "Data and patterns", "traits": ["data", "analytical"], "branches": ["DS", "ISE"]}
            ]
        },
        {
            "id": 5,
            "question": "What's most important to you in a career?",
            "options": [
                {"text": "High salary and growth", "traits": ["ambitious"], "branches": ["CSE", "AIML", "DS"]},
                {"text": "Stability and job security", "traits": ["security"], "branches": ["EEE", "CIVIL", "MECH"]},
                {"text": "Making a difference", "traits": ["purpose"], "branches": ["BIOTECH", "CIVIL", "CHEM"]},
                {"text": "Innovation and creativity", "traits": ["creativity", "innovative"], "branches": ["CSE", "AIML", "ECE"]}
            ]
        }
    ]
    
    def __init__(self):
        self.user_responses = []
        self.trait_scores = {}
        self.branch_scores = {}
    
    def get_questions(self) -> List[Dict]:
        """Return assessment questions."""
        return self.ASSESSMENT_QUESTIONS
    
    def process_responses(self, responses: List[Dict]) -> Dict:
        """
        Process user responses and calculate career matches.
        
        Args:
            responses: List of {question_id, option_index}
            
        Returns:
            Career recommendation with matches
        """
        self.user_responses = responses
        self.trait_scores = {}
        self.branch_scores = {}
        
        # Calculate scores from responses
        for response in responses:
            q_id = response.get('question_id')
            opt_idx = response.get('option_index', 0)
            
            question = next((q for q in self.ASSESSMENT_QUESTIONS if q['id'] == q_id), None)
            if not question or opt_idx >= len(question['options']):
                continue
                
            option = question['options'][opt_idx]
            
            # Add trait scores
            for trait in option.get('traits', []):
                self.trait_scores[trait] = self.trait_scores.get(trait, 0) + 1
            
            # Add branch scores
            for branch in option.get('branches', []):
                self.branch_scores[branch] = self.branch_scores.get(branch, 0) + 2
        
        # Calculate final matches
        matches = self._calculate_matches()
        
        return {
            "success": True,
            "top_matches": matches[:3],
            "all_matches": matches,
            "dominant_traits": self._get_dominant_traits(),
            "personality_summary": self._generate_summary()
        }
    
    def _calculate_matches(self) -> List[Dict]:
        """Calculate branch match percentages."""
        matches = []
        max_score = len(self.ASSESSMENT_QUESTIONS) * 2  # Max possible score per branch
        
        for branch_code, profile in self.CAREER_PROFILES.items():
            score = self.branch_scores.get(branch_code, 0)
            
            # Add trait-based bonus
            trait_bonus = 0
            for trait in profile.get('traits', []):
                if trait in self.trait_scores:
                    trait_bonus += 0.5
            
            total_score = score + trait_bonus
            match_percent = min(100, int((total_score / max_score) * 100) + 20)  # Base 20%
            
            matches.append({
                "branch": branch_code,
                "name": profile["name"],
                "match_percent": match_percent,
                "careers": profile.get("careers", [])[:3],
                "avg_salary": profile.get("avg_salary", "Varies"),
                "growth": profile.get("growth", "Moderate"),
                "description": profile.get("description", "")
            })
        
        # Sort by match percentage
        matches.sort(key=lambda x: x['match_percent'], reverse=True)
        
        return matches
    
    def _get_dominant_traits(self) -> List[str]:
        """Get top 5 dominant traits."""
        sorted_traits = sorted(self.trait_scores.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_traits[:5]]
    
    def _generate_summary(self) -> str:
        """Generate personality summary."""
        traits = self._get_dominant_traits()
        
        if not traits:
            return "Complete the assessment to discover your ideal career path!"
        
        trait_descriptions = {
            "technology": "tech-savvy",
            "logic": "logical thinker",
            "problem_solving": "problem solver",
            "creativity": "creative",
            "practical": "hands-on learner",
            "analytical": "analytical mind",
            "math": "mathematically inclined",
            "research": "research-oriented",
            "physics": "physics enthusiast",
            "data": "data-driven"
        }
        
        desc_traits = [trait_descriptions.get(t, t) for t in traits[:3]]
        
        return f"You are a {', '.join(desc_traits[:2])} with {desc_traits[2] if len(desc_traits) > 2 else 'great potential'}. Your analytical abilities and interests align well with technology-focused careers."
    
    def get_branch_details(self, branch_code: str) -> Optional[Dict]:
        """Get detailed info about a specific branch."""
        profile = self.CAREER_PROFILES.get(branch_code)
        if not profile:
            return None
            
        return {
            "code": branch_code,
            **profile
        }


# Singleton instance
_career_engine = None

def get_career_engine() -> CareerEngine:
    """Get or create career engine instance."""
    global _career_engine
    if _career_engine is None:
        _career_engine = CareerEngine()
    return _career_engine


if __name__ == "__main__":
    # Test
    engine = get_career_engine()
    
    # Simulate responses
    test_responses = [
        {"question_id": 1, "option_index": 0},  # Coding
        {"question_id": 2, "option_index": 0},  # Math
        {"question_id": 3, "option_index": 0},  # Independent
        {"question_id": 4, "option_index": 0},  # Puzzles
        {"question_id": 5, "option_index": 0},  # High salary
    ]
    
    result = engine.process_responses(test_responses)
    print(json.dumps(result, indent=2))
