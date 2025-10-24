#!/usr/bin/env python3
"""
Helper script to parse job descriptions and extract skills.
Use this to preview what skills will be extracted before running the full screening.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.requirements_parser import RequirementsParser


def main():
    """Parse job description and display extracted skills."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Parse job description and extract technical skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse default requirements file
  python3 parse_job_description.py
  
  # Parse specific file
  python3 parse_job_description.py data/requirements.txt
  
  # Save extracted skills to a new file
  python3 parse_job_description.py --output data/extracted_skills.txt
        """
    )
    
    parser.add_argument(
        'input_file',
        nargs='?',
        default='data/requirements.txt',
        help='Path to job description file (default: data/requirements.txt)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Save extracted skills to this file'
    )
    
    parser.add_argument(
        '--format',
        choices=['list', 'comma'],
        default='list',
        help='Output format: list (one per line) or comma (comma-separated)'
    )
    
    args = parser.parse_args()
    
    # Parse the requirements
    req_path = Path(args.input_file)
    
    if not req_path.exists():
        print(f"❌ Error: File not found: {req_path}")
        sys.exit(1)
    
    print(f"\n🔍 Parsing job description: {req_path}")
    print("="*80)
    
    req_parser = RequirementsParser()
    result = req_parser.parse_requirements(req_path)
    
    if not result['skills']:
        print("\n❌ No skills could be extracted from the file.")
        print("   Please check that the file contains a job description or skill list.")
        sys.exit(1)
    
    # Display results
    print(f"\n✅ Successfully extracted skills!")
    print(f"   Format detected: {result['format']}")
    print(f"   Total skills: {len(result['skills'])}")
    print(f"   Required skills: {len(result['required_skills'])}")
    print(f"   Nice-to-have skills: {len(result['nice_to_have'])}")
    
    print("\n" + "="*80)
    print("REQUIRED SKILLS (used for matching):")
    print("="*80)
    for i, skill in enumerate(result['required_skills'], 1):
        print(f"  {i:2d}. {skill}")
    
    if result['nice_to_have']:
        print("\n" + "="*80)
        print("NICE-TO-HAVE SKILLS (bonus points):")
        print("="*80)
        for i, skill in enumerate(result['nice_to_have'], 1):
            print(f"  {i:2d}. {skill}")
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if args.format == 'comma':
                f.write(', '.join(result['required_skills']))
            else:
                f.write('\n'.join(result['required_skills']))
        
        print(f"\n💾 Saved extracted skills to: {output_path}")
        print(f"   Format: {args.format}")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review the extracted skills above")
    print("2. If they look good, run the screening:")
    print("   python3 src/main.py")
    print("3. Or save them to a clean file:")
    print(f"   python3 parse_job_description.py {args.input_file} --output data/clean_skills.txt")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
