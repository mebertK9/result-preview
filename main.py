from collections import defaultdict
from flask import Flask, render_template, request, redirect
from models.team import Team
from models.team_stats import TeamStats
from data.games import games

app = Flask(__name__)

name_to_team = {}
teams = defaultdict(TeamStats)

def get_team(name):
    if name not in name_to_team:
        name_to_team[name] = Team(name)
    return name_to_team[name]

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

    return render_template('index.html',
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