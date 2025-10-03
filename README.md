
# 🎲 Yahtzee (Python Implementation)

This project is a simplified **Yahtzee game** implemented in Python for the Programming for Data Science course.  
It demonstrates core programming concepts such as functions, loops, dictionaries, comprehensions, and modular design.

---

## 📂 Project Structure

```

.
├── yahtzee.py   # Game logic: dice rolling, scoring, and scorecard utilities
├── main.py      # Terminal front-end: user interaction and game loop
└── README.md    # Project documentation (this file)

````

- **`yahtzee.py`**  
  Pure functions that implement the computational rules of Yahtzee:
  - Rolling and re-rolling dice  
  - Parsing and validating user input  
  - Detecting straights, kinds, full house, etc.  
  - Evaluating scores across categories  
  - Maintaining and displaying the scorecard  

- **`main.py`**  
  The orchestration layer that:
  - Runs the main game loop (13 rounds)  
  - Interacts with the player through the terminal  
  - Updates the scorecard and shows progress after each round  

---

## ▶️ How to Run

1. Make sure you have **Python 3.10+** installed.  
   (Type `python --version` in your terminal to check.)

2. Clone or download the project folder.  

3. Run the game from the terminal


## 🎮 Rules Recap

* You play **13 rounds** (one per category).
* Each round:

  1. You roll 5 dice (up to 3 times).
  2. After each roll, you can choose which dice to **keep** (e.g., typing `336` keeps [3, 3, 6]).
  3. After the final roll, you must assign the result to one scoring category.
* Each category can only be used **once**.
* Categories follow standard Yahtzee rules:

  * **Upper Section (1–6):** sum of dice showing that number.
  * **Three of a Kind / Four of a Kind:** sum of all dice if condition met.
  * **Full House (3+2):** 25 points.
  * **Small Straight (4 in a row):** 30 points.
  * **Large Straight (5 in a row):** 40 points.
  * **Yahtzee (all 5 equal):** 50 points.
  * **Chance:** sum of all dice.
* Bonus: +35 points if upper section subtotal ≥ 63.

---

## 🧑‍💻 Programming Concepts Illustrated

This assignment was designed to practice:

* **Functions & Docstrings** (clear contracts and behaviour)
* **Data structures** (`list`, `dict`, `Counter`)
* **Control flow** (loops, conditionals, defensive checks)
* **Dictionary comprehension** for empty scorecards
* **Modular design:** separating logic (`yahtzee.py`) from UI (`main.py`)
* **Standard library usage only:** `random`, `collections.Counter`

---

## 📸 Example Session

```
Welcome to Yahtzee!

=== Round 1 / 13 ===
Roll #1: [1, 3, 3, 4, 6]
Current dice: [1, 3, 3, 4, 6]
Type dice to KEEP (e.g., 336), or press Enter to keep none: 33
Roll #2: [3, 3, 4, 5, 6]
Stop here? (y/N): n
Locked (must keep at least): [3, 3]
Type dice to KEEP ... : 33456
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
Choose a number: 
```

```
