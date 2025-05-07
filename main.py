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


teams = defaultdict(TeamStats)

# 📝 Ergebnis eintragen: team1, team2, punkte_team1, punkte_team2
games = [
    ("Braunschweig", "Chemnitz", 82, 74),
    ("Chemnitz", "Braunschweig", 83, 95),
    ("Braunschweig", "Berlin", 73, 108),
    ("Berlin", "Braunschweig", 65, 61),
    ("Würzburg", "Braunschweig", 70, 53),
    
    ("Berlin", "Chemnitz", 78, 81),
    ("Chemnitz", "Berlin", 81, 103),
    ("Chemnitz", "Würzburg", 81, 77),
    ("Würzburg", "Chemnitz", 83, 90),
    
    ("Berlin", "Würzburg", 80, 84),
    ("Würzburg", "Berlin", 70, 69),
]

for t1, t2, p1, p2 in games:
    win1 = p1 > p2
    win2 = not win1
    teams[t1].record_game(p1, p2, t2, win1)
    teams[t2].record_game(p2, p1, t1, win2)

# 🧮 Sortierung: nach Win%, dann direktem Vergleich, dann Punktdifferenz
def compare_teams(a, b):
    if a.win_pct() != b.win_pct():
        return b.win_pct() - a.win_pct()
    # Direkter Vergleich
    a_wins_vs_b, _ = a.opponents.get(b_name := [name for name, obj in teams.items() if obj == b][0], [0, 0])
    b_wins_vs_a, _ = b.opponents.get(a_name := [name for name, obj in teams.items() if obj == a][0], [0, 0])
    if a_wins_vs_b != b_wins_vs_a:
        return b_wins_vs_a - a_wins_vs_b
    return b.point_diff() - a.point_diff()

sorted_teams = sorted(teams.items(), key=lambda x: (
    -x[1].win_pct(),
    -x[1].opponents[x[0]][0],  # direkter Vergleich
    -x[1].point_diff(),
))

# 📊 Tabelle anzeigen
print(f"{'Team':<15}{'Spiele':<7}{'Siege':<6}{'Win%':<6}{'Differenz':<10}")
for name, stats in sorted_teams:
    print(f"{name:<15}{stats.games:<7}{stats.wins:<6}{stats.win_pct():<6}{stats.point_diff():<10}")
