
from collections import defaultdict

class TeamStats:
    def __init__(self):
        self.games = 0
        self.wins = 0
        self.points = 0
        self.against = 0
        self.opponents = defaultdict(lambda: [0, 0])  # [Siege, Niederlagen]

    def record_game(self, scored, conceded, opponent, win):
        self.games += 1
        self.points += scored
        self.against += conceded
        if win:
            self.wins += 1
            self.opponents[opponent][0] += 1
        else:
            self.opponents[opponent][1] += 1

    def win_pct(self):
        return round(100 * self.wins / self.games, 1) if self.games else 0.0

    def point_diff(self):
        return self.points - self.against

    def __repr__(self):
        return f"TeamStats(games={self.games}, wins={self.wins}, winPercent={self.win_pct()}"
