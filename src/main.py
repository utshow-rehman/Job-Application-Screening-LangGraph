import os
import logging
from pathlib import Path
from typing import Dict, TypedDict
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# Import node functions
from nodes.extract_skills import extract_skills_node
from nodes.match_skills import match_skills_node
from nodes.calculate_fit import calculate_fit_node

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('screening_process.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """Type definition for the graph state."""
    resume_dir: str
    requirements_path: str
    candidates: list
    required_skills: list
    errors: list
    output_csv: str


def create_screening_workflow() -> StateGraph:
    # Initialize the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes to the graph
    workflow.add_node("extract_skills", extract_skills_node)
    workflow.add_node("match_skills", match_skills_node)
    workflow.add_node("calculate_fit", calculate_fit_node)
    
    # Define the workflow edges
    workflow.set_entry_point("extract_skills")
    workflow.add_edge("extract_skills", "match_skills")
    workflow.add_edge("match_skills", "calculate_fit")
    workflow.add_edge("calculate_fit", END)
    
    return workflow.compile()


def save_results_to_csv(candidates: list, output_path: str) -> None:
    """
    Save screening results to a CSV file.
    
    Args:
        candidates: List of candidate dictionaries with screening results
        output_path: Path where the CSV file should be saved
    """
    if not candidates:
        logger.warning("No candidates to save to CSV")
        return
    
    # Prepare data for CSV
    csv_data = []
    
    for candidate in candidates:
        csv_data.append({
            "Candidate Name": candidate.get("name", "Unknown"),
            "Resume File": candidate.get("file", "N/A"),
            "Matched Skills": ", ".join(candidate.get("matched_skills", [])),
            "Missing Skills": ", ".join(candidate.get("missing_skills", [])),
            "Fit Score (%)": candidate.get("fit_score", 0.0),
            "Base Score (%)": candidate.get("base_score", 0.0),
            "Bonus Score (%)": candidate.get("bonus_score", 0.0),
            "Total Skills": len(candidate.get("skills", [])),
            "Extra Skills Count": candidate.get("extra_skills_count", 0),
            "Error": candidate.get("error", "None")
        })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(csv_data)
    df = df.sort_values("Fit Score (%)", ascending=False)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    logger.info(f"Results saved to {output_path}")
    
    # Also display summary
    print("\n" + "="*80)
    print("SCREENING RESULTS SUMMARY")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    print(f"\nDetailed results saved to: {output_path}")


def save_error_log(errors: list, log_path: str) -> None:
    """
    Save error log to a file.
    
    Args:
        errors: List of error messages
        log_path: Path where the error log should be saved
    """
    if not errors:
        return
    
    with open(log_path, 'w') as f:
        f.write(f"Job Screening Error Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        for i, error in enumerate(errors, 1):
            f.write(f"{i}. {error}\n")
    
    logger.info(f"Error log saved to {log_path}")


def validate_setup() -> bool:
    """
    Validate that the environment is properly set up.
    
    Returns:
        True if setup is valid, False otherwise
    """
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment variables")
        logger.error("Please create a .env file with your OpenAI API key")
        return False
    
    return True


def main():
    """Main execution function."""
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting Job Application Screening System")
    logger.info("="*80)
    
    # Validate setup
    if not validate_setup():
        logger.error("Setup validation failed. Exiting.")
        return
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    resume_dir = base_dir / "data" / "resume"
    requirements_path = base_dir / "data" / "requirements.txt"
    output_csv = base_dir / "screening_results.csv"
    error_log = base_dir / "error_log.txt"
    
    # Verify paths exist
    if not resume_dir.exists():
        logger.error(f"Resume directory not found: {resume_dir}")
        logger.error("Please create the directory and add PDF resumes")
        return
    
    if not requirements_path.exists():
        logger.error(f"Requirements file not found: {requirements_path}")
        logger.error("Please create a requirements.txt file with job requirements")
        return
    
    # Initialize state
    initial_state: GraphState = {
        "resume_dir": str(resume_dir),
        "requirements_path": str(requirements_path),
        "candidates": [],
        "required_skills": [],
        "errors": [],
        "output_csv": str(output_csv)
    }
    
    try:
        # Create and run the workflow
        logger.info("Creating screening workflow...")
        workflow = create_screening_workflow()
        
        logger.info("Running screening workflow...")
        logger.info(f"  Resume directory: {resume_dir}")
        logger.info(f"  Requirements file: {requirements_path}")
        
        # Execute the workflow
        final_state = workflow.invoke(initial_state)
        
        # Save results
        logger.info("\nProcessing complete. Saving results...")
        save_results_to_csv(final_state["candidates"], str(output_csv))
        
        # Save error log if there were any errors
        if final_state.get("errors"):
            save_error_log(final_state["errors"], str(error_log))
            logger.warning(f"\n{len(final_state['errors'])} errors occurred during processing")
            logger.warning(f"See {error_log} for details")
        
        # Print summary statistics
        total_candidates = len(final_state["candidates"])
        successful = sum(1 for c in final_state["candidates"] if not c.get("error"))
        failed = total_candidates - successful
        
        print("\n" + "="*80)
        print("PROCESSING SUMMARY")
        print("="*80)
        print(f"Total resumes processed: {total_candidates}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Required skills: {len(final_state.get('required_skills', []))}")
        
        if successful > 0:
            avg_fit = sum(c.get("fit_score", 0) for c in final_state["candidates"] 
                         if not c.get("error")) / successful
            print(f"Average fit score: {avg_fit:.2f}%")
            
            best_candidate = max(final_state["candidates"], 
                               key=lambda c: c.get("fit_score", 0))
            print(f"Top candidate: {best_candidate['name']} ({best_candidate['fit_score']:.1f}%)")
        
        print("="*80)
        
        logger.info("\nJob Application Screening completed successfully!")
        
        # Offer to filter candidates
        if successful > 0:
            print("\n" + "="*80)
            print("CANDIDATE FILTERING")
            print("="*80)
            try:
                response = input("\nWould you like to filter candidates by fit score? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    threshold = input("Enter minimum fit score threshold (default 70): ").strip()
                    threshold = float(threshold) if threshold else 70.0
                    
                    print(f"\nFiltering candidates with fit score >= {threshold}%...")
                    from filter_candidates import filter_candidates
                    filter_candidates(str(output_csv), threshold=threshold)
            except KeyboardInterrupt:
                print("\n\nFiltering skipped.")
            except Exception as e:
                logger.warning(f"Error during filtering: {e}")
        
    except Exception as e:
        logger.error(f"Fatal error during screening process: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
