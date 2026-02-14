import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bidding War", layout="centered")

# Hide Streamlit chrome
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# The entire game logic is contained in this HTML/JS component
game_html = """
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
h1 { font-size: 1.4rem; font-weight: 800; text-align: center; margin-bottom: 10px; color: #1a1a2e; }
.info-box {
  background: #e8f4fd; border: 1px solid #bee3f8; border-radius: 8px;
  padding: 8px 12px; font-size: 0.82rem; margin-bottom: 12px; color: #2c5282; text-align: center;
}
.metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.metric {
  background: white; border-radius: 10px; padding: 10px; text-align: center;
  border: 1px solid #e0e0e0; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.metric-label { font-size: 0.72rem; color: #888; margin-bottom: 2px; }
.metric-value { font-size: 1.3rem; font-weight: bold; color: #222; }
.board {
  display: grid; grid-template-columns: 1fr 1fr 1fr;
  width: min(90vw, 300px); margin: 0 auto 16px auto;
  border: 3px solid #2d3748; border-radius: 10px; overflow: hidden;
}
.cell {
  aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
  font-size: 2rem; font-weight: 900; border: 1.5px solid #cbd5e0; min-height: 80px;
}
.cell.empty { cursor: pointer; background: white; color: #bbb; font-size: 0.85rem; }
.cell.x { background: #ebf8ff; color: #2b6cb0; }
.cell.o { background: #fff5f5; color: #c53030; }
.flash { padding: 10px; border-radius: 8px; margin-bottom: 12px; text-align: center; font-size: 0.9rem; }
.flash.success { background: #c6f6d5; color: #276749; }
.flash.error { background: #fed7d7; color: #9b2335; }
.bidding-box {
  background: white; border: 2px solid #3182ce; border-radius: 12px; padding: 16px;
}
.slider-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
input[type=range] { flex: 1; }
.bid-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.btn { border: none; border-radius: 8px; padding: 13px; font-weight: 700; cursor: pointer; }
.btn-primary { background: #3182ce; color: white; }
.btn-cancel { background: #edf2f7; color: #4a5568; }
.winner-box { text-align: center; padding: 20px; border-radius: 12px; }
</style>
</head>
<body>
<h1>💰 Bidding Tic-Tac-Toe</h1>
<div class="info-box">👉 <strong>Tap a square</strong> to select, then <strong>place your bid</strong></div>
<div class="metrics">
  <div class="metric"><div class="metric-label">Your Cash (X)</div><div class="metric-value" id="playerCash">$1000</div></div>
  <div class="metric"><div class="metric-label">AI Cash (O)</div><div class="metric-value" id="aiCash">$1000</div></div>
</div>
<div id="flash"></div>
<div class="board" id="board"></div>
<div id="biddingArea"></div>

<script>
const state = { board: Array(9).fill(null), cash: { Player: 1000, AI: 1000 }, winner: null, pending: null };

function checkWinner(b) {
  const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  for (const [a,bv,c] of lines) { if (b[a] && b[a] === b[bv] && b[a] === b[c]) return b[a]; }
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

function getBestMove(b) {
  let best = -Infinity, move = -1;
  for (let i = 0; i < 9; i++) {
    if (!b[i]) {
      b[i] = 'O';
      const score = minimax(b, 0, false);
      b[i] = null;
      if (score > best) { best = score; move = i; }
    }
  }
  return move;
}

function aiSmartBid(emptySquares, targetSq) {
  const aiCash = state.cash.AI;
  const playerCash = state.cash.Player;
  const tempAI = [...state.board]; tempAI[targetSq] = 'O';
  const tempPlayer = [...state.board]; tempPlayer[targetSq] = 'X';
  const isCritical = checkWinner(tempAI) === 'O' || checkWinner(tempPlayer) === 'X';

  if (isCritical) return aiCash > playerCash ? Math.min(aiCash, playerCash + 10) : aiCash;
  if (emptySquares > 6) return Math.floor(Math.random() * (aiCash * 0.24)) + Math.floor(aiCash * 0.01);
  return Math.floor(Math.random() * (aiCash * 0.35)) + Math.floor(aiCash * 0.1);
}

function render() {
  document.getElementById('playerCash').textContent = '$' + state.cash.Player;
  document.getElementById('aiCash').textContent = '$' + state.cash.AI;
  const boardEl = document.getElementById('board');
  boardEl.innerHTML = '';
  for (let i = 0; i < 9; i++) {
    const cell = document.createElement('div');
    const mark = state.board[i];
    cell.className = 'cell ' + (mark ? mark.toLowerCase() : (state.winner || state.pending !== null ? 'locked' : 'empty'));
    cell.textContent = mark || (i + 1);
    if (!mark && !state.winner && state.pending === null) cell.onclick = () => { state.pending = i; render(); };
    boardEl.appendChild(cell);
  }
  const area = document.getElementById('biddingArea');
  if (state.winner) {
    area.innerHTML = `<div class="winner-box"><h2>${state.winner === 'Draw' ? 'Draw!' : state.winner + ' Wins!'}</h2><button class="btn btn-primary" onclick="location.reload()">Reset</button></div>`;
  } else if (state.pending !== null) {
    area.innerHTML = `<div class="bidding-box"><div class="slider-row"><input type="range" id="bidSlider" min="0" max="${state.cash.Player}" step="10" oninput="document.getElementById('bidVal').textContent=this.value"> $<span id="bidVal">0</span></div><div class="bid-buttons"><button class="btn btn-primary" onclick="submitBid()">Bid</button><button class="btn btn-cancel" onclick="state.pending=null;render()">Cancel</button></div></div>`;
  } else { area.innerHTML = ''; }
}

function submitBid() {
  const bid = parseInt(document.getElementById('bidSlider').value);
  const aiBid = Math.min(aiSmartBid(state.board.filter(v => !v).length, state.pending), state.cash.AI);
  state.cash.Player -= bid; state.cash.AI -= aiBid;
  if (bid >= aiBid) { state.board[state.pending] = 'X'; } 
  else { state.board[getBestMove(state.board)] = 'O'; }
  state.pending = null; state.winner = checkWinner(state.board); render();
}
render();
</script>
</body>
</html>
"""

components.html(game_html, height=750, scrolling=True)
