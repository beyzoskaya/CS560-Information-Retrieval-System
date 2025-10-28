import re
import sys
from collections import Counter
import argparse
import matplotlib.pyplot as plt

"""
Generate all candidate words C with Damerau–Levenshtein distance 1 from x (edits1(x))
Keep only known words: K = {c in C | c ∈ dictionary}
If K is empty → no single-edit correction found → output a blank line (baseline requirement)
Otherwise, choose: best = argmax_{w ∈ K} frequency(w)
meaning --> pick the known candidate with the highest frequency in the corpus
"""

def parse_args():

    parser = argparse.ArgumentParser(
        description="Spelling Corrector using Damerau–Levenshtein distance"
    )

    parser.add_argument("corpus_file", help="Path to the corpus.txt file")
    parser.add_argument("input_file", help="File containing misspelled words (one per line)")
    parser.add_argument("output_file", help="Output file to save corrected words")

    parser.add_argument(
        "--correct",
        dest="correct_file",
        help="Optional file containing correct spellings (for accuracy evaluation)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug print statements for detailed processing info",
    )

    parser.add_argument(
        "--analyze",
        metavar="analysis_output",
        help="Write detailed candidate analysis to a file",
    )

    return parser.parse_args()

# tokenization
def words(text):
    return re.findall(r"[a-z]+", text.lower())

def build_dictionary(corpus_file, debug=False):
    if debug: print(f"[INFO] Building dictionary from: {corpus_file}")
    with open(corpus_file, 'r', encoding='utf-8') as f:
        corpus = f.read().lower()
        print(f"[INFO] Corpus size: {len(corpus)} characters")
        print("[INFO] Sample from corpus:", corpus[:100] + "...")
    word_freq = Counter(words(corpus))
    if debug:
        print(f"[INFO] Dictionary built with {len(word_freq)} unique words.")
        print("[INFO] Top 5 most common words:", word_freq.most_common(5))
    return word_freq

# Damerau-Levenshtein edit distance 
def edits1(word, debug=False):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = []

    for i in range(len(word) + 1):
        left = word[:i]
        right = word[i:]
        splits.append((left, right))

    deletes = []
    transposes = []
    replaces = []
    inserts = []

    for L, R in splits:
        # Deletion: remove the first character of the right part 
        if R:
            new_word = L + R[1:]
            deletes.append(new_word)
            print(f"[DEBUG] Deletion: {word} -> {new_word}")

        # Transposition: swap the first two characters of the right part 
        if len(R) > 1:
            new_word = L + R[1] + R[0] + R[2:]
            transposes.append(new_word)
            print(f"[DEBUG] Transposition: {word} -> {new_word}")

        # Replacement: replace first character of right part with each letter
        if R:
            for c in letters:
                new_word = L + c + R[1:]
                replaces.append(new_word)
                print(f"[DEBUG] Replacement: {word} -> {new_word}")

        # Insertion: insert each possible letter between left and right 
        for c in letters:
            new_word = L + c + R
            inserts.append(new_word)
            print(f"[DEBUG] Insertion: {word} -> {new_word}")

    all_edits = set(deletes + transposes + replaces + inserts)
    if debug:
        print(f"[DEBUG] {word} -> generated {len(all_edits)} edits")
    return all_edits

def edits2(word, debug=False):

    edit2_set = set()
    for e1 in edits1(word, debug):
        edit2_set.update(edits1(e1, debug))
    return edit2_set

def known(words, word_freq):

    known_words = set() 

    for w in words:
        if w in word_freq:
            known_words.add(w)

    return known_words

def correct(word, word_freq, debug=False, analysis_file=None):
    if debug: print(f"\n[PROCESSING] '{word}'")

    candidates = edits1(word, debug)
    known_candidates = known(candidates, word_freq)
    print(f"[DEBUG] Candidates generated: {len(candidates)}")
    print("[DEBUG] Known candidates found:", known_candidates)
    print("[DEBUG] Example frequencies:", {w: word_freq[w] for w in list(known_candidates)[:5]})

    if analysis_file:
        analysis_file.write(f"Word: {word}\n")
        analysis_file.write(f"Total generated candidates: {len(candidates)}\n")
        analysis_file.write(f"Known candidates ({len(known_candidates)}):\n")
        for w in sorted(known_candidates):
            analysis_file.write(f"   {w:<15} freq={word_freq[w]}\n")

    if not known_candidates:
        if debug: print("  [DEBUG] No known candidates found.")
        if analysis_file:
            analysis_file.write("=> No known candidates found. Output: (blank line)\n\n")
        return ""

    # best by highest frequency, tie-break by shorter word then alphabetically
    best = max(known_candidates, key=lambda w: (word_freq[w], -len(w), w))

    if debug:
        print(f"  [DEBUG] {len(known_candidates)} known candidate(s). Best: '{best}' (freq: {word_freq[best]})")

    if analysis_file:
        analysis_file.write(f"=> Selected best candidate: {best} (freq={word_freq[best]})\n\n")

    return best

def correct_with_ed2_fallback(word, word_freq, debug=False, analysis_file=None):
    """
    Baseline spelling corrector with edit-distance-2 fallback:
    - Step 1: generate edit-distance-1 candidates
    - Step 2: keep known words
    - Step 3: if no candidates found, generate edit-distance-2 candidates
    - Step 4: pick highest-frequency known candidate
    """
    if debug: print(f"\n[PROCESSING - ED2 fallback] '{word}'")

    candidates = edits1(word, debug)
    known_candidates = known(candidates, word_freq)

    if not known_candidates:
        if debug: print("  [DEBUG] No known candidates in edits1, trying edits2...")
        ed2_candidates = edits2(word, debug)
        known_candidates = known(ed2_candidates, word_freq)
        if not known_candidates:
            if debug: print("  [DEBUG] No known candidates found in edits2.")
            if analysis_file:
                analysis_file.write(f"Word: {word}\n=> No candidates found in edits1 or edits2. Output: (blank line)\n\n")
            return ""
        
    max_freq = max(word_freq[w] for w in known_candidates)
    top_candidates = [w for w in known_candidates if word_freq[w] == max_freq]
    best = min(top_candidates, key=lambda w: (len(w), w))

    if debug:
        print(f"  [DEBUG] Selected best candidate: '{best}' (freq={word_freq[best]})")

    if analysis_file:
        analysis_file.write(f"Word: {word}\n")
        analysis_file.write(f"Known candidates considered: {len(known_candidates)}\n")
        for w in sorted(known_candidates):
            analysis_file.write(f"   {w:<15} freq={word_freq[w]}\n")
        analysis_file.write(f"=> Selected best candidate: {best} (freq={word_freq[best]})\n\n")

    return best

def correct_file(input_file, output_file, word_freq, debug=False, analysis_output=None,
                 use_ed2_fallback=False):
    if debug: print(f"[INFO] Correcting words from: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        misspelled = [line.strip().lower() for line in f]

    analysis_file = None
    if analysis_output:
        if use_ed2_fallback:
            parts = analysis_output.rsplit('.', 1)
            analysis_file_name = parts[0] + "_ed2.txt" if len(parts) > 1 else analysis_output + "_ed2.txt"
        else:
            analysis_file_name = analysis_output
        analysis_file = open(analysis_file_name, 'w', encoding='utf-8')

    corrected = []
    for word in misspelled:
        if not word.strip():
            corrected.append("")
            continue
        if use_ed2_fallback:
            corrected_word = correct_with_ed2_fallback(word, word_freq, debug, analysis_file)
        else:
            corrected_word = correct(word, word_freq, debug, analysis_file)
        corrected.append(corrected_word)

    with open(output_file, 'w', encoding='utf-8') as f:
        for c in corrected:
            f.write(c + "\n")

    if analysis_file:
        analysis_file.close()
        print(f"[INFO] Detailed analysis saved to {analysis_file_name}")

    if debug: print(f"[INFO] Correction complete. Output saved to: {output_file}")

def compute_accuracy(predicted_file, gold_file):
    with open(predicted_file, 'r', encoding='utf-8') as f1, \
         open(gold_file, 'r', encoding='utf-8') as f2:
        pred = [line.strip() for line in f1]
        gold = [line.strip() for line in f2]
    total = len(gold)
    correct = sum(1 for p, g in zip(pred, gold) if p == g)
    accuracy = correct / total if total > 0 else 0.0
    print(f"[RESULT] Accuracy: {accuracy*100:.2f}% ({correct}/{total})")
    return accuracy

def compare_outputs(baseline_file, ed2_file, gold_file=None, diff_output_file="outputs/differences.txt"):

    with open(baseline_file, 'r', encoding='utf-8') as f:
        baseline = [line.strip() for line in f]

    with open(ed2_file, 'r', encoding='utf-8') as f:
        ed2 = [line.strip() for line in f]

    gold = None
    if gold_file:
        with open(gold_file, 'r', encoding='utf-8') as f:
            gold = [line.strip() for line in f]

    differences = []
    for i, (b, e) in enumerate(zip(baseline, ed2)):
        if b != e:
            diff_info = f"Line {i+1}: baseline='{b}' | ED2='{e}'"
            if gold:
                diff_info += f" | correct='{gold[i]}'"
            differences.append(diff_info)

    with open(diff_output_file, 'w', encoding='utf-8') as f:
        for line in differences:
            f.write(line + "\n")

    print(f"[INFO] {len(differences)} differences found. Saved to {diff_output_file}")
    return differences


def print_top_differences(differences, top_n=10):

    print(f"\n[INFO] Showing top {min(top_n, len(differences))} differences:")
    print(f"{'Line':<6} | {'Baseline':<15} | {'ED2':<15} | {'Correct':<15}")
    print("-" * 60)
    
    for entry in differences[:top_n]:
        parts = entry.split('|')
        line_num = parts[0].split()[1].rstrip(':')
        baseline = parts[1].split('=')[1].strip("' ")
        ed2 = parts[2].split('=')[1].strip("' ")
        correct = parts[3].split('=')[1].strip("' ") if len(parts) > 3 else ''
        print(f"{line_num:<6} | {baseline:<15} | {ed2:<15} | {correct:<15}")

def main():
    args = parse_args()
    word_freq = build_dictionary(args.corpus_file, args.debug)

    correct_file(
        args.input_file,
        args.output_file,
        word_freq,
        args.debug,
        args.analyze,
        use_ed2_fallback=False
    )
    if args.correct_file:
        print("\n[BASELINE VERSION ACCURACY]")
        compute_accuracy(args.output_file, args.correct_file)

    ed2_output = args.output_file.rsplit('.', 1)
    ed2_output = ed2_output[0] + "_ed2.txt" if len(ed2_output) > 1 else args.output_file + "_ed2.txt"

    correct_file(
        args.input_file,
        ed2_output,
        word_freq,
        args.debug,
        args.analyze,
        use_ed2_fallback=True
    )
    if args.correct_file:
        print("\n[ED2 FALLBACK HEURISTIC VERSION ACCURACY]")
        compute_accuracy(ed2_output, args.correct_file)

        differences = compare_outputs(
            baseline_file=args.output_file,
            ed2_file=ed2_output,
            gold_file=args.correct_file,
            diff_output_file="outputs/differences.txt"
        )
        print_top_differences(differences, top_n=10)

if __name__ == "__main__":
    main()

