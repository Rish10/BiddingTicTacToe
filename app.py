import streamlit as st
import random

# --- 1. MOBILE GRID FIX ---
st.set_page_config(page_title="Bidding War", layout="centered")
st.markdown("""
    <style>
    [data-testid="column"] { width: 32% !important; flex: 1 1 32% !important; min-width: 32% !important; padding: 2px !important; }
    .stButton > button { width: 100%; height: 80px !important; font-size: 24px !important; }
    .instruction-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE AI BRAIN (MINIMAX) ---
def check_winner(board):
    lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
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
    best_val = -1000
    move = -1
    for i in range(9):
        if board[i] is None:
            board[i] = 'O'
            move_val = minimax(board, 0, False)
            board[i] = None
            if move_val > best_val:
                move = i
                best_val = move_val
    return move

def calculate_ai_bid(board, ai_cash, player_cash):
    empty = board.count(None)
    # 1%-25% Rule for Early Game
    if empty > 6:
        return random.randint(max(1, int(ai_cash * 0.01)), max(2, int(ai_cash * 0.25)))
    return random.randint(int(ai_cash * 0.1), int(ai_cash * 0.5))

# --- 3. UI ---
st.title("💰 Strategic Bidding")

st.markdown("""
<div class="instruction-box">
    <strong>INSTRUCTIONS:</strong><br>
    1. Select a square. 2. Enter bid. <br>
    <b>If AI wins the bid, it will choose the best square for ITS victory!</b>
</div>
""", unsafe_allow_html=True)

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

c1, c2 = st.columns(2)
c1.metric("YOUR CASH", f"${st.session_state.cash['Player']}")
c2.metric("AI CASH", f"${st.session_state.cash['AI']}")

# Grid
for r in range(3):
    cols = st.columns(3)
    for c in range(3):
        idx = r * 3 + c
        mark = st.session_state.board[idx]
        if cols[c].button(mark if mark else " ", key=f"s{idx}", disabled=mark is not None or st.session_state.winner is not None):
            st.session_state.pending_move = idx
            st.rerun()

# Bidding
if 'pending_move' in st.session_state and st.session_state.winner is None:
    bid = st.number_input(f"Bid for Square {st.session_state.pending_move+1}:", 0, st.session_state.cash['Player'], step=50)
    
    if st.button("CONFIRM BID", type="primary", use_container_width=True):
        ai_bid = calculate_ai_bid(st.session_state.board, st.session_state.cash['AI'], st.session_state.cash['Player'])
        
        st.session_state.cash['Player'] -= bid
        st.session_state.cash['AI'] -= ai_bid
        
        if bid >= ai_bid:
            st.session_state.board[st.session_state.pending_move] = 'X'
            st.success(f"You won! AI bid ${ai_bid}")
        else:
            # AI WINS: It picks its own best move!
            best_sq = get_best_move(st.session_state.board)
            st.session_state.board[best_sq] = 'O'
            st.error(f"AI won the bid (${ai_bid}) and took Square {best_sq+1}!")
            
        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

if st.session_state.winner:
    st.header(f"Result: {st.session_state.winner}")
    if st.button("Play Again"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
