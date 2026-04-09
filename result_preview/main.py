import os
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user, login_required, current_user,
)
from werkzeug.security import check_password_hash
 
from models.team import Team
from models.team_stats import TeamStats
from data.games import saison_25_26
from data.users import USERS, ADMIN_USER
from data.persistence import load_user_state, save_user_state, load_stats  # ← replaces file I/O
from data.util.rettungsgasse import init_grid, apply_action, to_rettungswagen, ROWS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

# ── Flask-Login setup ─────────────────────────────────────────────────────────
 
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
 
class User(UserMixin):
    def __init__(self, username):
        self.id = username
 
@login_manager.user_loader
def load_user(username):
    if username in USERS:
        return User(username)
    return None

# Load persisted state on startup.

load_stats()

# ── Constants ─────────────────────────────────────────────────────────────────

GAMES_FILE = "data/games.py"

DEFAULT_TEAMS = {
    "BB Löwen Braunschweig",
    "MLP Academics Heidelberg",
    "Science City Jena",
    "SYNTAINICS MBC",
}

# Derived game lists (rebuilt by finalize_game).
# hypothetical is now keyed by saison_25_26 index — not pending_games index.
completed_games = [g for g in saison_25_26 if len(g) == 4]
pending_games   = [g for g in saison_25_26 if len(g) == 2]

name_to_team = {}

# ── Game data helpers ─────────────────────────────────────────────────────────

def get_team(name):
    if name not in name_to_team:
        name_to_team[name] = Team(name)
    return name_to_team[name]

def _build_stats(hypothetical, filter_teams=None):
    """Build TeamStats from completed games + current user's hypotheticals."""
    teams = defaultdict(TeamStats)
    for i, game in enumerate(saison_25_26):
        if len(game) == 4:
            t1, t2, p1, p2 = game
        elif i in hypothetical:
            t1, t2 = game
            p1, p2 = hypothetical[i]
        else:
            continue  # pending, no hypothetical set

        if filter_teams is not None:
            if t1 not in filter_teams or t2 not in filter_teams:
                continue

        t1_obj = get_team(t1)
        t2_obj = get_team(t2)
        win1 = p1 > p2
        teams[t1_obj].record_game(p1, p2, t2_obj, win1)
        teams[t2_obj].record_game(p2, p1, t1_obj, not win1)
    return teams

def _sort_key_simple(stats):
    return (-stats.plus_points(), -stats.point_diff(), -stats.points)

def compute_standings(hypothetical, filter_teams=None):
    full_stats = _build_stats(hypothetical, filter_teams)
    if filter_teams is not None:
        return sorted(full_stats.items(), key=lambda x: _sort_key_simple(x[1]))
    groups = {}
    for team, stats in full_stats.items():
        groups.setdefault(stats.plus_points(), []).append((team, stats))
    result = []
    for pts in sorted(groups.keys(), reverse=True):
        group = groups[pts]
        if len(group) == 1:
            result.extend(group)
        else:
            group_names = {team.name for team, _ in group}
            h2h_stats = _build_stats(hypothetical, filter_teams=group_names)
            def tiebreak_key(item, h2h=h2h_stats):
                team, full = item
                h2h_s = h2h.get(team, TeamStats())
                return (-h2h_s.plus_points(), -h2h_s.point_diff(), -h2h_s.points,
                        -full.point_diff(), -full.points)
            result.extend(sorted(group, key=tiebreak_key))
    return result

def write_games_py():
    """Rewrite saison_25_26 in games.py; saison_24_25 is left untouched."""
    with open(GAMES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    marker = "\nsaison_24_25"
    cut = content.find(marker)
    suffix = content[cut:] if cut != -1 else ""

    lines = ["saison_25_26 = [\n"]
    for game in saison_25_26:
        if len(game) == 2:
            lines.append(f'    ("{game[0]}", "{game[1]}"),\n')
        else:
            lines.append(f'    ("{game[0]}", "{game[1]}", {game[2]}, {game[3]}),\n')
    lines.append("]\n")

    with open(GAMES_FILE, "w", encoding="utf-8") as f:
        f.write("".join(lines))
        f.write(suffix)

# ── Auth routes ───────────────────────────────────────────────────────────────
 
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        pw_hash = USERS.get(username)
        if pw_hash and check_password_hash(pw_hash, password):
            login_user(User(username), remember=True)
            return redirect(url_for('home'))
        error = "Benutzername oder Passwort falsch."
    return render_template('login.html', error=error)
 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))
 
# ── Main route ────────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def home():
    state = load_user_state(current_user.id, DEFAULT_TEAMS)
    hypothetical = state["hypothetical"]
    grid = state["grid"]
    if(grid == {}):
        print(f"grid is empty")
        grid = init_grid()

    all_team_names = sorted({
        team for game in saison_25_26 for team in [game[0], game[1]]
    })

    raw_selected = request.args.getlist('teams')
    has_url_params = raw_selected or 'compare' in request.args

    if has_url_params:
        selected_teams = set(raw_selected)
        compare_teams  = set(request.args.getlist('compare'))
        state["selected_teams"] = selected_teams
        state["compare_teams"]  = compare_teams
        save_user_state(current_user.id, state)
    else:
        selected_teams = state["selected_teams"]
        compare_teams  = state["compare_teams"]

    # Count hypothetical games and wins per team
    hypo_count = {}
    hypo_wins  = {}
    for i, game in enumerate(saison_25_26):
        if len(game) == 2 and i in hypothetical:
            t1, t2 = game
            hypo_count[t1] = hypo_count.get(t1, 0) + 1
            hypo_count[t2] = hypo_count.get(t2, 0) + 1
            s1, s2 = hypothetical[i]
            if s1 > s2:
                hypo_wins[t1] = hypo_wins.get(t1, 0) + 1
            elif s2 > s1:
                hypo_wins[t2] = hypo_wins.get(t2, 0) + 1

    full_standings   = compute_standings(hypothetical)
    direct_standings = None
    if len(compare_teams) >= 2:
        direct_standings = [
            (team, stats)
            for team, stats in compute_standings(hypothetical, filter_teams=compare_teams)
            if team.name in compare_teams
        ]

    def game_visible(game):
        return game[0] in selected_teams or game[1] in selected_teams

    def is_compare_game(game):
        return len(compare_teams) >= 2 and game[0] in compare_teams and game[1] in compare_teams

    visible_completed = [
        (g, is_compare_game(g))
        for g in saison_25_26 if len(g) == 4
    ]
    visible_pending = [
        (i, game, is_compare_game(game))
        for i, game in enumerate(saison_25_26)
        if len(game) == 2 and game_visible(game)
    ]

    LOEWEN = "BB Löwen Braunschweig"

    # Build one game entry per grid row (None if no Löwen game in that row)
    loewen_pending = [
        {"idx": idx, "team1": game[0], "team2": game[1]}
        for idx, game, _ in visible_pending        # your existing list
        if LOEWEN in (game[0], game[1])
    ]
    # Pad to ROWS length with None
    lion_games = loewen_pending + [None] * (ROWS - len(loewen_pending))

    return render_template('index.html',
                           grid=to_rettungswagen(grid),
                           lion_games=lion_games,
                           all_team_names=all_team_names,
                           selected_teams=selected_teams,
                           compare_teams=compare_teams,
                           full_standings=full_standings,
                           direct_standings=direct_standings,
                           hypothetical=hypothetical,
                           hypo_count=hypo_count,
                           hypo_wins=hypo_wins,
                           visible_completed=visible_completed,
                           visible_pending=visible_pending,
                           is_admin=(current_user.id == ADMIN_USER))

# ── Score routes ──────────────────────────────────────────────────────────────

@app.route('/set_score/<int:idx>', methods=['POST'])
@login_required
def set_score(idx):
    state = load_user_state(current_user.id, DEFAULT_TEAMS)
    s1 = request.form.get('score1', '').strip()
    s2 = request.form.get('score2', '').strip()
    if s1 and s2:
        state["hypothetical"][idx] = (int(s1), int(s2))
    else:
        state["hypothetical"].pop(idx, None)
    save_user_state(current_user.id, state)
    return redirect(request.referrer or '/')

@app.route('/clear_score/<int:idx>')
@login_required
def clear_score(idx):
    state = load_user_state(current_user.id, DEFAULT_TEAMS)
    state["hypothetical"].pop(idx, None)
    save_user_state(current_user.id, state)
    return redirect(request.referrer or '/')

@app.route('/finalize/<int:idx>')
@login_required
def finalize_game(idx):
    """Write a hypothetical as a real result (irreversible). Admin only by convention."""
    if idx >= len(saison_25_26) or len(saison_25_26[idx]) != 2:
        return redirect('/')

    state = load_user_state(current_user.id, DEFAULT_TEAMS)
    if idx not in state["hypothetical"]:
        return redirect('/')

    t1, t2 = saison_25_26[idx]
    s1, s2 = state["hypothetical"][idx]

    # Write result into the in-memory game list
    saison_25_26[idx] = (t1, t2, s1, s2)

    # Rebuild derived lists
    completed_games[:] = [g for g in saison_25_26 if len(g) == 4]
    pending_games[:]   = [g for g in saison_25_26 if len(g) == 2]

    # Remove from this user's hypotheticals (index stays valid — no shift needed)
    del state["hypothetical"][idx]
    save_user_state(current_user.id, state)

    write_games_py()
    return redirect('/')

@app.route("/move", methods=["POST"])
@login_required
def move():
    state = load_user_state(current_user.id, DEFAULT_TEAMS)
    r = request.json["row"]
    s = request.json["action"]
    grid = state["grid"]
    print(f"grid: {grid}")
    if(grid == {}):
        print("grid is empty")
        grid = init_grid()
    state["grid"] = apply_action(grid, r, s)
    save_user_state(current_user.id, state)
    return jsonify(to_rettungswagen(state["grid"]))

@app.route("/reset", methods=["POST"])
@login_required
def reset():
    state = load_user_state(current_user.id, DEFAULT_TEAMS)
    state["grid"] = init_grid()
    save_user_state(current_user.id, state)
    return jsonify(to_rettungswagen(state["grid"]))
    
    #POST /move
    #Content-Type: application/json
    #
    #{
    #  "row": 2,
    #  "action": "NS"
    #}
    #
    #curl -X POST http://localhost:5000/move \
    #  -H "Content-Type: application/json" \
    #  -d '{"row": 2, "action": "NS"}'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)