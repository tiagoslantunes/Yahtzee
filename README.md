# 🎲 Yahtzee — Python Implementation 
A simplified **Yahtzee** for the *Programming for Data Science* course.
It showcases functions, loops, dictionaries/`Counter`, modular design, and robust input validation.

---

## 📂 Project Structure

```
.
├── yahtzee.py   # Game logic: rolling/re-rolling, scoring, scorecard, helpers
├── main.py      # Terminal front-end: interaction loop (13 rounds), final summary
└── README.md    # This document
```

* **`yahtzee.py`** (mostly “pure” logic + small I/O helpers):

  * `roll_dice`, `reroll` — uniform RNG for 1..6 and hand recombination
  * `_parse_keep_string`, `select_keep` — parse/validate “multiset” input (e.g., `336`) with a **non-decreasing lock** on kept dice
  * `has_straight` — straight detection via `set` + one pass
  * `evaluate` — per-category score vector
  * `_upper_subtotal`, `_lower_subtotal`, `_bonus` — subtotals and bonus
  * `display_scorecard`, `choose`, `_commit` — presentation and menuing
  * `play_round` — **one full round** (≤3 rolls → choose category)

* **`main.py`** (orchestration/UX):

  * initializes the scorecard, runs **exactly 13** rounds (one per category), shows the scorecard after each round, and computes `upper + bonus + lower` at the end.

---

## ▶️ How to Run

1. Requires **Python 3.10+**
2. From the project folder:

```bash
python main.py       # or: py -3 main.py (Windows)
```

---

## 🧠 Data Model & Invariants

* **Hand**: a sorted `list[int]` with 5 dice (easier to read and to spot patterns).
* **Scorecard**: `dict[str, int | None]` with keys

  ```
  ['1','2','3','4','5','6',
   'three_of_a_kind','four_of_a_kind','full_house',
   'four_straight','five_straight','yahtzee','chance']
  ```

  All start as `None` (meaning **unused** category).

**Invariants**

* Hand size is always 5.
* Each round fills **exactly one** category.
* Bonus is +35 if upper subtotal ≥ 63.

---

## 🔩 Logic, Function by Function

### Rolling & Re-rolling

* `roll_dice(n=5)`: returns `n` uniform integers in `[1..6]` using the standard library (`random`).
* `reroll(dice, kept)`: re-rolls only the complement of `kept`, then returns the **sorted** 5-die hand. Defensive guard if `kept` length is off.

### Choosing what to keep (UX + safety)

* `_parse_keep_string(s)`: `"336"` → `[3,3,6]`. Accepts only digits `1..6`, ignores whitespace, enforces ≤ 5 digits. Returns `None` on invalid input.
* `select_keep(dice)`: prompt loop that

  * shows the current hand,
  * validates with two `Counter` checks:

    1. **Sub-multiset of the pool**: `want[v] ≤ pool[v]` (you can’t keep dice you don’t have);
    2. **Non-decreasing lock** (if set): `want[v] ≥ lock[v]` (you can’t “un-keep” what you locked previously).
  * on error, prints an exact explanation (which faces and counts failed).

> 🔒 **Why the lock?** After roll #2, if you continue to roll #3 you must keep **at least** what you already decided to keep — you may only **add**. This avoids accidental regressions and makes roll #3 deterministic relative to your roll-#2 decision.

### Straight detection

* `has_straight(dice, length)`:

  * `vals = sorted(set(dice))` removes duplicates (repeats don’t extend runs),
  * single pass counts the longest consecutive run,
  * returns `True` if `longest ≥ length` (4 ⇒ small straight, 5 ⇒ large straight).

### Category scoring

* `evaluate(dice)` builds a **score vector**:

  * **Upper 1..6**: sum of dice matching the face;
  * **Three/Four of a Kind**: if any count ≥3/≥4, score = **sum of all dice**, else 0;
  * **Full House**: sorted counts equal to `[3,2]` ⇒ 25; else 0;
  * **Four/Five Straight**: `has_straight(...,4)` ⇒ 30; `has_straight(...,5)` ⇒ 40;
  * **Yahtzee**: any count == 5 ⇒ 50;
  * **Chance**: sum of all dice.

`Counter(dice)` is the ideal multiset ADT here; `sum(dice)` is reused.

### Subtotals, bonus, display

* `_upper_subtotal(card)`, `_lower_subtotal(card)`: sum only **non-None** entries (unused categories don’t count).
* `_bonus(upper)`: `35` if `upper ≥ 63`, else `0`.
* `display_scorecard(card)`: prints upper (1..6), upper subtotal, bonus; then lower with readable labels; then the running total (`upper + bonus + lower`).

### Menu and committing a score

* `choose(scores, used)`: lists **only** still-available categories (canonical order) showing the score you’d get **for this hand**, validates numeric choice.
* `_commit(card, final_dice)`: evaluates, calls `choose`, writes to the card, and confirms the committed score.

### One complete round

* `play_round(card)`:

  1. **Roll #1** → `select_keep` (no lock) → `reroll` → **Roll #2**
  2. Ask “Stop here? (y/N)”.

     * **“y”**: evaluate and commit immediately.
     * **“n”**: set the non-decreasing **lock** from what you kept after roll #2, ask `select_keep` again under that lock → `reroll` → **Roll #3** → evaluate and commit.
* In all paths, exactly **one** category is filled.

---

## 🔁 Control Flow (text summary)

```
[Start round]
  ↓
Roll #1 → keep (free) → Reroll → Roll #2
  ↓                ┌──────── “y” ────────┐
Stop here?  — “n”  │                      │
  ↓                │                Commit & return
Lock(keep2) → keep (non-decr.) → Reroll → Roll #3 → Commit
```

---

## 🧪 Quick Tests & Edge Cases

* `_parse_keep_string("")` → `[]`; `" 3 36 "` → `[3,3,6]`; `"307"` → invalid.
* `has_straight([1,2,3,4,6],4)` → `True`; `[1,1,3,4,5]` with `length=5` → `False`.
* `evaluate([2,2,2,5,6])`: `three_of_a_kind = 17`, `full_house = 0`, `chance = 17`.
* `select_keep([3,3,4,5,6])` with lock `Counter({3:2})` rejects `keep=[3]`.

---

## 📸 Example Session (condensed)

```
=== Round 1 / 13 ===
Roll #1: [1, 3, 3, 4, 6]
Type dice to KEEP (e.g., 336): 33
Roll #2: [3, 3, 4, 5, 6]
Stop here? (y/N) or press Enter to continue: n
Locked (must keep at least): [3, 3]
Type dice to KEEP: 33456
Roll #3: [3, 3, 4, 5, 6]

Available categories for this roll:
   1. 1               -> 0
   2. 2               -> 0
   3. 3               -> 6
   4. 4               -> 4
   5. 5               -> 5
   6. 6               -> 6
   7. three_of_a_kind -> 21
   8. four_of_a_kind  -> 0
   9. full_house      -> 0
  10. four_straight   -> 30
  11. five_straight   -> 40
  12. yahtzee         -> 0
  13. chance          -> 21
Choose a number: 10
You scored 30 points in 'four_straight'.
```

---

## ✅ Assignment Compliance Checklist

* Uses only **Python standard library** (`random`, `collections.Counter`).
* Exactly **two files**: `yahtzee.py` (logic) and `main.py` (front-end).
* Implements/uses the required functions: `roll_dice`, `create_empty_scorecard`, `select_keep`, `reroll`, `has_straight`, `evaluate`, `choose`, `display_scorecard`, `play_round`.
* **13 rounds**, printing the **scorecard after each round**.
* **+35 bonus** applied iff upper subtotal ≥ 63.
* Final output clearly shows **upper subtotal**, **bonus**, **lower subtotal**, and **final total**.

---

## 💡 Design Decisions (why this way?)

* Sorting the hand improves readability and simplifies straight detection.
* `Counter` is the right ADT for multiplicities: concise checks and clear error messages.
* **Logic vs UI** separation: `yahtzee.py` is testable; `main.py` handles flow/prints only.
* Non-decreasing **lock** on roll #3 matches real gameplay intent and prevents accidental “un-keeping”.
