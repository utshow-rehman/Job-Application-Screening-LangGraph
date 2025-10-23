# Job Application Screening System

A production-ready **LangGraph-based** system for automated job application screening. This system extracts skills from PDF resumes, matches them against job requirements, and calculates fit scores for each candidate.

## Features

- 🤖 **AI-Powered Skill Extraction**: Uses OpenAI GPT to intelligently extract skills from PDF resumes
- 🔍 **Smart Skill Matching**: Matches candidate skills against job requirements with synonym and variation handling
- 📊 **Comprehensive Scoring**: Calculates fit scores (0-100%) based on required skills and bonus points for extra skills
- 📁 **Batch Processing**: Processes multiple resumes automatically
- 📈 **CSV Output**: Generates detailed reports with candidate rankings
- 🛡️ **Robust Error Handling**: Gracefully handles corrupted PDFs, missing data, and API errors
- 📝 **Detailed Logging**: Comprehensive logging for debugging and audit trails

## Project Structure

```
Job Screening/
├── data/
│   ├── resume/                  # Place PDF resumes here
│   └── requirements.txt         # Job requirements (skills list)
├── src/
│   ├── nodes/
│   │   ├── extract_skills.py   # Extracts candidate skills from PDFs
│   │   ├── match_skills.py     # Matches skills against requirements
│   │   └── calculate_fit.py    # Calculates fit scores
│   └── main.py                  # Main orchestration script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
├── screening_results.csv        # Output (generated)
└── error_log.txt               # Error log (generated if errors occur)
```

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- PDF resumes to process

## Installation

1. **Clone or download this project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

4. **Add your data**:
   - Place PDF resumes in `data/resume/` directory
   - Edit `data/requirements.txt` to specify job requirements (one skill per line)

## Usage

### Basic Usage

Run the screening system:

```bash
cd src
python main.py
```

### What Happens

1. **Skill Extraction**: The system reads all PDF files in `data/resume/` and extracts candidate names and skills using GPT
2. **Skill Matching**: Extracted skills are matched against requirements in `data/requirements.txt`
3. **Fit Calculation**: A fit score (0-100%) is calculated for each candidate
4. **Results Output**: Results are saved to `screening_results.csv` and displayed in the console

### Output Files

- **`screening_results.csv`**: Main results file with columns:
  - Candidate Name
  - Resume File
  - Matched Skills
  - Missing Skills
  - Fit Score (%)
  - Base Score (%)
  - Bonus Score (%)
  - Total Skills
  - Extra Skills Count
  - Error (if any)

- **`error_log.txt`**: Generated only if errors occur during processing

- **`screening_process.log`**: Detailed log of the entire process

## Configuration

### Job Requirements

Edit `data/requirements.txt` to specify required skills. Two formats are supported:

**Line-separated** (recommended):
```
python
machine learning
sql
docker
git
```

**Comma-separated**:
```
python, machine learning, sql, docker, git
```

### Scoring Algorithm

The fit score is calculated as:

- **Base Score (70% weight)**: `(matched_skills / total_required_skills) × 100`
- **Bonus Score (30% weight)**: `(extra_skills / max_bonus_skills) × 100`
- **Final Score**: `(base_score × 0.7) + (bonus_score × 0.3)`

Extra skills are additional relevant skills the candidate has beyond the required list (up to 10 skills count for bonus).

### Customization

You can customize the scoring weights in `src/nodes/calculate_fit.py`:

```python
calculator = FitCalculator(
    match_weight=0.7,           # Weight for required skills
    extra_skills_weight=0.3,    # Weight for bonus skills
    max_extra_skills_bonus=10   # Max extra skills to count
)
```

## Example

### Input

**data/requirements.txt**:
```
python
machine learning
sql
docker
```

**data/resume/** contains:
- `john_doe.pdf`
- `jane_smith.pdf`

### Output

**screening_results.csv**:
```csv
Candidate Name,Resume File,Matched Skills,Missing Skills,Fit Score (%),Base Score (%),Bonus Score (%),Total Skills,Extra Skills Count,Error
Jane Smith,jane_smith.pdf,"python, machine learning, sql, docker",,100.0,100.0,30.0,8,3,None
John Doe,john_doe.pdf,"python, sql, docker",machine learning,78.5,75.0,30.0,6,2,None
```

## Advanced Features

### Intelligent Skill Matching

The system uses GPT to match skills intelligently, recognizing:
- **Synonyms**: "javascript" matches "js"
- **Related Skills**: "react" implies "javascript"
- **Variations**: "machine learning" matches "ml", "deep learning", "tensorflow"

### Error Handling

The system handles:
- Empty PDF files
- Corrupted PDF files
- Missing or invalid requirements file
- API errors and rate limits
- Invalid file formats

### Logging

Comprehensive logging is available in:
- Console output (INFO level)
- `screening_process.log` (detailed)
- `error_log.txt` (errors only, if any)

## Troubleshooting

### "OPENAI_API_KEY not found"
- Ensure you've created a `.env` file with your API key
- Verify the key is valid and has sufficient credits

### "Resume directory not found"
- Create the `data/resume/` directory
- Add at least one PDF resume file

### "No text extracted from PDF"
- Check if the PDF is valid and contains text (not just images)
- Try opening the PDF in a PDF reader to verify it's not corrupted

### "No required skills found"
- Verify `data/requirements.txt` exists and is not empty
- Check that skills are listed one per line or comma-separated

## Dependencies

- **langchain** (>=1.0.0): LLM application framework
- **langchain-core** (>=1.0.0): Core LangChain components
- **langgraph** (>=1.0.0): Workflow orchestration
- **langchain-openai** (>=1.0.0): OpenAI integration for LangChain
- **pandas** (>=2.2.0): Data manipulation and CSV export
- **pdfplumber** (>=0.11.0): PDF text extraction
- **openai** (>=2.0.0): OpenAI API client
- **python-dotenv** (>=1.0.0): Environment variable management
- **typing-extensions** (>=4.12.0): Type hints support

## Architecture

### LangGraph Workflow

```
┌─────────────────┐
│ Extract Skills  │  Read PDFs → Extract skills with GPT
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Match Skills   │  Compare skills → Find matches/gaps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate Fit   │  Compute scores → Rank candidates
└────────┬────────┘
         │
         ▼
    [CSV Output]
```

Each node is a pure function that takes state and returns updated state, enabling:
- **Modularity**: Each step is independent and testable
- **Reliability**: Easy error handling and recovery
- **Extensibility**: Simple to add new nodes or modify workflow

## Best Practices

1. **API Usage**: The system makes API calls for each resume. Monitor your OpenAI usage to manage costs.

2. **Resume Quality**: Better quality PDFs produce better results. Scanned images may not work well.

3. **Requirements**: Be specific with requirements. "Python" is better than "programming".

4. **Batch Size**: For large batches (50+ resumes), consider processing in smaller groups to avoid rate limits.

5. **Testing**: Test with a few resumes first before processing large batches.

## Contributing

This is a production-ready template. Feel free to customize:
- Modify scoring algorithms
- Add new workflow nodes
- Enhance skill matching logic
- Add additional output formats

## License

This project is provided as-is for use in job screening applications.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in `screening_process.log`
3. Verify your environment setup matches requirements

---

**Built with ❤️ using LangGraph and OpenAI**
