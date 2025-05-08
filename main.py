from collections import defaultdict
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)


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
            <input type="checkbox" name="teams" value="{{team}}" 
                   {% if not selected_teams or team in selected_teams %}checked{% endif %}
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
            <th>Difference</th>
        </tr>
        {% for name, stats in standings %}
        <tr>
            <td>{{name}}</td>
            <td>{{stats.games}}</td>
            <td>{{stats.wins}}</td>
            <td>{{stats.win_pct()}}</td>
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
                  ))


@app.route('/')
def home():
    process_games()
    edit_id = request.args.get('edit')
    try:
        edit_id = int(edit_id)
    except:
        edit_id = None
    
    all_teams = sorted(set(team for game in games for team in [game[0], game[1]]))
    selected_teams = request.args.getlist('teams')
    
    standings = get_sorted_teams()
    if selected_teams:
        standings = [(team, stats) for team, stats in standings if team in selected_teams]
    
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
