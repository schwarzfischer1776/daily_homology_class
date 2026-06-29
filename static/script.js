/* ── State ─────────────────────────────────────────────────────── */
let currentDate    = TODAY_STR;
let currentDay     = DAY_NUMBER;
let archiveCache   = null;
let attemptsLeft   = 3;
let answered       = false;

/* ── DOM refs ──────────────────────────────────────────────────── */
const card           = document.getElementById("problem-card");
const titleEl        = document.getElementById("problem-title");
const statementEl    = document.getElementById("problem-statement");
const tagsRowEl      = document.getElementById("tags-row");
const badgeDiff      = document.getElementById("badge-difficulty");
const badgeType      = document.getElementById("badge-type");
const dayCounter     = document.getElementById("day-counter");
const dateDisplay    = document.getElementById("date-display");
const answerQuestion = document.getElementById("answer-question");
const fieldEuler     = document.getElementById("field-euler");
const inputEuler     = document.getElementById("input-euler");
const inputExpr      = document.getElementById("input-expr");
const attemptsLeftEl = document.getElementById("attempts-left");
const btnCheck       = document.getElementById("btn-check");
const feedback       = document.getElementById("answer-feedback");
const liveContent    = document.getElementById("live-content");
const lockedCard     = document.getElementById("locked-card");
const lockedText     = document.getElementById("locked-text");
const solutionSec    = document.getElementById("solution-section");
const solutionAnswer = document.getElementById("solution-answer");
const solutionSteps  = document.getElementById("solution-steps");
const btnPrev        = document.getElementById("btn-prev");
const btnNext        = document.getElementById("btn-next");
const btnToday       = document.getElementById("btn-today");
const btnArchive     = document.getElementById("btn-archive");
const archiveOverlay = document.getElementById("archive-overlay");
const archiveList    = document.getElementById("archive-list");
const btnCloseArc    = document.getElementById("btn-close-archive");
const modeCheckbox   = document.getElementById("mode-checkbox");

/* ── Light / Dark mode ─────────────────────────────────────────── */
function applyMode(light) {
  document.body.classList.toggle("light", light);
  modeCheckbox.checked = light;
  localStorage.setItem("homology-light", light ? "1" : "0");
}

modeCheckbox.addEventListener("change", () => applyMode(modeCheckbox.checked));

// Restore on load
(function restoreMode() {
  const saved = localStorage.getItem("homology-light");
  if (saved === "1") applyMode(true);
})();

/* ── Helpers ───────────────────────────────────────────────────── */
function isoToDate(str) {
  const [y, m, d] = str.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function dateToIso(d) {
  const y  = d.getFullYear();
  const mo = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${y}-${mo}-${dd}`;
}

function addDays(isoStr, n) {
  const d = isoToDate(isoStr);
  d.setDate(d.getDate() + n);
  return dateToIso(d);
}

function formatDate(isoStr) {
  const d = isoToDate(isoStr);
  return d.toLocaleDateString("en-US", {
    weekday: "long", year: "numeric", month: "long", day: "numeric"
  });
}

function escHtml(s) {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

async function typeset(el) {
  if (window.MathJax && MathJax.typesetPromise) {
    await MathJax.typesetPromise([el]);
  }
}

/* ── Answer checking ───────────────────────────────────────────── */
const MAX_ATTEMPTS = 3;

// Normalise a problem payload into the {euler, expr_value, expr_latex, infinite}
// shape the checker expects.
function targetOf(problem) {
  if (!problem) return {};
  if (problem.functional) {
    return {
      euler: problem.euler,
      expr_value: problem.functional.value,
      expr_latex: problem.functional.latex,
      infinite: problem.infinite,
    };
  }
  return problem.target || {};
}

function updateAttempts() {
  if (answered) { attemptsLeftEl.textContent = ""; return; }
  const n = attemptsLeft;
  attemptsLeftEl.textContent = `${n} attempt${n === 1 ? "" : "s"} left`;
  attemptsLeftEl.classList.toggle("low", n <= 1);
}

function lockInputs() {
  inputEuler.disabled = true;
  inputExpr.disabled  = true;
  btnCheck.disabled   = true;
}

function checkAnswer(target) {
  if (answered || attemptsLeft <= 0) return;

  const needEuler = !target.infinite;

  // Parse the functional value (always required).
  const exprRaw = inputExpr.value.trim();
  const exprVal = parseInt(exprRaw, 10);

  // Parse the Euler characteristic (only for finite-dimensional spaces).
  const eulerRaw = inputEuler.value.trim();
  const eulerVal = parseInt(eulerRaw, 10);

  if (exprRaw === "" || isNaN(exprVal) || (needEuler && (eulerRaw === "" || isNaN(eulerVal)))) {
    setFeedback("Please enter an integer in each field.", "wrong");
    if (needEuler && (eulerRaw === "" || isNaN(eulerVal))) shakeInput(inputEuler);
    if (exprRaw === "" || isNaN(exprVal)) shakeInput(inputExpr);
    return;
  }

  const eulerOk = !needEuler || eulerVal === target.euler;
  const exprOk  = exprVal === target.expr_value;

  if (eulerOk && exprOk) {
    answered = true;
    markField(inputEuler, needEuler ? true : null);
    markField(inputExpr, true);
    lockInputs();
    updateAttempts();
    setFeedback("✓ Correct! Here is the homology class.", "correct");
    revealSolution();
    return;
  }

  // Wrong — consume one attempt.
  attemptsLeft--;
  if (needEuler) markField(inputEuler, eulerOk ? true : false);
  markField(inputExpr, exprOk ? true : false);

  if (attemptsLeft <= 0) {
    answered = true;
    lockInputs();
    updateAttempts();
    setFeedback("✗ Out of attempts. Come back stronger tomorrow!", "wrong");
    return;
  }

  // Hint at which field is wrong without giving the value away.
  let which;
  if (needEuler && !eulerOk && !exprOk) which = "Both χ(X) and Υ(X) are off";
  else if (needEuler && !eulerOk)       which = "χ(X) is off";
  else                                   which = "Υ(X) is off";
  updateAttempts();
  setFeedback(`✗ ${which}. ${attemptsLeft} attempt${attemptsLeft === 1 ? "" : "s"} left.`, "wrong");
}

/* ── Solution reveal ───────────────────────────────────────────── */
async function revealSolution() {
  const problem = currentProblem();
  if (!problem) return;
  try {
    const res = await fetch(`/api/solution/${problem.id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const { solution } = await res.json();
    solutionAnswer.textContent = solution.answer || "";
    solutionSteps.innerHTML = (solution.steps || [])
      .map(s => `<li>${escHtml(s)}</li>`)
      .join("");
    solutionSec.classList.remove("hidden");
    await typeset(solutionSec);
    solutionSec.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    console.error(err);
  }
}

function markField(input, ok) {
  input.classList.remove("correct", "wrong");
  if (ok === true)  input.classList.add("correct");
  if (ok === false) { shakeInput(input); setTimeout(() => input.classList.remove("wrong"), 400); }
}

function setFeedback(msg, cls) {
  feedback.textContent = msg;
  feedback.className = "answer-feedback " + (cls || "");
}

function shakeInput(input) {
  input.classList.remove("wrong");
  void input.offsetWidth; // reflow to restart animation
  input.classList.add("wrong");
}

/* ── Render problem ────────────────────────────────────────────── */
function renderLocked(data) {
  liveContent.style.display = "none";
  lockedCard.classList.remove("hidden");
  if (data.before_start) {
    lockedText.textContent =
      `The Daily (Co)homology Class begins on ${formatDate(EPOCH_STR)}.`;
  } else {
    lockedText.textContent =
      `Day ${data.day_number + 1} unlocks on ${formatDate(data.date)}. ` +
      `Come back then for a fresh space to dissect.`;
  }
}

function renderProblem(data) {
  // Locked / preview day: hide the live problem and show the teaser.
  if (data.locked || !data.problem) {
    renderLocked(data);
    return;
  }
  liveContent.style.display = "";
  lockedCard.classList.add("hidden");

  const { problem, day_number } = data;
  const target = targetOf(problem);

  // Hide any previously revealed solution.
  solutionSec.classList.add("hidden");
  solutionAnswer.textContent = "";
  solutionSteps.innerHTML = "";

  // Reset state
  answered     = false;
  attemptsLeft = problem.max_attempts || MAX_ATTEMPTS;
  inputEuler.value = "";
  inputExpr.value  = "";
  inputEuler.disabled = false;
  inputExpr.disabled  = false;
  inputEuler.className = "answer-input";
  inputExpr.className  = "answer-input";
  btnCheck.disabled = false;
  setFeedback("", "");

  // The Euler-characteristic field only applies to finite-dimensional spaces.
  fieldEuler.style.display = target.infinite ? "none" : "";
  updateAttempts();

  // Meta
  badgeDiff.textContent = problem.difficulty;
  badgeDiff.className   = `badge badge-${problem.difficulty}`;
  badgeType.textContent = problem.type;
  dayCounter.textContent = `Day ${day_number + 1} · Problem #${problem.id}`;

  // Title
  titleEl.textContent = "";
  // MathJax will typeset $ in innerHTML — use textContent would escape it, so use innerHTML safely
  titleEl.innerHTML = problem.title
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Statement
  statementEl.textContent = problem.statement;

  // Tags
  tagsRowEl.innerHTML = problem.tags
    .map(t => `<span class="tag">${escHtml(t)}</span>`)
    .join("");

  // Answer question — restate the functional next to the input boxes.
  if (target.infinite) {
    answerQuestion.textContent =
      `Enter the value of the Betti-number functional  $\\Upsilon(X) = ${target.expr_latex}$.`;
  } else {
    answerQuestion.textContent =
      `Enter the Euler characteristic  $\\chi(X)$  and the value of  $\\Upsilon(X) = ${target.expr_latex}$.`;
  }

  // Typeset everything
  typeset(card);
}

/* ── Load problem for date ─────────────────────────────────────── */
async function loadDate(iso) {
  card.classList.add("loading");
  try {
    const res = await fetch(`/api/problem/date/${iso}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data      = await res.json();
    _currentProblem = data.problem;
    currentDate     = iso;
    currentDay      = data.day_number;
    dateDisplay.textContent = formatDate(iso);
    renderProblem(data);
  } catch (err) {
    console.error(err);
  } finally {
    card.classList.remove("loading");
  }
}

/* ── Events ────────────────────────────────────────────────────── */
// Check answer on button click or Enter key
btnCheck.addEventListener("click", () => {
  const problem = currentProblem();
  if (problem) checkAnswer(targetOf(problem));
});

[inputEuler, inputExpr].forEach(el => {
  el.addEventListener("keydown", e => {
    if (e.key === "Enter") btnCheck.click();
  });
});

// We keep a reference to the current rendered problem
let _currentProblem = null;
function currentProblem() { return _currentProblem; }

/* ── Archive ───────────────────────────────────────────────────── */
btnArchive.addEventListener("click", async () => {
  archiveOverlay.classList.remove("hidden");
  if (archiveCache) return;
  try {
    const res  = await fetch("/api/problems");
    const data = await res.json();
    archiveCache = data.problems;
    renderArchive(archiveCache);
  } catch {
    archiveList.innerHTML = "<p class='loading-text'>Failed to load archive.</p>";
  }
});

btnCloseArc.addEventListener("click", () => archiveOverlay.classList.add("hidden"));
archiveOverlay.addEventListener("click", e => {
  if (e.target === archiveOverlay) archiveOverlay.classList.add("hidden");
});

function renderArchive(entries) {
  archiveList.innerHTML = entries.map(e => {
    const dayLabel = `Day ${e.day_number + 1}`;
    if (e.released) {
      const cls = `archive-item-badge badge-${e.difficulty}`;
      return `<div class="archive-item" data-date="${e.date}">
        <span class="archive-item-num">${dayLabel}</span>
        <span class="archive-item-title">${escHtml(e.title)}</span>
        <span class="${cls}">${e.difficulty}</span>
      </div>`;
    }
    return `<div class="archive-item archive-item-locked">
      <span class="archive-item-num">${dayLabel}</span>
      <span class="archive-item-title archive-item-locked-title">🔒 Unlocks ${formatShort(e.date)}</span>
    </div>`;
  }).join("");

  archiveList.querySelectorAll(".archive-item[data-date]").forEach(el => {
    el.addEventListener("click", async () => {
      archiveOverlay.classList.add("hidden");
      await loadDate(el.dataset.date);
    });
  });
}

function formatShort(isoStr) {
  return isoToDate(isoStr).toLocaleDateString("en-US",
    { month: "short", day: "numeric", year: "numeric" });
}

btnPrev.onclick  = () => loadDate(addDays(currentDate, -1));
btnNext.onclick  = () => loadDate(addDays(currentDate, 1));
btnToday.onclick = () => { if (currentDate !== TODAY_STR) loadDate(TODAY_STR); };

/* ── Init ──────────────────────────────────────────────────────── */
(function init() {
  dateDisplay.textContent = formatDate(TODAY_STR);
  _currentProblem         = INITIAL_PROBLEM;
  renderProblem({ problem: INITIAL_PROBLEM, day_number: DAY_NUMBER });
})();
