import streamlit as st
import random

# --- MINIMAX LOGIC ---
def check_winner(board):
    lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a]
    if None not in board: return "Draw"
    return None

def minimax(board, depth, is_maxing):
    res = check_winner(board)
    if res == 'O': return 10 - depth
    if res == 'X': return depth - 10
    if res == "Draw": return 0

    if is_maxing:
        best = -1000
        for i in range(9):
            if board[i] is None:
                board[i] = 'O'
                best = max(best, minimax(board, depth + 1, False))
                board[i] = None
        return best
    else:
        best = 1000
        for i in range(9):
            if board[i] is None:
                board[i] = 'X'
                best = min(best, minimax(board, depth + 1, True))
                board[i] = None
        return best

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

# --- NEW SMART BIDDING LOGIC ---
def calculate_smart_bid(board, ai_cash, player_cash, target_move):
    empty_squares = board.count(None)
    
    # 1. CHECK FOR IMMEDIATE WIN/LOSS (Best Case Logic)
    # If AI can win or MUST block player from winning this turn
    temp_board_ai = list(board)
    temp_board_ai[target_move] = 'O'
    
    temp_board_player = list(board)
    temp_board_player[target_move] = 'X'
    
    is_critical = check_winner(temp_board_ai) == 'O' or check_winner(temp_board_player) == 'X'

    if is_critical and empty_squares <= 6:
        # Go aggressive if it's a game-deciding move
        return min(ai_cash, player_cash + 1)

    # 2. EARLY GAME (1% - 25% Rule)
    if empty_squares > 6:
        low_bound = max(1, int(ai_cash * 0.01))
        high_bound = max(2, int(ai_cash * 0.25))
        return random.randint(low_bound, high_bound)
    
    # 3. MID/LATE GAME (Standard Strategic)
    return random.randint(int(ai_cash * 0.2), int(ai_cash * 0.5))

# --- UI SETUP ---
st.set_page_config(page_title="Strategic Bidding AI", page_icon="💰")
st.title("💰 Bidding Tic-Tac-Toe: Pro Edition")

st.info("""
👉 **Step 1:** Select an empty square.  
👉 **Step 2:** Enter your bid.  
👉 **Rule:** Both players lose their bid amount every turn!
""")

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

c1, c2 = st.columns(2)
c1.metric("Your Cash", f"${st.session_state.cash['Player']}")
c2.metric("AI Cash", f"${st.session_state.cash['AI']}")

grid = st.columns(3)
for i in range(9):
    with grid[i % 3]:
        mark = st.session_state.board[i]
        lbl = mark if mark else " "
        if st.button(lbl, key=f"btn{i}", use_container_width=True, 
                     disabled=mark is not None or st.session_state.winner is not None):
            st.session_state.pending_move = i
            st.rerun()

if 'pending_move' in st.session_state and st.session_state.winner is None:
    st.write(f"### Bidding on Square {st.session_state.pending_move + 1}")
    player_bid = st.number_input("Enter your bid:", 0, st.session_state.cash['Player'], step=10)
    
    if st.button("Submit Bid"):
        target = st.session_state.pending_move
        ai_bid = calculate_smart_bid(st.session_state.board, st.session_state.cash['AI'], st.session_state.cash['Player'], target)
        
        # Deduction logic
        st.session_state.cash['Player'] -= player_bid
        st.session_state.cash['AI'] -= ai_bid
        
        if player_bid >= ai_bid:
            st.session_state.board[target] = 'X'
            st.success(f"You won! You bid ${player_bid}, AI bid ${ai_bid}")
        else:
            # AI wins bid, but it uses Minimax to pick the actual BEST square
            best_sq = get_best_move(st.session_state.board)
            st.session_state.board[best_sq] = 'O'
            st.error(f"AI outbid you! AI bid ${ai_bid}. It took square {best_sq+1}")

        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

if st.session_state.winner:
    if st.session_state.winner == "Draw": st.info("It's a Draw!")
    else: st.success(f"Winner: {st.session_state.winner}!")
    if st.button("Restart Game"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
