import streamlit as st
import random

# --- GAME LOGIC ---
def check_winner(board):
    lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a]
    return None

# --- UI SETUP ---
st.title("💰 Bidding Tic-Tac-Toe")
st.write("Highest bidder wins the square. Tie bids go to the AI!")

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

# Stats Display
col1, col2 = st.columns(2)
col1.metric("Your Cash", f"${st.session_state.cash['Player']}")
col2.metric("AI Cash", f"${st.session_state.cash['AI']}")

# Game Board
grid = st.columns(3)
for i in range(9):
    with grid[i % 3]:
        label = st.session_state.board[i] if st.session_state.board[i] else f"Square {i+1}"
        if st.button(label, key=f"btn{i}", disabled=st.session_state.board[i] is not None or st.session_state.winner is not None):
            st.session_state.pending_move = i

# Bidding Interface
if 'pending_move' in st.session_state and st.session_state.winner is None:
    bid = st.number_input("Enter your bid:", min_value=0, max_value=st.session_state.cash['Player'], step=1)
    if st.button("Submit Bid"):
        move = st.session_state.pending_move
        ai_bid = random.randint(1, st.session_state.cash['AI'])
        
        if bid >= ai_bid:
            st.session_state.board[move] = 'X'
            st.session_state.cash['Player'] -= bid
            st.success(f"You won the bid! (AI bid ${ai_bid})")
        else:
            st.session_state.board[move] = 'O'
            st.session_state.cash['AI'] -= ai_bid
            st.error(f"AI won the bid with ${ai_bid}!")
        
        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

if st.session_state.winner:
    st.balloons()
    st.header(f"Winner: {st.session_state.winner}!")
    if st.button("Reset Game"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()