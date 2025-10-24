

import logging
from pathlib import Path
from typing import Dict, List, Set
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.requirements_parser import RequirementsParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillMatcher:
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        """Initialize with faster, cheaper model for matching."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self._match_cache = {}  # Cache for skill matching results
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR assistant specialized in matching skills.
Given a list of required skills and a list of candidate skills, determine:
1. Which required skills are matched by the candidate (including synonyms and variations)
2. Which required skills are missing

IMPORTANT RULES:
- ONLY return required skills in the MATCHED/MISSING lists
- Use the EXACT skill names from the required list
- A required skill is MATCHED if the candidate has that skill or a clear synonym/variant
- If a required skill has no match, it must be in MISSING
- Every required skill must appear in either MATCHED or MISSING

Consider these equivalences:
- "python" matches "python programming", "python3", "django", "flask"
- "javascript" matches "js", "node.js", "react", "angular", "vue"
- "java" matches "java programming", "spring", "spring boot", "hibernate"
- "sql" matches "mysql", "postgresql", "database", "rdbms"
- "aws" matches "amazon web services", "ec2", "s3", "lambda"
- "git" matches "github", "gitlab", "version control"
- "docker" matches "containerization", "kubernetes"
- "rest api" matches "restful", "api development", "web services"

RESPONSE FORMAT (strict):
MATCHED: skill1, skill2, skill3
MISSING: skill4, skill5, skill6

Example:
Required: java, spring boot, mysql, docker, git
Candidate: python, spring framework, postgresql, github, aws

Response:
MATCHED: spring boot, git
MISSING: java, mysql, docker

Use EXACT skill names from required list. No brackets, no extra text.
"""),
            ("user", """Required skills: {required_skills}
Candidate skills: {candidate_skills}""")
        ])
    
    def read_requirements(self, requirements_path: Path) -> List[str]:
        """
        Read and parse requirements file using intelligent parser.
        Handles both simple lists and full job descriptions.
        """
        try:
            parser = RequirementsParser()
            result = parser.parse_requirements(requirements_path)
            
            skills = result["required_skills"]
            
            if not skills:
                logger.warning("No skills extracted from requirements file")
                return []
            
            logger.info(f"Extracted {len(skills)} required skills from {requirements_path.name}")
            logger.info(f"Format detected: {result['format']}")
            
            # Log the skills for verification
            logger.info(f"Required skills: {', '.join(skills[:10])}{'...' if len(skills) > 10 else ''}")
            
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
        Match candidate skills against required skills with caching.
        
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
        
        # Create cache key
        cache_key = (
            tuple(sorted(required_skills)),
            tuple(sorted(candidate_skills))
        )
        
        # Check cache
        if cache_key in self._match_cache:
            logger.debug("Using cached matching result")
            return self._match_cache[cache_key]
        
        try:
            # Use LLM to intelligently match skills
            chain = self.prompt_template | self.llm
            response = chain.invoke({
                "required_skills": ", ".join(required_skills),
                "candidate_skills": ", ".join(candidate_skills)
            })
            
            # Parse the response with validation
            matching_result = self.parse_matching_response(response.content, required_skills)
            
            # Cache the result
            self._match_cache[cache_key] = matching_result
            
            return matching_result
            
        except Exception as e:
            logger.error(f"Error matching skills: {str(e)}")
            # Fallback to simple exact matching
            result = self.simple_match(required_skills, candidate_skills)
            self._match_cache[cache_key] = result
            return result
    
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
