/* ── State ─────────────────────────────────────────────────────── */
let currentDate    = TODAY_STR;
let currentDay     = DAY_NUMBER;
let hintsRevealed  = 0;
let solutionLocked = true;
let archiveCache   = null;
let _currentHints  = [];
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
const hintsContainer = document.getElementById("hints-container");
const hintCounterEl  = document.getElementById("hint-counter");
const btnHint        = document.getElementById("btn-hint");
const answerQuestion = document.getElementById("answer-question");
const fieldEuler     = document.getElementById("field-euler");
const inputEuler     = document.getElementById("input-euler");
const inputExpr      = document.getElementById("input-expr");
const attemptsLeftEl = document.getElementById("attempts-left");
const btnCheck       = document.getElementById("btn-check");
const feedback       = document.getElementById("answer-feedback");
const btnGiveup      = document.getElementById("btn-giveup");
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
  btnGiveup.style.display = "none";
}

function checkAnswer(target) {
  if (answered || attemptsLeft <= 0) return;

  const needEuler = !target.infinite;

  // Parse the expression value (always required).
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
    setFeedback("✓ Correct! The solution is now unlocked.", "correct");
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
    setFeedback("✗ Out of attempts — here is the worked solution.", "wrong");
    revealSolution();
    return;
  }

  // Hint at which field is wrong without giving the value away.
  let which;
  if (needEuler && !eulerOk && !exprOk) which = "Both χ(X) and F(X) are off";
  else if (needEuler && !eulerOk)       which = "χ(X) is off";
  else                                   which = "F(X) is off";
  updateAttempts();
  setFeedback(`✗ ${which}. ${attemptsLeft} attempt${attemptsLeft === 1 ? "" : "s"} left.`, "wrong");
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

function revealSolution() {
  solutionLocked = false;
  solutionSec.classList.remove("hidden");
  typeset(solutionSec);
  solutionSec.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/* ── Render problem ────────────────────────────────────────────── */
function renderProblem(data) {
  const { problem, day_number } = data;
  const target = problem.target || {};

  // Reset state
  hintsRevealed  = 0;
  solutionLocked = true;
  answered       = false;
  attemptsLeft   = problem.max_attempts || MAX_ATTEMPTS;
  solutionSec.classList.add("hidden");
  hintsContainer.innerHTML = "";
  inputEuler.value = "";
  inputExpr.value  = "";
  inputEuler.disabled = false;
  inputExpr.disabled  = false;
  inputEuler.className = "answer-input";
  inputExpr.className  = "answer-input";
  btnCheck.disabled = false;
  btnGiveup.style.display = "";
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

  // Hints
  _currentHints = problem.hints || [];
  updateHintCounter(_currentHints.length);
  btnHint.disabled    = _currentHints.length === 0;
  btnHint.textContent = "Reveal Next Hint";

  // Answer question — restate the functional next to the input boxes.
  if (target.infinite) {
    answerQuestion.textContent =
      `Enter the value of the Betti-number functional  $F(X) = ${target.expr_latex}$.`;
  } else {
    answerQuestion.textContent =
      `Enter the Euler characteristic  $\\chi(X)$  and the value of  $F(X) = ${target.expr_latex}$.`;
  }

  // Solution (pre-populate but keep hidden)
  solutionAnswer.textContent = problem.solution.answer;
  solutionSteps.innerHTML = (problem.solution.steps || [])
    .map(s => `<li>${escHtml(s)}</li>`)
    .join("");

  // Typeset everything
  typeset(card);
}

function updateHintCounter(total) {
  hintCounterEl.textContent = `${hintsRevealed} / ${total} revealed`;
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
btnHint.addEventListener("click", () => {
  if (hintsRevealed >= _currentHints.length) return;
  const hint = _currentHints[hintsRevealed];
  const div  = document.createElement("div");
  div.className = "hint-item";
  // Wrap hint number + text; escHtml to prevent XSS but let MathJax parse $
  div.innerHTML = `<span class="hint-number">${hintsRevealed + 1}</span>${escHtml(hint)}`;
  hintsContainer.appendChild(div);
  typeset(div);
  hintsRevealed++;
  updateHintCounter(_currentHints.length);
  if (hintsRevealed >= _currentHints.length) {
    btnHint.disabled    = true;
    btnHint.textContent = "All hints revealed";
  }
});

// Check answer on button click or Enter key
btnCheck.addEventListener("click", () => {
  const problem = currentProblem();
  if (problem) checkAnswer(problem.target);
});

[inputEuler, inputExpr].forEach(el => {
  el.addEventListener("keydown", e => {
    if (e.key === "Enter") btnCheck.click();
  });
});

btnGiveup.addEventListener("click", () => {
  answered = true;
  lockInputs();
  updateAttempts();
  setFeedback("Solution revealed. Come back stronger tomorrow!", "wrong");
  revealSolution();
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

function renderArchive(problems) {
  archiveList.innerHTML = problems.map(p => {
    const cls = `archive-item-badge badge-${p.difficulty}`;
    return `<div class="archive-item" data-id="${p.id}">
      <span class="archive-item-num">#${p.id}</span>
      <span class="archive-item-title">${escHtml(p.title)}</span>
      <span class="${cls}">${p.difficulty}</span>
    </div>`;
  }).join("");

  archiveList.querySelectorAll(".archive-item").forEach(el => {
    el.addEventListener("click", async () => {
      archiveOverlay.classList.add("hidden");
      const id         = Number(el.dataset.id);
      const targetIdx  = problems.findIndex(p => p.id === id);
      if (targetIdx < 0) return;
      const epoch           = new Date(2025, 0, 1);
      const today           = isoToDate(TODAY_STR);
      const daysSinceEpoch  = Math.round((today - epoch) / 86400000);
      const cycleStart      = daysSinceEpoch - (daysSinceEpoch % TOTAL_PROBLEMS);
      const targetDays      = cycleStart + targetIdx;
      const targetDate      = new Date(epoch);
      targetDate.setDate(targetDate.getDate() + targetDays);
      await loadDate(dateToIso(targetDate));
    });
  });
}

btnPrev.onclick  = () => loadDate(addDays(currentDate, -1));
btnNext.onclick  = () => loadDate(addDays(currentDate, 1));
btnToday.onclick = () => { if (currentDate !== TODAY_STR) loadDate(TODAY_STR); };

/* ── Init ──────────────────────────────────────────────────────── */
(function init() {
  dateDisplay.textContent = formatDate(TODAY_STR);
  _currentProblem         = INITIAL_PROBLEM;
  _currentHints           = INITIAL_PROBLEM.hints || [];
  renderProblem({ problem: INITIAL_PROBLEM, day_number: DAY_NUMBER });
})();
