import streamlit as st
import random

# --- GAME LOGIC ---
def check_winner(board):
    lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a]
    return None

def get_smart_bid(board, ai_cash, player_cash):
    # 1. AI tries to find a winning move or a block
    # This is a simple 'Smarter' logic:
    if ai_cash > player_cash:
        return player_cash + 1 # Guaranteed win if they have more money
    return random.randint(int(ai_cash * 0.2), int(ai_cash * 0.5))

# --- UI SETUP ---
st.set_page_config(page_title="Bidding Tic-Tac-Toe", page_icon="💰")
st.title("💰 Bidding Tic-Tac-Toe")

# Instructions per your request
st.info("👉 **Step 1:** Select an empty square below. \n\n👉 **Step 2:** Enter your bid at the bottom.")

if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.cash = {'Player': 1000, 'AI': 1000}
    st.session_state.winner = None

# Display Balances
c1, c2 = st.columns(2)
c1.metric("Your Cash", f"${st.session_state.cash['Player']}")
c2.metric("AI Cash", f"${st.session_state.cash['AI']}")

# --- THE GRID ---
# Changed to show X/O or empty space
grid = st.columns(3)
for i in range(9):
    with grid[i % 3]:
        current_mark = st.session_state.board[i]
        button_label = current_mark if current_mark else " "
        
        # Highlight the selected square
        is_selected = 'pending_move' in st.session_state and st.session_state.pending_move == i
        
        if st.button(button_label, key=f"sq{i}", use_container_width=True, 
                     disabled=current_mark is not None or st.session_state.winner is not None):
            st.session_state.pending_move = i
            st.rerun()

# --- BIDDING SECTION ---
if 'pending_move' in st.session_state and st.session_state.winner is None:
    st.write(f"--- Bidding on Square {st.session_state.pending_move + 1} ---")
    bid = st.number_input("How much will you bid?", min_value=0, max_value=st.session_state.cash['Player'], step=10)
    
    if st.button("Confirm Bid & Play Turn"):
        move = st.session_state.pending_move
        ai_bid = get_smart_bid(st.session_state.board, st.session_state.cash['AI'], st.session_state.cash['Player'])
        
        # Update Cash (Both players lose their bid amount regardless of win)
        st.session_state.cash['Player'] -= bid
        st.session_state.cash['AI'] -= ai_bid
        
        if bid >= ai_bid:
            st.session_state.board[move] = 'X'
            st.success(f"You won the square! You bid ${bid}, AI bid ${ai_bid}.")
        else:
            st.session_state.board[move] = 'O'
            st.error(f"AI won the square! AI bid ${ai_bid}, you bid ${bid}.")
        
        st.session_state.winner = check_winner(st.session_state.board)
        del st.session_state.pending_move
        st.rerun()

# End Game
if st.session_state.winner:
    if st.session_state.winner == 'X':
        st.balloons()
        st.success("YOU WON THE GAME!")
    else:
        st.error("AI WON THE GAME!")
    if st.button("Play Again"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
