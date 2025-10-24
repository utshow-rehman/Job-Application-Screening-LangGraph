# Candidate Filtering - Cheat Sheet

## The One Command You Need

```bash
python3 quick_filter.py 70
```

That's it! This will:
- ✅ Filter candidates with fit score >= 70%
- ✅ Copy their resumes to a new folder
- ✅ Generate a summary report

---

## Common Commands

| Command | What It Does |
|---------|--------------|
| `python3 quick_filter.py` | Filter with 70% threshold (default) |
| `python3 quick_filter.py 80` | Filter with 80% threshold |
| `python3 quick_filter.py 60` | Filter with 60% threshold |
| `python3 quick_filter.py 70 --no-copy` | Filter without copying resumes |

---

## Output Location

Look for a folder named:
```
selected_candidates_70pct_YYYYMMDD_HHMMSS/
```

Inside you'll find:
- `filtered_results_threshold_70.csv` - Filtered data (open in Excel)
- `selection_summary.txt` - Human-readable report
- `resumes/` - All qualified candidate resumes

---

## Quick Examples

### Example 1: Get candidates for phone screen
```bash
python3 quick_filter.py 60
```

### Example 2: Get candidates for technical interview
```bash
python3 quick_filter.py 75
```

### Example 3: Get top candidates for final round
```bash
python3 quick_filter.py 85
```

### Example 4: Share with hiring manager
```bash
python3 quick_filter.py 70
zip -r candidates.zip selected_candidates_70pct_*/
# Email candidates.zip
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Results file not found" | Run `python3 src/main.py` first |
| "No candidates found" | Lower your threshold |
| "python3: command not found" | Use `python` instead |

---

## Time Saved

**Before:** 30-60 minutes of manual work
**After:** 5 seconds ⚡

---

## Need More Help?

- 📖 **Quick Start**: Read `QUICK_START.md`
- 📖 **Full Guide**: Read `FILTERING_GUIDE.md`
- 📖 **Solution Summary**: Read `SOLUTION_SUMMARY.md`

---

## Your Scenario

You said:
> "I have 40 resumes. 20 candidates match greater than 70%. How can I find those resumes?"

**Answer:**
```bash
python3 quick_filter.py 70
```

Now you have:
- ✅ A CSV with only those 20 candidates
- ✅ All 20 resume PDFs in one folder
- ✅ A summary report
- ✅ Ready to review or share

**Problem solved!** 🎉
