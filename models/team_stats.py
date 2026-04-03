
from collections import defaultdict

class TeamStats:
    def __init__(self):
        self.games = 0
        self.wins = 0
        self.points = 0
        self.against = 0
        self.opponents = defaultdict(lambda: [0, 0, 0, 0])  # [h2h_wins, h2h_losses, h2h_scored, h2h_conceded]

    def record_game(self, scored, conceded, opponent, win):
        self.games += 1
        self.points += scored
        self.against += conceded
        self.opponents[opponent][2] += scored
        self.opponents[opponent][3] += conceded
        if win:
            self.wins += 1
            self.opponents[opponent][0] += 1
        else:
            self.opponents[opponent][1] += 1

    def plus_points(self):
        return self.wins * 2

    def minus_points(self):
        return (self.games - self.wins) * 2

    def point_diff(self):
        return self.points - self.against

    def __repr__(self):
        return f"TeamStats(games={self.games}, wins={self.wins}, plus={self.plus_points()})"
