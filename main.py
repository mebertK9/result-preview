from collections import defaultdict
from flask import Flask, render_template, request, redirect
from models.team import Team
from models.team_stats import TeamStats
from data.games import saison_25_26

app = Flask(__name__)

name_to_team = {}

completed_games = [g for g in saison_25_26 if len(g) == 4]
pending_games = [g for g in saison_25_26 if len(g) == 2]

hypothetical = {}  # {index_in_pending_games: (score1, score2)}

DEFAULT_TEAMS = {
    "BB Löwen Braunschweig",
    "MLP Academics Heidelberg",
    "Science City Jena",
    "SYNTAINICS MBC",
}

def get_team(name):
    if name not in name_to_team:
        name_to_team[name] = Team(name)
    return name_to_team[name]

def compute_standings(filter_teams=None):
    teams = defaultdict(TeamStats)

    all_games = list(completed_games)
    for idx, (t1, t2) in enumerate(pending_games):
        if idx in hypothetical:
            p1, p2 = hypothetical[idx]
            all_games.append((t1, t2, p1, p2))

    for t1, t2, p1, p2 in all_games:
        if filter_teams is not None:
            if t1 not in filter_teams or t2 not in filter_teams:
                continue
        t1_obj = get_team(t1)
        t2_obj = get_team(t2)
        win1 = p1 > p2
        teams[t1_obj].record_game(p1, p2, t2_obj, win1)
        teams[t2_obj].record_game(p2, p1, t1_obj, not win1)

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
    all_team_names = sorted(set(
        team for game in saison_25_26 for team in [game[0], game[1]]))
    all_teams = [get_team(n) for n in all_team_names]

    raw_selected = request.args.getlist('teams')
    selected_teams = set(raw_selected) if raw_selected else set(DEFAULT_TEAMS)

    direct_compare = request.args.get('direct_compare') == '1'

    full_standings = compute_standings()

    direct_standings = None
    if direct_compare:
        direct_standings = [
            (team, stats) for team, stats in compute_standings(filter_teams=selected_teams)
            if team.name in selected_teams
        ]

    def game_visible(game):
        return game[0] in selected_teams or game[1] in selected_teams

    visible_completed = [g for g in completed_games if game_visible(g)]
    visible_pending = [(idx, g) for idx, g in enumerate(pending_games) if game_visible(g)]

    return render_template('index.html',
                           all_teams=all_team_names,
                           selected_teams=selected_teams,
                           direct_compare=direct_compare,
                           full_standings=full_standings,
                           direct_standings=direct_standings,
                           hypothetical=hypothetical,
                           visible_completed=visible_completed,
                           visible_pending=visible_pending)

@app.route('/set_score/<int:idx>', methods=['POST'])
def set_score(idx):
    score1 = request.form.get('score1', '').strip()
    score2 = request.form.get('score2', '').strip()
    if score1 and score2:
        hypothetical[idx] = (int(score1), int(score2))
    else:
        hypothetical.pop(idx, None)
    return redirect(request.referrer or '/')

@app.route('/clear_score/<int:idx>')
def clear_score(idx):
    hypothetical.pop(idx, None)
    return redirect(request.referrer or '/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
