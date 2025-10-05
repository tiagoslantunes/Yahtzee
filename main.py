# main.py

# Terminal Front-End for Yahtzee
# Orchestrates user interaction and round progression.


from yahtzee import (
    create_empty_scorecard,
    display_scorecard,
    play_round,
    _upper_subtotal,
    _lower_subtotal,
    _bonus,
)

def main():
    """
    Main game loop for Yahtzee (13 rounds).

    Responsibilities:
    - Initialize the scorecard (dictionary with upper/lower categories).
    - Iterate exactly 13 rounds (each commits to one category).
    - After each round, display a formatted scorecard (subtotals and bonus).
    - At the end, compute final total = upper + bonus + lower, and report.

    Notes:
    - This function exemplifies *flow control* with a `for` loop,
      *function calls* into a logic module, and *I/O* via `print()` — the same
      building blocks introduced early. 
    """
    print("Welcome to Yahtzee!\n")
    print("Instructions:")
    print("- Each round you may roll up to 3 times.")
    print("- After each roll you can choose which dice to keep (e.g., 336).")
    print("- Then select a scoring category. Each category can be used only once.\n")

    # Create the scorecard using a dictionary comprehension in yahtzee.py: all categories -> None (sentinel for “unused”).
    card = create_empty_scorecard()

    # Fixed-length match: there are exactly 13 categories, so we run 13 rounds.
    # After each round we print the scorecard to give immediate feedback and
    # maintain user awareness of remaining categories and the bonus track.
    for rnd in range(1, 14):
        print(f"=== Round {rnd} / 13 ===")
        play_round(card)  # one category is filled inside this call
        display_scorecard(card) # present subtotals/bonus/total progressively

    # Final tally: compute upper subtotal, apply bonus policy, add lower subtotal.
    # Keeping the arithmetic here (rather than inside display) makes the flow explicit.
    up = _upper_subtotal(card)
    b  = _bonus(up)
    low = _lower_subtotal(card)
    final_total = up + b + low
    
    # Closing summary with clearly labeled components, then the grand total.
    print("\nGame over!")
    print(f"Upper subtotal : {up}")
    print(f"Bonus          : {b}")
    print(f"Lower subtotal : {low}")
    print(f"Final score    : {final_total}")
    
if __name__ == "__main__":
    main()
