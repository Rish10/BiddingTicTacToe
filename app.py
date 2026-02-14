import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Bidding War", layout="centered")

# --- GAME LOGIC ---
def check_winner(board):
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a]
    return "Draw" if None not in board else None

def minimax(board, depth, is_maxing):
    res = check_winner(board)
    if res == 'O': return 10 - depth
    if res == 'X': return depth - 10
    if res == "Draw": return 0
    scores = []
    for i in range(9):
        if board[i] is None:
            board[i] = 'O' if is_maxing else 'X'
            scores.append(minimax(board, depth + 1, not is_maxing))
            board[i] = None
    return max(scores) if is_maxing else min(scores)

def get_best_move(board):
    best_val, move = -1000, -1
    for i in range(9):
        if board[i] is None:
            board[i] = 'O'
            val = minimax(board, 0, False)
            board[i] = None
            if val > best_val:
                best_val, move = val, i
    return move

def calculate_ai_bid(board, ai_cash, player_cash):
    empty = board.count(None)
    if empty > 6:
        return random.randint(max(1, int(ai_cash * 0.01)), max(2, int(ai_cash * 0.25)))
    return random.randint(int(ai_cash * 0.1), int(ai_cash * 0.5))

# --- SESSION STATE ---
if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None
    st.session_state.pending_move = None
    st.session_state.flash = None

# --- HANDLE INCOMING ACTION FROM COMPONENT ---
params = st.query_params
if "sq" in params and st.session_state.pending_move is None and st.session_state.winner is None:
    sq = int(params["sq"])
    if st.session_state.board[sq] is None:
        st.session_state.pending_move = sq
    st.query_params.clear()
    st.rerun()

if "bid" in params and "sq_confirm" in params and st.session_state.winner is None:
    sq = int(params["sq_confirm"])
    bid = int(params["bid"])
    board = st.session_state.board
    ai_bid = calculate_ai_bid(board, st.session_state.cash['AI'], st.session_state.cash['Player'])
    st.session_state.cash['Player'] -= bid
    st.session_state.cash['AI'] -= ai_bid
    if bid >= ai_bid:
        st.session_state.board[sq] = 'X'
        st.session_state.flash = (f"You won the bid! AI bid ${ai_bid} 🎉", "success")
    else:
        best_sq = get_best_move(st.session_state.board)
        st.session_state.board[best_sq] = 'O'
        st.session_state.flash = (f"AI won (${ai_bid}) → took Square {best_sq+1} 😤", "error")
    st.session_state.winner = check_winner(st.session_state.board)
    st.session_state.pending_move = None
    st.query_params.clear()
    st.rerun()

if "cancel" in params:
    st.session_state.pending_move = None
    st.query_params.clear()
    st.rerun()

if "reset" in params:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

# --- BUILD THE FULL HTML UI ---
board = st.session_state.board
pending = st.session_state.pending_move
winner = st.session_state.winner
p_cash = st.session_state.cash['Player']
ai_cash = st.session_state.cash['AI']
flash = st.session_state.flash

# Build cell HTML
cells = ""
for i in range(9):
    mark = board[i]
    if mark == 'X':
        cells += f'<div class="cell taken x">X</div>'
    elif mark == 'O':
        cells += f'<div class="cell taken o">O</div>'
    elif winner is not None or pending is not None:
        cells += f'<div class="cell locked">{i+1}</div>'
    else:
        cells += f'<div class="cell empty" onclick="selectSquare({i})">{i+1}</div>'

# Flash message
flash_html = ""
if flash:
    msg, kind = flash
    color = "#1e7e34" if kind == "success" else "#c0392b"
    bg = "#d4edda" if kind == "success" else "#f8d7da"
    flash_html = f'<div style="background:{bg};color:{color};padding:10px 14px;border-radius:8px;margin-bottom:12px;font-weight:600;">{msg}</div>'
    st.session_state.flash = None

# Bidding section
bidding_html = ""
if pending is not None and winner is None:
    bidding_html = f"""
    <div class="bidding-box">
        <div class="bid-title">🎯 Square {pending+1} selected — place your bid</div>
        <input type="number" id="bidInput" min="0" max="{p_cash}" value="0" step="10" />
        <div class="bid-buttons">
            <button class="btn-primary" onclick="submitBid()">✅ Submit Bid</button>
            <button class="btn-cancel" onclick="cancelBid()">❌ Cancel</button>
        </div>
    </div>
    """

# Winner section
winner_html = ""
if winner:
    if winner == "Draw":
        msg, emoji = "It's a Draw!", "🤝"
        color = "#856404"
        bg = "#fff3cd"
    elif winner == "X":
        msg, emoji = "You Win!", "🎉"
        color = "#155724"
        bg = "#d4edda"
    else:
        msg, emoji = "AI Wins!", "🤖"
        color = "#721c24"
        bg = "#f8d7da"
    winner_html = f"""
    <div style="background:{bg};color:{color};padding:16px;border-radius:10px;text-align:center;margin-top:12px;">
        <div style="font-size:2rem;">{emoji}</div>
        <div style="font-size:1.4rem;font-weight:bold;">{msg}</div>
        <button class="btn-primary" style="margin-top:12px;" onclick="resetGame()">🔄 Play Again</button>
    </div>
    """

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: transparent;
    padding: 8px;
  }}
  h1 {{
    font-size: 1.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 10px;
  }}
  .info-box {{
    background: #e8f4fd;
    border: 1px solid #bee3f8;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.85rem;
    margin-bottom: 12px;
    color: #2c5282;
  }}
  .metrics {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 14px;
  }}
  .metric {{
    background: #f7f7f7;
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
    border: 1px solid #e0e0e0;
  }}
  .metric-label {{ font-size: 0.75rem; color: #666; }}
  .metric-value {{ font-size: 1.3rem; font-weight: bold; color: #222; }}

  /* THE BOARD — hardcoded 3 columns, no flexbox, no Streamlit interference */
  .board {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    width: 100%;
    max-width: 320px;
    margin: 0 auto 16px auto;
    border: 3px solid #333;
    border-radius: 8px;
    overflow: hidden;
  }}
  .cell {{
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: bold;
    border: 1.5px solid #bbb;
    min-height: 80px;
    transition: background 0.15s;
  }}
  .cell.empty {{
    cursor: pointer;
    background: #fff;
    color: #999;
    font-size: 1rem;
  }}
  .cell.empty:hover {{ background: #e8f4fd; color: #1a73e8; }}
  .cell.empty:active {{ background: #c9e3fa; }}
  .cell.locked {{ background: #f0f0f0; color: #ccc; font-size: 1rem; cursor: not-allowed; }}
  .cell.taken {{ background: #f9f9f9; cursor: default; }}
  .cell.x {{ color: #1a73e8; }}
  .cell.o {{ color: #e53935; }}

  .bidding-box {{
    background: #f0f7ff;
    border: 2px solid #1a73e8;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
  }}
  .bid-title {{
    font-weight: 700;
    margin-bottom: 10px;
    font-size: 1rem;
  }}
  input[type=number] {{
    width: 100%;
    padding: 10px;
    font-size: 1.2rem;
    border: 2px solid #1a73e8;
    border-radius: 8px;
    margin-bottom: 10px;
    text-align: center;
  }}
  .bid-buttons {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }}
  .btn-primary {{
    background: #1a73e8;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    width: 100%;
  }}
  .btn-primary:active {{ background: #1558b0; }}
  .btn-cancel {{
    background: #f1f3f4;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
  }}
</style>
</head>
<body>

<h1>💰 Bidding Tic-Tac-Toe</h1>

<div class="info-box">
  👉 <strong>Step 1:</strong> Tap a numbered square &nbsp;|&nbsp; 👉 <strong>Step 2:</strong> Enter your bid
</div>

{flash_html}

<div class="metrics">
  <div class="metric">
    <div class="metric-label">Your Cash 🟦</div>
    <div class="metric-value">${p_cash}</div>
  </div>
  <div class="metric">
    <div class="metric-label">AI Cash 🟥</div>
    <div class="metric-value">${ai_cash}</div>
  </div>
</div>

<div class="board">
  {cells}
</div>

{bidding_html}
{winner_html}

<script>
  function go(params) {{
    const url = new URL(window.parent.location.href);
    Object.keys(params).forEach(k => url.searchParams.set(k, params[k]));
    window.parent.location.href = url.toString();
  }}

  function selectSquare(idx) {{
    go({{ sq: idx }});
  }}

  function submitBid() {{
    const bid = parseInt(document.getElementById('bidInput').value) || 0;
    go({{ sq_confirm: {pending if pending is not None else 0}, bid: bid }});
  }}

  function cancelBid() {{
    go({{ cancel: 1 }});
  }}

  function resetGame() {{
    go({{ reset: 1 }});
  }}
</script>
</body>
</html>
"""

components.html(html, height=750, scrolling=False)
