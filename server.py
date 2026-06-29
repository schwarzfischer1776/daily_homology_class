import json
from datetime import date
from flask import Flask, render_template, jsonify, abort

from problemset import ProblemSet

app = Flask(__name__)

# Loads problems from problems_data/*.json and the release schedule.
PS = ProblemSet()


def _date_payload(d: date):
    """Build the API payload for a given date, handling locked/preview days."""
    n = PS.day_number(d)
    if n < 0:
        return {
            "problem": None,
            "locked": True,
            "before_start": True,
            "date": d.isoformat(),
            "day_number": n,
            "epoch": PS.epoch.isoformat(),
        }
    if not PS.is_released(d):
        # Future day: reveal that a problem is coming, but not its content.
        return {
            "problem": None,
            "locked": True,
            "before_start": False,
            "date": d.isoformat(),
            "day_number": n,
        }
    return {
        "problem": PS.problem_for_date(d),
        "locked": False,
        "date": d.isoformat(),
        "day_number": n,
    }


@app.route("/")
def index():
    today = date.today()
    payload = _date_payload(today)
    return render_template(
        "index.html",
        problem_json=json.dumps(payload["problem"]),
        today_str=today.isoformat(),
        epoch_str=PS.epoch.isoformat(),
        day_number=payload["day_number"],
        total_problems=PS.total,
    )


@app.route("/api/problem/today")
def api_today():
    return jsonify(_date_payload(date.today()))


@app.route("/api/problem/date/<date_str>")
def api_by_date(date_str):
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        abort(400, "Invalid date format. Use YYYY-MM-DD.")
    return jsonify(_date_payload(d))


@app.route("/api/solution/<int:problem_id>")
def api_solution(problem_id):
    """The worked homology computation, revealed once the puzzle is solved."""
    sol = PS.solution_for(problem_id)
    if sol is None:
        abort(404, f"Solution for problem {problem_id} not found.")
    return jsonify({"id": problem_id, "solution": sol})


@app.route("/api/problems")
def api_list():
    return jsonify({"problems": PS.archive(), "total": PS.total})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
