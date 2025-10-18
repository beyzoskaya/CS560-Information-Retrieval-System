from spell_corrector import edits1, known

# Frequency-threshold enhanced corrector
def correct_with_frequency_threshold(word, word_freq, min_freq=2, debug=False, analysis_file=None):

    if debug: print(f"\n[PROCESSING - frequency threshold] '{word}'")

    candidates = edits1(word, debug)
    known_candidates = known(candidates, word_freq)
    filtered_candidates = set(w for w in known_candidates if word_freq[w] >= min_freq)

    if analysis_file:
        analysis_file.write(f"Word: {word}\n")
        analysis_file.write(f"Total generated candidates: {len(candidates)}\n")
        analysis_file.write(f"Known candidates ({len(known_candidates)}):\n")
        for w in sorted(known_candidates):
            analysis_file.write(f"   {w:<15} freq={word_freq[w]}\n")
        analysis_file.write(f"Filtered candidates (freq >= {min_freq}): {len(filtered_candidates)}\n")
        for w in sorted(filtered_candidates):
            analysis_file.write(f"   {w:<15} freq={word_freq[w]}\n")

    if not filtered_candidates:
        if debug: print("  [DEBUG] No candidates pass frequency threshold.")
        if analysis_file:
            analysis_file.write("=> No candidates pass threshold. Output: (blank line)\n\n")
        return ""

    # Pick best candidate (highest frequency, tie-breaker by shorter word then alphabetically)
    best = max(filtered_candidates, key=lambda w: (word_freq[w], -len(w), w))

    if debug:
        print(f"  [DEBUG] {len(filtered_candidates)} candidates pass threshold. Best: '{best}' (freq: {word_freq[best]})")

    if analysis_file:
        analysis_file.write(f"=> Selected best candidate: {best} (freq={word_freq[best]})\n\n")

    return best

def correct_with_first_letter(word, word_freq, debug=False, analysis_file=None):
    """
    Baseline spelling corrector with first-letter heuristic stacked:
    - Generates all edit-distance-1 candidates
    - Keeps known words
    - Picks the candidate with highest frequency (baseline)
    - If multiple candidates have same max frequency, prefer those with same first letter
    """
    if debug: print(f"\n[PROCESSING - first-letter stacked heuristic] '{word}'")

    candidates = edits1(word, debug)
    known_candidates = known(candidates, word_freq)

    if not known_candidates:
        if debug: print("  [DEBUG] No known candidates found.")
        if analysis_file:
            analysis_file.write(f"Word: {word}\n=> No known candidates found. Output: (blank line)\n\n")
        return ""

    # Find max frequency among known candidates
    max_freq = max(word_freq[w] for w in known_candidates)
    top_candidates = [w for w in known_candidates if word_freq[w] == max_freq]

    # Apply first-letter heuristic only among top candidates
    preferred_candidates = [w for w in top_candidates if w[0] == word[0]]

    if preferred_candidates:
        best_candidates = preferred_candidates
        if debug: print(f"  [DEBUG] First-letter filter applied among top frequency candidates")
    else:
        best_candidates = top_candidates
        if debug: print(f"  [DEBUG] No top candidates match first letter; using all top frequency candidates")

    best = min(best_candidates, key=lambda w: (len(w), w))

    if debug:
        print(f"  [DEBUG] Selected best candidate: '{best}' (freq={word_freq[best]})")

    if analysis_file:
        analysis_file.write(f"Word: {word}\n")
        analysis_file.write(f"Total generated candidates: {len(candidates)}\n")
        analysis_file.write(f"Known candidates ({len(known_candidates)}):\n")
        for w in sorted(known_candidates):
            analysis_file.write(f"   {w:<15} freq={word_freq[w]}\n")
        analysis_file.write(f"Top frequency candidates (freq={max_freq}): {len(top_candidates)}\n")
        for w in sorted(top_candidates):
            analysis_file.write(f"   {w:<15} freq={word_freq[w]}\n")
        if preferred_candidates:
            analysis_file.write(f"Preferred candidates (same first letter '{word[0]}'): {len(preferred_candidates)}\n")
            for w in sorted(preferred_candidates):
                analysis_file.write(f"   {w:<15} freq={word_freq[w]}\n")
        analysis_file.write(f"=> Selected best candidate: {best} (freq={word_freq[best]})\n\n")

    return best

def correct_with_vowel_replacement(word, word_freq, debug=False, analysis_file=None):
    """
    Baseline spelling corrector with vowel-replacement heuristic:
    - Generates edit-distance-1 candidates
    - Adds vowel-replaced candidates
    - Picks highest-frequency known candidate
    """
    vowels = 'aeiou'

    if debug: print(f"\n[PROCESSING - vowel replacement heuristic] '{word}'")

    candidates = edits1(word, debug)
    known_candidates = known(candidates, word_freq)

    vowel_candidates = set()
    for w in known_candidates.union({word}): 
        w_list = list(w)
        for i, c in enumerate(w_list):
            if c in vowels:
                for v in vowels:
                    if v != c:
                        new_word = w[:i] + v + w[i+1:]
                        vowel_candidates.add(new_word)

    known_vowel_candidates = known(vowel_candidates, word_freq)

    all_candidates = known_candidates.union(known_vowel_candidates)

    if not all_candidates:
        if debug: print("  [DEBUG] No known candidates found.")
        if analysis_file:
            analysis_file.write(f"Word: {word}\n=> No known candidates found. Output: (blank line)\n\n")
        return ""
    
    max_freq = max(word_freq[w] for w in all_candidates)
    top_candidates = [w for w in all_candidates if word_freq[w] == max_freq]
    best = min(top_candidates, key=lambda w: (len(w), w))

    if debug:
        print(f"  [DEBUG] {len(all_candidates)} candidates considered. Best: '{best}' (freq={word_freq[best]})")

    if analysis_file:
        analysis_file.write(f"Word: {word}\n")
        analysis_file.write(f"Baseline known candidates ({len(known_candidates)}): {sorted(known_candidates)}\n")
        analysis_file.write(f"Vowel-replacement known candidates ({len(known_vowel_candidates)}): {sorted(known_vowel_candidates)}\n")
        analysis_file.write(f"=> Selected best candidate: {best} (freq={word_freq[best]})\n\n")

    return best