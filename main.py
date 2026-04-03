import json
import os
from collections import defaultdict
from flask import Flask, render_template, request, redirect
from models.team import Team
from models.team_stats import TeamStats
from data.games import saison_25_26

app = Flask(__name__)

name_to_team = {}

completed_games = [g for g in saison_25_26 if len(g) == 4]
pending_games = [g for g in saison_25_26 if len(g) == 2]

DEFAULT_TEAMS = {
    "BB Löwen Braunschweig",
    "MLP Academics Heidelberg",
    "Science City Jena",
    "SYNTAINICS MBC",
}

STATE_FILE = "data/state.json"

hypothetical = {}
saved_selected_teams = set(DEFAULT_TEAMS)
saved_compare_teams = set()

def load_state():
    global hypothetical, saved_selected_teams, saved_compare_teams
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        hypothetical = {int(k): tuple(v) for k, v in data.get("hypothetical", {}).items()}
        saved_selected_teams = set(data.get("selected_teams", list(DEFAULT_TEAMS)))
        saved_compare_teams = set(data.get("compare_teams", []))

def save_state(selected_teams, compare_teams):
    data = {
        "hypothetical": {str(k): list(v) for k, v in hypothetical.items()},
        "selected_teams": sorted(selected_teams),
        "compare_teams": sorted(compare_teams),
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

load_state()

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
    global saved_selected_teams, saved_compare_teams
    all_team_names = sorted(set(
        team for game in saison_25_26 for team in [game[0], game[1]]))

    raw_selected = request.args.getlist('teams')
    if raw_selected:
        selected_teams = set(raw_selected)
    else:
        selected_teams = set(saved_selected_teams)

    compare_teams = set(request.args.getlist('compare'))

    if raw_selected or 'compare' in request.args:
        saved_selected_teams = selected_teams
        saved_compare_teams = compare_teams
        save_state(selected_teams, compare_teams)

    full_standings = compute_standings()

    direct_standings = None
    if len(compare_teams) >= 2:
        direct_standings = [
            (team, stats)
            for team, stats in compute_standings(filter_teams=compare_teams)
            if team.name in compare_teams
        ]

    def game_visible(game):
        return game[0] in selected_teams or game[1] in selected_teams

    def is_compare_game(game):
        return len(compare_teams) >= 2 and game[0] in compare_teams and game[1] in compare_teams

    visible_completed = [(g, is_compare_game(g)) for g in completed_games if game_visible(g)]
    visible_pending = [(idx, g, is_compare_game(g)) for idx, g in enumerate(pending_games) if game_visible(g)]

    return render_template('index.html',
                           all_team_names=all_team_names,
                           selected_teams=selected_teams,
                           compare_teams=compare_teams,
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
    save_state(saved_selected_teams, saved_compare_teams)
    return redirect(request.referrer or '/')

@app.route('/clear_score/<int:idx>')
def clear_score(idx):
    hypothetical.pop(idx, None)
    save_state(saved_selected_teams, saved_compare_teams)
    return redirect(request.referrer or '/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
