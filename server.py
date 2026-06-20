import copy
import json
from datetime import date, timedelta
from flask import Flask, render_template, jsonify, abort
from problems import PROBLEMS
from targets import TARGETS

app = Flask(__name__)

EPOCH = date(2025, 1, 1)

# Merge target info into a deep copy of each problem so the originals are untouched.
_PROBLEMS = []
for _p in PROBLEMS:
    _p2 = copy.deepcopy(_p)
    _p2["target"] = TARGETS.get(_p2["id"], {"type": "euler", "question": r"Compute $\chi(X)$.", "value": 0})
    _PROBLEMS.append(_p2)


def problem_for_date(d: date):
    delta = (d - EPOCH).days
    if delta < 0:
        return None
    return _PROBLEMS[delta % len(_PROBLEMS)]


@app.route("/")
def index_dev():
    render_template(
        "index_dev.html"
    )

def index():
    today = date.today()
    problem = problem_for_date(today)
    day_number = (today - EPOCH).days
    return render_template(
        "index.html",
        problem_json=json.dumps(problem),
        today_str=today.isoformat(),
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


#if __name__ == "__main__":
#    app.run(debug=True, port=5001)
