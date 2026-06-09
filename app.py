import streamlit as st
import time
from quiz_engine import QuizEngine, Message

st.set_page_config(
    page_title="GUESS IT ⚡ Informatika Teknologi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Styling (Cyberpunk / Matrix Style)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Orbitron:wght@500;700&display=swap');

:root {
  --neon-purple: #bd93f9;
  --neon-cyan:   #8be9fd;
  --neon-green:  #50fa7b;
  --neon-red:    #ff5555;
  --dark-bg:     #110f18;
  --gold:        #ffb86c;
  --cream:       #f8f8f2;
}

html, body, .stApp {
  background: linear-gradient(135deg, #0d0b14 0%, #171226 50%, #0d0b14 100%) !important;
  font-family: 'Fira Code', monospace !important;
  color: var(--cream) !important;
}

#MainMenu, footer, header { display: none !important; }
.stDeployButton { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }

.main .block-container {
  max-width: 100% !important;
  padding: 0 1rem 2rem !important;
}

/* ── HEADER ── */
.guess_it-header {
  text-align: center;
  padding: 1.5rem 1rem 1rem;
}
.guess_it-logo {
  font-size: 3rem;
  filter: drop-shadow(0 0 15px var(--neon-purple));
  animation: pulse-glow 2s ease-in-out infinite;
}
@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 15px var(--neon-purple)); }
  50%       { filter: drop-shadow(0 0 30px var(--neon-cyan)); }
}
.guess_it-title {
  font-family: 'Orbitron', sans-serif !important;
  font-size: 2.2rem !important;
  font-weight: 700 !important;
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-cyan), var(--neon-purple));
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s linear infinite;
  margin: 0 !important;
}
@keyframes shimmer { 0%{background-position:0% center} 100%{background-position:200% center} }
.guess_it-sub {
  font-size: 0.8rem;
  color: var(--gold);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

/* ── PANEL KIRI PROFIL & STATS ── */
.left-panel-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.9rem;
  color: var(--neon-cyan);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(139,233,253,0.3);
  margin-bottom: 15px;
}
.profile-card {
  background: rgba(189,147,249,0.08);
  border: 1px solid rgba(189,147,249,0.3);
  border-radius: 10px;
  padding: 15px;
  text-align: center;
  margin-bottom: 15px;
}
.avatar-guess {
  font-size: 2.5rem;
  margin-bottom: 5px;
}
.profile-user {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--neon-cyan);
}
.profile-title {
  font-size: 0.75rem;
  color: var(--gold);
  margin-bottom: 12px;
}
.xp-container {
  text-align: left;
}
.xp-bar-bg {
  background: rgba(258,258,258,0.1);
  border-radius: 5px;
  height: 8px;
  width: 100%;
  overflow: hidden;
  margin-top: 4px;
}
.xp-bar-fill {
  background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan));
  height: 100%;
  transition: width 0.5s ease-in-out;
}
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}
.stat-mini-card {
  background: rgba(139,233,253,0.05);
  border: 1px solid rgba(139,233,253,0.15);
  border-radius: 6px;
  padding: 10px;
}
.stat-label {
  font-size: 0.65rem;
  color: rgba(248,248,242,0.6);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--cream);
  line-height: 1.1;
}
.stat-value.purple { color: var(--neon-purple); }
.stat-value.green { color: var(--neon-green); }

/* ── STATE BADGE ── */
.state-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(139,233,253,0.1);
  border: 1px solid rgba(139,233,253,0.3);
  border-radius: 50px;
  padding: 0.3rem 0.9rem;
  font-size: 0.72rem;
  color: var(--neon-cyan);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
}
.state-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--neon-green);
  box-shadow: 0 0 8px var(--neon-green);
  display: inline-block;
}

/* ── CHATBOX TERMINAL ── */
.chat-wrapper { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1rem; }
.msg-bot {
  background: rgba(23, 18, 38, 0.85);
  border: 1px solid rgba(189,147,249,0.25);
  border-radius: 4px 15px 15px 15px;
  padding: 0.9rem 1.1rem;
  position: relative;
  max-width: 92%;
  font-size: 0.88rem;
  line-height: 1.6;
  margin-left: 10px;
}
.msg-bot.tag-success { border-color: var(--neon-green); background: rgba(80,250,123,0.05); }
.msg-bot.tag-danger { border-color: var(--neon-red); background: rgba(255,85,85,0.05); }
.msg-bot.tag-hero { border-color: var(--neon-cyan); background: rgba(139,233,253,0.05); }
.msg-bot.tag-action { border-color: var(--gold); background: rgba(255,184,108,0.05); }

.msg-user {
  background: linear-gradient(135deg, var(--neon-purple), #9a66e6);
  border-radius: 15px 4px 15px 15px;
  padding: 0.7rem 1.1rem;
  align-self: flex-end;
  max-width: 78%;
  font-size: 0.88rem;
  color: white;
  font-weight: 500;
}
.msg-bot-avatar {
  position: absolute;
  top: -10px; left: -10px;
  width: 26px; height: 26px;
  background: var(--neon-purple);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem;
  box-shadow: 0 0 8px var(--neon-purple);
}

/* ── STYLE TEXT INPUT MANUAl ── */
div[data-testid="stTextInput"] input {
  background-color: rgba(13, 11, 20, 0.8) !important;
  color: var(--neon-cyan) !important;
  border: 1px solid rgba(139,233,253,0.3) !important;
  font-family: 'Fira Code', monospace !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--neon-cyan) !important;
  box-shadow: 0 0 10px rgba(139,233,253,0.5) !important;
}

/* ── HOVER SUBMIT BUTTON ── */
.stButton > button {
  background: rgba(139,233,253,0.1) !important;
  border: 1px solid rgba(139,233,253,0.4) !important;
  border-radius: 6px !important;
  color: var(--neon-cyan) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 0.85rem !important;
}
.stButton > button:hover {
  background: var(--neon-cyan) !important;
  color: #110f18 !important;
  box-shadow: 0 0 12px var(--neon-cyan);
}
</style>
""", unsafe_allow_html=True)

def stream_text(text):
    """FITUR 3: Typewriter Effect"""
    for char in text:
        yield char
        time.sleep(0.01)

    # Render seluruh histori chat
    for role, text, emoji, tag in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="chat-wrapper"><div class="msg-user">{text}</div></div>', unsafe_allow_html=True)
        else:
            tag_class = f"tag-{tag}" if tag else ""
            st.markdown(f'<div class="chat-wrapper"><div class="msg-bot {tag_class}"><div class="msg-bot-avatar">{emoji or "🤖"}</div><div>', unsafe_allow_html=True)
            st.write_stream(stream_text(text.replace('\n', '  \n')))
            st.markdown('</div></div></div>', unsafe_allow_html=True)

def init_session():
    if "engine" not in st.session_state:
        st.session_state.engine = QuizEngine()
        st.session_state.chat_history = []
        st.session_state.step_count = 0

        greet_msgs = st.session_state.engine.start()
        for m in greet_msgs:
            st.session_state.chat_history.append(("bot", m.text, m.emoji, m.tag))

def process_action(text_input: str):
    st.session_state.chat_history.append(("user", text_input, "", ""))
    st.session_state.step_count += 1

    responses = st.session_state.engine.process_input(text_input)
    for m in responses:
        st.session_state.chat_history.append(("bot", m.text, m.emoji, m.tag))


init_session()
engine = st.session_state.engine
stats = engine.session_data

col_left, col_right = st.columns([1, 3], gap="medium")

with col_left:
    st.markdown('<div class="left-panel-title">📡 Network Agent Profile</div>', unsafe_allow_html=True)

    user_xp = stats.get("accumulated_xp", 0)
    xp_percentage = min(100, int((user_xp / 180) * 100))
    
    st.markdown(f"""
    <div class="profile-card">
        <div class="avatar-guess">🧑‍💻</div>
        <div class="profile-user">{stats.get('player_name')}</div>
        <div class="profile-title">{stats.get('player_title')}</div>
        <div class="xp-container">
            <div class="stat-label">System XP Progress ({user_xp}/180)</div>
            <div class="xp-bar-bg">
                <div class="xp-bar-fill" style="width: {xp_percentage}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚙️ Konfigurasi Enkripsi Agen"):
        change_name = st.text_input("Ganti Nama Samaran:", value=stats.get('player_name'))
        if change_name and change_name.strip() and change_name != stats.get('player_name'):
            stats['player_name'] = change_name
            st.rerun()

    score = stats.get("score", 0)
    streak = stats.get("streak", 0)
    current_lvl = stats.get("current_level", 1)
    l_idx = stats.get("level_idx", 0)
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-mini-card">
            <div class="stat-label">MATCH SCORE</div>
            <div class="stat-value purple">{score} PTS</div>
        </div>
        <div class="stat-mini-card">
            <div class="stat-label">COMBO STREAK</div>
            <div class="stat-value green">{streak}x</div>
        </div>
        <div class="stat-mini-card">
            <div class="stat-label">MAIN LEVEL</div>
            <div class="stat-value" style="color:var(--gold);">LVL {current_lvl}</div>
        </div>
        <div class="stat-mini-card">
            <div class="stat-label">LEVEL TASK</div>
            <div class="stat-value">Q-{min(l_idx + 1, 3)}/3</div>
        </div>
    </div>
    <div class="stat-mini-card" style="margin-top: 8px;">
        <div class="stat-label">⚙️ ACTIVE MACHINE STATE</div>
        <div style="font-size:0.85rem; color:#8be9fd; font-weight:bold; margin-top:2px;">{engine.get_state()}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔌 Force Reboot System", use_container_width=True):
        st.session_state.clear()
        st.rerun()

with col_right:
    st.markdown("""
    <div class="guess_it-header">
      <div class="guess_it-logo">⚡</div>
      <div class="guess_it-title">GUESS IT</div>
      <div class="guess_it-sub">Mainframe Informatika Quiz </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align:center"><span class="state-badge"><span class="state-dot"></span>TERMINAL CONNECTED</span></div>', unsafe_allow_html=True)
    
    for role, text, emoji, tag in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="chat-wrapper"><div class="msg-user">{text}</div></div>', unsafe_allow_html=True)
        else:
            formatted = text.replace('\n', '<br>')
            tag_class = f"tag-{tag}" if tag else ""
            st.markdown(
                f'<div class="chat-wrapper">'
                f'<div class="msg-bot {tag_class}">'
                f'<div class="msg-bot-avatar">{emoji or "🤖"}</div>'
                f'<div>{formatted}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            
    st.markdown("<br>", unsafe_allow_html=True)

    current_state = engine.get_state()
    quick_replies = {
        "GREETING":        [("⚡ MULAI", "MULAI")],
        "MAIN_MENU":       [("🎮 KUIS", "KUIS"), ("🏆 RANKING", "RANKING"), ("💡 FACT", "FACT"), ("🔌 SHUTDOWN", "SHUTDOWN")],
        "CHECKING_ANSWER": [("▶️ LANJUT", "LANJUT")],
        "LEVEL_UP":        [("▶️ LANJUT", "LANJUT")],
        "SHOW_LEADERBOARD": [("📊 HASIL", "KEMBALI"),("🏠 MENU", "MENU")],
        "SHOW_TIPS":       [("🏠 MENU", "MENU")],
        "FEEDBACK":        [("🏆 RANKING", "RANKING"), ("✅ SELESAI", "done")],
        "END":             [("🔄 REBOOT", "REBOOT")],
    }
    if current_state in quick_replies:
        btns = quick_replies[current_state]
        cols = st.columns(len(btns))
        for i, (label, cmd) in enumerate(btns):
            with cols[i]:
                if st.button(label, key=f"qr_{cmd}_{st.session_state.step_count}", use_container_width=True):
                    process_action(cmd)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_input, col_btn = st.columns([5, 1])
    
    with col_input:
        user_text = st.text_input(
            "Masukkan perintah terminal...",
            key=f"input_{st.session_state.step_count}",
            placeholder="Ketik instruksi di sini (contoh: MULAI, KUIS, LANJUT)...",
            label_visibility="collapsed"
        )
    
    with col_btn:
        send = st.button("Kirim 📤", type="primary", key=f"send_{st.session_state.step_count}", use_container_width=True)
        
    if (send or user_text) and user_text.strip():
        process_action(user_text.strip())
        st.rerun()
        
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)