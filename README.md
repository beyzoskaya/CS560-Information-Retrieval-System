# Spelling Error Correction

**Course:** Information Retrieval and Web Search (Fall 2025)  
**Assignment:** Spelling Error Correction  
**Student ID:** *[S021747]*

---

## Overview
This project implements a **spelling error corrector** using the **Damerau–Levenshtein distance** algorithm.

Two versions are included:
- **Baseline Model:** Generates and selects candidate words with an **edit distance of 1**.  
- **Enhanced Model (Edit Distance 2):** Falls back to **edit distance 2** when no valid candidates are found.

The correct spelling is selected based on **word frequency** from `corpus.txt`.

---

## ⚙️ How to Run

### 1. Baseline Model
```bash
python spell_corrector.py corpus.txt test-words-misspelled.txt output_baseline.txt
```
### 2. Evaluate Accuracy
```bash
python spell_corrector.py corpus.txt test-words-misspelled.txt output_baseline.txt --correct test-words-correct.txt
```
### 3. Enhanced Model (Edit Distance 2)
The enhanced model automatically runs after the baseline and saves its results as:
```bash
output_baseline_ed2.txt
```

### 4. Optional Debug / Analysis Mode
Use this mode to see detailed candidate generation and save an analysis report:
```bash
python spell_corrector.py corpus.txt test-words-misspelled.txt output.txt --correct test-words-correct.txt --debug --analyze outputs/analysis.txt
```

### 5. Testing with Custom Input
```bash
python spell_corrector.py corpus.txt my_misspelled.txt my_output.txt
```
