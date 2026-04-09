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

def to_rettungswagen(grid: list[list[str]]) -> list[tuple[int | None, int | None]]:
    """
    Transforms the internal grid representation into a list of (left_pos, right_pos) tuples.

    Grid columns: 0=left shoulder, 1=left lane, 2=right lane, 3=right shoulder
    Car identifiers: "G" = left car, "L" = right car

    Position is None if the car is not present in that row (no car drawn).
    Returns a list of (G_position, L_position) per row.
    """
    result = []
    for row in grid:
        g_pos = row.index("G") if "G" in row else None
        l_pos = row.index("L") if "L" in row else None
        result.append((g_pos, l_pos))
    return result

def init_grid() -> list[list[str]]:
    """Creates and returns the initial grid state."""
    grid = [["-" for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(MANDATORY_ROWS):
        grid[r][1] = "G"
        grid[r][2] = "L"
    for r in range(MANDATORY_ROWS, ROWS):
        grid[r][2] = "L"
    return grid


def apply_action(grid: list[list[str]], r: int, kind: str, s: str) -> list[list[str]]:
    """
    Applies the player's action string to row r and returns the updated grid.

    For rows with G and L (r < MANDATORY_ROWS): s is two chars, e.g. "SN"
    For rows with L only (r >= MANDATORY_ROWS): s is one char, e.g. "S"

    Action semantics:
      G: N = move left (col 1 -> 0), S = move to mandatory target
      L: S = move right (col 2 -> 3), N = move to mandatory target
    """
    if r < MANDATORY_ROWS:
        action_l = action_g = ""
        if(kind == "G"):
            action_g = s
            action_l = ""
        elif(kind == "L"):
            action_l = s
            action_g = ""

        if grid[r][1] == "G" and action_g in ("N", "S"):
            if action_g == "N":
                grid[r][0] = "G"
                grid[r][1] = "-"
            else:
                if place_in_mandatory_target(grid, "G"):
                    grid[r][1] = "-"

        if grid[r][2] == "L" and action_l in ("N", "S"):
            if action_l == "S":
                grid[r][3] = "L"
                grid[r][2] = "-"
            else:
                if place_in_mandatory_target(grid, "L"):
                    grid[r][2] = "-"
    else:
        if grid[r][2] == "L":
            if s == "S":
                grid[r][3] = "L"
                grid[r][2] = "-"
            else:
                if place_in_mandatory_target(grid, "L"):
                    grid[r][2] = "-"

    return grid
