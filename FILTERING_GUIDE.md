# Candidate Filtering Guide

## Problem
When you have 40 resumes and 20 candidates score above 70%, it's hard to:
- Identify which resumes to review
- Access the actual resume files
- Share selected candidates with others

## Solution
This system provides **automatic filtering and resume extraction** based on fit scores.

---

## Quick Start

### Method 1: Quick Filter (Easiest)
After running the screening process, simply run:

```bash
python quick_filter.py
```

This will:
- ✅ Filter candidates with fit score >= 70%
- ✅ Copy their resumes to a new folder
- ✅ Generate a filtered CSV with only selected candidates
- ✅ Create a summary report

### Method 2: Custom Threshold
Filter with a different threshold (e.g., 80%):

```bash
python quick_filter.py 80
```

### Method 3: Interactive (During Screening)
When you run the main screening process:

```bash
python src/main.py
```

At the end, you'll be prompted:
```
Would you like to filter candidates by fit score? (y/n): y
Enter minimum fit score threshold (default 70): 75
```

---

## Advanced Usage

### Using the Filter Module Directly

```bash
# Basic filtering
python src/filter_candidates.py

# Custom threshold
python src/filter_candidates.py --threshold 80

# Custom input/output paths
python src/filter_candidates.py --input results.csv --output my_selections/

# Filter without copying resumes (CSV only)
python src/filter_candidates.py --no-copy-resumes

# Get help
python src/filter_candidates.py --help
```

---

## Output Structure

When you filter candidates, a new folder is created with this structure:

```
selected_candidates_70pct_20250124_143022/
├── filtered_results_threshold_70.csv    # Filtered CSV with selected candidates
├── selection_summary.txt                # Detailed text summary
└── resumes/                             # Folder with selected resume PDFs
    ├── jatin-varlyanis-resume.pdf
    ├── john-doe-resume.pdf
    └── jane-smith-resume.pdf
```

### What's Included

1. **filtered_results_threshold_XX.csv**
   - Same format as original screening_results.csv
   - Only includes candidates meeting the threshold
   - Sorted by fit score (highest first)

2. **selection_summary.txt**
   - Human-readable summary
   - Complete details for each selected candidate
   - Statistics (selection rate, total candidates, etc.)

3. **resumes/ folder**
   - Contains copies of all selected candidates' resumes
   - Easy to share with hiring managers
   - Original filenames preserved

---

## Example Output

```
================================================================================
CANDIDATE FILTERING RESULTS (Threshold: 70%)
================================================================================
Total candidates in original results: 40
Candidates meeting threshold: 20
Selection rate: 50.0%
================================================================================

SELECTED CANDIDATES:
--------------------------------------------------------------------------------

Jatin Varlyani
  📄 File: jatin-varlyanis-resume.pdf
  📊 Fit Score: 100.0%
  ✅ Matched Skills: python, javascript, react, node.js, aws
  ❌ Missing Skills: 

John Doe
  📄 File: john-doe-resume.pdf
  📊 Fit Score: 85.5%
  ✅ Matched Skills: python, java, sql, docker
  ❌ Missing Skills: kubernetes

[... more candidates ...]

================================================================================

📁 Resume files copied: 20/20
   Location: selected_candidates_70pct_20250124_143022/resumes

📄 Filtered results saved to: selected_candidates_70pct_20250124_143022/filtered_results_threshold_70.csv
📄 Summary saved to: selected_candidates_70pct_20250124_143022/selection_summary.txt

✅ All files saved to: /path/to/selected_candidates_70pct_20250124_143022
================================================================================
```

---

## Use Cases

### 1. Initial Screening (70% threshold)
```bash
python quick_filter.py 70
```
Get a broad pool of qualified candidates.

### 2. Shortlist for Interviews (80% threshold)
```bash
python quick_filter.py 80
```
Get only the top candidates for interviews.

### 3. Multiple Rounds
```bash
# Round 1: Phone screen (60%)
python quick_filter.py 60

# Round 2: Technical interview (75%)
python quick_filter.py 75

# Round 3: Final interviews (85%)
python quick_filter.py 85
```

### 4. Share with Hiring Manager
```bash
python quick_filter.py 70
# Then zip and send the entire folder:
zip -r selected_candidates.zip selected_candidates_70pct_*/
```

---

## Tips

1. **Multiple Thresholds**: Run the filter multiple times with different thresholds to compare pools
2. **Timestamp Folders**: Each run creates a timestamped folder, so nothing gets overwritten
3. **CSV Import**: Import the filtered CSV into Excel/Google Sheets for further analysis
4. **Resume Review**: The resumes folder makes it easy to review PDFs without searching

---

## Troubleshooting

### No candidates found
```
⚠️  No candidates found with fit score >= 80%
   Highest score in results: 75.5%
```
**Solution**: Lower your threshold or improve job requirements matching.

### Resume files not found
```
⚠️  Warning: 2 resume files not found:
   - missing-resume.pdf
```
**Solution**: Check that resume files are in `data/resume/` directory.

### Results file not found
```
❌ Error: Screening results file not found
```
**Solution**: Run the screening process first: `python src/main.py`

---

## Integration with Your Workflow

```python
# In your own Python scripts
from src.filter_candidates import filter_candidates

# Filter programmatically
filter_candidates(
    results_csv="screening_results.csv",
    threshold=75.0,
    output_dir="my_selections",
    copy_resumes=True
)
```

---

## Summary

**Before**: Manually search through 40 resumes to find the 20 that scored > 70%

**After**: Run `python quick_filter.py` and get:
- ✅ Filtered list of qualified candidates
- ✅ All their resumes in one folder
- ✅ Detailed summary report
- ✅ Ready to share with your team

**Time saved**: Hours → Seconds 🚀
