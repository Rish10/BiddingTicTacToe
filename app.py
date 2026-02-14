import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bidding War", layout="centered")

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

components.html("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f4f6fb;
  min-height: 100vh;
  padding: 16px;
}

h1 {
  font-size: 1.4rem;
  font-weight: 800;
  text-align: center;
  margin-bottom: 10px;
  color: #1a1a2e;
}

.info-box {
  background: #e8f4fd;
  border: 1px solid #bee3f8;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.82rem;
  margin-bottom: 12px;
  color: #2c5282;
  text-align: center;
}

.metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}
.metric {
  background: white;
  border-radius: 10px;
  padding: 10px;
  text-align: center;
  border: 1px solid #e0e0e0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.metric-label { font-size: 0.72rem; color: #888; margin-bottom: 2px; }
.metric-value { font-size: 1.3rem; font-weight: bold; color: #222; }

/* THE BOARD — pure CSS grid, always 3 columns */
.board {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  width: min(90vw, 300px);
  margin: 0 auto 16px auto;
  border: 3px solid #2d3748;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 900;
  border: 1.5px solid #cbd5e0;
  min-height: 80px;
  transition: background 0.12s, transform 0.1s;
  position: relative;
}
.cell.empty {
  cursor: pointer;
  background: white;
  color: #bbb;
  font-size: 0.85rem;
  font-weight: 600;
}
.cell.empty:hover  { background: #ebf8ff; color: #3182ce; }
.cell.empty:active { background: #bee3f8; transform: scale(0.95); }
.cell.locked { background: #f7fafc; color: #ddd; font-size: 0.85rem; cursor: not-allowed; }
.cell.x { background: #ebf8ff; color: #2b6cb0; cursor: default; }
.cell.o { background: #fff5f5; color: #c53030; cursor: default; }

/* FLASH */
.flash {
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  text-align: center;
  animation: fadeIn 0.3s ease;
}
.flash.success { background: #c6f6d5; color: #276749; }
.flash.error   { background: #fed7d7; color: #9b2335; }
.flash.info    { background: #bee3f8; color: #2c5282; }
@keyframes fadeIn { from { opacity:0; transform:translateY(-4px); } to { opacity:1; transform:none; } }

/* BIDDING BOX */
.bidding-box {
  background: white;
  border: 2px solid #3182ce;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: 0 2px 8px rgba(49,130,206,0.15);
  animation: fadeIn 0.25s ease;
}
.bid-title { font-weight: 700; margin-bottom: 4px; font-size: 0.95rem; color: #2d3748; }
.bid-hint  { font-size: 0.75rem; color: #888; margin-bottom: 10px; }

.slider-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
input[type=range] {
  flex: 1;
  -webkit-appearance: none;
  height: 6px;
  border-radius: 3px;
  background: #bee3f8;
  outline: none;
}
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: #3182ce;
  cursor: pointer;
}
.bid-amount {
  font-size: 1.4rem;
  font-weight: 800;
  color: #3182ce;
  min-width: 70px;
  text-align: center;
}

.bid-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

.btn {
  border: none; border-radius: 8px;
  padding: 13px; font-size: 0.95rem;
  font-weight: 700; cursor: pointer; width: 100%;
  transition: transform 0.1s, opacity 0.1s;
}
.btn:active { transform: scale(0.97); opacity: 0.85; }
.btn-primary { background: #3182ce; color: white; }
.btn-cancel  { background: #edf2f7; color: #4a5568; border: 1px solid #e2e8f0; }
.btn-reset   {
  display: block; width: 100%;
  background: #3182ce; color: white;
  border: none; border-radius: 8px;
  padding: 14px; font-size: 1rem;
  font-weight: 700; cursor: pointer;
  margin-top: 12px;
}

/* WINNER */
.winner-box {
  text-align: center;
  padding: 20px 16px;
  border-radius: 12px;
  margin-top: 4px;
  animation: fadeIn 0.4s ease;
}
.winner-emoji { font-size: 2.5rem; }
.winner-text  { font-size: 1.4rem; font-weight: 800; margin: 6px 0 0; }

/* DANGER HIGHLIGHT on board */
.cell.danger { background: #fff5f5 !important; }
.cell.winning { background: #f0fff4 !important; }
</style>
</head>
<body>

<h1>💰 Bidding Tic-Tac-Toe</h1>
<div class="info-box">
  👉 <strong>Tap a square</strong> to select it, then <strong>place your bid</strong>
</div>

<div class="metrics">
  <div class="metric">
    <div class="metric-label">Your Cash 🟦 (X)</div>
    <div class="metric-value" id="playerCash">$1000</div>
  </div>
  <div class="metric">
    <div class="metric-label">AI Cash 🟥 (O)</div>
    <div class="metric-value" id="aiCash">$1000</div>
  </div>
</div>

<div id="flash"></div>
<div class="board" id="board"></div>
<div id="biddingArea"></div>

<script>
// ── STATE ──────────────────────────────────────────────
const state = {
  board: Array(9).fill(null),
  cash: { Player: 1000, AI: 1000 },
  winner: null,
  pending: null,
};

// ── AI LOGIC ───────────────────────────────────────────
function checkWinner(b) {
  const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  for (const [a,bv,c] of lines) {
    if (b[a] && b[a] === b[bv] && b[a] === b[c]) return b[a];
  }
  return b.includes(null) ? null : 'Draw';
}

function minimax(b, depth, isMax) {
  const r = checkWinner(b);
  if (r === 'O') return 10 - depth;
  if (r === 'X') return depth - 10;
  if (r === 'Draw') return 0;
  let best = isMax ? -Infinity : Infinity;
  for (let i = 0; i < 9; i++) {
    if (!b[i]) {
      b[i] = isMax ? 'O' : 'X';
      const score = minimax(b, depth + 1, !isMax);
      b[i] = null;
      best = isMax ? Math.max(best, score) : Math.min(best, score);
    }
  }
  return best;
}

// SMARTER MOVE SELECTION
function getBestMove(b) {
  let best = -Infinity, move = -1;
  for (let i = 0; i < 9; i++) {
    if (!b[i]) {
      b[i] = 'O';
      const score = minimax(b, 0, false);
      b[i] = null;
      if (score > best) {
        best = score;
        move = i;
      }
    }
  }
  return move;
}

// SMARTER BIDDING LOGIC
function aiRandomBid(emptySquares, targetSq) {
  const aiCash = state.cash.AI;
  const playerCash = state.cash.Player;

  // 1. Evaluate square importance
  const tempBoardAI = [...state.board];
  tempBoardAI[targetSq] = 'O';
  const canAIWin = checkWinner(tempBoardAI) === 'O';

  const tempBoardPlayer = [...state.board];
  tempBoardPlayer[targetSq] = 'X';
  const canPlayerWin = checkWinner(tempBoardPlayer) === 'X';

  // 2. High Priority: If someone can win this turn
  if (canAIWin || canPlayerWin) {
    // If AI has more money, bid PlayerCash + 10 to guarantee the win
    if (aiCash > playerCash) return Math.min(aiCash, playerCash + 10);
    // Otherwise, go all in
    return aiCash;
  }

  // 3. Normal Play: Apply 1%-25% Early Game Rule
  if (emptySquares > 6) {
    const minBid = Math.max(1, Math.floor(aiCash * 0.05));
    const maxBid = Math.floor(aiCash * 0.25);
    return Math.floor(Math.random() * (maxBid - minBid + 1)) + minBid;
  }

  // 4. Mid/Late Game: Strategic aggressive bidding
  let multiplier = aiCash > playerCash ? 0.4 : 0.3;
  return Math.floor(Math.random() * (aiCash * multiplier)) + Math.floor(aiCash * 0.1);
}

// ── FLASH ───────────────────────────────────────────────
let flashTimer = null;
function showFlash(msg, kind) {
  const el = document.getElementById('flash');
  el.innerHTML = `<div class="flash ${kind}">${msg}</div>`;
  if (flashTimer) clearTimeout(flashTimer);
  flashTimer = setTimeout(() => { el.innerHTML = ''; }, 3500);
}

// ── SQUARE IMPORTANCE HINTS ─────────────────────────────
function getSquareHint(idx) {
  const tempAI = [...state.board];
  tempAI[idx] = 'O';
  if (checkWinner(tempAI) === 'O') return 'winning'; // AI wins here

  const tempP = [...state.board];
  tempP[idx] = 'X';
  if (checkWinner(tempP) === 'X') return 'danger';  // Player wins here

  return '';
}

// ── RENDER ──────────────────────────────────────────────
function render() {
  document.getElementById('playerCash').textContent = '$' + state.cash.Player;
  document.getElementById('aiCash').textContent     = '$' + state.cash.AI;

  // Board
  const boardEl = document.getElementById('board');
  boardEl.innerHTML = '';
  for (let i = 0; i < 9; i++) {
    const cell = document.createElement('div');
    const mark = state.board[i];
    if (mark === 'X') {
      cell.className = 'cell x'; cell.textContent = 'X';
    } else if (mark === 'O') {
      cell.className = 'cell o'; cell.textContent = 'O';
    } else if (state.winner || state.pending !== null) {
      cell.className = 'cell locked'; cell.textContent = i + 1;
    } else {
      const hint = getSquareHint(i);
      cell.className = 'cell empty' + (hint ? ' ' + hint : '');
      cell.textContent = i + 1;
      cell.onclick = () => selectSquare(i);
    }
    boardEl.appendChild(cell);
  }

  // Bidding / winner area
  const area = document.getElementById('biddingArea');
  if (state.winner) {
    let bg, color, emoji, msg;
    if (state.winner === 'Draw') { bg='#fffff0'; color='#975a16'; emoji='🤝'; msg='Draw!'; }
    else if (state.winner === 'X') { bg='#f0fff4'; color='#276749'; emoji='🎉'; msg='You Win!'; }
    else { bg='#fff5f5'; color='#9b2335'; emoji='🤖'; msg='AI Wins!'; }
    area.innerHTML = `
      <div class="winner-box" style="background:${bg};border:2px solid ${color};">
        <div class="winner-emoji">${emoji}</div>
        <div class="winner-text" style="color:${color};">${msg}</div>
        <button class="btn-reset" onclick="resetGame()">🔄 Play Again</button>
      </div>`;
  } else if (state.pending !== null) {
    const maxBid = state.cash.Player;

    // Show a hint about whether this is a critical square
    const tempAI = [...state.board]; tempAI[state.pending] = 'O';
    const tempP  = [...state.board]; tempP[state.pending]  = 'X';
    const aiWins = checkWinner(tempAI) === 'O';
    const pWins  = checkWinner(tempP)  === 'X';
    let hintText = '';
    if (aiWins)      hintText = '⚠️ AI wins if it gets this square — bid high!';
    else if (pWins)  hintText = '🏆 You win if you get this square — bid high!';
    else             hintText = 'Tip: outbid the AI to claim this square.';

    area.innerHTML = `
      <div class="bidding-box">
        <div class="bid-title">🎯 Square ${state.pending + 1} selected</div>
        <div class="bid-hint">${hintText}</div>
        <div class="slider-row">
          <input type="range" id="bidSlider" min="0" max="${maxBid}" value="0" step="10"
            oninput="document.getElementById('bidDisplay').textContent='$'+this.value">
          <div class="bid-amount" id="bidDisplay">$0</div>
        </div>
        <div class="bid-buttons">
          <button class="btn btn-primary" onclick="submitBid()">✅ Submit</button>
          <button class="btn btn-cancel"  onclick="cancelBid()">❌ Cancel</button>
        </div>
      </div>`;
  } else {
    area.innerHTML = '';
  }
}

// ── ACTIONS ─────────────────────────────────────────────
function selectSquare(i) {
  if (state.board[i] || state.winner || state.pending !== null) return;
  state.pending = i;
  render();
}

function submitBid() {
  const slider = document.getElementById('bidSlider');
  const bid = parseInt(slider ? slider.value : 0) || 0;
  const sq = state.pending;
  const empty = state.board.filter(v => v === null).length;
  const aiBid = Math.min(aiRandomBid(empty, sq), state.cash.AI);

  state.cash.Player = Math.max(0, state.cash.Player - bid);
  state.cash.AI     = Math.max(0, state.cash.AI - aiBid);

  if (bid >= aiBid) {
    state.board[sq] = 'X';
    showFlash(`You won Square ${sq+1}! AI bid $${aiBid} 🎉`, 'success');
  } else {
    const best = getBestMove(state.board);
    state.board[best] = 'O';
    showFlash(`AI won (bid $${aiBid}) → took its best square 😤`, 'error');
  }

  state.pending = null;
  state.winner = checkWinner(state.board);
  render();
}

function cancelBid() {
  state.pending = null;
  render();
}

function resetGame() {
  state.board   = Array(9).fill(null);
  state.cash    = { Player: 1000, AI: 1000 };
  state.winner  = null;
  state.pending = null;
  document.getElementById('flash').innerHTML = '';
  render();
}

// ── INIT ────────────────────────────────────────────────
render();
</script>
</body>
</html>
""", height=720, scrolling=True)
