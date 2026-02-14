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

  // 3. Normal Play: Apply your 1%-25% Early Game Rule
  if (emptySquares > 6) {
    const minBid = Math.max(1, Math.floor(aiCash * 0.05));
    const maxBid = Math.floor(aiCash * 0.25);
    return Math.floor(Math.random() * (maxBid - minBid + 1)) + minBid;
  }

  // 4. Mid/Late Game: Strategic aggressive bidding
  // AI bids more if it has more cash than the player
  let multiplier = aiCash > playerCash ? 0.4 : 0.3;
  return Math.floor(Math.random() * (aiCash * multiplier)) + Math.floor(aiCash * 0.1);
}
