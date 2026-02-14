import streamlit as st
import random

# --- 1. MOBILE GRID FIX (CSS) ---
st.markdown("""
    <style>
    [data-testid="column"] {
        width: 31% !important;
        flex: 1 1 31% !important;
        min-width: 31% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex;
        flex-wrap: nowrap !important;
        gap: 0.5rem;
    }
    button {
        height: 80px !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---
def check_winner(board):
    lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a]
    if None not in board: return "Draw"
    return None

def calculate_smart_bid(board, ai_cash, player_cash, target_move):
    empty_squares = board.count(None)
    
    # Check for immediate win/loss (Best Case)
    temp_board_ai = list(board)
    temp_board_ai[target_move] = 'O'
    temp_board_player = list(board)
    temp_board_player[target_move] = 'X'
    
    is_critical = check_winner(temp_board_ai) == 'O' or check_winner(temp_board_player) == 'X'

    if is_critical:
        # If it's the winning move, AI is willing to spend more
        return min(ai_cash, player_cash + 1 if ai_cash > player_cash else ai_cash)

    # 1% - 25% Rule for Early Game
    if empty_squares > 6:
        return random.randint(max(1, int(ai_cash * 0.01)), max(2, int(ai_cash * 0.25)))
    
    # Mid/Late Game Strategy
    return random.randint(int(ai_cash * 0.15), int(ai_cash * 0.45))

# --- 3. UI SETUP ---
st.title("💰 Bidding Tic-Tac-Toe")

st.info("""
👉 **Step 1:** Tap an empty square.  
👉 **Step 2:** Enter your bid below.  
**Both players lose their bid every turn!**
""")

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

# Stats
c1, c2 = st.columns(2)
c1.metric("Your Cash", f"${st.session_state.cash['Player']}")
c2.metric("AI Cash", f"${st.session_state.cash['AI']}")

# --- 4. THE GRID ---
# We use a single row container to help with mobile spacing
grid_container = st.container()
with grid_container:
    col_a, col_b, col_c = st.columns(3)
    cols = [col_a, col_b, col_c]
    for i in range(9):
        with cols[i % 3]:
            mark = st.session_state.board[i]
            lbl = mark if mark else " "
            # Highlight selected square with a different label or style
            is_selected = 'pending_move' in st.session_state and st.session_state.pending_move == i
            button_text = f"[{lbl}]" if is_selected else lbl
            
            if st.button(button_text, key=f"btn{i}", use_container_width=True, 
                         disabled=mark is not None or st.session_state.winner is not None):
                st.session_state.pending_move = i
                st.rerun()

# --- 5. BIDDING ---
if 'pending_move' in st.session_state and st.session_state.winner is None:
    st.markdown(f"### 🎯 Bidding on Square {st.session_state.pending_move + 1}")
    player_bid = st.number_input("How much will you bid?", 0, st.session_state.cash['Player'], step=10)
    
    if st.button("Confirm Bid & Play", type="primary", use_container_width=True):
        target = st.session_state.pending_move
        ai_bid = calculate_smart_bid(st.session_state.board, st.session_state.cash['AI'], st.session_state.cash['Player'], target)
        
        # Money is gone for both!
        st.session_state.cash['Player'] -= player_bid
        st.session_state.cash['AI'] -= ai_bid
        
        if player_bid >= ai_bid:
            st.session_state.board[target] = 'X'
            st.success(f"You won! AI bid ${ai_bid}")
        else:
            st.session_state.board[target] = 'O'
            st.error(f"AI won the bid with ${ai_bid}!")

        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

if st.session_state.winner:
    st.divider()
    if st.session_state.winner == "Draw": st.warning("It's a Draw!")
    else: st.success(f"🏆 Winner: {st.session_state.winner}!")
    if st.button("New Game", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
