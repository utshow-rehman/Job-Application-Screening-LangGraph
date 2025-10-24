#!/usr/bin/env python3
"""
Filter and export candidates based on screening results.

This script allows you to:
1. Filter candidates by fit score threshold
2. Copy selected resumes to a separate folder
3. Generate a filtered results CSV
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd


def filter_candidates(
    results_csv: str,
    threshold: float = 70.0,
    output_dir: str = None,
    copy_resumes: bool = True
) -> None:
    """
    Filter candidates based on fit score and optionally copy their resumes.
    
    Args:
        results_csv: Path to the screening results CSV file
        threshold: Minimum fit score threshold (default: 70.0)
        output_dir: Directory to save filtered results and resumes
        copy_resumes: Whether to copy resume files to output directory
    """
    # Read the screening results
    try:
        df = pd.read_csv(results_csv)
    except FileNotFoundError:
        print(f"Error: Results file not found: {results_csv}")
        return
    except Exception as e:
        print(f"Error reading results file: {e}")
        return
    
    # Filter candidates by threshold
    filtered_df = df[df['Fit Score (%)'] >= threshold].copy()
    
    if filtered_df.empty:
        print(f"\n⚠️  No candidates found with fit score >= {threshold}%")
        print(f"   Highest score in results: {df['Fit Score (%)'].max():.1f}%")
        return
    
    # Sort by fit score (descending)
    filtered_df = filtered_df.sort_values('Fit Score (%)', ascending=False)
    
    # Create output directory if needed
    if output_dir is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"selected_candidates_{threshold}pct_{timestamp}"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save filtered CSV
    filtered_csv_path = output_path / f"filtered_results_threshold_{threshold}.csv"
    filtered_df.to_csv(filtered_csv_path, index=False)
    
    # Print summary
    print("\n" + "="*80)
    print(f"CANDIDATE FILTERING RESULTS (Threshold: {threshold}%)")
    print("="*80)
    print(f"Total candidates in original results: {len(df)}")
    print(f"Candidates meeting threshold: {len(filtered_df)}")
    print(f"Selection rate: {len(filtered_df)/len(df)*100:.1f}%")
    print("="*80)
    print("\nSELECTED CANDIDATES:")
    print("-"*80)
    
    # Display selected candidates
    for idx, row in filtered_df.iterrows():
        print(f"\n{row['Candidate Name']}")
        print(f"  📄 File: {row['Resume File']}")
        print(f"  📊 Fit Score: {row['Fit Score (%)']}%")
        print(f"  ✅ Matched Skills: {row['Matched Skills']}")
        if row['Missing Skills']:
            print(f"  ❌ Missing Skills: {row['Missing Skills']}")
    
    print("\n" + "="*80)
    
    # Copy resume files if requested
    if copy_resumes:
        resume_dir = Path(results_csv).parent / "data" / "resume"
        if not resume_dir.exists():
            # Try alternative path
            resume_dir = Path(results_csv).parent.parent / "data" / "resume"
        
        if resume_dir.exists():
            resumes_output_dir = output_path / "resumes"
            resumes_output_dir.mkdir(exist_ok=True)
            
            copied_count = 0
            missing_files = []
            
            for idx, row in filtered_df.iterrows():
                resume_file = row['Resume File']
                source_path = resume_dir / resume_file
                
                if source_path.exists():
                    dest_path = resumes_output_dir / resume_file
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
                else:
                    missing_files.append(resume_file)
            
            print(f"\n📁 Resume files copied: {copied_count}/{len(filtered_df)}")
            print(f"   Location: {resumes_output_dir}")
            
            if missing_files:
                print(f"\n⚠️  Warning: {len(missing_files)} resume files not found:")
                for file in missing_files:
                    print(f"   - {file}")
        else:
            print(f"\n⚠️  Resume directory not found: {resume_dir}")
            print("   Resume files were not copied.")
    
    # Save a summary text file
    summary_path = output_path / "selection_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(f"Candidate Selection Summary\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Threshold: {threshold}%\n")
        f.write(f"Total candidates screened: {len(df)}\n")
        f.write(f"Candidates selected: {len(filtered_df)}\n")
        f.write(f"Selection rate: {len(filtered_df)/len(df)*100:.1f}%\n\n")
        f.write(f"{'='*80}\n")
        f.write(f"SELECTED CANDIDATES (sorted by fit score):\n")
        f.write(f"{'='*80}\n\n")
        
        for idx, row in filtered_df.iterrows():
            f.write(f"{row['Candidate Name']}\n")
            f.write(f"  Resume: {row['Resume File']}\n")
            f.write(f"  Fit Score: {row['Fit Score (%)']}%\n")
            f.write(f"  Base Score: {row['Base Score (%)']}%\n")
            f.write(f"  Bonus Score: {row['Bonus Score (%)']}%\n")
            f.write(f"  Total Skills: {row['Total Skills']}\n")
            f.write(f"  Matched Skills: {row['Matched Skills']}\n")
            if row['Missing Skills']:
                f.write(f"  Missing Skills: {row['Missing Skills']}\n")
            f.write(f"\n{'-'*80}\n\n")
    
    print(f"\n📄 Filtered results saved to: {filtered_csv_path}")
    print(f"📄 Summary saved to: {summary_path}")
    print(f"\n✅ All files saved to: {output_path.absolute()}")
    print("="*80 + "\n")


def main():
    """Main execution function with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Filter candidates based on screening results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Filter candidates with fit score >= 70%
  python filter_candidates.py
  
  # Filter with custom threshold
  python filter_candidates.py --threshold 80
  
  # Filter without copying resume files
  python filter_candidates.py --no-copy-resumes
  
  # Specify custom input/output paths
  python filter_candidates.py --input results.csv --output selected_candidates/
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        default='screening_results.csv',
        help='Path to screening results CSV file (default: screening_results.csv)'
    )
    
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=70.0,
        help='Minimum fit score threshold in percentage (default: 70.0)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output directory for filtered results (default: auto-generated with timestamp)'
    )
    
    parser.add_argument(
        '--no-copy-resumes',
        action='store_true',
        help='Do not copy resume files, only generate filtered CSV'
    )
    
    args = parser.parse_args()
    
    # Resolve input path
    input_path = Path(args.input)
    if not input_path.is_absolute():
        # Try to find it relative to script location
        script_dir = Path(__file__).parent.parent
        input_path = script_dir / args.input
    
    filter_candidates(
        results_csv=str(input_path),
        threshold=args.threshold,
        output_dir=args.output,
        copy_resumes=not args.no_copy_resumes
    )


if __name__ == "__main__":
    main()
