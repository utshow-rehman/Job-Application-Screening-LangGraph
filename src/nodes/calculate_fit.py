import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitCalculator:
    """Calculates candidate fit scores based on skill matching."""
    
    def __init__(self, 
                 match_weight: float = 0.7,
                 extra_skills_weight: float = 0.3,
                 max_extra_skills_bonus: int = 10):
        """
        Initialize the fit calculator.
        
        Args:
            match_weight: Weight for matched required skills (0-1)
            extra_skills_weight: Weight for extra relevant skills (0-1)
            max_extra_skills_bonus: Maximum number of extra skills to count for bonus
        """
        self.match_weight = match_weight
        self.extra_skills_weight = extra_skills_weight
        self.max_extra_skills_bonus = max_extra_skills_bonus
    
    def calculate_fit_score(self, 
                           matched_skills: List[str],
                           missing_skills: List[str],
                           all_candidate_skills: List[str],
                           required_skills: List[str]) -> Dict[str, any]:
        """
        Calculate the fit score for a candidate.
        
        The score is calculated as:
        - Base score (70% weight): (matched_skills / total_required_skills) * 100
        - Bonus score (30% weight): (extra_skills / max_bonus_skills) * 100
        - Final score: (base_score * match_weight) + (bonus_score * extra_skills_weight)
        
        Args:
            matched_skills: List of required skills the candidate has
            missing_skills: List of required skills the candidate lacks
            all_candidate_skills: Complete list of candidate's skills
            required_skills: Complete list of required skills
            
        Returns:
            Dictionary with score, breakdown, and explanation
        """
        total_required = len(required_skills)
        num_matched = len(matched_skills)
        
        if total_required == 0:
            logger.warning("No required skills to calculate fit against")
            return {
                "fit_score": 0.0,
                "base_score": 0.0,
                "bonus_score": 0.0,
                "explanation": "No required skills defined"
            }
        
        # Calculate base score (percentage of required skills matched)
        base_percentage = (num_matched / total_required) * 100
        
        # Calculate extra skills (skills not in required list)
        required_skills_lower = set(s.lower() for s in required_skills)
        matched_skills_lower = set(s.lower() for s in matched_skills)
        all_skills_lower = set(s.lower() for s in all_candidate_skills)
        
        # Extra skills are those the candidate has that aren't in required list
        # but also aren't already counted as matched
        extra_skills = all_skills_lower - required_skills_lower
        num_extra = min(len(extra_skills), self.max_extra_skills_bonus)
        
        # Calculate bonus score (extra skills as percentage of max bonus)
        bonus_percentage = (num_extra / self.max_extra_skills_bonus) * 100 if self.max_extra_skills_bonus > 0 else 0
        
        # Calculate weighted final score
        final_score = (base_percentage * self.match_weight) + (bonus_percentage * self.extra_skills_weight)
        
        # Ensure score is between 0 and 100
        final_score = max(0.0, min(100.0, final_score))
        
        explanation = self._generate_explanation(
            num_matched, total_required, num_extra, 
            base_percentage, bonus_percentage, final_score
        )
        
        return {
            "fit_score": round(final_score, 2),
            "base_score": round(base_percentage, 2),
            "bonus_score": round(bonus_percentage, 2),
            "matched_count": num_matched,
            "required_count": total_required,
            "extra_skills_count": num_extra,
            "explanation": explanation
        }
    
    def _generate_explanation(self, 
                            matched: int, 
                            total: int, 
                            extra: int,
                            base_pct: float, 
                            bonus_pct: float, 
                            final: float) -> str:
        """
        Generate human-readable explanation of the score.
        
        Args:
            matched: Number of matched required skills
            total: Total number of required skills
            extra: Number of extra skills
            base_pct: Base percentage score
            bonus_pct: Bonus percentage score
            final: Final weighted score
            
        Returns:
            Explanation string
        """
        return (
            f"Matched {matched}/{total} required skills ({base_pct:.1f}% base score). "
            f"Has {extra} additional relevant skills ({bonus_pct:.1f}% bonus). "
            f"Final weighted score: {final:.1f}%"
        )


def calculate_fit_node(state: Dict) -> Dict:
    """
    LangGraph node function to calculate fit scores for all candidates.
    
    Args:
        state: Graph state containing 'candidates' and 'required_skills'
        
    Returns:
        Updated state with fit scores added to each candidate
    """
    candidates = state.get("candidates", [])
    required_skills = state.get("required_skills", [])
    
    if not candidates:
        logger.warning("No candidates to calculate fit for")
        return state
    
    if not required_skills:
        logger.warning("No required skills found")
        return state
    
    calculator = FitCalculator()
    logger.info(f"Calculating fit scores for {len(candidates)} candidate(s)")
    
    for candidate in candidates:
        matched_skills = candidate.get("matched_skills", [])
        missing_skills = candidate.get("missing_skills", [])
        all_skills = candidate.get("skills", [])
        
        if candidate.get("error"):
            # Assign 0 score to candidates with errors
            candidate["fit_score"] = 0.0
            candidate["base_score"] = 0.0
            candidate["bonus_score"] = 0.0
            candidate["score_explanation"] = "Resume processing failed"
            logger.warning(f"Skipping fit calculation for {candidate['name']} due to error")
            continue
        
        # Calculate fit score
        score_result = calculator.calculate_fit_score(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            all_candidate_skills=all_skills,
            required_skills=required_skills
        )
        
        # Add scores to candidate data
        candidate["fit_score"] = score_result["fit_score"]
        candidate["base_score"] = score_result["base_score"]
        candidate["bonus_score"] = score_result["bonus_score"]
        candidate["matched_count"] = score_result["matched_count"]
        candidate["required_count"] = score_result["required_count"]
        candidate["extra_skills_count"] = score_result["extra_skills_count"]
        candidate["score_explanation"] = score_result["explanation"]
        
        logger.info(f"{candidate['name']}: Fit score = {score_result['fit_score']:.1f}%")
    
    # Sort candidates by fit score (descending)
    candidates.sort(key=lambda c: c.get("fit_score", 0), reverse=True)
    
    return state


if __name__ == "__main__":
    # Test the calculator
    test_state = {
        "candidates": [
            {
                "name": "John Doe",
                "skills": ["python", "machine learning", "sql", "docker", "kubernetes", "aws"],
                "matched_skills": ["python", "machine learning", "sql"],
                "missing_skills": ["java"],
                "file": "john_doe.pdf",
                "error": None
            }
        ],
        "required_skills": ["python", "machine learning", "sql", "java"]
    }
    
    result = calculate_fit_node(test_state)
    for candidate in result['candidates']:
        print(f"\n{candidate['name']}:")
        print(f"  Fit Score: {candidate['fit_score']:.1f}%")
        print(f"  {candidate['score_explanation']}")
