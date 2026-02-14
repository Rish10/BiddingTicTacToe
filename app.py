import streamlit as st
import random

# --- 1. HORIZONTAL GAP CRUSHER ---
st.set_page_config(page_title="Bidding War", layout="centered")

st.markdown("""
    <style>
    /* Target the container that holds the columns to remove the horizontal gap */
    [data-testid="stHorizontalBlock"] {
        gap: 2px !important; /* This controls the space between Column 1, 2, and 3 */
        flex-wrap: nowrap !important;
    }

    /* Ensure columns take up the full available width with no internal padding */
    [data-testid="column"] {
        padding-left: 0px !important;
        padding-right: 0px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
    }

    /* Button Styling to make them look like a unified grid */
    .stButton > button {
        width: 100% !important;
        height: 28vw !important; 
        max-height: 100px !important;
        font-size: 30px !important;
        font-weight: bold !important;
        border: 1px solid #ddd !important;
        border-radius: 4px !important;
    }

    /* Tighten vertical spacing between rows */
    div.element-container {
        margin-bottom: -10px !important;
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

# --- 3. UI ---
st.title("💰 Bidding Tic-Tac-Toe")

# YOUR ORIGINAL INSTRUCTIONS
st.info("""
👉 **Step 1:** Select an empty square below. \n
👉 **Step 2:** Enter your bid at the bottom.
""")

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

c1, c2 = st.columns(2)
c1.metric("Your Cash", f"${st.session_state.cash['Player']}")
c2.metric("AI Cash", f"${st.session_state.cash['AI']}")

# --- 4. THE COMPACT GRID ---
for r in range(3):
    # Using a single columns call for each row to control 'gap'
    cols = st.columns(3)
    for c in range(3):
        idx = r * 3 + c
        mark = st.session_state.board[idx]
        if cols[c].button(mark if mark else " ", key=f"s{idx}", disabled=mark is not None or st.session_state.winner is not None):
            st.session_state.pending_move = idx
            st.rerun()

# --- 5. BIDDING ---
if 'pending_move' in st.session_state and st.session_state.winner is None:
    st.markdown(f"### 🎯 Bidding on Square {st.session_state.pending_move + 1}")
    bid = st.number_input("Enter your bid:", 0, st.session_state.cash['Player'], step=10)
    
    if st.button("Submit Bid", type="primary", use_container_width=True):
        ai_bid = calculate_ai_bid(st.session_state.board, st.session_state.cash['AI'], st.session_state.cash['Player'])
        st.session_state.cash['Player'] -= bid
        st.session_state.cash['AI'] -= ai_bid
        
        if bid >= ai_bid:
            st.session_state.board[st.session_state.pending_move] = 'X'
            st.success(f"You won! AI bid ${ai_bid}")
        else:
            best_sq = get_best_move(st.session_state.board)
            st.session_state.board[best_sq] = 'O'
            st.error(f"AI won (${ai_bid}) and took Square {best_sq+1}!")
            
        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

if st.session_state.winner:
    st.divider()
    st.success(f"Winner: {st.session_state.winner}!")
    if st.button("Reset Game", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
