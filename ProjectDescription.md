You are an expert software engineer. Generate a **full, production-ready LangGraph project** for a **Job Application Screening System** based on this specification.  

---

## Project Requirements

### 1. Project Structure
```text
project-root/
├─ data/
│  ├─ resume/               # contains multiple PDF resumes
│  └─ requirements.txt      # job requirements in plain text
├─ src/
│  ├─ nodes/
│  │  ├─ extract_skills.py  # extracts candidate skills from PDFs
│  │  ├─ match_skills.py    # matches extracted skills against job requirements
│  │  └─ calculate_fit.py   # calculates a fit score
│  └─ main.py               # orchestrates the LangGraph workflow
├─ requirements.txt          # Python dependencies
└─ README.md
````

---

### 2. Node Details

* **extract_skills.py**

  * Read all PDFs in `data/resume/`.
  * Extract candidate skills using OpenAI GPT or industry-standard NLP libraries.
  * Handle empty or corrupted PDFs gracefully.
  * Normalize extracted skills for comparison.

* **match_skills.py**

  * Read `data/requirements.txt`.
  * Match extracted skills to job requirements.
  * Handle synonyms and variations in skill names.
  * Return matched and missing skills per candidate.

* **calculate_fit.py**

  * Compute a **fit score** (0–100%) based on matched vs missing skills.
  * Include extra relevant skills as a positive factor.

* **main.py**

  * Orchestrates the workflow using LangGraph.
  * Processes all resumes and requirements.
  * Outputs a CSV: `Candidate Name | Matched Skills | Missing Skills | Fit Score`.
  * Handles errors gracefully and logs issues.

---

### 3. Requirements

* Python 3.10+
* Dependencies: `langchain`, `langgraph`, `pandas`, `pdfplumber`, `openai`, `python-dotenv`
* Provide a `requirements.txt` file.
* Proper logging, error handling, and type hints.
* Clean, modular, production-ready code with docstrings.

---

### 4. Output

* CSV file summarizing each candidate's skills and fit score.
* Optional log file for resumes that fail processing.

---

### 5. Coding Practices

* Follow industry best practices for Python.
* Modular, reusable code.
* Handle all corner cases (empty PDFs, missing files, empty requirements, corrupted PDFs).
* Comments explaining all steps.


