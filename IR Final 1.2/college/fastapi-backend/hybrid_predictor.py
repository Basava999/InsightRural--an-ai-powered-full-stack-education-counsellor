import math
from typing import Dict, Any

class HybridIntelligencePredictor:
    """
    The Core ML and Math engine behind the InsightRural Risk Analyzer.
    It computes Compound Risk Scores combining historical cutoff data,
    financial parameters, and career alignment.
    """
    
    def __init__(self, db_session=None):
        self.db_session = db_session

    def calculate_academic_risk(self, student_rank: int, historical_closing_rank: int) -> Dict[str, Any]:
        """
        Calculates academic risk based on the distance between the student's rank 
        and the historical closing rank.
        """
        if historical_closing_rank == 0:
            return {"score": 100, "level": "High", "reasoning": "No historical data available."}

        # Calculate difference percentage
        diff_percent = ((student_rank - historical_closing_rank) / historical_closing_rank) * 100
        
        if student_rank <= historical_closing_rank:
            # Safe zone
            buffer = abs(diff_percent)
            if buffer > 20:
                return {"score": 10, "level": "Low", "reasoning": "Extremely safe. Rank is significantly better than historical cutoffs."}
            else:
                return {"score": 30, "level": "Low", "reasoning": "Safe, but competitive. Rank is within the closing cutoff margin."}
        else:
            # Danger zone (Rank is worse than cutoff)
            if diff_percent < 5:
                return {"score": 60, "level": "Medium", "reasoning": "Borderline risk. Very close to the cutoff, might secure a seat in extended rounds."}
            elif diff_percent < 15:
                return {"score": 80, "level": "High", "reasoning": "High risk. Rank is notably behind the cutoff. Requires strong luck or category shifts."}
            else:
                return {"score": 95, "level": "Critical", "reasoning": "Critical risk. Highly unlikely to secure a seat based on historical trends."}

    def calculate_financial_risk(self, family_income: float, tuition_fee: float, hostel_fee: float, has_scholarship: bool, needs_loan: bool) -> Dict[str, Any]:
        """
        Calculates financial burden based on income, Total Cost of Attendance (TCOA), and aid.
        """
        tcoa = tuition_fee + hostel_fee
        
        # Apply standard scholarship heuristics
        aid_reduction = 0
        if has_scholarship:
            if family_income < 250000:
                aid_reduction = tuition_fee * 0.9 # Full fee waiver assumption
            elif family_income < 800000:
                aid_reduction = tuition_fee * 0.4 # Partial SNQ/OBC waiver
                
        net_cost = max(0, tcoa - aid_reduction)
        
        # Affordability ratio (Net cost vs Annual Income)
        affordability_ratio = net_cost / family_income if family_income > 0 else float('inf')
        
        if affordability_ratio < 0.15:
            return {"score": 15, "level": "Low", "reasoning": "Easily affordable. Costs are well within comfortable limits."}
        elif affordability_ratio < 0.35:
            if needs_loan:
                return {"score": 45, "level": "Medium", "reasoning": "Manageable with an education loan. Repayment won't be severely crippling."}
            else:
                return {"score": 55, "level": "Medium", "reasoning": "Noticeable financial strain, but manageable without severe debt."}
        else:
            if needs_loan:
                return {"score": 85, "level": "High", "reasoning": "High financial burden. Loan EMI will constitute a major part of future entry-level salary."}
            else:
                return {"score": 95, "level": "Critical", "reasoning": "Unsustainable cost without external financial intervention or heavy loans."}

    def calculate_placement_risk(self, placement_avg_lpa: float, college_tier: int) -> Dict[str, Any]:
        """Calculates placement success probability and employment risk."""
        if placement_avg_lpa > 0:
            if placement_avg_lpa >= 8.5:
                return {"score": 10, "level": "Low", "reasoning": f"Excellent. Average package of ₹{placement_avg_lpa} LPA indicates strong career growth."}
            elif placement_avg_lpa >= 5.0:
                return {"score": 40, "level": "Medium", "reasoning": f"Moderate. Standard starting package of ₹{placement_avg_lpa} LPA."}
            else:
                return {"score": 75, "level": "High", "reasoning": f"High risk. Average starting package of ₹{placement_avg_lpa} LPA is below standard."}
        else:
            # Tier fallback
            if college_tier == 1:
                return {"score": 15, "level": "Low", "reasoning": "Low risk. Tier 1 college with strong historical recruitment records."}
            elif college_tier == 2:
                return {"score": 45, "level": "Medium", "reasoning": "Moderate risk. Tier 2 college with standard placement rates."}
            else:
                return {"score": 80, "level": "High", "reasoning": "High risk. Tier 3 college. Relies heavily on off-campus hiring."}

    def calculate_scholarship_opportunity(self, family_income: float, category: str, gender: str, state: str = "Karnataka") -> Dict[str, Any]:
        """Evaluates potential financial aid eligibility."""
        score = 0
        schemes = []
        if family_income < 450000 and state.lower() == "karnataka":
            score += 40
            schemes.append("Supernumerary Quota (SNQ)")
        if category in ["SC", "ST"] and family_income <= 250000:
            score += 50
            schemes.append("SSP Post-Matric SC/ST")
        elif category in ["OBC", "2A", "2B", "3A", "3B"] and family_income <= 100000:
            score += 30
            schemes.append("SSP Post-Matric OBC")
        if gender.lower() == "female" and family_income < 800000:
            score += 20
            schemes.append("AICTE Pragati Scholarship")
            
        score = min(100, max(0, score))
        level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
        return {
            "score": score,
            "level": level,
            "reasoning": f"Estimated aid eligibility score of {score}/100. Potential matches: {', '.join(schemes) if schemes else 'General Merit Schemes'}."
        }

    def calculate_roi_score(self, placement_avg_lpa: float, tuition_fee: float, hostel_fee: float, college_tier: int) -> Dict[str, Any]:
        """Calculates Return on Investment index (ROI)."""
        total_4year_cost = (tuition_fee + hostel_fee) * 4
        avg_lpa = placement_avg_lpa
        if avg_lpa == 0:
            avg_lpa = 10.0 if college_tier == 1 else 5.5 if college_tier == 2 else 3.5
            
        if total_4year_cost == 0:
            roi_ratio = float('inf')
        else:
            roi_ratio = (avg_lpa * 100000) / total_4year_cost
            
        if roi_ratio >= 1.5:
            score = 95
            level = "Excellent"
            reasoning = f"Outstanding ROI. Starting salary of ₹{avg_lpa} LPA exceeds total cost of ₹{total_4year_cost:,.0f}."
        elif roi_ratio >= 0.7:
            score = 75
            level = "High"
            reasoning = f"Good ROI. Expected starting salary is ₹{avg_lpa} LPA compared to a total cost of ₹{total_4year_cost:,.0f}."
        elif roi_ratio >= 0.35:
            score = 50
            level = "Moderate"
            reasoning = f"Moderate ROI. Standard starting salary of ₹{avg_lpa} LPA vs total cost of ₹{total_4year_cost:,.0f}."
        else:
            score = 25
            level = "Low"
            reasoning = f"Low ROI. Total cost of ₹{total_4year_cost:,.0f} is high relative to starting package of ₹{avg_lpa} LPA."
            
        return {
            "score": score,
            "level": level,
            "reasoning": reasoning
        }

    def calculate_career_alignment(self, student_skills: list, student_interests: list, branch_name: str) -> Dict[str, Any]:
        """
        Evaluates if the selected branch aligns with the student's actual skills.
        """
        # Simplified keyword matching for demonstration
        branch_lower = branch_name.lower()
        skills_text = " ".join([s.lower() for s in student_skills])
        interests_text = " ".join([i.lower() for i in student_interests])
        
        alignment_score = 50 # Base neutral
        
        if "computer" in branch_lower or "software" in branch_lower or "it" in branch_lower or "artificial" in branch_lower or "data" in branch_lower:
            if "coding" in skills_text or "programming" in skills_text:
                alignment_score += 30
            if "ai" in interests_text or "software" in interests_text or "robotics" in interests_text:
                alignment_score += 20
        elif "mechanical" in branch_lower or "civil" in branch_lower:
            if "physics" in skills_text or "math" in skills_text:
                alignment_score += 20
            if "robotics" in interests_text or "building" in interests_text:
                alignment_score += 20

        alignment_score = min(100, max(0, alignment_score))
        
        level = "High" if alignment_score >= 80 else "Medium" if alignment_score >= 50 else "Low"
        return {"score": alignment_score, "level": level, "reasoning": f"Alignment score of {alignment_score}/100 based on mapping skills/interests to branch curriculum."}

    def calculate_compound_risk(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        The master engine that aggregates all sub-risks into the flagship Compound Risk Score.
        """
        # Extract parameters
        rank = profile.get("rank", 100000)
        hist_rank = profile.get("historical_closing_rank", rank - 1000) # Mock if not passed
        
        income = profile.get("income", 500000)
        fees = profile.get("fees", 100000)
        hostel = profile.get("hostel_fees", 0)
        scholarship = profile.get("has_scholarship", False)
        loan = profile.get("loan_required", False)
        
        skills = profile.get("skills", [])
        interests = profile.get("interests", [])
        branch = profile.get("branch", "General")
        
        placement_avg_lpa = profile.get("placement_avg_lpa", 0.0)
        college_tier = profile.get("college_tier", 3)
        gender = profile.get("gender", "Male")
        state = profile.get("state", "Karnataka")
        
        # Calculate Sub-scores
        academic = self.calculate_academic_risk(rank, hist_rank)
        financial = self.calculate_financial_risk(income, fees, hostel, scholarship, loan)
        career = self.calculate_career_alignment(skills, interests, branch)
        placement = self.calculate_placement_risk(placement_avg_lpa, college_tier)
        scholarship_opp = self.calculate_scholarship_opportunity(income, profile.get("category", "GM"), gender, state)
        roi = self.calculate_roi_score(placement_avg_lpa, fees, hostel, college_tier)
        
        # Weighting: Academic (30%), Financial (25%), Placement (25%), Career Mismatch Risk (20%)
        # Note: Career alignment is 0-100 (100 is good). We invert it for risk (100 - score).
        career_risk_score = 100 - career["score"]
        
        compound_risk_score = (
            (academic["score"] * 0.30) + 
            (financial["score"] * 0.25) + 
            (placement["score"] * 0.25) + 
            (career_risk_score * 0.20)
        )
        
        # Regret Probability uses an exponential curve to heavily penalize severe mismatches
        regret_probability = round(1 / (1 + math.exp(-0.1 * (compound_risk_score - 50))) * 100)
        
        # Overall Success Score is inverse of risk
        success_score = max(0, min(100, 100 - compound_risk_score))
        
        return {
            "compound_risk_score": round(compound_risk_score, 1),
            "success_score": round(success_score, 1),
            "regret_probability": regret_probability,
            "components": {
                "academic": academic,
                "financial": financial,
                "career": career,
                "placement": placement,
                "scholarship_opp": scholarship_opp,
                "roi": roi
            }
        }
