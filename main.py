from collections import defaultdict
from flask import Flask, render_template, request, redirect
from models.team import Team
from models.team_stats import TeamStats
from data.games import saison_25_26

app = Flask(__name__)

name_to_team = {}
teams = defaultdict(TeamStats)

completed_games = [g for g in saison_25_26 if len(g) == 4]
pending_games = [g for g in saison_25_26 if len(g) == 2]

hypothetical = {}  # {index_in_pending_games: (score1, score2)}

def get_team(name):
    if name not in name_to_team:
        name_to_team[name] = Team(name)
    return name_to_team[name]

def process_games():
    teams.clear()
    for t1, t2, p1, p2 in completed_games:
        t1 = get_team(t1)
        t2 = get_team(t2)
        if t1.calculate and t2.calculate:
            win1 = p1 > p2
            teams[t1].record_game(p1, p2, t2, win1)
            teams[t2].record_game(p2, p1, t1, not win1)

    for idx, (t1, t2) in enumerate(pending_games):
        if idx in hypothetical:
            p1, p2 = hypothetical[idx]
            t1 = get_team(t1)
            t2 = get_team(t2)
            if t1.calculate and t2.calculate:
                win1 = p1 > p2
                teams[t1].record_game(p1, p2, t2, win1)
                teams[t2].record_game(p2, p1, t1, not win1)

def get_sorted_teams():
    return sorted(teams.items(),
                  key=lambda x: (
                      -x[1].plus_points(),
                      -x[1].opponents[x[0]][0],
                      -(x[1].opponents[x[0]][2] - x[1].opponents[x[0]][3]),
                      -x[1].opponents[x[0]][2],
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
        get_team(team) for game in saison_25_26 for team in [game[0], game[1]]),
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
                          completed_games=completed_games,
                          pending_games=pending_games,
                          hypothetical=hypothetical,
                          standings=standings,
                          edit_id=edit_id,
                          all_teams=all_teams,
                          selected_teams=selected_teams)

@app.route('/set_score/<int:idx>', methods=['POST'])
def set_score(idx):
    score1 = request.form.get('score1', '').strip()
    score2 = request.form.get('score2', '').strip()
    if score1 and score2:
        hypothetical[idx] = (int(score1), int(score2))
    else:
        hypothetical.pop(idx, None)
    return redirect('/')

@app.route('/clear_score/<int:idx>')
def clear_score(idx):
    hypothetical.pop(idx, None)
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
