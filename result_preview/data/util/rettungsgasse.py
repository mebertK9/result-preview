#!/usr/bin/env python3

ROWS = 7
COLS = 4
MANDATORY_ROWS = 5   # Reihen mit G und L


def print_table(grid):
    print()
    for r in range(ROWS):
        size = ROWS - 1
        print(" | ".join(grid[size - r]))
    print()


def place_in_mandatory_target(grid, token) -> bool:
    """
    platziert in den ersten freien Zielreihen unterhalb der mandatory rows
    (hier: Reihe 6, dann 7)
    """
    for r in range(MANDATORY_ROWS, ROWS):
        if grid[r][0] == "-":
            grid[r][0] = token
            return True
    return False


def main():
    # Tabelle initialisieren
    grid = [["-" for _ in range(COLS)] for _ in range(ROWS)]

    # Reihen 1..MANDATORY_ROWS
    for r in range(MANDATORY_ROWS):
        grid[r][1] = "G"
        grid[r][2] = "L"

    # restliche Reihen: nur L
    for r in range(MANDATORY_ROWS, ROWS):
        grid[r][2] = "L"

    print("Startzustand:")
    print_table(grid)

    for r in range(ROWS):

        # -------------------------------
        # Reihen mit G und L
        # -------------------------------
        if r < MANDATORY_ROWS:

            while True:
                s = input(f"Runde {r+1} (Aktion für G,L z.B. SN): ").strip().upper()
                if len(s) == 2 and all(c in "SN" for c in s):
                    break
                print("Bitte genau zwei Zeichen S oder N eingeben.")

            action_g, action_l = s[0], s[1]

            # --- G ---
            if grid[r][1] == "G":
                if action_g == "N":
                    grid[r][0] = "G"
                    grid[r][1] = "-"
                else:  # S
                    if place_in_mandatory_target(grid, "G"):
                        grid[r][1] = "-"

            # --- L ---
            if grid[r][2] == "L":
                if action_l == "S":
                    grid[r][3] = "L"
                    grid[r][2] = "-"
                else:  # N
                    if place_in_mandatory_target(grid, "L"):
                        grid[r][2] = "-"

        # -------------------------------
        # nur L Reihen
        # -------------------------------
        else:
            while True:
                s = input(f"Runde {r+1} (Aktion für L): ").strip().upper()
                if len(s) == 1 and s in "SN":
                    break
                print("Bitte S oder N eingeben.")

            if grid[r][2] == "L":
                if s == "S":
                    grid[r][3] = "L"
                    grid[r][2] = "-"
                else:  # N
                    if place_in_mandatory_target(grid, "L"):
                        grid[r][2] = "-"

        print_table(grid)


if __name__ == "__main__":
    main()