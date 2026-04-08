#!/usr/bin/env python3

ROWS = 7
COLS = 4

def print_table(grid):
    print()
    for r in range(ROWS):
        size = ROWS -1
        print(" | ".join(grid[size - r]))
    print()

def place_in_row6_or_7(grid, token) -> bool:
    moved = False
    if grid[5][0] == "-":
        grid[5][0] = token
        moved = True
    elif grid[6][0] == "-":
        grid[6][0] = token
        moved = True
    return moved

def main():
    # Tabelle initialisieren
    grid = [["-" for _ in range(COLS)] for _ in range(ROWS)]

    # Reihen 1-5
    for r in range(5):
        grid[r][1] = "G"
        grid[r][2] = "L"

    # Reihen 6-7
    grid[5][2] = "L"
    grid[6][2] = "L"

    print("Startzustand:")
    print_table(grid)

    for r in range(ROWS):
        if r < 5:
            # zwei Eingaben: G und L
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
                    if(place_in_row6_or_7(grid, "G")):
                        grid[r][1] = "-"

            # --- L ---
            if grid[r][2] == "L":
                if action_l == "S":
                    grid[r][3] = "L"
                    grid[r][2] = "-"
                else:  # N
                    if(place_in_row6_or_7(grid, "L")):
                        grid[r][2] = "-"    

        else:
            # nur L in Reihe 6-7
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
                    if(place_in_row6_or_7(grid, "L")):
                        grid[r][2] = "-"

        print_table(grid)

if __name__ == "__main__":
    main()