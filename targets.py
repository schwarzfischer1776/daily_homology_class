# Target answer for each problem.
# "euler"  → compute χ(X) (integer, possibly negative)
# "betti"  → compute β_n = rank H_n(X; Z)  (non-negative integer)
# value    → the correct integer answer
# question → short LaTeX string shown in the answer box

TARGETS = {
    1:  {
        "type": "euler",
        "question": r"Compute $\chi(S^1)$.",
        "value": 0,
    },
    2:  {
        "type": "euler",
        "question": r"Compute $\chi(S^2)$.",
        "value": 2,
    },
    3:  {
        "type": "euler",
        "question": r"Apply the general formula: compute $\chi(S^4)$.",
        "value": 2,
    },
    4:  {
        "type": "euler",
        "question": r"Compute $\chi(D^n)$ (your answer should be independent of $n$).",
        "value": 1,
    },
    5:  {
        "type": "euler",
        "question": r"Compute $\chi(T^2)$.",
        "value": 0,
    },
    6:  {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{R}P^2)$.",
        "value": 1,
    },
    7:  {
        "type": "euler",
        "question": r"Compute $\chi(K)$ for the Klein bottle $K$.",
        "value": 0,
    },
    8:  {
        "type": "euler",
        "question": r"Compute $\chi(S^1 \vee S^1)$.",
        "value": -1,
    },
    9:  {
        "type": "euler",
        "question": r"Compute $\chi(M)$ for the Möbius band $M$.",
        "value": 0,
    },
    10: {
        "type": "euler",
        "question": r"Compute $\chi(S^2)$ (compare with $\chi(S^1)$ to settle the question).",
        "value": 2,
    },
    11: {
        "type": "betti",
        "n": 2,
        "question": r"Compute $\beta_2(T^2) = \operatorname{rank} H_2(T^2;\,\mathbb{Z})$.",
        "value": 1,
    },
    12: {
        "type": "euler",
        "question": r"Compute $\chi(\Sigma_3)$ for the closed orientable surface of genus $3$.",
        "value": -4,
    },
    13: {
        "type": "euler",
        "question": r"Compute $\chi(S^1 \vee S^2)$.",
        "value": 1,
    },
    14: {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{R}P^1)$.",
        "value": 0,
    },
    15: {
        "type": "betti",
        "n": 3,
        "question": r"Compute $\beta_3(\mathbb{R}P^3) = \operatorname{rank} H_3(\mathbb{R}P^3;\,\mathbb{Z})$.",
        "value": 1,
    },
    16: {
        "type": "euler",
        "question": r"Apply the general formula to compute $\chi(\mathbb{R}P^6)$.",
        "value": 1,
    },
    17: {
        "type": "euler",
        "question": r"Apply the general formula to compute $\chi(\mathbb{C}P^3)$.",
        "value": 4,
    },
    18: {
        "type": "euler",
        "question": r"Use the product formula $\chi(X\times Y)=\chi(X)\chi(Y)$ to compute $\chi(S^2 \times S^4)$.",
        "value": 4,
    },
    19: {
        "type": "betti",
        "n": 2,
        "question": r"Compute $\beta_2(T^3) = \operatorname{rank} H_2(T^3;\,\mathbb{Z})$.",
        "value": 3,
    },
    20: {
        "type": "betti",
        "n": 1,
        "question": r"Compute $\beta_1(S^1\times\mathbb{R}P^2) = \operatorname{rank} H_1(S^1\times\mathbb{R}P^2;\,\mathbb{Z})$.",
        "value": 1,
    },
    21: {
        "type": "euler",
        "question": r"Compute $\chi(N_4)$ for the non-orientable surface with $4$ crosscaps.",
        "value": -2,
    },
    22: {
        "type": "betti",
        "n": 5,
        "question": r"Compute $\beta_5(D^5, S^4) = \operatorname{rank} H_5(D^5, S^4;\,\mathbb{Z})$.",
        "value": 1,
    },
    23: {
        "type": "euler",
        "question": r"Use Mayer–Vietoris to compute $\chi(S^6)$.",
        "value": 2,
    },
    24: {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{R}P^2)$ (compare with $\chi(T^2)=0$ to settle the homeomorphism question).",
        "value": 1,
    },
    25: {
        "type": "betti",
        "n": 3,
        "question": r"Compute $\beta_3(SO(3)) = \operatorname{rank} H_3(SO(3);\,\mathbb{Z})$.",
        "value": 1,
    },
    26: {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{R}P^4)$.",
        "value": 1,
    },
    27: {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{C}P^2)$.",
        "value": 3,
    },
    28: {
        "type": "betti",
        "n": 1,
        "question": r"Compute $\beta_1(K) = \operatorname{rank} H_1(K;\,\mathbb{Z})$ (free rank only, ignore torsion).",
        "value": 1,
    },
    29: {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{C}P^4)$ using the ring structure you found.",
        "value": 5,
    },
    30: {
        "type": "betti",
        "n": 1,
        "question": r"Compute $\beta_1(T^2) = \operatorname{rank} H^1(T^2;\,\mathbb{Z})$.",
        "value": 2,
    },
    31: {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{R}P^4)$ (the Euler characteristic is coefficient-independent).",
        "value": 1,
    },
    32: {
        "type": "betti",
        "n": 3,
        "question": r"Compute $\beta_3(L(5,2)) = \operatorname{rank} H_3(L(5,2);\,\mathbb{Z})$.",
        "value": 1,
    },
    33: {
        "type": "betti",
        "n": 1,
        "question": r"Compute $\beta_1(L(7,1)) = \operatorname{rank} H_1(L(7,1);\,\mathbb{Z})$ (free rank; torsion does not count).",
        "value": 0,
    },
    34: {
        "type": "betti",
        "n": 5,
        "question": r"Compute $\beta_5(\mathbb{R}P^\infty) = \operatorname{rank} H_5(\mathbb{R}P^\infty;\,\mathbb{Z})$ (Betti number = free rank).",
        "value": 0,
    },
    35: {
        "type": "betti",
        "n": 6,
        "question": r"Compute $\beta_6(\mathbb{C}P^\infty) = \operatorname{rank} H_6(\mathbb{C}P^\infty;\,\mathbb{Z})$.",
        "value": 1,
    },
    36: {
        "type": "betti",
        "n": 3,
        "question": r"Compute $\beta_3(S^3 \times S^3) = \operatorname{rank} H_3(S^3\times S^3;\,\mathbb{Z})$.",
        "value": 2,
    },
    37: {
        "type": "betti",
        "n": 2,
        "question": r"Compute $\beta_2(\mathbb{C}P^2) = \operatorname{rank} H_2(\mathbb{C}P^2;\,\mathbb{Z})$ (compare with $\beta_2(S^4)=0$).",
        "value": 1,
    },
    38: {
        "type": "euler",
        "question": r"Compute $\chi(K3)$ for the $K3$ surface.",
        "value": 24,
    },
    39: {
        "type": "euler",
        "question": r"Apply the formula you proved: compute $\chi(\Sigma_4)$ for the genus-$4$ surface.",
        "value": -6,
    },
    40: {
        "type": "euler",
        "question": r"Apply Poincaré duality: compute $\chi(\mathbb{C}P^3)$.",
        "value": 4,
    },
    41: {
        "type": "betti",
        "n": 1,
        "question": r"Compute $\beta_1(F(\mathbb{R}^2,2)) = \operatorname{rank} H_1(F(\mathbb{R}^2,2);\,\mathbb{Z})$.",
        "value": 1,
    },
    42: {
        "type": "euler",
        "question": r"Compute $\chi(\mathbb{C}P^2 \,\#\, \mathbb{C}P^2)$.",
        "value": 4,
    },
}
