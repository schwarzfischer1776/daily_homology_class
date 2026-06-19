/* ── State ─────────────────────────────────────────────────────── */
let currentDate    = TODAY_STR;
let currentDay     = DAY_NUMBER;
let hintsRevealed  = 0;
let solutionLocked = true;
let archiveCache   = null;
let _currentHints  = [];

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
const answerInput    = document.getElementById("answer-input");
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
function checkAnswer(target) {
  const raw = answerInput.value.trim();
  if (raw === "") return;

  const entered = parseInt(raw, 10);
  if (isNaN(entered)) {
    setFeedback("Please enter an integer.", "wrong");
    shakeInput();
    return;
  }

  if (entered === target.value) {
    // Correct!
    answerInput.classList.remove("wrong");
    answerInput.classList.add("correct");
    answerInput.disabled = true;
    btnCheck.disabled = true;
    btnGiveup.style.display = "none";
    setFeedback("✓ Correct! The solution is now unlocked.", "correct");
    revealSolution();
  } else {
    answerInput.classList.remove("correct");
    answerInput.classList.add("wrong");
    shakeInput();
    setFeedback("✗ Not quite — try again.", "wrong");
    // Remove wrong class after animation
    setTimeout(() => answerInput.classList.remove("wrong"), 400);
  }
}

function setFeedback(msg, cls) {
  feedback.textContent = msg;
  feedback.className = "answer-feedback " + (cls || "");
}

function shakeInput() {
  answerInput.classList.remove("wrong");
  void answerInput.offsetWidth; // reflow to restart animation
  answerInput.classList.add("wrong");
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
  solutionSec.classList.add("hidden");
  hintsContainer.innerHTML = "";
  answerInput.value = "";
  answerInput.disabled = false;
  answerInput.className = "answer-input";
  btnCheck.disabled = false;
  btnGiveup.style.display = "";
  setFeedback("", "");

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

  // Answer question
  answerQuestion.textContent = target.question || "Compute the requested invariant.";

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

answerInput.addEventListener("keydown", e => {
  if (e.key === "Enter") btnCheck.click();
});

btnGiveup.addEventListener("click", () => {
  answerInput.disabled = true;
  btnCheck.disabled    = true;
  btnGiveup.style.display = "none";
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
