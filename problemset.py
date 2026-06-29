"""Loads the problem set from the ``problems_data/`` JSON folder and manages the
daily release schedule.

Each problem lives in its own JSON file (see ``problems_data/001.json`` for the
schema), so new problems can be added simply by dropping another file in that
folder — by you, or by other contributors.

The *release schedule* (which problem appears on which day) is kept in
``schedule.json``.  It is generated once, in a random order (so problems do not
appear easy-to-hard), and then frozen so the ordering is stable across restarts.
Any newly added problems are appended to the end of the queue automatically.
"""

import copy
import json
import os
import random
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_DIR = os.path.join(HERE, "problems_data")
SCHEDULE_FILE = os.path.join(HERE, "schedule.json")

MAX_ATTEMPTS = 3

# Which Betti-number functional to use for the answer the player must enter:
#   "decimal" — square-root / fraction functional; answer is a decimal that
#               must be entered correct to 3 decimal places (needs a calculator).
#   "integer" — the original integer-valued functional.
# Flip this (or set the HOMOLOGY_MODE env var) to switch the whole site over.
FUNCTIONAL_MODE = os.environ.get("HOMOLOGY_MODE", "integer").lower()

# How many problems should already be published the very first time the schedule
# is created.  Day 0 ... PUBLISHED_AT_START-1 are unlocked immediately.
PUBLISHED_AT_START = 7

# Seed so the initial "random" order is reproducible if the schedule is deleted.
_SHUFFLE_SEED = 1729


# ─────────────────────────────────────────────────────────────────────────────
# Statement generation (player-facing task: compute chi and the Betti functional)
# ─────────────────────────────────────────────────────────────────────────────
def _build_statement(problem):
    space = problem["space"]
    func = problem["functional"]
    expr = func["latex"]
    decimal = func.get("decimal", False)
    decimals = func.get("decimals", 3)
    infinite = problem["euler"] is None
    intro = (
        rf"Let $X = {space}$, and write $\beta_n = \operatorname{{rank}} "
        rf"H_n(X;\,\mathbb{{Z}})$ for its Betti numbers. "
    )
    if infinite:
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
    if decimal:
        what = (
            rf"the Euler characteristic (an integer) and $\Upsilon$ rounded to "
            rf"{decimals} decimal places"
            if not infinite
            else rf"$\Upsilon$ rounded to {decimals} decimal places"
        )
        outro = rf" Enter {what} below — you have {MAX_ATTEMPTS} attempts."
    else:
        outro = (
            rf" Enter the integer{'' if infinite else 's'} below — "
            rf"you have {MAX_ATTEMPTS} attempts."
        )
    return intro + ask + outro


# ─────────────────────────────────────────────────────────────────────────────
# Loading
# ─────────────────────────────────────────────────────────────────────────────
def _select_functional(obj):
    """Pick the active functional for the current FUNCTIONAL_MODE and tag it with
    metadata the client uses to decide integer vs. decimal answer handling."""
    use_decimal = FUNCTIONAL_MODE == "decimal" and obj.get("functional_decimal")
    if use_decimal:
        fd = obj["functional_decimal"]
        return {
            "latex": fd["latex"],
            "value": fd["value"],
            "decimal": True,
            "decimals": fd.get("decimals", 3),
        }
    fi = obj["functional"]
    return {
        "latex": fi["latex"],
        "value": fi["value"],
        "decimal": False,
        "decimals": 0,
    }


def _load_raw():
    """Read every ``*.json`` file in PROBLEMS_DIR, keyed by problem id."""
    problems = {}
    for name in sorted(os.listdir(PROBLEMS_DIR)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(PROBLEMS_DIR, name)
        with open(path, encoding="utf-8") as f:
            obj = json.load(f)
        pid = obj["id"]
        if pid in problems:
            raise ValueError(f"Duplicate problem id {pid} (in {name}).")
        # Light validation so a bad contribution fails loudly at startup.
        for key in ("id", "title", "type", "difficulty", "tags",
                    "space", "euler", "betti", "functional", "solution"):
            if key not in obj:
                raise ValueError(f"{name}: missing required key '{key}'.")
        obj["infinite"] = obj["euler"] is None
        obj["functional"] = _select_functional(obj)
        obj["statement"] = _build_statement(obj)
        obj["max_attempts"] = MAX_ATTEMPTS
        problems[pid] = obj
    if not problems:
        raise RuntimeError(f"No problem JSON files found in {PROBLEMS_DIR}.")
    return problems


# ─────────────────────────────────────────────────────────────────────────────
# Schedule
# ─────────────────────────────────────────────────────────────────────────────
def _load_or_create_schedule(all_ids):
    """Return (epoch_date, order) where ``order`` is a list of problem ids in
    release order and ``order[i]`` is published on ``epoch + i`` days.

    The schedule is persisted to SCHEDULE_FILE.  Existing entries are never
    reshuffled; problems not yet in the schedule are appended (in a shuffled
    order) so adding new files keeps already-published days stable.
    """
    all_ids = list(all_ids)
    schedule = None
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, encoding="utf-8") as f:
            schedule = json.load(f)

    if schedule is None:
        # First run: random order, and back-date the epoch so that
        # PUBLISHED_AT_START problems are already available today.
        order = list(all_ids)
        random.Random(_SHUFFLE_SEED).shuffle(order)
        epoch = date.today() - timedelta(days=PUBLISHED_AT_START - 1)
        schedule = {"epoch": epoch.isoformat(), "order": order}
        _write_schedule(schedule)
    else:
        order = list(schedule["order"])
        known = set(order)
        # Drop ids whose JSON file disappeared; append brand-new ids.
        order = [pid for pid in order if pid in set(all_ids)]
        new_ids = [pid for pid in all_ids if pid not in known]
        if new_ids:
            random.Random(_SHUFFLE_SEED + len(order)).shuffle(new_ids)
            order.extend(new_ids)
        if order != schedule["order"]:
            schedule["order"] = order
            _write_schedule(schedule)

    epoch = date.fromisoformat(schedule["epoch"])
    return epoch, schedule["order"]


def _write_schedule(schedule):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2)
        f.write("\n")


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
class ProblemSet:
    def __init__(self):
        self._by_id = _load_raw()
        self.epoch, self.order = _load_or_create_schedule(self._by_id.keys())
        self.total = len(self.order)

    # ── date / release helpers ──────────────────────────────────────────────
    def day_number(self, d: date) -> int:
        """Days since the epoch (day 0 == first published problem)."""
        return (d - self.epoch).days

    def today_index(self) -> int:
        return self.day_number(date.today())

    def is_released(self, d: date) -> bool:
        n = self.day_number(d)
        return 0 <= n <= self.today_index()

    def id_for_index(self, release_index: int):
        """Problem id published at a given release index (cycles after one pass)."""
        if release_index < 0:
            return None
        return self.order[release_index % self.total]

    def _public_copy(self, pid):
        """A deep copy of the problem with the solution stripped out — the
        solution is only delivered separately, after the puzzle is solved."""
        p = copy.deepcopy(self._by_id[pid])
        p.pop("solution", None)
        p.pop("functional_decimal", None)  # only the active functional is exposed
        return p

    def problem_for_date(self, d: date):
        """Returns the public problem dict for a released date, else ``None``."""
        if not self.is_released(d):
            return None
        return self._public_copy(self.id_for_index(self.day_number(d)))

    def unlock_date_for(self, d: date) -> date:
        return self.epoch + timedelta(days=self.day_number(d))

    def solution_for(self, pid):
        p = self._by_id.get(pid)
        return p["solution"] if p else None

    # ── archive ─────────────────────────────────────────────────────────────
    def archive(self):
        """One entry per release slot in the first cycle.  Released slots carry
        full metadata; locked slots are previews carrying only their date."""
        today_idx = self.today_index()
        entries = []
        for i in range(self.total):
            d = self.epoch + timedelta(days=i)
            released = i <= today_idx
            entry = {
                "release_index": i,
                "day_number": i,
                "date": d.isoformat(),
                "released": released,
            }
            if released:
                p = self._by_id[self.id_for_index(i)]
                entry.update({
                    "id": p["id"],
                    "title": p["title"],
                    "type": p["type"],
                    "difficulty": p["difficulty"],
                    "tags": p["tags"],
                })
            entries.append(entry)
        return entries
