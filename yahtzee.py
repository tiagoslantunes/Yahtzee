# yahtzee.py


# Yahtzee Game Logic 

# This module encapsulates the computational logic of the game (pure functions, plus small I/O helpers). 
# - We use *functions* with explicit docstrings to describe contracts and behaviour. ("Functions" & documentation)  [1]
# - We employ *built-in data structures* (lists, dicts) and standard control-flow (ifs/loops).  [2][3]
# - We demonstrate *dictionary comprehension* to construct an empty scorecard mapping all categories to a sentinel `None`.  [2]
# - We rely on the *Python Standard Library* only (no third-party libs): `random` for dice, `collections.Counter` for counting multiplicities. [3]

# [1] Functions & docstrings.
# [2] Data types (lists/dicts), comprehensions, slices, typecast.
# [3] Importing modules from the standard library, namespaces.


from collections import Counter     # Standard counting Abstract Data Type for multiplicities [3]
import random                       # Pseudo-Random Number Generator for dice rolls (uniform 1..6) [3]


# Canonical Category Definitions

# Note: we separate *upper* and *lower* sections as two lists so we can compute subtotals and bonus cleanly using membership.

UPPER_CATEGORIES = ['1', '2', '3', '4', '5', '6']
LOWER_CATEGORIES = [
    'three_of_a_kind',
    'four_of_a_kind',
    'full_house',
    'four_straight',
    'five_straight',
    'yahtzee',
    'chance',
]
# Concatenate via list addition to preserve order
ALL_CATEGORIES = UPPER_CATEGORIES + LOWER_CATEGORIES


def roll_dice(n: int = 5) -> list[int]:
    """
    Roll `n` unbiased six-faced dice.

    Returns:
    list[int]
        A Python list with `n` integer outcomes in [1, 6].

    Notes:
    - Uses `random.randint(1, 6)` from the standard library (no third-party).
    - The list is a suitable *sequence* for further transformations (slicing, sorting, counting)
    """
    # Control-flow: list comprehension to compactly generate `n` samples. This is both idiomatic and efficient.
    return [random.randint(1, 6) for _ in range(n)]


def create_empty_scorecard() -> dict[str, int | None]:
    """
    Construct an empty Yahtzee scorecard.

    Returns:
    dict[str, int|None]
        A dictionary mapping every category key to `None`. `None` is used as a sentinel to indicate "unused".

    Implementation Detail (didactic):
    We employ a *dictionary comprehension*:
        {k: None for k in ALL_CATEGORIES}
    This expression iterates over the sequence `ALL_CATEGORIES` and
    binds each key `k` to `None`, yielding a new dictionary, i.e., a
    "comprehension dictionary for the empty scoreboard (upper+lower)". 
    """
    return {k: None for k in ALL_CATEGORIES}


def _parse_keep_string(s: str | None) -> list[int] | None:
    """
    Parse a multiset-encoding string of kept dice (e.g., "336" -> [3, 3, 6]).

    Parameters:
    s : str | None
        Raw user input, "" (empty string)/None correspond to "keep none".

    Returns:
    list[int] | None
        Parsed list of die faces (integers 1..6) on success.
        Returns `None` if invalid symbols are present.

    Why do we compute a helper?
    Separating parsing from prompting keeps a **clean namespace** and improves **testability** 
    """
    if not s:               # If the caller provides None or an empty string, the semantic is "keep nothing", so we return [].
        return []
    s = "".join(s.split())  # Defensive: remove *all* whitespace (not just leading/trailing) to allow flexible input (e.g., " 3 3 6 " -> "336").
    digits: list[int] = []  # We will accumulate validated digits as integers in this list.
    for ch in s:    # Iterate over each character in the cleaned string.

        # Defensive input handling: only accept characters '1'..'6'.
        if ch in '123456':
            digits.append(int(ch)) # If ch is in '123456', we convert to int and append to the result
        else:
            return None            # As soon as we encounter an invalid symbol (e.g., '0', '7', 'x'), we abort and signal invalid input by returning None.
    return digits                  # If we reach this point, every character was a valid die face.


def select_keep(dice: list[int]) -> list[int]:
    """
    Prompt the player to select which dice to **keep** (up to two re-rolls later).

    Parameters:
    dice : list[int]
        Current 5-dice roll.

    Returns:
    list[int]
        A list representing a *sub-multiset* of `dice` that the player keeps.

    Input Contract & Validation:
    - Input is a multiset string, e.g., "336" means keep two 3s and one 6.
    - We validate that the chosen multiset is contained in the rolled dice, using `collections.Counter` to compare **multiplicities** 
    - Robustness: Any invalid character, or requesting dice not present, triggers a clear message and re-prompt (no crashes).
    """
    while True:  # While loop until a valid selection is provided. 
        print(f"Current dice: {dice}")
        raw = input("Type dice to KEEP (e.g., 336), or press Enter to keep none: ") # Read raw user input for the multiset-encoding of kept dice.
        kept = _parse_keep_string(raw)
        
        if kept is None:
            print("Invalid input: use only digits 1–6. Try again.") # If parsing failed, we provide feedback and restart the loop.
            continue

        # Verify multiset containment via Counters (hash-table semantics)
        # At this point, `kept` is a well-typed list[int] but might still be semantically invalid if it requests dice that are not present in `dice`.

        # We therefore compare *multiplicities* using Counter (multiset semantics):
        
        pool = Counter(dice) # multiplicity of the actually rolled dice
        
        want = Counter(kept) # multiplicity of the requested 'kept' dice
        
        # The selection is valid iff for every face value v, want[v] <= pool[v].
        if all(want[v] <= pool[v] for v in want):  # if any requested count exceeds what's in the pool, the choice is invalid.
            return kept # Successful path: the requested sub-multiset is feasible.

            
        print("You asked to keep dice you don't have. Try again.") # Failure path: user asked to keep dice not present (e.g., extra copies).
       


def reroll(dice: list[int], kept: list[int]) -> list[int]:
    """
    Reroll the dice that were not kept and return the new combined 5-dice hand.

    Parameters:
    dice : list[int]
        The prior (pre-reroll) 5-dice list.
    kept : list[int]
        Player-chosen sub-multiset to preserve.

    Returns:
    list[int]
        The updated, sorted 5-dice list after re-rolling the remainder.

    Notes:
    - Demonstrates basic **sequence operations**: concatenation and sorting.
    - Uses a small guard (if `kept` length > 5) to be defensive.
    """
    num_kept = len(kept) # Compute how many dice the player intends to preserve.
    
    if num_kept > len(dice):  # Defensive guard: if the caller passes more kept dice than exist in `dice`, cap to the current hand size. This prevents negative counts in the next step.
        kept = kept[:len(dice)]
        num_kept = len(kept)
        
    need = 5 - num_kept # Determine how many dice must be rolled so that total hand size remains 5.
    
    new_rolls = roll_dice(need) # Generate the required number of fresh dice using the Pseudo-Random Number Generator (uniform 1..6).
    combined = kept + new_rolls # Construct the new hand by concatenating (list concatenation) the preserved dice with the new rolls.

    # Normalize presentation/order: sorting makes the hand easier to read and simplifies downstream pattern checks (e.g., straights) when desired.
    combined.sort()  # Side-effect on list object (method vs function distinction)
    
    return combined # Return the updated 5-dice hand.


def has_straight(dice: list[int], length: int) -> bool:
    """
    Determine if `dice` contains a straight (sequence) of a given `length`.

    Parameters:
    dice : list[int]
        Hand to analyze (length 5).
    length : int
        Required sequence length (4 for small straight, 5 for large straight).

    Returns:
    bool
        True iff there is a run of consecutive integers of at least `length`.

    Algorithmic Notes (didactic):
    - Convert to a *set* to remove duplicates, then sort -> strictly increasing. 
    - Single pass counts the longest consecutive run (classic O(k) scan).
    """
    # Remove duplicates using set() (since repeated faces do not help extend a sequence) and sort ascending so consecutive values differ by exactly +1 if they belong to the same run.
    vals = sorted(set(dice))

    # Early exit: if no values remain (theoretically impossible with 5 dice, but safe for generality), there cannot be a straight.
    if not vals:
        return False

    
   
    longest = 1  # records the best streak seen so far.
    run = 1 # tracks the current consecutive streak length while scanning.
    
    # Linear scan over the strictly increasing sequence:
    for i in range(1, len(vals)):
        if vals[i] == vals[i - 1] + 1: # if the current value extends the prior by +1, we grow the streak;
            run += 1
            longest = max(longest, run) # Maintain the maximum run length encountered so far.
        else:
            # Gap detected
            run = 1                    # otherwise we reset the streak to 1 starting at the current value.
            
    return longest >= length # A straight of requested size exists iff the longest consecutive streak meets or exceeds `length` (e.g., longest>=4 for small straight).


def evaluate(dice: list[int]) -> dict[str, int]:
    """
    Compute the **score value** of the current `dice` for every category.

    Returns:
    dict[str, int]
        A dictionary score vector: category => score given this exact roll.

    Scoring Rules (Assignment Spec):
    - '1'..'6' : sum of all dice matching that face.
    - three_of_a_kind : if any face has count >= 3, score = sum(all dice), else 0.
    - four_of_a_kind  : if any face has count >= 4, score = sum(all dice), else 0.
    - full_house      : exactly counts (3, 2) -> 25, else 0.
    - four_straight   : has straight length >= 4 -> 30, else 0.
    - five_straight   : has straight length >= 5 -> 40, else 0.
    - yahtzee         : any face has count == 5 -> 50, else 0.
    - chance          : sum(all dice).

    Pedagogical Emphasis:
    - Uses `Counter` as an efficient multiset (hash-table) to query frequencies.
    - Demonstrates `for` loops, generator expressions, and function calls
      (modular decomposition) — all foundational syllabus topics. 
    """

    # Build a multiset of face frequencies, e.g., [3,3,3,5,6] -> {3:3, 5:1, 6:1}.
    counts = Counter(dice)
    
    # Sum of all dice is reused in multiple categories (3/4-kind, chance).
    total = sum(dice)
    
    # Initialize the score vector (category => numeric score for this specific roll).
    scores: dict[str, int] = {}

    # Upper section via explicit loop (could also be a dict comprehension).
    for face in range(1, 7):
        scores[str(face)] = face * counts[face] # For each face 1..6, the score is (face value) * (frequency of that face)

    # Kinds:
    
    # Three of a kind:
    # Valid iff some face appears at least 3 times; then score is sum(all dice), else 0.
    # any(c >= 3 ...) expresses “∃ face with multiplicity ≥ 3”.
    scores['three_of_a_kind'] = total if any(c >= 3 for c in counts.values()) else 0

    # Four of a kind:
    # Analogous logic with threshold 4.
    scores['four_of_a_kind']  = total if any(c >= 4 for c in counts.values()) else 0

    # Full house (3 + 2):
    # Sort the multiset cardinalities in descending order and compare to [3,2].
    cs = sorted(counts.values(), reverse=True)
    scores['full_house'] = 25 if cs == [3, 2] else 0

    # Straights:
    # Delegate detection to `has_straight`, which checks the longest consecutive run.
    # Small straight (length>=4) therefore 30; Large straight (length>=5) therefore 40.
    scores['four_straight'] = 30 if has_straight(dice, 4) else 0
    scores['five_straight'] = 40 if has_straight(dice, 5) else 0

    # Yahtzee (all five identical):
    # True iff some face has multiplicity exactly 5 therefore fixed 50 points.
    scores['yahtzee'] = 50 if any(c == 5 for c in counts.values()) else 0

    # Chance:
    # Fallback category that always scores the total of the dice (no pattern required).
    scores['chance'] = total

    return scores  # Return the complete category, score mapping for this roll.


def _upper_subtotal(card: dict[str, int | None]) -> int:
    """Sum over the *upper* keys, skipping `None` (unused).
     Generator expression iterates deterministically over the required keys (UPPER_CATEGORIES = ['1','2','3','4','5','6']). 
     For each key `k`, we include card[k] in the sum only if the entry is not None (i.e., the category has been scored). Using a comprehension.
     This avoids treating "unused" as zero and matches the scorecard semantics."""
    
    return sum(card[k] for k in UPPER_CATEGORIES if card[k] is not None)


def _lower_subtotal(card: dict[str, int | None]) -> int:
    """Sum over the *lower* keys, skipping `None` (unused).
    Same pattern as above, but over the lower section categories."""
    return sum(card[k] for k in LOWER_CATEGORIES if card[k] is not None)


def _bonus(upper_subtotal: int) -> int:
    """Upper-section bonus policy: +35 iff subtotal >= 63.
    Conditional expression (ternary): return 35 when the threshold condition
    is satisfied, else 0. Using >= implements the inclusive policy “at least 63”."""
    
    return 35 if upper_subtotal >= 63 else 0


def _fmt(v: int | None) -> str:
    """Human-readable rendering for score entries.
    Map internal sentinel None (meaning “unused category”) to a dash "-". Otherwise,
    convert the integer to a string for display. This keeps presentation concerns localized to one helper."""
    return "-" if v is None else str(v)


def display_scorecard(card: dict[str, int | None]) -> None:
    """
    Pretty-print the current scorecard, including:
    - Upper subtotal, bonus (threshold 63), lower subtotal, and total.

    Notes:
    - Simple I/O with `print()` and string formatting 
    """
    print("\n=== SCORECARD ===")
    # Upper (1..6)
    print("Upper Section")
    for k in UPPER_CATEGORIES:
        # Iterate in canonical order to match the specification and user expectations.
        # Format specifier `:>1` right-aligns the single-character key within width 1.
        print(f"  {k:>1}: {_fmt(card[k])}")

    # Compute upper subtotal and bonus via dedicated helpers to keep this function focused on presentation.
    up = _upper_subtotal(card)
    b  = _bonus(up)
    print(f"  Subtotal (1–6): {up}")
    print(f"  Bonus (+35 if >=63): {b}")

    
    # Lower (combinatorics)
    print("\nLower Section")
    # Dictinary with readable labels for lower categories.
    # We keep a mapping separate from internal keys to decouple display text (localizable) from logic keys.
    labels = {
        'three_of_a_kind': 'Three of a Kind',
        'four_of_a_kind':  'Four of a Kind',
        'full_house':      'Full House (25)',
        'four_straight':   'Four Straight (30)',
        'five_straight':   'Five Straight (40)',
        'yahtzee':         'Yahtzee (50)',
        'chance':          'Chance',
    }
    for k in LOWER_CATEGORIES:
        # Left-align each label within 20 characters for a neat column;  `_fmt` renders None as "-" so unused categories are visually distinct.
        print(f"  {labels[k]:<20} : {_fmt(card[k])}")

    
    # Totals 
    # Lower subtotal and grand total. Keeping these computations at the end matches the visual flow of the printed sheet and avoids duplicated work.
    low = _lower_subtotal(card)
    total = up + b + low

    print("\n---") # A thin separator before the summary block to improve scannability.
    
    # Consistent label alignment improves readability in monospaced terminals.
    print(f"Upper subtotal : {up}")
    print(f"Bonus          : {b}")
    print(f"Lower subtotal : {low}")
    print(f"TOTAL          : {total}")
    print("=================\n")


def choose(scores: dict[str, int], used: set[str]) -> str:
    """
    Display the available scoring categories and obtain a valid user choice.

    Behavior:
    - Builds a numbered menu of categories that are not yet used (order preserved from `ALL_CATEGORIES`).
    - Prompts the user to enter the **number** of the desired option.
    - Validates the input (must be a digit and within the menu range).
    - Returns the key of the chosen category (e.g., 'full_house').

    Parameters:
    scores : dict[str, int]
        The score vector for the current roll (from `evaluate(dice)`).
        Used only to display the potential score for each category.
    used : set[str]
        Categories already filled in the scorecard (thus unavailable).

    Returns:
    str
        The key of the chosen category (e.g., 'three_of_a_kind').

    Implementation Notes:
    - `avail` is derived from `ALL_CATEGORIES` to preserve canonical order.
    - Validation is two-step: format (digit) and valid range [1..len(avail)].
    """
    # Filter categories that remain available (not in `used`), preserving order.
    avail = [k for k in ALL_CATEGORIES if k not in used]

    # Display numbered menu (1..N) with potential scores for this roll.
    print("\nAvailable categories for this roll:")
    for idx, key in enumerate(avail, start=1):
        # idx: menu number, right-aligned in 2 spaces.
        # key: category name, left-aligned in 15 spaces.
        # scores[key]: the points this roll would score in that category.
        print(f"  {idx:>2}. {key:<15} -> {scores[key]}")

    # Validation loop: keep asking until user provides a valid option.
    while True:
        raw = input("Choose a number: ").strip() # Read raw input and trim whitespace.

        # Check 1 — must be digits only (rejects empty string, signs, letters).
        if not raw.isdigit():
            print("Please enter a number (e.g., 1, 2, ...).")
            continue

        # Safe conversion after digit check.
        choice_idx = int(raw)

        # Check 2 — must be within range [1..len(avail)].
        if 1 <= choice_idx <= len(avail):
            # Map menu number (1-based) to list index (0-based).
            return avail[choice_idx - 1]

        # Out of range: clear feedback on valid interval.
        print(f"Out of range. Enter a number between 1 and {len(avail)}.")


def play_round(card: dict[str, int | None]) -> dict[str, int | None]:
    """
    Play one **complete** Yahtzee round (≤ 3 rolls then commit to a category).

    Side Effects:
    Mutates `card` by setting exactly one category to a numeric score.

    Pedagogical Trace:
    - Demonstrates *loops* (bounded iteration with optional early exit), *conditionals*,
      modular function calls (`select_keep`, `reroll`, `evaluate`, `choose`), and
      *state mutation* within a dictionary — all core topics in introductory Python.
    """
    # Initial roll of all five dice; sort to normalize presentation and make patterns visually apparent to the player.
    dice = roll_dice(5)
    dice.sort()
    print(f"\n--- New Round ---")
    print(f"Roll #1: {dice}")

    # At most two additional rolls are allowed (roll #2 and roll #3).
    # Each iteration asks the player which dice to *keep* and re-rolls the rest.
    # We explicitly guard the "Stop here?" prompt so only 'y' or 'n' (or Enter=default 'n') are accepted.
    for roll_no in (2, 3):
        # Query the player for a sub-multiset of the current hand to preserve.
        kept = select_keep(dice)

        # Produce a new 5-dice hand by re-rolling the complement of `kept`.
        dice = reroll(dice, kept)
        print(f"Roll #{roll_no}: {dice}")

        # Offer an early stop only after roll #2 (optional). By the rules, after roll #3 we must stop, so no prompt is shown then.
        if roll_no < 3:
            # IMPORTANT clarification: advise that answering 'n' (or pressing Enter)
            # performs the next (final) roll while *preserving the same `kept` selection*
            # the player just chose. This makes the third roll deterministic with respect to the previous keep decision.
            while True:
                ans = input("Stop here? (y/N): ").strip().lower() # Read and clean input.

                # Defensive input handling: we explicitly guard acceptable inputs.
                # Empty string defaults to 'n' (as conventional `(y/N)` semantics indicate).
                if ans == "":
                    ans = "n"

                if ans in {"y", "n"}:
                    break  # Validated input; proceed to branch below.
                else:
                    print("Please answer with 'y' (yes) or 'n' (no).")

            if ans == "y":
                # Early commit: keep the current hand; do not consume the remaining roll.
                break
            else:
                # Explicitly model the third (final) roll using the SAME `kept` multiset.
                # Didactic point: this encodes the *policy guarantee* that declining to stop
                # will *preserve* the keep set for the next roll, avoiding another prompt.
                dice = reroll(dice, kept)
                print(f"Roll #3: {dice}")
                break  # We have reached the maximum number of rolls.

    # Compute the per-category scores for the final hand (pure function).
    scores_now = evaluate(dice)

    # Derive the set of categories already filled so we present only feasible choices (no double assignment).
    used = {k for k, v in card.items() if v is not None}

    # Let the player pick among the remaining categories, with validation.
    choice = choose(scores_now, used)

    # Commit: mutate the scorecard by recording the chosen category's score for THIS round only.
    #  Exactly one category is filled per round.
    card[choice] = scores_now[choice]

    # Immediate feedback to the player for transparency.
    print(f"You scored {scores_now[choice]} points in '{choice}'.")

    # Return the updated scorecard so the caller (main loop) can display it.
    return card
 
