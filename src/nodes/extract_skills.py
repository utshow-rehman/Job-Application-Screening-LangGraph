import logging
from pathlib import Path
from typing import Dict, List, Optional
import pdfplumber
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillExtractor:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0):

        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR assistant specialized in parsing resumes.
Extract the following information from the resume text:
1. Candidate name
2. All technical and professional skills (programming languages, frameworks, tools, soft skills, certifications, etc.)

Return your response in the following format:
NAME: [candidate name]
SKILLS: [comma-separated list of skills, normalized to lowercase]

If the resume is empty or you cannot extract information, return:
NAME: Unknown
SKILLS: none
"""),
            ("user", "Resume text:\n\n{resume_text}")
        ])
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:

        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    logger.warning(f"PDF is empty: {pdf_path}")
                    return None
                
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if not text.strip():
                    logger.warning(f"No text extracted from PDF: {pdf_path}")
                    return None
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {str(e)}")
            return None
    
    def parse_llm_response(self, response: str) -> Dict[str, any]:
        """
        Parse the LLM response to extract name and skills.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Dictionary with 'name' and 'skills' keys
        """
        lines = response.strip().split('\n')
        name = "Unknown"
        skills = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("NAME:"):
                name = line.replace("NAME:", "").strip()
            elif line.startswith("SKILLS:"):
                skills_str = line.replace("SKILLS:", "").strip()
                if skills_str.lower() != "none":
                    # Split by comma and normalize
                    skills = [s.strip().lower() for s in skills_str.split(',') if s.strip()]
        
        return {
            "name": name,
            "skills": skills
        }
    
    def extract_skills_from_resume(self, pdf_path: Path) -> Dict[str, any]:
        """
        Extract candidate name and skills from a resume PDF.
        
        Args:
            pdf_path: Path to the resume PDF
            
        Returns:
            Dictionary containing candidate name, skills, and file path
        """
        logger.info(f"Processing resume: {pdf_path.name}")
        
        # Extract text from PDF
        resume_text = self.extract_text_from_pdf(pdf_path)
        
        if not resume_text:
            logger.warning(f"Failed to extract text from {pdf_path.name}")
            return {
                "file": pdf_path.name,
                "name": "Unknown",
                "skills": [],
                "error": "Failed to extract text from PDF"
            }
        
        try:
            # Use LLM to extract skills
            chain = self.prompt_template | self.llm
            response = chain.invoke({"resume_text": resume_text})
            
            # Parse the response
            parsed_data = self.parse_llm_response(response.content)
            
            result = {
                "file": pdf_path.name,
                "name": parsed_data["name"],
                "skills": parsed_data["skills"],
                "error": None
            }
            
            logger.info(f"Extracted {len(parsed_data['skills'])} skills from {pdf_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {str(e)}")
            return {
                "file": pdf_path.name,
                "name": "Unknown",
                "skills": [],
                "error": str(e)
            }


def extract_skills_node(state: Dict) -> Dict:
    """
    LangGraph node function to extract skills from all resumes.
    
    Args:
        state: Graph state containing 'resume_dir' key
        
    Returns:
        Updated state with 'candidates' list
    """
    resume_dir = Path(state.get("resume_dir", "data/resume"))
    
    if not resume_dir.exists():
        logger.error(f"Resume directory does not exist: {resume_dir}")
        return {
            **state,
            "candidates": [],
            "errors": [f"Resume directory not found: {resume_dir}"]
        }
    
    # Find all PDF files
    pdf_files = list(resume_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {resume_dir}")
        return {
            **state,
            "candidates": [],
            "errors": ["No PDF files found in resume directory"]
        }
    
    logger.info(f"Found {len(pdf_files)} resume(s) to process")
    
    # Extract skills from each resume
    extractor = SkillExtractor()
    candidates = []
    errors = []
    
    for pdf_file in pdf_files:
        result = extractor.extract_skills_from_resume(pdf_file)
        candidates.append(result)
        
        if result.get("error"):
            errors.append(f"{result['file']}: {result['error']}")
    
    return {
        **state,
        "candidates": candidates,
        "errors": errors
    }


if __name__ == "__main__":
    # Test the extractor
    test_state = {"resume_dir": "data/resume"}
    result = extract_skills_node(test_state)
    print(f"Processed {len(result['candidates'])} candidates")
    for candidate in result['candidates']:
        print(f"\n{candidate['name']}: {', '.join(candidate['skills'][:5])}...")
