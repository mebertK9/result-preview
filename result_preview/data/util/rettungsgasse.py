#!/usr/bin/env python3

COLS = 4


class Rettungsgasse:
    """
    Manages the rescue-lane grid for a single game instance.

    Parameters
    ----------
    rows           : total number of rows in the grid
    mandatory_rows : number of rows that must contain both a guest and a lion car
    """

    def __init__(self, rows: int, mandatory_rows: int) -> None:
        if mandatory_rows > rows:
            raise ValueError("mandatory_rows must be less than rows")
        self.rows = rows
        self.mandatory_rows = mandatory_rows
        self.grid: list[list[dict]] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def init_grid(
        self,
        lion_games: list[dict],
        all_comp_games: list[dict | None],
    ) -> list[list[dict]]:
        """Creates and returns the initial grid state."""
        self.grid = [[{} for _ in range(COLS)] for _ in range(self.rows)]

        for r in range(self.mandatory_rows):
            guest_index = all_comp_games[r]["idx"]
            self.grid[r][1] = {"idx": guest_index, "type": "left", "lane": 1}

            lion_index = lion_games[r]["idx"]
            self.grid[r][2] = {"idx": lion_index, "type": "right", "lane": 2}

        for r in range(self.mandatory_rows, self.rows):
            if r < len(all_comp_games) and all_comp_games[r] is not None:
                guest_index = all_comp_games[r]["idx"]
                self.grid[r][0] = {"idx": guest_index, "type": "left", "lane": 0}

            lion_index = lion_games[r]["idx"]
            self.grid[r][3] = {"idx": lion_index, "type": "right", "lane": 3}

        return self.grid

    def apply_action(self, r: int, kind: str, s: str) -> list[list[dict]]:
        """
        Applies a player action to row *r* and returns the updated grid.

        For rows with guest and lion (r < mandatory_rows):
            kind="G" / kind="L" selects which car to move.
        For rows with lion only (r >= mandatory_rows):
            kind must be "L".

        Action codes
        ------------
        G – N : move guest left  (lane 1 -> 0)
        G – S : move guest to the first free mandatory-target slot
        L – S : move lion  right (lane 2 -> 3)
        L – N : move lion  to the first free mandatory-target slot
        """
        if kind not in ("G", "L") or s not in ("S", "N", ""):
            raise ValueError(
                f"Invalid kind or action: kind={kind!r}, s={s!r}"
            )

        action_g = s if kind == "G" else None
        action_l = s if kind == "L" else None

        if self._is_guest(self.grid[r][1]):
            to_move = self.grid[r][1]
            if action_g == "N":
                to_move["lane"] = 0
                self.grid[r][0] = to_move
                self.grid[r][1] = {}
            if action_g == "S":
                if self._place_in_mandatory_target(to_move):
                    to_move["lane"] = 0
                    self.grid[r][0] = to_move
                    self.grid[r][1] = {}


        if self._is_lion(self.grid[r][2]):
            to_move = self.grid[r][2]
            if action_l == "S":
                to_move["lane"] = 3
                self.grid[r][3] = to_move
                self.grid[r][2] = {}
            if action_l == "N":
                if self._place_in_mandatory_target(to_move):
                    to_move["lane"] = 3
                    self.grid[r][3] = to_move
                    self.grid[r][2] = {}

        return self.grid

    def print_table(self) -> None:
        """Prints the current grid to stdout."""
        for r in self.grid:
            row = ""
            for car in r:
                row += "|"
                if car == {}:
                    row += " --------- "
                else:
                    row += f" {car['type']} ({car['idx']}) "
            row += "|"
            print(row)
        print()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_lion(self, car: dict) -> bool:
        return car != {} and car["type"] == "right"

    def _is_guest(self, car: dict) -> bool:
        return car != {} and car["type"] == "left"

    def _place_in_mandatory_target(self, moving_car: dict) -> bool:
        """
        Places *moving_car* in the first free target slot below the
        mandatory rows (lane 3 -> lane 1 swap).  Returns True on success.
        """
        for r in range(self.mandatory_rows, self.rows):
            if self.grid[r][1] == {} and self.grid[r][2] == {}:
                waiting_car_left = self.grid[r][0]
                waiting_car_left["lane"] = 1
                self.grid[r][1] = waiting_car_left
            
                waiting_car_right = self.grid[r][3]
                waiting_car_right["lane"] = 2
                self.grid[r][2] = waiting_car_right

                self.mandatory_rows = r

                return True
        return False