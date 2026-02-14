import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Bidding War", layout="centered")

# Hide Streamlit chrome to give the component full space
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

components.html("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f4f6fb;
  min-height: 100vh;
  padding: 16px;
}

h1 {
  font-size: 1.4rem;
  font-weight: 800;
  text-align: center;
  margin-bottom: 10px;
  color: #1a1a2e;
}

.info-box {
  background: #e8f4fd;
  border: 1px solid #bee3f8;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.82rem;
  margin-bottom: 12px;
  color: #2c5282;
  text-align: center;
}

.metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}
.metric {
  background: white;
  border-radius: 10px;
  padding: 10px;
  text-align: center;
  border: 1px solid #e0e0e0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.metric-label { font-size: 0.72rem; color: #888; margin-bottom: 2px; }
.metric-value { font-size: 1.3rem; font-weight: bold; color: #222; }

/* THE BOARD */
.board {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  width: min(90vw, 300px);
  margin: 0 auto 16px auto;
  border: 3px solid #2d3748;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 900;
  border: 1.5px solid #cbd5e0;
  min-height: 80px;
  transition: background 0.12s, transform 0.1s;
  position: relative;
}
.cell.empty {
  cursor: pointer;
  background: white;
  color: #bbb;
  font-size: 0.85rem;
  font-weight: 600;
}
.cell.empty:hover  { background: #ebf8ff; color: #3182ce; }
.cell.empty:active { background: #bee3f8; transform: scale(0.95); }
.cell.locked { background: #f7fafc; color: #ddd; font-size: 0.85rem; cursor: not-allowed; }
.cell.x { background: #ebf8ff; color: #2b6cb0; cursor: default; }
.cell.o { background: #fff5f5; color: #c53030; cursor: default; }

/* FLASH */
.flash {
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  text-align: center;
  animation: fadeIn 0.3s ease;
}
.flash.success { background: #c6f6d5; color: #276749; }
.flash.error   { background: #fed7d7
