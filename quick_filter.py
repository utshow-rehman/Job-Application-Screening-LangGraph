#!/usr/bin/env python3
"""
Quick filter script - Run this anytime to filter your screening results.

Usage:
    python quick_filter.py              # Filter with 70% threshold
    python quick_filter.py 80           # Filter with 80% threshold
    python quick_filter.py 70 --no-copy # Filter without copying resumes
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.filter_candidates import filter_candidates

if __name__ == "__main__":
    # Parse simple command line arguments
    threshold = 70.0
    copy_resumes = True
    
    if len(sys.argv) > 1:
        try:
            threshold = float(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid threshold '{sys.argv[1]}'. Using default 70.0")
            threshold = 70.0
    
    if '--no-copy' in sys.argv or '--no-copy-resumes' in sys.argv:
        copy_resumes = False
    
    # Run the filter
    results_csv = Path(__file__).parent / "screening_results.csv"
    
    if not results_csv.exists():
        print(f"❌ Error: Screening results file not found: {results_csv}")
        print("   Please run the screening process first (python src/main.py)")
        sys.exit(1)
    
    print(f"\n🔍 Filtering candidates from: {results_csv}")
    print(f"   Threshold: {threshold}%")
    print(f"   Copy resumes: {'Yes' if copy_resumes else 'No'}\n")
    
    filter_candidates(
        results_csv=str(results_csv),
        threshold=threshold,
        copy_resumes=copy_resumes
    )
