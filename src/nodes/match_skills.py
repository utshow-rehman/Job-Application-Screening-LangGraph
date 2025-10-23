

import logging
from pathlib import Path
from typing import Dict, List, Set
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillMatcher:
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0):
   
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR assistant specialized in matching skills.
Given a list of required skills and a list of candidate skills, determine:
1. Which required skills are matched by the candidate (including synonyms and variations)
2. Which required skills are missing

IMPORTANT RULES:
- ONLY return required skills in the MATCHED list, never return candidate skills that aren't required
- A required skill can only be marked as MATCHED if the candidate has that skill or a clear synonym/variant
- If a required skill has no match in the candidate's skills, it must be in MISSING

Consider these equivalences (and similar patterns):
- "python" matches "python programming", "python3", "python 2.7", etc.
- "javascript" matches "js", "ecmascript", but also "node.js", "react", "angular", "vue" (frameworks imply the language)
- "java" matches "java programming", "java 8", "java ee", "spring" (framework implies language)
- "ruby" matches "ruby programming", "ruby on rails", "rails" (framework implies language)
- "machine learning" matches "ml", "deep learning", "neural networks", "tensorflow", "pytorch"
- "sql" matches "mysql", "postgresql", "database", "rdbms", "t-sql"
- "aws" matches "amazon web services", "ec2", "s3", "lambda"
- "git" matches "github", "gitlab", "version control"
- "docker" matches "containerization", "kubernetes"
- "rest api" matches "restful", "api development", "web services"

Return your response in the following format:
MATCHED: [comma-separated list of ONLY the required skills that the candidate has - use the exact required skill names]
MISSING: [comma-separated list of ONLY the required skills that the candidate lacks - use the exact required skill names]

Be reasonable in matching - if a candidate has a clear synonym or related framework, consider it a match. But NEVER return skills that aren't in the required list in the MATCHED section.
"""),
            ("user", """Required skills: {required_skills}
Candidate skills: {candidate_skills}""")
        ])
    
    def read_requirements(self, requirements_path: Path) -> List[str]:
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract skills - assume they are comma-separated or line-separated
            skills = []
            
            # Try comma-separated first
            if ',' in content:
                skills = [s.strip().lower() for s in content.split(',') if s.strip()]
            else:
                # Try line-separated
                skills = [line.strip().lower() for line in content.split('\n') 
                         if line.strip() and not line.strip().startswith('#')]
            
            logger.info(f"Loaded {len(skills)} required skills from {requirements_path.name}")
            return skills
            
        except Exception as e:
            logger.error(f"Error reading requirements file: {str(e)}")
            return []
    
    def parse_matching_response(self, response: str, required_skills: List[str]) -> Dict[str, List[str]]:
        """
        Parse the LLM response to extract matched and missing skills.
        
        Args:
            response: Raw response from LLM
            required_skills: List of required skills to validate against
            
        Returns:
            Dictionary with 'matched' and 'missing' keys
        """
        lines = response.strip().split('\n')
        matched = []
        missing = []
        
        # Create a set of required skills for validation
        required_skills_lower = set(s.lower() for s in required_skills)
        
        for line in lines:
            line = line.strip()
            if line.startswith("MATCHED:"):
                matched_str = line.replace("MATCHED:", "").strip()
                if matched_str.lower() not in ["none", ""]:
                    matched_raw = [s.strip().lower() for s in matched_str.split(',') if s.strip()]
                    # VALIDATION: Only include skills that are in the required skills list
                    matched = [s for s in matched_raw if s in required_skills_lower]
                    
                    # Log warning if LLM returned non-required skills
                    invalid_skills = [s for s in matched_raw if s not in required_skills_lower]
                    if invalid_skills:
                        logger.warning(f"LLM returned non-required skills in MATCHED: {invalid_skills}")
                        
            elif line.startswith("MISSING:"):
                missing_str = line.replace("MISSING:", "").strip()
                if missing_str.lower() not in ["none", ""]:
                    missing_raw = [s.strip().lower() for s in missing_str.split(',') if s.strip()]
                    # VALIDATION: Only include skills that are in the required skills list
                    missing = [s for s in missing_raw if s in required_skills_lower]
        
        # Ensure all required skills are accounted for
        accounted_skills = set(matched) | set(missing)
        unaccounted = required_skills_lower - accounted_skills
        if unaccounted:
            # Add unaccounted skills to missing
            missing.extend(list(unaccounted))
            logger.warning(f"Some required skills were not in LLM response, adding to missing: {unaccounted}")
        
        return {
            "matched": matched,
            "missing": missing
        }
    
    def match_candidate_skills(self, required_skills: List[str], 
                              candidate_skills: List[str]) -> Dict[str, List[str]]:
        """
        Match candidate skills against required skills.
        
        Args:
            required_skills: List of required skills
            candidate_skills: List of candidate's skills
            
        Returns:
            Dictionary with 'matched' and 'missing' skill lists
        """
        if not required_skills:
            logger.warning("No required skills provided")
            return {"matched": [], "missing": []}
        
        if not candidate_skills:
            logger.warning("Candidate has no skills")
            return {"matched": [], "missing": required_skills}
        
        try:
            # Use LLM to intelligently match skills
            chain = self.prompt_template | self.llm
            response = chain.invoke({
                "required_skills": ", ".join(required_skills),
                "candidate_skills": ", ".join(candidate_skills)
            })
            
            # Parse the response with validation
            matching_result = self.parse_matching_response(response.content, required_skills)
            
            return matching_result
            
        except Exception as e:
            logger.error(f"Error matching skills: {str(e)}")
            # Fallback to simple exact matching
            return self.simple_match(required_skills, candidate_skills)
    
    def simple_match(self, required_skills: List[str], 
                    candidate_skills: List[str]) -> Dict[str, List[str]]:
        """
        Fallback simple matching (exact string matching).
        
        Args:
            required_skills: List of required skills
            candidate_skills: List of candidate's skills
            
        Returns:
            Dictionary with 'matched' and 'missing' skill lists
        """
        candidate_set = set(s.lower() for s in candidate_skills)
        matched = []
        missing = []
        
        for req_skill in required_skills:
            req_skill_lower = req_skill.lower()
            # Check for exact match or substring match
            if req_skill_lower in candidate_set or \
               any(req_skill_lower in c_skill for c_skill in candidate_set):
                matched.append(req_skill)
            else:
                missing.append(req_skill)
        
        return {"matched": matched, "missing": missing}


def match_skills_node(state: Dict) -> Dict:
    """
    LangGraph node function to match skills for all candidates.
    
    Args:
        state: Graph state containing 'candidates' and 'requirements_path'
        
    Returns:
        Updated state with matching results added to each candidate
    """
    requirements_path = Path(state.get("requirements_path", "data/requirements.txt"))
    candidates = state.get("candidates", [])
    
    if not requirements_path.exists():
        error_msg = f"Requirements file not found: {requirements_path}"
        logger.error(error_msg)
        return {
            **state,
            "errors": state.get("errors", []) + [error_msg]
        }
    
    if not candidates:
        logger.warning("No candidates to process")
        return state
    
    # Read job requirements
    matcher = SkillMatcher()
    required_skills = matcher.read_requirements(requirements_path)
    
    if not required_skills:
        error_msg = "No valid skills found in requirements file"
        logger.error(error_msg)
        return {
            **state,
            "errors": state.get("errors", []) + [error_msg]
        }
    
    # Match skills for each candidate
    logger.info(f"Matching skills for {len(candidates)} candidate(s)")
    
    for candidate in candidates:
        candidate_skills = candidate.get("skills", [])
        
        if candidate.get("error"):
            # Skip candidates with extraction errors
            candidate["matched_skills"] = []
            candidate["missing_skills"] = required_skills.copy()
            continue
        
        matching_result = matcher.match_candidate_skills(required_skills, candidate_skills)
        
        candidate["matched_skills"] = matching_result["matched"]
        candidate["missing_skills"] = matching_result["missing"]
        
        logger.info(f"{candidate['name']}: {len(matching_result['matched'])}/{len(required_skills)} skills matched")
    
    # Store required skills in state for later use
    state["required_skills"] = required_skills
    
    return state


if __name__ == "__main__":
    # Test the matcher
    test_state = {
        "candidates": [
            {
                "name": "John Doe",
                "skills": ["python", "machine learning", "sql", "docker"],
                "file": "john_doe.pdf",
                "error": None
            }
        ],
        "requirements_path": "data/requirements.txt"
    }
    
    result = match_skills_node(test_state)
    for candidate in result['candidates']:
        print(f"\n{candidate['name']}:")
        print(f"  Matched: {', '.join(candidate.get('matched_skills', []))}")
        print(f"  Missing: {', '.join(candidate.get('missing_skills', []))}")
