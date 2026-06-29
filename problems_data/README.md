# Problem set

Each problem is one JSON file in this folder. To add a problem, drop in a new
file (any name ending in `.json`; `NNN.json` zero-padded by id is the
convention). The app picks it up on the next restart and **appends it to the
end of the release queue** — existing days are never reshuffled.

## Schema

```jsonc
{
  "id": 43,                     // unique integer id (required)
  "title": "Homology of ...",   // shown as the heading; may contain $LaTeX$
  "type": "homology",           // e.g. "homology" / "cohomology"
  "difficulty": "easy",         // "easy" | "medium" | "hard"
  "tags": ["CW complex", "spheres"],

  "space": "S^1",               // LaTeX for X, WITHOUT surrounding $ … $
  "euler": 0,                   // Euler characteristic χ(X) as an int,
                                //   or null for infinite-dimensional X
  "betti": [1, 1],              // [β_0, β_1, …] free ranks (torsion ignored)

  "functional": {
    "latex": "11\\beta_0 + 13\\beta_1",  // the Betti functional Υ(X), LaTeX
    "value": 24                          // its integer value — the answer the
                                         //   player enters in integer mode
  },

  "functional_decimal": {       // optional: harder, decimal-valued functional
    "latex": "\\sqrt{1 + 2\\beta_0^2 + 3\\beta_1^2} + \\dfrac{2\\beta_0 + 3\\beta_1}{4}",
    "value": 3.69949,           // full-precision value; checked to `decimals` dp
    "decimals": 3               // how many decimal places the player must match
  },

  "solution": {                 // revealed only after the puzzle is solved
    "answer": "$H_0 \\cong \\mathbb{Z}, \\; H_1 \\cong \\mathbb{Z}$",
    "steps": [
      "Give X a CW structure …",
      "The cellular chain complex is …"
    ]
  }
}
```

Notes:
- The player is asked for χ (`euler`, always an integer) and Υ. For
  infinite-dimensional spaces set `"euler": null`; only Υ is then asked.
- `functional.value` must be the correct value of `functional.latex` evaluated
  at the given `betti` numbers — likewise `functional_decimal.value` for the
  decimal one. They are checked against the player's input, so keep them
  consistent.
- All math is LaTeX (MathJax). Inside JSON, backslashes must be escaped: write
  `\\beta_0`, `\\mathbb{Z}`, etc.

### Integer vs. decimal mode

The site runs in one of two modes, set by `FUNCTIONAL_MODE` in
`../problemset.py` (or the `HOMOLOGY_MODE` env var):

- `"decimal"` (default) — uses `functional_decimal`; the player must enter Υ
  correct to `decimals` decimal places (a calculator is needed, so the answer
  can't be brute-forced). Falls back to the integer functional for any problem
  lacking a `functional_decimal`.
- `"integer"` — uses the plain integer `functional`.

Switch with e.g. `HOMOLOGY_MODE=integer python3 server.py`, or edit the default.

## Release schedule

The mapping of "which problem on which day" lives in `../schedule.json`
(`epoch` = the date of day 1, `order` = problem ids in release order). It is
generated once in a random order and then frozen. Delete it to regenerate a
fresh random schedule.
