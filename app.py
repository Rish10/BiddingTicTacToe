import streamlit as st
import random

# --- MINIMAX CORE ---
def check_winner(board):
    lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a]
    if None not in board: return "Draw"
    return None

def minimax(board, is_ai):
    res = check_winner(board)
    if res == 'O': return 10
    if res == 'X': return -10
    if res == "Draw": return 0

    scores = []
    for i in range(9):
        if board[i] is None:
            board[i] = 'O' if is_ai else 'X'
            scores.append(minimax(board, not is_ai))
            board[i] = None
    return max(scores) if is_ai else min(scores)

def get_best_move(board):
    best_score = -float('inf')
    move = None
    for i in range(9):
        if board[i] is None:
            board[i] = 'O'
            score = minimax(board, False)
            board[i] = None
            if score > best_score:
                best_score = score
                move = i
    return move

# --- SMART BIDDING LOGIC ---
def calculate_ai_bid(board, ai_cash, player_cash, target_move):
    # If AI can win right now, go all in!
    temp_board = list(board)
    temp_board[target_move] = 'O'
    if check_winner(temp_board) == 'O':
        return ai_cash 

    # Otherwise, bid strategically based on how much the player has
    base_bid = player_cash // 3
    return min(ai_cash, random.randint(base_bid, base_bid + 50))

# --- STREAMLIT UI ---
st.set_page_config(page_title="Expert Bidding AI", page_icon="🤖")
st.title("🤖 Minimax Bidding Tic-Tac-Toe")
st.info("The AI is now using a Minimax algorithm. It knows the best moves—can you outmaneuver its wallet?")

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

col1, col2 = st.columns(2)
col1.metric("Your Wallet", f"${st.session_state.cash['Player']}")
col2.metric("AI Wallet", f"${st.session_state.cash['AI']}")

# Grid Layout
grid = st.columns(3)
for i in range(9):
    with grid[i % 3]:
        mark = st.session_state.board[i]
        lbl = mark if mark else " "
        if st.button(lbl, key=f"s{i}", use_container_width=True, disabled=mark is not None or st.session_state.winner is not None):
            st.session_state.pending_move = i
            st.rerun()

# Bidding Process
if 'pending_move' in st.session_state and st.session_state.winner is None:
    player_bid = st.number_input("Your Bid:", 0, st.session_state.cash['Player'], step=10)
    
    if st.button("Confirm Bid"):
        target = st.session_state.pending_move
        ai_bid = calculate_ai_bid(st.session_state.board, st.session_state.cash['AI'], st.session_state.cash['Player'], target)
        
        # Deduct from both
        st.session_state.cash['Player'] -= player_bid
        st.session_state.cash['AI'] -= ai_bid
        
        if player_bid >= ai_bid:
            st.session_state.board[target] = 'X'
            st.success(f"You won the square! AI bid ${ai_bid}")
        else:
            # If AI wins the bid, it plays its BEST calculated move, 
            # not necessarily the one you clicked!
            actual_move = get_best_move(st.session_state.board)
            st.session_state.board[actual_move] = 'O'
            st.error(f"AI outbid you with ${ai_bid} and took a strategic square!")

        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

if st.session_state.winner:
    st.header(f"Result: {st.session_state.winner}")
    if st.button("Rematch?"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
