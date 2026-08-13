import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)

class HybridMLPredictor:
    """
    Advanced ML Predictor combining historical cutoffs, category mapping,
    financial fit, location preference, and placement scores.
    
    Weights:
    - 40% Historical Cutoff Match
    - 20% Branch Preference
    - 15% Category Match
    - 10% Financial Fit
    - 10% Location Preference
    - 5% Placement Score
    """

    def __init__(self):
        self.weights = {
            "historical": 0.40,
            "branch": 0.20,
            "category": 0.15,
            "financial": 0.10,
            "location": 0.10,
            "placement": 0.05
        }

    def _calculate_historical_match(self, student_rank: int, closing_rank: int) -> float:
        """
        Calibrated sigmoid function to score historical rank match.
        If student rank is much lower (better) than closing rank -> ~1.0
        If student rank is much higher (worse) than closing rank -> ~0.0
        """
        if closing_rank <= 0:
            return 0.0
        
        diff_ratio = (closing_rank - student_rank) / closing_rank
        # Sigmoid curve calibration centered slightly below closing rank for safety margin
        score = 1 / (1 + math.exp(-10 * (diff_ratio - (-0.05))))
        return min(max(score, 0.0), 1.0)

    def _calculate_financial_fit(self, budget: float, annual_fee: float) -> float:
        """Score based on how well the college fee fits the student's budget."""
        if budget <= 0 or annual_fee <= 0:
            return 0.5  # Neutral if unknown
        if annual_fee <= budget:
            return 1.0
        # Exponential decay if over budget
        over_budget_ratio = (annual_fee - budget) / budget
        score = math.exp(-2 * over_budget_ratio)
        return max(score, 0.0)

    def _calculate_location_fit(self, preferred_state: str, college_state: str) -> float:
        if not preferred_state or not college_state:
            return 0.5
        return 1.0 if preferred_state.lower() == college_state.lower() else 0.2

    def _calculate_placement_score(self, avg_lpa: float) -> float:
        # Scale: 0 to 20 LPA gives 0.0 to 1.0
        if not avg_lpa:
            return 0.4 # Default
        return min(avg_lpa / 20.0, 1.0)

    def predict(self, student_profile: Dict[str, Any], colleges_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates unified hybrid scores for a list of colleges.
        """
        student_rank = student_profile.get('rank', 999999)
        budget = student_profile.get('budget_per_year', 0)
        preferred_state = student_profile.get('preferred_state', '')
        
        predictions = []
        for college in colleges_data:
            closing_rank = college.get('closing_rank', 0)
            annual_fee = college.get('annual_fee', 0)
            college_state = college.get('state', '')
            avg_placement = college.get('avg_placement_lpa', 0)
            
            # Sub-scores
            hist_score = self._calculate_historical_match(student_rank, closing_rank)
            branch_score = 1.0  # Assumes pre-filtered by branch preference
            cat_score = 1.0     # Assumes closing_rank is already category-specific
            fin_score = self._calculate_financial_fit(budget, annual_fee)
            loc_score = self._calculate_location_fit(preferred_state, college_state)
            place_score = self._calculate_placement_score(avg_placement)
            
            # Hybrid Recommendation Score
            final_score = (
                hist_score * self.weights["historical"] +
                branch_score * self.weights["branch"] +
                cat_score * self.weights["category"] +
                fin_score * self.weights["financial"] +
                loc_score * self.weights["location"] +
                place_score * self.weights["placement"]
            )
            
            # Calibrate to Percentage
            probability = final_score * 100
            
            # Classification
            if probability >= 80:
                category = "Safe"
            elif probability >= 45:
                category = "Moderate"
            else:
                category = "Dream"
                
            # Explainability
            reasons = []
            if hist_score > 0.8: reasons.append("Rank strongly aligns with historical cutoffs.")
            if hist_score < 0.2: reasons.append("Highly ambitious based on rank trends.")
            if fin_score < 0.5: reasons.append("Fee structure exceeds preferred budget.")
            if loc_score == 1.0: reasons.append("Matches preferred location.")
            
            predictions.append({
                "college_id": college.get('id'),
                "college_name": college.get('name'),
                "probability": round(probability, 1),
                "classification": category,
                "hybrid_score": final_score,
                "reasons": reasons
            })
            
        # Sort by highest probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        return predictions

if __name__ == "__main__":
    predictor = HybridMLPredictor()
    student = {"rank": 5000, "budget_per_year": 150000, "preferred_state": "Karnataka"}
    colleges = [
        {"id": 1, "name": "IIT Bombay", "closing_rank": 50, "annual_fee": 200000, "state": "Maharashtra", "avg_placement_lpa": 25.0},
        {"id": 2, "name": "NIT Surathkal", "closing_rank": 6000, "annual_fee": 140000, "state": "Karnataka", "avg_placement_lpa": 15.0}
    ]
    res = predictor.predict(student, colleges)
    for r in res:
        print(r)
