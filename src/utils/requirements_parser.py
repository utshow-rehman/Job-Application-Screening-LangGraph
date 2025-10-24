"""
Intelligent requirements parser that extracts skills from job descriptions.
Handles both structured skill lists and unstructured job descriptions.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Set
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class RequirementsParser:
    """Parse job requirements from various formats."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        """Initialize with a faster, cheaper model for parsing."""
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing job descriptions and extracting technical skills.

Your task: Extract ONLY the concrete technical skills, tools, and technologies from the job description.

INCLUDE:
- Programming languages (Java, Python, JavaScript, etc.)
- Frameworks (Spring Boot, React, Django, etc.)
- Databases (MySQL, PostgreSQL, MongoDB, etc.)
- Tools & Technologies (Docker, Git, AWS, Kafka, etc.)
- Specific methodologies (Agile, REST API, Microservices, etc.)

EXCLUDE:
- Soft skills (communication, teamwork, problem-solving)
- General terms (computer science, software engineering)
- Years of experience
- Educational requirements
- Job responsibilities

Return ONLY a comma-separated list of technical skills in lowercase.
Be specific and extract 10-25 key technical skills.

Example output:
java, spring boot, rest api, mysql, postgresql, mongodb, docker, git, junit, mockito, microservices, kafka, aws, swagger

DO NOT include explanations or categories, ONLY the comma-separated skill list."""),
            ("user", "Job Description:\n\n{job_description}")
        ])
    
    def parse_requirements(self, requirements_path: Path) -> Dict[str, any]:
        """
        Parse requirements file and extract skills.
        
        Args:
            requirements_path: Path to requirements file
            
        Returns:
            Dictionary with 'skills', 'required_skills', 'nice_to_have', and 'raw_text'
        """
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                logger.error("Requirements file is empty")
                return self._empty_result()
            
            # Check if it's a simple skill list or a job description
            if self._is_simple_skill_list(content):
                logger.info("Detected simple skill list format")
                skills = self._parse_simple_list(content)
                return {
                    "skills": skills,
                    "required_skills": skills,
                    "nice_to_have": [],
                    "raw_text": content,
                    "format": "simple_list"
                }
            else:
                logger.info("Detected job description format - using AI to extract skills")
                return self._parse_job_description(content)
                
        except Exception as e:
            logger.error(f"Error parsing requirements: {str(e)}")
            return self._empty_result()
    
    def _is_simple_skill_list(self, content: str) -> bool:
        """
        Determine if content is a simple skill list or a job description.
        
        Args:
            content: File content
            
        Returns:
            True if simple list, False if job description
        """
        # Check for job description indicators
        jd_indicators = [
            'job title', 'job summary', 'responsibilities', 'qualifications',
            'we are looking', 'the ideal candidate', 'years of experience',
            'bachelor', 'degree', 'role', 'position'
        ]
        
        content_lower = content.lower()
        
        # If it has multiple job description indicators, it's a JD
        indicator_count = sum(1 for indicator in jd_indicators if indicator in content_lower)
        if indicator_count >= 2:
            return False
        
        # If it's mostly short lines, it's likely a skill list
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        if lines:
            avg_line_length = sum(len(l) for l in lines) / len(lines)
            if avg_line_length < 50 and len(lines) > 3:
                return True
        
        # If it has commas and short phrases, likely a list
        if ',' in content and len(content) < 500:
            return True
        
        return False
    
    def _parse_simple_list(self, content: str) -> List[str]:
        """
        Parse a simple comma or line-separated skill list.
        
        Args:
            content: File content
            
        Returns:
            List of skills
        """
        skills = []
        
        # Try comma-separated first
        if ',' in content:
            skills = [s.strip().lower() for s in content.split(',') if s.strip()]
        else:
            # Try line-separated
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # Skip empty lines, comments, and markdown headers
                if not line or line.startswith('#') or line.startswith('*') or line.startswith('-'):
                    continue
                # Remove bullet points and clean
                line = re.sub(r'^[\*\-\•]\s*', '', line)
                if line:
                    skills.append(line.lower())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill not in seen and len(skill) > 1:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _parse_job_description(self, content: str) -> Dict[str, any]:
        """
        Parse a full job description using AI.
        
        Args:
            content: Job description text
            
        Returns:
            Dictionary with extracted skills
        """
        try:
            # Use LLM to extract skills
            chain = self.prompt_template | self.llm
            response = chain.invoke({"job_description": content})
            
            # Parse the response
            skills_text = response.content.strip()
            skills = [s.strip().lower() for s in skills_text.split(',') if s.strip()]
            
            # Try to categorize into required vs nice-to-have
            required_skills, nice_to_have = self._categorize_skills(content, skills)
            
            logger.info(f"Extracted {len(skills)} total skills ({len(required_skills)} required, {len(nice_to_have)} nice-to-have)")
            
            return {
                "skills": skills,
                "required_skills": required_skills,
                "nice_to_have": nice_to_have,
                "raw_text": content,
                "format": "job_description"
            }
            
        except Exception as e:
            logger.error(f"Error using AI to parse job description: {str(e)}")
            return self._empty_result()
    
    def _categorize_skills(self, content: str, skills: List[str]) -> tuple:
        """
        Categorize skills into required vs nice-to-have based on job description.
        
        Args:
            content: Job description text
            skills: List of extracted skills
            
        Returns:
            Tuple of (required_skills, nice_to_have_skills)
        """
        content_lower = content.lower()
        
        # Find sections
        nice_to_have_section = False
        required_section = False
        
        # Look for nice-to-have indicators
        nice_indicators = ['nice to have', 'preferred', 'bonus', 'plus', 'optional']
        required_indicators = ['required', 'must have', 'essential', 'necessary']
        
        required_skills = []
        nice_to_have = []
        
        # Simple heuristic: if skill appears in nice-to-have section, mark it
        for skill in skills:
            # Check context around the skill
            skill_positions = [m.start() for m in re.finditer(re.escape(skill), content_lower)]
            
            if not skill_positions:
                # Default to required if not found
                required_skills.append(skill)
                continue
            
            # Check if any occurrence is in a nice-to-have section
            is_nice = False
            for pos in skill_positions:
                # Look at 200 chars before the skill
                context_start = max(0, pos - 200)
                context = content_lower[context_start:pos]
                
                if any(indicator in context for indicator in nice_indicators):
                    is_nice = True
                    break
            
            if is_nice:
                nice_to_have.append(skill)
            else:
                required_skills.append(skill)
        
        # If we couldn't categorize, treat all as required
        if not required_skills and not nice_to_have:
            required_skills = skills
        
        return required_skills, nice_to_have
    
    def _empty_result(self) -> Dict[str, any]:
        """Return empty result structure."""
        return {
            "skills": [],
            "required_skills": [],
            "nice_to_have": [],
            "raw_text": "",
            "format": "unknown"
        }


def parse_requirements_file(requirements_path: Path) -> List[str]:
    """
    Convenience function to parse requirements and return skill list.
    
    Args:
        requirements_path: Path to requirements file
        
    Returns:
        List of required skills
    """
    parser = RequirementsParser()
    result = parser.parse_requirements(requirements_path)
    return result["required_skills"]


if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        req_path = Path(sys.argv[1])
    else:
        req_path = Path("data/requirements.txt")
    
    parser = RequirementsParser()
    result = parser.parse_requirements(req_path)
    
    print(f"\n{'='*80}")
    print(f"REQUIREMENTS PARSING RESULTS")
    print(f"{'='*80}")
    print(f"Format detected: {result['format']}")
    print(f"Total skills: {len(result['skills'])}")
    print(f"Required skills: {len(result['required_skills'])}")
    print(f"Nice-to-have skills: {len(result['nice_to_have'])}")
    print(f"\n{'='*80}")
    print(f"REQUIRED SKILLS:")
    print(f"{'='*80}")
    for i, skill in enumerate(result['required_skills'], 1):
        print(f"{i:2d}. {skill}")
    
    if result['nice_to_have']:
        print(f"\n{'='*80}")
        print(f"NICE-TO-HAVE SKILLS:")
        print(f"{'='*80}")
        for i, skill in enumerate(result['nice_to_have'], 1):
            print(f"{i:2d}. {skill}")
