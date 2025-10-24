# Quick Start Guide - Candidate Filtering

## The Problem You Had

You have **40 resumes** screened, and **20 candidates** scored above 70%. But now:
- ❌ Hard to find which specific resumes to review
- ❌ Need to manually search by name
- ❌ Time-consuming to collect the right PDF files
- ❌ Difficult to share results with hiring team

## The Solution (30 seconds)

### Step 1: Run Screening (if not done already)
```bash
cd src
python3 main.py
```

### Step 2: Filter Qualified Candidates
```bash
python3 quick_filter.py 70
```

**That's it!** 🎉

## What You Get

```
selected_candidates_70pct_20251024_143022/
├── filtered_results_threshold_70.csv    ← Open in Excel
├── selection_summary.txt                ← Human-readable summary
└── resumes/                             ← All qualified resumes!
    ├── john-doe.pdf
    ├── jane-smith.pdf
    ├── alex-johnson.pdf
    └── ... (17 more resumes)
```

## Real Example

### Before Filtering
```csv
Candidate Name,Resume File,Fit Score (%)
John Doe,john-doe.pdf,85.5
Jane Smith,jane-smith.pdf,92.0
Bob Wilson,bob-wilson.pdf,45.0
Alice Brown,alice-brown.pdf,78.5
... (36 more rows)
```

### After Running: `python3 quick_filter.py 70`
```
================================================================================
CANDIDATE FILTERING RESULTS (Threshold: 70%)
================================================================================
Total candidates: 40
Candidates selected: 20
Selection rate: 50.0%
================================================================================

SELECTED CANDIDATES:
--------------------------------------------------------------------------------

Jane Smith
  📄 File: jane-smith.pdf
  📊 Fit Score: 92.0%
  ✅ Matched Skills: python, react, node.js, aws, docker

John Doe
  📄 File: john-doe.pdf
  📊 Fit Score: 85.5%
  ✅ Matched Skills: python, java, sql, kubernetes

Alice Brown
  📄 File: alice-brown.pdf
  📊 Fit Score: 78.5%
  ✅ Matched Skills: javascript, react, mongodb

... (17 more candidates)

================================================================================

📁 Resume files copied: 20/20
   Location: selected_candidates_70pct_20251024_143022/resumes

✅ All files saved to: /path/to/selected_candidates_70pct_20251024_143022
================================================================================
```

## Common Use Cases

### 1. Initial Phone Screen (60% threshold)
```bash
python3 quick_filter.py 60
```
→ Get a broad pool for initial contact

### 2. Technical Interview (70% threshold)
```bash
python3 quick_filter.py 70
```
→ Get qualified candidates for technical rounds

### 3. Final Interviews (85% threshold)
```bash
python3 quick_filter.py 85
```
→ Get only top candidates for final rounds

### 4. Share with Hiring Manager
```bash
python3 quick_filter.py 70
# Then zip the folder:
zip -r qualified_candidates.zip selected_candidates_70pct_*/
# Email the zip file!
```

## Different Thresholds Comparison

| Threshold | Use Case | Typical Pool Size |
|-----------|----------|-------------------|
| 50% | Very broad initial screening | ~60% of candidates |
| 60% | Phone screen candidates | ~40% of candidates |
| 70% | Technical interview candidates | ~25% of candidates |
| 80% | Final round candidates | ~10% of candidates |
| 90% | Top tier only | ~5% of candidates |

## Tips

1. **Run multiple times**: Each run creates a new timestamped folder, so nothing gets overwritten
   ```bash
   python3 quick_filter.py 60  # Broad pool
   python3 quick_filter.py 80  # Narrow pool
   ```

2. **Import to Excel**: Open the filtered CSV in Excel for further analysis
   ```bash
   # On Windows
   start selected_candidates_70pct_*/filtered_results_threshold_70.csv
   
   # On Mac
   open selected_candidates_70pct_*/filtered_results_threshold_70.csv
   
   # On Linux
   xdg-open selected_candidates_70pct_*/filtered_results_threshold_70.csv
   ```

3. **Review resumes**: All PDFs are in one place
   ```bash
   cd selected_candidates_70pct_*/resumes
   # Now open any PDF viewer and review!
   ```

4. **Share with team**: Zip and send
   ```bash
   zip -r candidates.zip selected_candidates_70pct_*/
   # Email candidates.zip to your team
   ```

## Troubleshooting

### "No candidates found with fit score >= 80%"
```
⚠️  No candidates found with fit score >= 80%
   Highest score in results: 75.5%
```
**Solution**: Lower your threshold or review your job requirements

### "Results file not found"
```
❌ Error: Screening results file not found
```
**Solution**: Run the screening first: `python3 src/main.py`

## Time Saved

| Task | Before | After |
|------|--------|-------|
| Find qualified candidates | 30 min | 5 sec |
| Collect resume PDFs | 20 min | 5 sec |
| Create summary report | 15 min | 5 sec |
| Share with team | 10 min | 1 min |
| **Total** | **75 min** | **30 sec** |

**Time saved: 99.3%** ⚡

---

## Next Steps

- 📖 Read [FILTERING_GUIDE.md](FILTERING_GUIDE.md) for advanced features
- 📖 Read [README.md](README.md) for full system documentation
- 🚀 Start filtering your candidates!

---

**Questions?** Check the [FILTERING_GUIDE.md](FILTERING_GUIDE.md) for detailed documentation.
