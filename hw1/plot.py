import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import re

# --- File paths ---
baseline_file = "outputs/output.txt"
ed2_file = "outputs/output_ed2.txt"
gold_file = "inputs/test-words-correct.txt"
corpus_file = "inputs/corpus.txt"

# --- Load predictions ---
with open(baseline_file, 'r', encoding='utf-8') as f:
    baseline_list = [line.strip() for line in f]

with open(ed2_file, 'r', encoding='utf-8') as f:
    ed2_list = [line.strip() for line in f]

with open(gold_file, 'r', encoding='utf-8') as f:
    gold_list = [line.strip() for line in f]

# --- Build corpus frequency ---
with open(corpus_file, 'r', encoding='utf-8') as f:
    corpus_text = f.read().lower()
word_freq = Counter(re.findall(r"[a-z]+", corpus_text))

# --- Comparison statistics ---
only_baseline_correct = 0
only_ed2_correct = 0
both_correct = 0
neither_correct = 0

for b, e, g in zip(baseline_list, ed2_list, gold_list):
    b_corr = b == g
    e_corr = e == g
    if b_corr and not e_corr:
        only_baseline_correct += 1
    elif e_corr and not b_corr:
        only_ed2_correct += 1
    elif b_corr and e_corr:
        both_correct += 1
    else:
        neither_correct += 1

summary_table = pd.DataFrame({
    "Category": ["Only Baseline Correct", "Only ED2 Correct", "Both Correct", "Neither Correct"],
    "Count": [only_baseline_correct, only_ed2_correct, both_correct, neither_correct]
})
print("\n[INFO] Summary of prediction differences:\n", summary_table)

# --- Heatmap for top differences ---
diff_indices = [i for i, (b,e,g) in enumerate(zip(baseline_list, ed2_list, gold_list)) if b != e]
top_n = 20
diff_indices = diff_indices[:top_n]

words = [gold_list[i] for i in diff_indices]
baseline_preds = [baseline_list[i] for i in diff_indices]
ed2_preds = [ed2_list[i] for i in diff_indices]
gold_words = [gold_list[i] for i in diff_indices]
frequencies = [word_freq[g] for g in gold_words]

data = pd.DataFrame({
    "Baseline": [1 if b==g else 0 for b,g in zip(baseline_preds, gold_words)],
    "ED2": [1 if e==g else 0 for e,g in zip(ed2_preds, gold_words)],
}, index=words)

annotations = pd.DataFrame({
    "Baseline": [f"{freq}" if b==0 else "" for b,freq in zip(data["Baseline"], frequencies)],
    "ED2": [f"{freq}" if e==0 else "" for e,freq in zip(data["ED2"], frequencies)]
}, index=words)

plt.figure(figsize=(10, len(words)*0.6))
sns.heatmap(data, annot=annotations, fmt='', cmap="Greens", cbar=False, linewidths=0.5, linecolor='gray')
plt.title("Enhanced Correctness Heatmap with Word Frequencies")
plt.xlabel("Model")
plt.ylabel("Word")
plt.tight_layout()
plt.savefig("plots/enhanced_baseline_vs_ed2_heatmap.png", dpi=300)
plt.show()

print("[INFO] Heatmap saved to 'plots/enhanced_baseline_vs_ed2_heatmap.png'")
