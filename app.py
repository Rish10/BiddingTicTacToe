import streamlit as st
import random

# --- 1. THE ULTIMATE MOBILE GRID FIX ---
st.set_page_config(page_title="Bidding War", layout="centered")

# This CSS forces the columns to stay at 30% width and prevents stacking
st.markdown("""
    <style>
    /* Force columns to stay side-by-side */
    [data-testid="column"] {
        width: 31% !important;
        flex: 1 1 31% !important;
        min-width: 31% !important;
    }
    /* Make the horizontal block not wrap */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
    }
    /* Square buttons that fit mobile screens */
    .stButton > button {
        width: 100% !important;
        height: 20vw !important; /* Based on screen width */
        max-height: 90px !important;
        font-size: 24px !important;
        margin-bottom: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GAME LOGIC ---
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

# --- 3. UI & RESTORED INSTRUCTIONS ---
st.title("💰 Bidding Tic-Tac-Toe")

# RESTORED INSTRUCTIONS
st.info("""
👉 **Step 1:** Select an empty square below. \n
👉 **Step 2:** Enter your bid at the bottom.
""")

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

# Balances
c1, c2 = st.columns(2)
c1.metric("Your Cash", f"${st.session_state.cash['Player']}")
c2.metric("AI Cash", f"${st.session_state.cash['AI']}")

# --- 4. THE GRID ---
# Using a loop to create 3 distinct row containers for stability
for r in range(3):
    cols = st.columns(3)
    for c in range(3):
        idx = r * 3 + c
        mark = st.session_state.board[idx]
        if cols[c].button(mark if mark else " ", key=f"s{idx}", disabled=mark is not None or st.session_state.winner is not None):
            st.session_state.pending_move = idx
            st.rerun()

# --- 5. BIDDING ---
if 'pending_move' in st.session_state and st.session_state.winner is None:
    st.write(f"### Bidding on Square {st.session_state.pending_move + 1}")
    bid = st.number_input("Enter your bid:", 0, st.session_state.cash['Player'], step=10)
    
    if st.button("Submit Bid", type="primary", use_container_width=True):
        ai_bid = calculate_ai_bid(st.session_state.board, st.session_state.cash['AI'], st.session_state.cash['Player'])
        
        # Money is gone for both!
        st.session_state.cash['Player'] -= bid
        st.session_state.cash['AI'] -= ai_bid
        
        if bid >= ai_bid:
            st.session_state.board[st.session_state.pending_move] = 'X'
            st.success(f"You won! AI bid ${ai_bid}")
        else:
            # AI wins and picks ITS best move using Minimax
            best_sq = get_best_move(st.session_state.board)
            st.session_state.board[best_sq] = 'O'
            st.error(f"AI won the bid (${ai_bid}) and took Square {best_sq+1}!")
            
        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

if st.session_state.winner:
    st.divider()
    if st.session_state.winner == "Draw": st.warning("It's a Draw!")
    else: st.success(f"Winner: {st.session_state.winner}!")
    if st.button("Reset Game", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
