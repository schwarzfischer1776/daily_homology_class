import copy
import json
from datetime import date, timedelta
from flask import Flask, render_template, jsonify, abort
from problems import PROBLEMS
from targets import TARGETS

app = Flask(__name__)

# Day 1 of the cycle is today; problem #1 is shown on this date.
EPOCH = date.today()

MAX_ATTEMPTS = 3


def _build_statement(target):
    """Generate the player-facing task: compute chi(X) and the Betti functional."""
    space = target["space"]
    expr = target["expr_latex"]
    intro = (
        rf"Let $X = {space}$, and write $\beta_n = \operatorname{{rank}} "
        rf"H_n(X;\,\mathbb{{Z}})$ for its Betti numbers. "
    )
    if target["infinite"]:
        ask = (
            r"Since $X$ is infinite-dimensional its Euler characteristic is "
            r"undefined, so evaluate only the Betti-number functional "
            rf"$$\Upsilon(X) \;=\; {expr}.$$"
        )
    else:
        ask = (
            r"Compute the Euler characteristic $\chi(X)$, then evaluate the "
            rf"Betti-number functional $$\Upsilon(X) \;=\; {expr}.$$"
        )
    outro = rf" Enter the integer{'' if target['infinite'] else 's'} below — you have {MAX_ATTEMPTS} attempts."
    return intro + ask + outro


# Merge target info into a deep copy of each problem so the originals are untouched.
_DEFAULT_TARGET = {
    "space": "X",
    "euler": 0,
    "betti": [],
    "expr_latex": r"\beta_0",
    "expr_value": 0,
    "infinite": False,
}

_PROBLEMS = []
for _p in PROBLEMS:
    _p2 = copy.deepcopy(_p)
    _t = TARGETS.get(_p2["id"], _DEFAULT_TARGET)
    _p2["target"] = _t
    _p2["max_attempts"] = MAX_ATTEMPTS
    # Reframe the task: the player enters chi(X) and the functional value,
    # not the homology groups. The original statement is kept as background.
    _p2["statement"] = _build_statement(_t)
    # Hints and worked solutions are intentionally not exposed — they would
    # make the puzzle too easy.
    _p2.pop("hints", None)
    _p2.pop("solution", None)
    _PROBLEMS.append(_p2)


def problem_for_date(d: date):
    delta = (d - EPOCH).days
    if delta < 0:
        return None
    return _PROBLEMS[delta % len(_PROBLEMS)]


@app.route("/")
def index():
    today = date.today()
    problem = problem_for_date(today)
    day_number = (today - EPOCH).days
    return render_template(
        "index.html",
        problem_json=json.dumps(problem),
        today_str=today.isoformat(),
        epoch_str=EPOCH.isoformat(),
        day_number=day_number,
        total_problems=len(_PROBLEMS),
    )


@app.route("/api/problem/today")
def api_today():
    today = date.today()
    p = problem_for_date(today)
    day_number = (today - EPOCH).days
    return jsonify({"problem": p, "date": today.isoformat(), "day_number": day_number})


@app.route("/api/problem/date/<date_str>")
def api_by_date(date_str):
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        abort(400, "Invalid date format. Use YYYY-MM-DD.")
    p = problem_for_date(d)
    if p is None:
        abort(404, "No problem before the epoch date 2025-01-01.")
    day_number = (d - EPOCH).days
    return jsonify({"problem": p, "date": d.isoformat(), "day_number": day_number})


@app.route("/api/problem/<int:problem_id>")
def api_by_id(problem_id):
    for p in _PROBLEMS:
        if p["id"] == problem_id:
            return jsonify(p)
    abort(404, f"Problem {problem_id} not found.")


@app.route("/api/problems")
def api_list():
    meta = [
        {
            "id": p["id"],
            "title": p["title"],
            "type": p["type"],
            "difficulty": p["difficulty"],
            "tags": p["tags"],
        }
        for p in _PROBLEMS
    ]
    return jsonify({"problems": meta, "total": len(_PROBLEMS)})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
