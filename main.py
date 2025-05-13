from collections import defaultdict
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)


class Team:

    def __init__(self, name):
        self.name = name
        self.calculate = True

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Team) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


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


name_to_team = {}


def get_team(name):
    if name not in name_to_team:
        name_to_team[name] = Team(name)
    return name_to_team[name]


teams = defaultdict(TeamStats)
games = [("EWE Baskets Oldenburg", "MLP Academics Heidelberg", 105, 82),
         ("BG Göttingen", "Skyliners Frankfurt", 72, 100),
         ("Bamberg Baskets", "BB Löwen Braunschweig", 77, 96),
         ("SYNTAINICS MBC", "Rostock Seawolves", 84, 87),
         ("Chemnitz 99ers", "ratiopharm Ulm", 86, 90),
         ("MHP RIESEN Ludwigsburg", "Bayern München", 78, 70),
         ("Veolia Towers Hamburg", "Alba Berlin", 97, 80),
         ("SC RASTA Vechta", "Telekom Baskets Bonn", 83, 75),
         ("ratiopharm Ulm", "FIT/One Würzburg Baskets", 85, 76),
         ("Alba Berlin", "EWE Baskets Oldenburg", 105, 70),
         ("Rostock Seawolves", "BG Göttingen", 102, 74),
         ("Telekom Baskets Bonn", "SYNTAINICS MBC", 95, 80),
         ("Bayern München", "Veolia Towers Hamburg", 81, 80),
         ("MLP Academics Heidelberg", "SC RASTA Vechta", 80, 74),
         ("Skyliners Frankfurt", "Bamberg Baskets", 58, 66),
         ("BB Löwen Braunschweig", "MHP RIESEN Ludwigsburg", 91, 71),
         ("Bayern München", "Chemnitz 99ers", 73, 59),
         ("MHP RIESEN Ludwigsburg", "Rostock Seawolves", 70, 64),
         ("SYNTAINICS MBC", "MLP Academics Heidelberg", 93, 108),
         ("EWE Baskets Oldenburg", "Telekom Baskets Bonn", 91, 96),
         ("FIT/One Würzburg Baskets", "Skyliners Frankfurt", 89, 70),
         ("Bamberg Baskets", "ratiopharm Ulm", 77, 98),
         ("SC RASTA Vechta", "BB Löwen Braunschweig", 91, 88),
         ("BG Göttingen", "Veolia Towers Hamburg", 75, 92),
         ("Rostock Seawolves", "FIT/One Würzburg Baskets", 65, 92),
         ("BB Löwen Braunschweig", "MLP Academics Heidelberg", 65, 72),
         ("ratiopharm Ulm", "MHP RIESEN Ludwigsburg", 63, 62),
         ("Skyliners Frankfurt", "SYNTAINICS MBC", 69, 79),
         ("BG Göttingen", "Bayern München", 81, 95),
         ("Telekom Baskets Bonn", "Alba Berlin", 91, 87),
         ("Veolia Towers Hamburg", "EWE Baskets Oldenburg", 87, 78),
         ("Chemnitz 99ers", "SC RASTA Vechta", 88, 77),
         ("FIT/One Würzburg Baskets", "Veolia Towers Hamburg", 91, 85),
         ("SYNTAINICS MBC", "Bayern München", 79, 75),
         ("EWE Baskets Oldenburg", "ratiopharm Ulm", 93, 66),
         ("SC RASTA Vechta", "Skyliners Frankfurt", 74, 80),
         ("MHP RIESEN Ludwigsburg", "BG Göttingen", 91, 62),
         ("Bamberg Baskets", "Rostock Seawolves", 75, 89),
         ("MLP Academics Heidelberg", "Telekom Baskets Bonn", 76, 95),
         ("Alba Berlin", "Chemnitz 99ers", 78, 81),
         ("EWE Baskets Oldenburg", "Bamberg Baskets", 67, 59),
         ("ratiopharm Ulm", "SC RASTA Vechta", 85, 76),
         ("Skyliners Frankfurt", "MLP Academics Heidelberg", 72, 95),
         ("Veolia Towers Hamburg", "SYNTAINICS MBC", 75, 96),
         ("Alba Berlin", "BB Löwen Braunschweig", 65, 61),
         ("Rostock Seawolves", "Chemnitz 99ers", 60, 68),
         ("Bayern München", "FIT/One Würzburg Baskets", 70, 69),
         ("Telekom Baskets Bonn", "MHP RIESEN Ludwigsburg", 79, 89),
         ("Rostock Seawolves", "Skyliners Frankfurt", 83, 66),
         ("MLP Academics Heidelberg", "FIT/One Würzburg Baskets", 67, 72),
         ("ratiopharm Ulm", "Veolia Towers Hamburg", 82, 72),
         ("MHP RIESEN Ludwigsburg", "SC RASTA Vechta", 77, 79),
         ("Bamberg Baskets", "Alba Berlin", 87, 82),
         ("Chemnitz 99ers", "BG Göttingen", 96, 88),
         ("SYNTAINICS MBC", "EWE Baskets Oldenburg", 92, 77),
         ("BB Löwen Braunschweig", "Bayern München", 72, 90),
         ("SC RASTA Vechta", "Bamberg Baskets", 101, 98),
         ("Alba Berlin", "ratiopharm Ulm", 96, 88),
         ("BG Göttingen", "MLP Academics Heidelberg", 73, 95),
         ("FIT/One Würzburg Baskets", "BB Löwen Braunschweig", 70, 53),
         ("Rostock Seawolves", "Telekom Baskets Bonn", 64, 69),
         ("Chemnitz 99ers", "EWE Baskets Oldenburg", 87, 78),
         ("SYNTAINICS MBC", "MHP RIESEN Ludwigsburg", 76, 70),
         ("Skyliners Frankfurt", "Bayern München", 84, 91),
         ("MLP Academics Heidelberg", "Veolia Towers Hamburg", 73, 68),
         ("SYNTAINICS MBC", "Bamberg Baskets", 99, 94),
         ("BB Löwen Braunschweig", "Chemnitz 99ers", 82, 74),
         ("EWE Baskets Oldenburg", "Skyliners Frankfurt", 102, 92),
         ("ratiopharm Ulm", "BG Göttingen", 109, 70),
         ("Bayern München", "Telekom Baskets Bonn", 93, 73),
         ("SC RASTA Vechta", "Alba Berlin", 96, 93),
         ("MHP RIESEN Ludwigsburg", "FIT/One Würzburg Baskets", 82, 91),
         ("MLP Academics Heidelberg", "Rostock Seawolves", 86, 81),
         ("Veolia Towers Hamburg", "Skyliners Frankfurt", 91, 78),
         ("Chemnitz 99ers", "FIT/One Würzburg Baskets", 81, 77),
         ("Alba Berlin", "MHP RIESEN Ludwigsburg", 60, 74),
         ("BB Löwen Braunschweig", "SYNTAINICS MBC", 76, 70),
         ("Telekom Baskets Bonn", "ratiopharm Ulm", 75, 95),
         ("Bayern München", "SC RASTA Vechta", 77, 78),
         ("BG Göttingen", "Bamberg Baskets", 97, 88),
         ("Skyliners Frankfurt", "BB Löwen Braunschweig", 91, 92),
         ("ratiopharm Ulm", "MLP Academics Heidelberg", 67, 69),
         ("Bamberg Baskets", "Telekom Baskets Bonn", 92, 73),
         ("SC RASTA Vechta", "Veolia Towers Hamburg", 69, 79),
         ("Rostock Seawolves", "Bayern München", 70, 80),
         ("EWE Baskets Oldenburg", "BG Göttingen", 111, 94),
         ("MHP RIESEN Ludwigsburg", "Chemnitz 99ers", 69, 65),
         ("FIT/One Würzburg Baskets", "Alba Berlin", 70, 69),
         ("Veolia Towers Hamburg", "MHP RIESEN Ludwigsburg", 66, 73),
         ("BB Löwen Braunschweig", "Rostock Seawolves", 80, 63),
         ("FIT/One Würzburg Baskets", "SYNTAINICS MBC", 86, 76),
         ("Chemnitz 99ers", "Telekom Baskets Bonn", 88, 123),
         ("MLP Academics Heidelberg", "Bamberg Baskets", 68, 79),
         ("BG Göttingen", "Alba Berlin", 83, 109),
         ("Bayern München", "EWE Baskets Oldenburg", 89, 75),
         ("Skyliners Frankfurt", "ratiopharm Ulm", 87, 85),
         ("Telekom Baskets Bonn", "FIT/One Würzburg Baskets", 81, 90),
         ("Rostock Seawolves", "Veolia Towers Hamburg", 92, 78),
         ("MHP RIESEN Ludwigsburg", "Skyliners Frankfurt", 82, 61),
         ("BB Löwen Braunschweig", "EWE Baskets Oldenburg", 83, 82),
         ("Bamberg Baskets", "Chemnitz 99ers", 81, 80),
         ("SYNTAINICS MBC", "Alba Berlin", 94, 76),
         ("MLP Academics Heidelberg", "Bayern München", 59, 87),
         ("BG Göttingen", "SC RASTA Vechta", 66, 86),
         ("SC RASTA Vechta", "EWE Baskets Oldenburg", 98, 91),
         ("Telekom Baskets Bonn", "BG Göttingen", 80, 67),
         ("FIT/One Würzburg Baskets", "Bamberg Baskets", 70, 82),
         ("Veolia Towers Hamburg", "BB Löwen Braunschweig", 86, 91),
         ("Chemnitz 99ers", "SYNTAINICS MBC", 82, 72),
         ("MHP RIESEN Ludwigsburg", "MLP Academics Heidelberg", 63, 67),
         ("Alba Berlin", "Rostock Seawolves", 85, 96),
         ("Bayern München", "ratiopharm Ulm", 70, 62),
         ("FIT/One Würzburg Baskets", "BG Göttingen", 79, 78),
         ("Chemnitz 99ers", "Skyliners Frankfurt", 85, 66),
         ("Rostock Seawolves", "SC RASTA Vechta", 87, 83),
         ("SYNTAINICS MBC", "ratiopharm Ulm", 89, 92),
         ("Alba Berlin", "Bayern München", 88, 81),
         ("BB Löwen Braunschweig", "Telekom Baskets Bonn", 74, 94),
         ("EWE Baskets Oldenburg", "MHP RIESEN Ludwigsburg", 70, 64),
         ("Bamberg Baskets", "Veolia Towers Hamburg", 80, 83),
         ("Veolia Towers Hamburg", "Telekom Baskets Bonn", 91, 84),
         ("EWE Baskets Oldenburg", "FIT/One Würzburg Baskets", 96, 85),
         ("BG Göttingen", "BB Löwen Braunschweig", 86, 107),
         ("ratiopharm Ulm", "Rostock Seawolves", 82, 72),
         ("SC RASTA Vechta", "SYNTAINICS MBC", 87, 79),
         ("MHP RIESEN Ludwigsburg", "Bamberg Baskets", 92, 73),
         ("Skyliners Frankfurt", "Alba Berlin", 61, 75),
         ("MLP Academics Heidelberg", "Chemnitz 99ers", 81, 66),
         ("Chemnitz 99ers", "Veolia Towers Hamburg", 69, 60),
         ("Rostock Seawolves", "EWE Baskets Oldenburg", 122, 118),
         ("SYNTAINICS MBC", "BG Göttingen", 93, 91),
         ("Alba Berlin", "MLP Academics Heidelberg", 92, 65),
         ("Telekom Baskets Bonn", "Skyliners Frankfurt", 70, 77),
         ("BB Löwen Braunschweig", "ratiopharm Ulm", 98, 89),
         ("FIT/One Würzburg Baskets", "SC RASTA Vechta", 74, 86),
         ("Bamberg Baskets", "Bayern München", 69, 68),
         ("SC RASTA Vechta", "Chemnitz 99ers", 89, 66),
         ("BG Göttingen", "SYNTAINICS MBC", 80, 94),
         ("ratiopharm Ulm", "Telekom Baskets Bonn", 84, 75),
         ("MHP RIESEN Ludwigsburg", "BB Löwen Braunschweig", 69, 83),
         ("Bayern München", "Bamberg Baskets", 84, 82),
         ("Veolia Towers Hamburg", "FIT/One Würzburg Baskets", 68, 66),
         ("EWE Baskets Oldenburg", "Alba Berlin", 97, 92),
         ("Skyliners Frankfurt", "Rostock Seawolves", 72, 77),
         ("Veolia Towers Hamburg", "BG Göttingen", 91, 82),
         ("Bamberg Baskets", "SYNTAINICS MBC", 87, 69),
         ("FIT/One Würzburg Baskets", "EWE Baskets Oldenburg", 102, 112),
         ("Telekom Baskets Bonn", "Chemnitz 99ers", 80, 84),
         ("Rostock Seawolves", "MLP Academics Heidelberg", 88, 82),
         ("Bayern München", "Alba Berlin", 99, 86),
         ("MHP RIESEN Ludwigsburg", "ratiopharm Ulm", 92, 71),
         ("BB Löwen Braunschweig", "SC RASTA Vechta", 103, 70),
         ("ratiopharm Ulm", "SYNTAINICS MBC", 92, 66),
         ("Skyliners Frankfurt", "BG Göttingen", 95, 94),
         ("Chemnitz 99ers", "BB Löwen Braunschweig", 83, 95),
         ("MLP Academics Heidelberg", "MHP RIESEN Ludwigsburg", 86, 73),
         ("FIT/One Würzburg Baskets", "Rostock Seawolves", 93, 97),
         ("Alba Berlin", "Veolia Towers Hamburg", 92, 77),
         ("SC RASTA Vechta", "Bayern München", 79, 65),
         ("Bamberg Baskets", "EWE Baskets Oldenburg", 103, 85),
         ("Chemnitz 99ers", "MLP Academics Heidelberg", 72, 65),
         ("SYNTAINICS MBC", "SC RASTA Vechta", 91, 83),
         ("Bayern München", "Skyliners Frankfurt", 70, 56),
         ("MHP RIESEN Ludwigsburg", "Telekom Baskets Bonn", 81, 61),
         ("BB Löwen Braunschweig", "Veolia Towers Hamburg", 91, 79),
         ("Rostock Seawolves", "Alba Berlin", 71, 78),
         ("Bamberg Baskets", "FIT/One Würzburg Baskets", 93, 98),
         ("BG Göttingen", "ratiopharm Ulm", 72, 91),
         ("ratiopharm Ulm", "BB Löwen Braunschweig", 111, 75),
         ("FIT/One Würzburg Baskets", "MHP RIESEN Ludwigsburg", 77, 60),
         ("Skyliners Frankfurt", "Veolia Towers Hamburg", 78, 84),
         ("Telekom Baskets Bonn", "Rostock Seawolves", 83, 72),
         ("SC RASTA Vechta", "BG Göttingen", 87, 79),
         ("MLP Academics Heidelberg", "EWE Baskets Oldenburg", 95, 79),
         ("Chemnitz 99ers", "Bayern München", 72, 94),
         ("Alba Berlin", "Bamberg Baskets", 86, 77),
         ("Telekom Baskets Bonn", "SC RASTA Vechta", 88, 94),
         ("Veolia Towers Hamburg", "Rostock Seawolves", 78, 77),
         ("Bamberg Baskets", "Skyliners Frankfurt", 92, 85),
         ("BG Göttingen", "Chemnitz 99ers", 90, 94),
         ("EWE Baskets Oldenburg", "BB Löwen Braunschweig", 102, 90),
         ("SYNTAINICS MBC", "FIT/One Würzburg Baskets", 110, 101),
         ("ratiopharm Ulm", "Alba Berlin", 101, 90),
         ("Bayern München", "MLP Academics Heidelberg", 87, 78),
         ("SC RASTA Vechta", "ratiopharm Ulm", 73, 84),
         ("Rostock Seawolves", "SYNTAINICS MBC", 84, 76),
         ("Telekom Baskets Bonn", "Bamberg Baskets", 87, 77),
         ("EWE Baskets Oldenburg", "Veolia Towers Hamburg", 99, 81),
         ("MLP Academics Heidelberg", "BG Göttingen", 93, 86),
         ("FIT/One Würzburg Baskets", "Chemnitz 99ers", 83, 90),
         ("Skyliners Frankfurt", "MHP RIESEN Ludwigsburg", 77, 69),
         ("BB Löwen Braunschweig", "Alba Berlin", 73, 108),
         ("ratiopharm Ulm", "Skyliners Frankfurt", 115, 88),
         ("Bayern München", "Rostock Seawolves", 91, 66),
         ("Veolia Towers Hamburg", "SC RASTA Vechta", 86, 73),
         ("MHP RIESEN Ludwigsburg", "EWE Baskets Oldenburg", 66, 79),
         ("SYNTAINICS MBC", "BB Löwen Braunschweig", 82, 77),
         ("BG Göttingen", "Telekom Baskets Bonn", 85, 112),
         ("Alba Berlin", "FIT/One Würzburg Baskets", 80, 84),
         ("Bamberg Baskets", "MLP Academics Heidelberg", 90, 93),
         ("SC RASTA Vechta", "MHP RIESEN Ludwigsburg", 64, 70),
         ("Rostock Seawolves", "ratiopharm Ulm", 85, 67),
         ("EWE Baskets Oldenburg", "SYNTAINICS MBC", 95, 97),
         ("Telekom Baskets Bonn", "Veolia Towers Hamburg", 93, 96),
         ("FIT/One Würzburg Baskets", "Bayern München", 75, 81),
         ("BB Löwen Braunschweig", "Bamberg Baskets", 114, 88),
         ("Skyliners Frankfurt", "Chemnitz 99ers", 65, 70),
         ("MLP Academics Heidelberg", "Alba Berlin", 90, 86),
         ("SYNTAINICS MBC", "Skyliners Frankfurt", 85, 72),
         ("BG Göttingen", "FIT/One Würzburg Baskets", 80, 97),
         ("Rostock Seawolves", "MHP RIESEN Ludwigsburg", 94, 89),
         ("Veolia Towers Hamburg", "MLP Academics Heidelberg", 88, 81),
         ("Alba Berlin", "SC RASTA Vechta", 83, 58),
         ("Telekom Baskets Bonn", "EWE Baskets Oldenburg", 81, 76),
         ("ratiopharm Ulm", "Chemnitz 99ers", 117, 87),
         ("Bayern München", "BB Löwen Braunschweig", 94, 72),
         ("MLP Academics Heidelberg", "SYNTAINICS MBC", 87, 78),
         ("BB Löwen Braunschweig", "BG Göttingen", 101, 77),
         ("Skyliners Frankfurt", "Telekom Baskets Bonn", 76, 70),
         ("SC RASTA Vechta", "Rostock Seawolves", 68, 84),
         ("Chemnitz 99ers", "Bamberg Baskets", 99, 98),
         ("EWE Baskets Oldenburg", "Bayern München", 83, 94),
         ("MHP RIESEN Ludwigsburg", "Alba Berlin", 63, 79),
         ("FIT/One Würzburg Baskets", "ratiopharm Ulm", 89, 72),
         ("SYNTAINICS MBC", "Chemnitz 99ers", 97, 95),
         ("BG Göttingen", "MHP RIESEN Ludwigsburg", 74, 79),
         ("SC RASTA Vechta", "FIT/One Würzburg Baskets", 78, 86),
         ("Veolia Towers Hamburg", "Bayern München", 74, 70),
         ("Rostock Seawolves", "Bamberg Baskets", 98, 74),
         ("Telekom Baskets Bonn", "MLP Academics Heidelberg", 85, 80),
         ("Alba Berlin", "Skyliners Frankfurt", 89, 68),
         ("ratiopharm Ulm", "EWE Baskets Oldenburg", 119, 92),
         ("Bamberg Baskets", "BG Göttingen", 92, 101),
         ("MLP Academics Heidelberg", "BB Löwen Braunschweig", 74, 94),
         ("FIT/One Würzburg Baskets", "Telekom Baskets Bonn", 83, 75),
         ("Skyliners Frankfurt", "SC RASTA Vechta", 74, 75),
         ("MHP RIESEN Ludwigsburg", "Veolia Towers Hamburg", 89, 78),
         ("EWE Baskets Oldenburg", "Rostock Seawolves", 92, 79),
         ("Bayern München", "SYNTAINICS MBC", 90, 88),
         ("Chemnitz 99ers", "Alba Berlin", 81, 103),
         ("ratiopharm Ulm", "Bayern München", 109, 94),
         ("SC RASTA Vechta", "MLP Academics Heidelberg", 78, 60),
         ("Alba Berlin", "SYNTAINICS MBC", 90, 62),
         ("Telekom Baskets Bonn", "BB Löwen Braunschweig", 85, 81),
         ("Veolia Towers Hamburg", "Bamberg Baskets", 93, 114),
         ("BG Göttingen", "EWE Baskets Oldenburg", 93, 96),
         ("Skyliners Frankfurt", "FIT/One Würzburg Baskets", 70, 85),
         ("Chemnitz 99ers", "MHP RIESEN Ludwigsburg", 104, 100),
         ("Alba Berlin", "Telekom Baskets Bonn", 102, 88),
         ("MLP Academics Heidelberg", "ratiopharm Ulm", 74, 90),
         ("Bamberg Baskets", "MHP RIESEN Ludwigsburg", 73, 75),
         ("EWE Baskets Oldenburg", "SC RASTA Vechta", 91, 75),
         ("SYNTAINICS MBC", "Veolia Towers Hamburg", 102, 81),
         ("Bayern München", "BG Göttingen", 94, 86),
         ("Chemnitz 99ers", "Rostock Seawolves", 108, 102),
         ("BB Löwen Braunschweig", "Skyliners Frankfurt", 79, 72),
         ("Skyliners Frankfurt", "EWE Baskets Oldenburg", 83, 72),
         ("FIT/One Würzburg Baskets", "MLP Academics Heidelberg", 85, 102),
         ("Veolia Towers Hamburg", "Chemnitz 99ers", 88, 93),
         ("MHP RIESEN Ludwigsburg", "SYNTAINICS MBC", 85, 76),
         ("Alba Berlin", "BG Göttingen", 101, 69),
         ("ratiopharm Ulm", "Bamberg Baskets", 92, 77),
         ("Rostock Seawolves", "BB Löwen Braunschweig", 48, 67),
         ("Telekom Baskets Bonn", "Bayern München", 86, 90),
         ("BG Göttingen", "Rostock Seawolves", 88, 85),
         ("SYNTAINICS MBC", "Telekom Baskets Bonn", 100, 94),
         ("Bayern München", "MHP RIESEN Ludwigsburg", 73, 72),
         ("Bamberg Baskets", "SC RASTA Vechta", 86, 73),
         ("EWE Baskets Oldenburg", "Chemnitz 99ers", 104, 94),
         ("Veolia Towers Hamburg", "ratiopharm Ulm", 64, 79),
         ("BB Löwen Braunschweig", "FIT/One Würzburg Baskets", 86, 72),
         ("MLP Academics Heidelberg", "Skyliners Frankfurt", 84, 75)]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Basketball Stats</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 8px; border: 1px solid #ddd; }
        form { margin: 20px 0; }
        input { margin: 5px; padding: 5px; }
    </style>
</head>
<body>
    <h2>Add New Game</h2>
    <form method="POST" action="/add_game">
        <input name="team1" placeholder="Team 1" required>
        <input name="team2" placeholder="Team 2" required>
        <input name="score1" type="number" placeholder="Score Team 1" required>
        <input name="score2" type="number" placeholder="Score Team 2" required>
        <input type="submit" value="Add Game">
    </form>

    <h2>Teams</h2>
    <form method="GET" id="teamFilter">
        {% for team in all_teams %}
        <label style="display: inline-block; margin-right: 15px;">
            <input type="checkbox" name="teams" value="{{team.name}}" 
                   {% if not selected_teams or team.name in selected_teams %}checked{% endif %}
                   onchange="this.form.submit()">
            {{team}}
        </label>
        {% endfor %}
    </form>

    <h2>Current Standings</h2>
    <table>
        <tr>
            <th>Team</th>
            <th>Games</th>
            <th>Wins</th>
            <th>Win%</th>
            <th>Points</th>
            <th>Against</th>
            <th>Difference</th>
        </tr>
        {% for name, stats in standings %}
        <tr>
            <td>{{name}}</td>
            <td>{{stats.games}}</td>
            <td>{{stats.wins}}</td>
            <td>{{stats.win_pct()}}</td>
            <td>{{stats.points}}</td>
            <td>{{stats.against}}</td>
            <td>{{stats.point_diff()}}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>Games</h2>
    <table>
        <tr>
            <th>Team 1</th>
            <th>Team 2</th>
            <th>Score</th>
            <th>Actions</th>
        </tr>
        {% for game in games %}
        <tr id="game{{loop.index0}}">
            {% if edit_id == loop.index0 %}
            <td colspan="3">
                <form method="POST" action="/edit_game/{{loop.index0}}" style="margin:0">
                    <input name="team1" value="{{game[0]}}" required>
                    <input name="team2" value="{{game[1]}}" required>
                    <input name="score1" type="number" value="{{game[2]}}" required>
                    <input name="score2" type="number" value="{{game[3]}}" required>
                    <input type="submit" value="Save">
                </form>
            </td>
            {% else %}
            <td>{{game[0]}}</td>
            <td>{{game[1]}}</td>
            <td>{{game[2]}} - {{game[3]}}</td>
            {% endif %}
            <td>
                <a href="/?edit={{loop.index0}}" class="edit">Edit</a>
                <a href="/delete_game/{{loop.index0}}" class="delete">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>"""


def process_games():
    teams.clear()
    for t1, t2, p1, p2 in games:
        t1 = get_team(t1)
        t2 = get_team(t2)
        if t1.calculate and t2.calculate:
            win1 = p1 > p2
            win2 = not win1
            teams[t1].record_game(p1, p2, t2, win1)
            teams[t2].record_game(p2, p1, t1, win2)


def get_sorted_teams():
    return sorted(teams.items(),
                  key=lambda x: (
                      -x[1].win_pct(),
                      -x[1].opponents[x[0]][0],
                      -x[1].point_diff(),
                      -x[1].points,
                  ))


@app.route('/')
def home():
    edit_id = request.args.get('edit')
    try:
        edit_id = int(edit_id)
    except:
        edit_id = None

    all_teams = sorted(set(
        get_team(team) for game in games for team in [game[0], game[1]]),
                       key=lambda t: t.name)
    selected_teams = request.args.getlist('teams')
    for team in all_teams:
        team.calculate = team.name in selected_teams or not selected_teams

    process_games()

    standings = get_sorted_teams()
    if selected_teams:
        standings = [(team, stats) for team, stats in standings
                     if team.name in selected_teams]

    return render_template_string(HTML_TEMPLATE,
                                  games=games,
                                  standings=standings,
                                  edit_id=edit_id,
                                  all_teams=all_teams,
                                  selected_teams=selected_teams)


@app.route('/add_game', methods=['POST'])
def add_game():
    team1 = request.form['team1']
    team2 = request.form['team2']
    score1 = int(request.form['score1'])
    score2 = int(request.form['score2'])
    games.append((team1, team2, score1, score2))
    return redirect('/')


@app.route('/edit_game/<int:game_index>', methods=['POST'])
def edit_game(game_index):
    team1 = request.form['team1']
    team2 = request.form['team2']
    score1 = int(request.form['score1'])
    score2 = int(request.form['score2'])
    games[game_index] = (team1, team2, score1, score2)
    return redirect('/')


@app.route('/delete_game/<int:game_index>')
def delete_game(game_index):
    del games[game_index]
    return redirect('/')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
