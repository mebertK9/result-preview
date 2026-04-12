#!/usr/bin/env python3

ROWS = 7
COLS = 4
MANDATORY_ROWS = 5   # Reihen mit G und L

def print_table(grid):
    for r in grid:
        row = ""
        for car in r:
            row = row + "|"
            if car == {}:
                row = row + " --------- "
            else:
                row = row + f" {car['type']} ({car['idx']}) "
        row = row + "|"
        print(row)
    print()


def place_in_mandatory_target(grid, token) -> bool:
    """
    platziert in den ersten freien Zielreihen unterhalb der mandatory rows
    (hier: Reihe 6, dann 7)
    """
    for r in range(MANDATORY_ROWS, ROWS):
        if grid[r][0] == {}:
            token["lane"] = 0
            grid[r][0] = token
            return True
    return False


def init_grid(loewen_games: list[dict], all_comp_games: list[dict | None]) -> list[list[str]]:
    """Creates and returns the initial grid state."""
    grid = [[{} for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(MANDATORY_ROWS):
        guest_index = all_comp_games[r]["idx"]
        grid[r][1] = {
            "idx": guest_index,
            "type": "left",
            "lane": 1
        }
        loewen_index= loewen_games[r]["idx"]
        grid[r][2] = {
            "idx": loewen_index,
            "type": "right",
            "lane": 2
        }
    for r in range(MANDATORY_ROWS, ROWS):
        loewen_index= loewen_games[r]["idx"]
        grid[r][2] = {
            "idx": loewen_index,
            "type": "right",
            "lane": 2
        }

    print("init grid:")
    print_table(grid)

    return grid


def update_grid(grid, loewen_games: list[dict], all_comp_games: dict[str, list[dict | None]]) -> list[list[str]]:
    """Creates and returns the initial grid state."""

    for r in range(MANDATORY_ROWS):
        guest_index = all_comp_games[r].idx
        grid[MANDATORY_ROWS-1-r][1] = {
            "idx": guest_index,
            "type": "right",
            "lane": 1
        }
        loewen_index= loewen_games[r].idx
        grid[MANDATORY_ROWS-1-r][2] = {
            "idx": loewen_index,
            "type": "left",
            "lane": 2
        }
    for r in range(MANDATORY_ROWS, ROWS):
        loewen_index= loewen_games[r].idx
        grid[r][2] = {
            "idx": loewen_index,
            "type": "right",
            "lane": 2
        }

    print("init grid:")
    print_table(grid)

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
    if kind not in ("G", "L") or s not in ("S", "N", ""):
        raise ValueError(f"Invalid car type (kind) or action: kind={kind}, s={s}")
    
    def is_loewe(car):
        return car != {} and car["type"] == "right"
    def is_gegner(car):
        return car != {} and car["type"] == "left"

    if r < MANDATORY_ROWS:
        action_l = action_g = ""
        if(kind == "G"):
            action_g = s
            action_l = ""
        elif(kind == "L"):
            action_l = s
            action_g = ""

        if is_gegner(grid[r][1]):
            to_move = grid[r][1]
            if action_g == "N":
                to_move["lane"] = 0
                grid[r][0] = to_move
                grid[r][1] = {}
            elif (action_g == "S"):
                if place_in_mandatory_target(grid, to_move): 
                    grid[r][1] = {}

        if is_loewe(grid[r][2]):
            to_move = grid[r][2]
            if action_l == "S":
                to_move["lane"] = 3
                grid[r][3] = to_move
                grid[r][2] = {}
            elif(action_l == "N"):
                if place_in_mandatory_target(grid, to_move): 
                    grid[r][2] = {}
    else:
        if is_loewe(grid[r][2]):
            to_move = grid[r][2]
            if s == "S":
                to_move["lane"] = 3
                grid[r][3] = to_move
                grid[r][2] = {}
            elif(s == "N"):
                if place_in_mandatory_target(grid, to_move): 
                    grid[r][2] = {}

    print("After movement")
    print_table(grid)

    return grid
