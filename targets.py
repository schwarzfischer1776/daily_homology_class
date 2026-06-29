# Target data for each daily problem.
#
# For every topological space X the player must enter TWO integers:
#
#   1. the Euler characteristic  chi(X)               ("euler")
#   2. the value of an algebraic FUNCTIONAL of the    ("functional")
#      Betti numbers  beta_n = rank H_n(X; Z).
#
# The functional varies from space to space and is shown (as LaTeX) in the
# problem statement.  Because it mixes several Betti numbers together it
# produces a "large" number that cannot be guessed without having computed
# every Betti number correctly.
#
# For infinite-dimensional spaces (RP^infinity, CP^infinity) the Euler
# characteristic is undefined, so only the functional is requested.
#
# Each _DEF entry:
#   space       LaTeX name of X (without surrounding $)
#   euler       chi(X) as an int, or None if X is infinite-dimensional
#   betti       [beta_0, beta_1, ...]  (free ranks; torsion ignored)
#   expr_latex  the functional, as a LaTeX string in the beta_n
#   expr_fn     callable(b) -> number computing the functional, where b is the
#               Betti list zero-padded so any index is safe to read
#
# expr_value is computed from expr_fn at import time and asserted to be an
# integer, so the displayed LaTeX and the checked answer can never drift apart.

import math

_sqrt = math.sqrt

# pid : (space, euler, betti, expr_latex, expr_fn)
_DEFS = {
    1: (r"S^1", 0, [1, 1],
        r"11\,\beta_0 + 13\,\beta_1 + 5\,\beta_0\beta_1",
        lambda b: 11*b[0] + 13*b[1] + 5*b[0]*b[1]),

    2: (r"S^2", 2, [1, 0, 1],
        r"7\,\beta_0 + 12\,\beta_1 + 19\,\beta_2 + 3\,\beta_2^2",
        lambda b: 7*b[0] + 12*b[1] + 19*b[2] + 3*b[2]**2),

    3: (r"S^4", 2, [1, 0, 0, 0, 1],
        r"5\,\beta_0 + 6\,\beta_1 + 7\,\beta_2 + 8\,\beta_3 + 9\,\beta_4 + 4\,\beta_4^2",
        lambda b: 5*b[0] + 6*b[1] + 7*b[2] + 8*b[3] + 9*b[4] + 4*b[4]**2),

    4: (r"D^n", 1, [1],
        r"17\,\beta_0 + 6\,\beta_0^2",
        lambda b: 17*b[0] + 6*b[0]**2),

    5: (r"T^2", 0, [1, 2, 1],
        r"7\,\beta_0 + \sqrt{9\,\beta_1^2 + 24\,\beta_1\beta_2 + 16\,\beta_2^2}",
        lambda b: 7*b[0] + _sqrt(9*b[1]**2 + 24*b[1]*b[2] + 16*b[2]**2)),

    6: (r"\mathbb{R}P^2", 1, [1, 0, 0],
        r"14\,\beta_0 + 9\,\beta_1 + 11\,\beta_2 + 2\,\beta_1\beta_2",
        lambda b: 14*b[0] + 9*b[1] + 11*b[2] + 2*b[1]*b[2]),

    7: (r"K", 0, [1, 1, 0],
        r"10\,\beta_0 + 12\,\beta_1 + 15\,\beta_2 + \beta_1^2",
        lambda b: 10*b[0] + 12*b[1] + 15*b[2] + b[1]**2),

    8: (r"S^1 \vee S^1", -1, [1, 2],
        r"9\,\beta_0 + 10\,\beta_1 + 3\,\beta_1^2",
        lambda b: 9*b[0] + 10*b[1] + 3*b[1]**2),

    9: (r"M", 0, [1, 1],
        r"13\,\beta_0 + 8\,\beta_1 + 4\,\beta_0\beta_1",
        lambda b: 13*b[0] + 8*b[1] + 4*b[0]*b[1]),

    10: (r"S^2", 2, [1, 0, 1],
         r"6\,\beta_0 + 15\,\beta_1 + 21\,\beta_2 + 2\,\beta_2^2",
         lambda b: 6*b[0] + 15*b[1] + 21*b[2] + 2*b[2]**2),

    11: (r"T^2", 0, [1, 2, 1],
         r"4\,\beta_0 + 7\,\beta_1 + 9\,\beta_2 + 2\,\beta_1^2",
         lambda b: 4*b[0] + 7*b[1] + 9*b[2] + 2*b[1]**2),

    12: (r"\Sigma_3", -4, [1, 6, 1],
         r"2\,\beta_0 + 3\,\beta_1 + 5\,\beta_2 + \beta_1^2",
         lambda b: 2*b[0] + 3*b[1] + 5*b[2] + b[1]**2),

    13: (r"S^1 \vee S^2", 1, [1, 1, 1],
         r"8\,\beta_0 + 11\,\beta_1 + 13\,\beta_2 + 3\,\beta_1\beta_2",
         lambda b: 8*b[0] + 11*b[1] + 13*b[2] + 3*b[1]*b[2]),

    14: (r"\mathbb{R}P^1", 0, [1, 1],
         r"12\,\beta_0 + 14\,\beta_1 + 2\,\beta_0\beta_1",
         lambda b: 12*b[0] + 14*b[1] + 2*b[0]*b[1]),

    15: (r"\mathbb{R}P^3", 0, [1, 0, 0, 1],
         r"5\,\beta_0 + 7\,\beta_1 + 9\,\beta_2 + 11\,\beta_3 + 4\,\beta_3^2",
         lambda b: 5*b[0] + 7*b[1] + 9*b[2] + 11*b[3] + 4*b[3]**2),

    16: (r"\mathbb{R}P^6", 1, [1, 0, 0, 0, 0, 0, 0],
         r"19\,\beta_0 + 2\,\beta_1 + 3\,\beta_2 + 4\,\beta_3 + 5\,\beta_4 + 6\,\beta_5 + 7\,\beta_6",
         lambda b: 19*b[0] + 2*b[1] + 3*b[2] + 4*b[3] + 5*b[4] + 6*b[5] + 7*b[6]),

    17: (r"\mathbb{C}P^3", 4, [1, 0, 1, 0, 1, 0, 1],
         r"3\,\beta_0 + 4\,\beta_1 + \sqrt{4\,\beta_2^2 + 12\,\beta_2\beta_4 + 9\,\beta_4^2} + 6\,\beta_3 + 8\,\beta_5 + 10\,\beta_6",
         lambda b: 3*b[0] + 4*b[1] + _sqrt(4*b[2]**2 + 12*b[2]*b[4] + 9*b[4]**2) + 6*b[3] + 8*b[5] + 10*b[6]),

    18: (r"S^2 \times S^4", 4, [1, 0, 1, 0, 1, 0, 1],
         r"2\,\beta_0 + 3\,\beta_1 + 4\,\beta_2 + 5\,\beta_3 + 6\,\beta_4 + 7\,\beta_5 + 8\,\beta_6",
         lambda b: 2*b[0] + 3*b[1] + 4*b[2] + 5*b[3] + 6*b[4] + 7*b[5] + 8*b[6]),

    19: (r"T^3", 0, [1, 3, 3, 1],
         r"\dfrac{2\,\beta_1^2 + 4\,\beta_2^2 + 6\,\beta_3}{1 + \beta_0}",
         lambda b: (2*b[1]**2 + 4*b[2]**2 + 6*b[3]) / (1 + b[0])),

    20: (r"S^1 \times \mathbb{R}P^2", 0, [1, 1, 0],
         r"11\,\beta_0 + 13\,\beta_1 + 17\,\beta_2 + 2\,\beta_1^2",
         lambda b: 11*b[0] + 13*b[1] + 17*b[2] + 2*b[1]**2),

    21: (r"N_4", -2, [1, 3, 0],
         r"4\,\beta_0 + 6\,\beta_1 + 8\,\beta_2 + \beta_1^2",
         lambda b: 4*b[0] + 6*b[1] + 8*b[2] + b[1]**2),

    22: (r"(D^5,\, S^4)", -1, [0, 0, 0, 0, 0, 1],
         r"2\,\beta_0 + 3\,\beta_1 + 4\,\beta_2 + 5\,\beta_3 + 6\,\beta_4 + 7\,\beta_5 + 5\,\beta_5^2",
         lambda b: 2*b[0] + 3*b[1] + 4*b[2] + 5*b[3] + 6*b[4] + 7*b[5] + 5*b[5]**2),

    23: (r"S^6", 2, [1, 0, 0, 0, 0, 0, 1],
         r"3\,\beta_0 + 2\,\beta_1 + 2\,\beta_2 + 2\,\beta_3 + 2\,\beta_4 + 2\,\beta_5 + 13\,\beta_6 + 4\,\beta_6^2",
         lambda b: 3*b[0] + 2*b[1] + 2*b[2] + 2*b[3] + 2*b[4] + 2*b[5] + 13*b[6] + 4*b[6]**2),

    24: (r"\mathbb{R}P^2", 1, [1, 0, 0],
         r"16\,\beta_0 + 7\,\beta_1 + 9\,\beta_2 + 3\,\beta_1\beta_2",
         lambda b: 16*b[0] + 7*b[1] + 9*b[2] + 3*b[1]*b[2]),

    25: (r"SO(3)", 0, [1, 0, 0, 1],
         r"6\,\beta_0 + 8\,\beta_1 + 10\,\beta_2 + 12\,\beta_3 + 2\,\beta_3^2",
         lambda b: 6*b[0] + 8*b[1] + 10*b[2] + 12*b[3] + 2*b[3]**2),

    26: (r"\mathbb{R}P^4", 1, [1, 0, 0, 0, 0],
         r"21\,\beta_0 + 2\,\beta_1 + 3\,\beta_2 + 4\,\beta_3 + 5\,\beta_4",
         lambda b: 21*b[0] + 2*b[1] + 3*b[2] + 4*b[3] + 5*b[4]),

    27: (r"\mathbb{C}P^2", 3, [1, 0, 1, 0, 1],
         r"\dfrac{4\,\beta_0 + 2\,\beta_1 + 8\,\beta_2 + 2\,\beta_3 + 6\,\beta_4}{1 + \beta_2}",
         lambda b: (4*b[0] + 2*b[1] + 8*b[2] + 2*b[3] + 6*b[4]) / (1 + b[2])),

    28: (r"K", 0, [1, 1, 0],
         r"9\,\beta_0 + 11\,\beta_1 + 13\,\beta_2 + 2\,\beta_0\beta_1",
         lambda b: 9*b[0] + 11*b[1] + 13*b[2] + 2*b[0]*b[1]),

    29: (r"\mathbb{C}P^4", 5, [1, 0, 1, 0, 1, 0, 1, 0, 1],
         r"2\,\beta_0 + 3\,\beta_2 + 4\,\beta_4 + 5\,\beta_6 + 6\,\beta_8 + (\beta_1+\beta_3+\beta_5+\beta_7)",
         lambda b: 2*b[0] + 3*b[2] + 4*b[4] + 5*b[6] + 6*b[8] + (b[1]+b[3]+b[5]+b[7])),

    30: (r"T^2", 0, [1, 2, 1],
         r"5\,\beta_0 + 6\,\beta_1 + 7\,\beta_2 + 2\,\beta_1\beta_2",
         lambda b: 5*b[0] + 6*b[1] + 7*b[2] + 2*b[1]*b[2]),

    31: (r"\mathbb{R}P^4", 1, [1, 0, 0, 0, 0],
         r"23\,\beta_0 + 2\,\beta_1 + 3\,\beta_2 + 4\,\beta_3 + 5\,\beta_4",
         lambda b: 23*b[0] + 2*b[1] + 3*b[2] + 4*b[3] + 5*b[4]),

    32: (r"L(5,2)", 0, [1, 0, 0, 1],
         r"7\,\beta_0 + 9\,\beta_1 + 11\,\beta_2 + 13\,\beta_3",
         lambda b: 7*b[0] + 9*b[1] + 11*b[2] + 13*b[3]),

    33: (r"L(7,1)", 0, [1, 0, 0, 1],
         r"8\,\beta_0 + 10\,\beta_1 + 12\,\beta_2 + 14\,\beta_3",
         lambda b: 8*b[0] + 10*b[1] + 12*b[2] + 14*b[3]),

    34: (r"\mathbb{R}P^\infty", None, [1, 0, 0, 0, 0, 0, 0],
         r"15\,\beta_0 + 2\,\beta_1 + 3\,\beta_2 + 4\,\beta_3 + 5\,\beta_4 + 6\,\beta_5 + 7\,\beta_6",
         lambda b: 15*b[0] + 2*b[1] + 3*b[2] + 4*b[3] + 5*b[4] + 6*b[5] + 7*b[6]),

    35: (r"\mathbb{C}P^\infty", None, [1, 0, 1, 0, 1, 0, 1],
         r"2\,\beta_0 + 3\,\beta_1 + 4\,\beta_2 + 5\,\beta_3 + 6\,\beta_4 + 7\,\beta_5 + 8\,\beta_6",
         lambda b: 2*b[0] + 3*b[1] + 4*b[2] + 5*b[3] + 6*b[4] + 7*b[5] + 8*b[6]),

    36: (r"S^3 \times S^3", 0, [1, 0, 0, 2, 0, 0, 1],
         r"3\,\beta_0 + 2\,\beta_1 + 2\,\beta_2 + 5\,\beta_3 + 2\,\beta_4 + 2\,\beta_5 + 7\,\beta_6 + \beta_3^2",
         lambda b: 3*b[0] + 2*b[1] + 2*b[2] + 5*b[3] + 2*b[4] + 2*b[5] + 7*b[6] + b[3]**2),

    37: (r"\mathbb{C}P^2", 3, [1, 0, 1, 0, 1],
         r"6\,\beta_0 + 7\,\beta_1 + 8\,\beta_2 + 9\,\beta_3 + 10\,\beta_4",
         lambda b: 6*b[0] + 7*b[1] + 8*b[2] + 9*b[3] + 10*b[4]),

    38: (r"K3", 24, [1, 0, 22, 0, 1],
         r"\dfrac{2\,\beta_2 + 4\,\beta_4 + 2\,\beta_1 + 2\,\beta_3}{1 + \beta_0}",
         lambda b: (2*b[2] + 4*b[4] + 2*b[1] + 2*b[3]) / (1 + b[0])),

    39: (r"\Sigma_4", -6, [1, 8, 1],
         r"2\,\beta_0 + 3\,\beta_1 + 5\,\beta_2 + \beta_1^2",
         lambda b: 2*b[0] + 3*b[1] + 5*b[2] + b[1]**2),

    40: (r"\mathbb{C}P^3", 4, [1, 0, 1, 0, 1, 0, 1],
         r"2\,\beta_0 + 2\,\beta_1 + 4\,\beta_2 + 2\,\beta_3 + 6\,\beta_4 + 2\,\beta_5 + 8\,\beta_6",
         lambda b: 2*b[0] + 2*b[1] + 4*b[2] + 2*b[3] + 6*b[4] + 2*b[5] + 8*b[6]),

    41: (r"F(\mathbb{R}^2, 2)", 0, [1, 1],
         r"17\,\beta_0 + 19\,\beta_1 + 4\,\beta_0\beta_1",
         lambda b: 17*b[0] + 19*b[1] + 4*b[0]*b[1]),

    42: (r"\mathbb{C}P^2 \,\#\, \mathbb{C}P^2", 4, [1, 0, 2, 0, 1],
         r"3\,\beta_0 + 2\,\beta_1 + 5\,\beta_2 + 2\,\beta_3 + 7\,\beta_4 + \beta_2^2",
         lambda b: 3*b[0] + 2*b[1] + 5*b[2] + 2*b[3] + 7*b[4] + b[2]**2),
}


def _pad(betti, n=16):
    return list(betti) + [0] * (n - len(betti))


def _build():
    targets = {}
    for pid, (space, euler, betti, expr_latex, expr_fn) in _DEFS.items():
        raw = expr_fn(_pad(betti))
        val = round(raw)
        if abs(raw - val) > 1e-9:
            raise ValueError(
                f"Problem {pid}: functional is not integer-valued ({raw})."
            )
        targets[pid] = {
            "space": space,
            "euler": euler,                 # int or None (infinite-dimensional)
            "betti": list(betti),
            "expr_latex": expr_latex,
            "expr_value": int(val),
            "infinite": euler is None,
        }
    return targets


TARGETS = _build()


if __name__ == "__main__":
    for pid in sorted(TARGETS):
        t = TARGETS[pid]
        chi = "undefined" if t["euler"] is None else t["euler"]
        print(f"#{pid:>2}  X = {t['space']:<24}  "
              f"chi = {chi!s:<9}  betti = {t['betti']!s:<18}  "
              f"F = {t['expr_value']}")
