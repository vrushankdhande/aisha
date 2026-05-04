import streamlit as st
import io
import base64
import requests
from gtts import gTTS

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Aisha — Platinum Insurance",
    page_icon="🛡️",
    layout="centered"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}
.stApp {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
}
.header-box {
    background: linear-gradient(135deg, #1a2332, #1e3a5f);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.header-box h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #e6edf3;
    margin: 0 0 6px 0;
}
.header-box p { color: #8b949e; font-size: 0.95rem; margin: 0; }
.badge {
    display: inline-block;
    background: #1f6feb22;
    border: 1px solid #1f6feb66;
    color: #58a6ff;
    font-size: 0.75rem;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
    font-weight: 500;
}
.status-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 20px;
    font-size: 0.9rem;
}
.dot-idle   { width:10px;height:10px;border-radius:50%;background:#8b949e;display:inline-block; }
.dot-active { width:10px;height:10px;border-radius:50%;background:#3fb950;display:inline-block;animation:pulse 1.2s infinite; }
.dot-listen { width:10px;height:10px;border-radius:50%;background:#f78166;display:inline-block;animation:pulse 0.7s infinite; }
@keyframes pulse { 0%,100%{opacity:1}50%{opacity:0.3} }
.chat-container {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 14px;
    padding: 20px;
    min-height: 320px;
    max-height: 460px;
    overflow-y: auto;
    margin-bottom: 20px;
}
.msg-bot { display:flex;align-items:flex-start;gap:12px;margin-bottom:16px; }
.msg-bot .avatar {
    width:36px;height:36px;border-radius:50%;
    background:linear-gradient(135deg,#1f6feb,#388bfd);
    display:flex;align-items:center;justify-content:center;
    font-size:1rem;flex-shrink:0;
}
.msg-bot .bubble {
    background:#1c2128;border:1px solid #30363d;
    border-radius:4px 14px 14px 14px;
    padding:10px 14px;max-width:80%;font-size:0.92rem;line-height:1.5;color:#e6edf3;
}
.msg-bot .label { font-size:0.72rem;color:#58a6ff;font-weight:600;margin-bottom:4px; }
.msg-user { display:flex;align-items:flex-start;gap:12px;margin-bottom:16px;flex-direction:row-reverse; }
.msg-user .avatar {
    width:36px;height:36px;border-radius:50%;
    background:linear-gradient(135deg,#238636,#3fb950);
    display:flex;align-items:center;justify-content:center;
    font-size:1rem;flex-shrink:0;
}
.msg-user .bubble {
    background:#132d0e;border:1px solid #238636;
    border-radius:14px 4px 14px 14px;
    padding:10px 14px;max-width:80%;font-size:0.92rem;line-height:1.5;color:#e6edf3;
}
.msg-user .label { font-size:0.72rem;color:#3fb950;font-weight:600;margin-bottom:4px;text-align:right; }
.step-progress { display:flex;gap:6px;margin-bottom:20px;justify-content:center; }
.step-dot { width:8px;height:8px;border-radius:50%;background:#21262d;transition:all 0.3s; }
.step-dot.done  { background:#3fb950; }
.step-dot.active{ background:#58a6ff;transform:scale(1.3); }
.lang-badge {
    display:inline-block;background:#1f6feb22;border:1px solid #1f6feb44;
    color:#79c0ff;font-size:0.75rem;padding:2px 8px;border-radius:12px;margin-left:8px;
}
.summary-card {
    background:linear-gradient(135deg,#161b22,#1c2128);
    border:1px solid #30363d;border-radius:14px;padding:24px;margin-top:20px;
}
.summary-card h3 {
    font-family:'DM Serif Display',serif;color:#e6edf3;
    margin:0 0 18px 0;font-size:1.3rem;
}
.summary-row {
    display:flex;justify-content:space-between;
    padding:10px 0;border-bottom:1px solid #21262d;font-size:0.9rem;
}
.summary-row:last-child { border-bottom:none; }
.summary-key { color:#8b949e;font-weight:500; }
.summary-val { color:#e6edf3;font-weight:400;text-align:right;max-width:55%; }
.stButton>button {
    background:linear-gradient(135deg,#1f6feb,#388bfd) !important;
    color:white !important;border:none !important;border-radius:10px !important;
    padding:14px 28px !important;font-size:1rem !important;font-weight:600 !important;
    width:100% !important;box-shadow:0 4px 15px rgba(31,111,235,0.3) !important;
}
.stButton>button:disabled {
    background:#21262d !important;color:#8b949e !important;box-shadow:none !important;
}
.instruction-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
    font-size: 0.88rem;
    color: #8b949e;
    text-align: center;
}
.instruction-box strong { color: #58a6ff; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIG  —  store API key in Streamlit secrets
# ─────────────────────────────────────────────
# In Streamlit Cloud → Settings → Secrets, add:
#   GEMINI_API_KEY = "your-key-here"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

# ─────────────────────────────────────────────
# QUESTIONS  (multilingual)
# ─────────────────────────────────────────────
QUESTIONS = {
    'en': {
        0: "Hi, this is Aisha from Platinum Insurance Broker. Am I speaking with {name}?",
        1: "Just a quick follow-up on your medical insurance. Is this a good time?",
        2: "Would you prefer English, Hindi, or Arabic?",
        3: "May I know your age?",
        4: "Which city are you currently living in?",
        5: "Do you currently have any medical insurance?",
        6: "Which company are you insured with?",
        7: "When is your policy expiring?",
        8: "Are you looking to get a new health insurance plan soon?",
    },
    'hi': {
        0: "नमस्ते, मैं Aisha बोल रही हूँ Platinum Insurance Broker से। क्या मैं {name} से बात कर रही हूँ?",
        1: "आपके medical insurance के बारे में बात करनी थी। क्या अभी ठीक रहेगा?",
        2: "क्या आप English, Hindi या Arabic में बात करना पसंद करेंगी?",
        3: "क्या आप अपनी उम्र बता सकती हैं?",
        4: "आप अभी किस शहर में रह रही हैं?",
        5: "क्या आपके पास अभी कोई medical insurance है?",
        6: "आप किस company से insured हैं?",
        7: "आपकी policy कब expire हो रही है?",
        8: "क्या आप जल्द ही नया health insurance plan लेना चाहती हैं?",
    },
    'ar': {
        0: "مرحباً، أنا عائشة من Platinum Insurance Broker. هل أتحدث مع {name}؟",
        1: "لدي متابعة سريعة بخصوص تأمينك الطبي. هل الوقت مناسب؟",
        2: "هل تفضلين العربية أم الإنجليزية أم الهندية؟",
        3: "هل يمكنني معرفة عمرك؟",
        4: "في أي مدينة تقيمين حالياً؟",
        5: "هل لديك تأمين طبي حالياً؟",
        6: "مع أي شركة أنت مؤمّنة؟",
        7: "متى تنتهي صلاحية بوليصتك؟",
        8: "هل تفكرين في خطة تأمين صحي جديدة قريباً؟",
    }
}

QUESTION_LABELS = {
    0: "Name Confirmed", 1: "Good Time to Talk", 2: "Preferred Language",
    3: "Age", 4: "City", 5: "Has Insurance",
    6: "Insurance Company", 7: "Policy Expiry", 8: "Looking for New Plan"
}
FAREWELL = {
    'en': "Thank you for your time. Our advisor will contact you shortly. Have a great day!",
    'hi': "आपके समय के लिए धन्यवाद। हमारे advisor जल्द संपर्क करेंगे। शुभ दिन!",
    'ar': "شكراً على وقتك. سيتواصل معك مستشارنا قريباً. يوماً سعيداً!"
}
WRONG_PERSON = {
    'en': "I'm sorry to bother you. I was looking for {name}. Have a great day, goodbye!",
    'hi': "माफ करें आपको परेशान किया। मैं {name} से बात करना चाहती थी। शुभ दिन, धन्यवाद!",
    'ar': "آسف على الإزعاج. كنت أبحث عن {name}. يوماً سعيداً، مع السلامة!"
}
SORRY     = {'en': "Sorry, could you repeat that?", 'hi': "माफ करें, दोबारा बोलें?", 'ar': "آسفة، هل يمكنك الإعادة؟"}
QUICK_ACK = {'en': "Got it, thank you.", 'hi': "समझ गई, धन्यवाद।", 'ar': "فهمت، شكراً."}
LANG_FLAGS = {'en': '🇬🇧 English', 'hi': '🇮🇳 Hindi', 'ar': '🇦🇪 Arabic'}
GTTS_LANG  = {'en': 'en', 'hi': 'hi', 'ar': 'ar'}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        'step': 0,
        'call_lang': 'en',
        'messages': [],
        'collected': {},
        'caller_name': '',
        'phase': 'setup',        # setup → speaking → listening → done
        'current_question': '',
        'tts_audio': None,       # bytes of current TTS mp3 to autoplay
        'waiting_for_audio': False,
        'finished': False,
        'end_call': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def make_tts(text: str, lang: str) -> bytes:
    """Generate TTS mp3 bytes using gTTS (works on Streamlit Cloud)."""
    clean = (text.replace("*","").replace("#","").replace("`","")
             .replace("\n"," ").replace("  "," ").strip())
    tts = gTTS(text=clean, lang=GTTS_LANG.get(lang, 'en'), slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def transcribe_with_gemini(audio_bytes: bytes, lang: str) -> str:
    """Send audio to Gemini REST API for transcription — no Google SDK needed."""
    lang_hint = {'en': 'English', 'hi': 'Hindi', 'ar': 'Arabic'}.get(lang, 'English')
    prompt = (
        f"The user is speaking in {lang_hint}. "
        "Transcribe the audio exactly as spoken. "
        "Return ONLY the transcript text, no extra commentary. "
        "If the audio is silent or inaudible, return an empty string."
    )
    import base64 as _b64
    audio_b64 = _b64.b64encode(audio_bytes).decode("utf-8")
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "audio/wav",
                        "data": audio_b64
                    }
                }
            ]
        }]
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        transcript = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        if len(transcript) < 2 or transcript.lower().startswith("i cannot"):
            return ""
        return transcript
    except Exception as e:
        st.warning(f"Transcription error: {e}")
        return ""


def get_question_text(step: int) -> str:
    lang = st.session_state.call_lang
    return QUESTIONS[lang][step].replace(
        "{name}", st.session_state.caller_name or "you"
    )


def is_negative(text: str) -> bool:
    lower = text.lower()
    neg_words = ["no", "nope", "nahi", "nahin", "नहीं", "نه", "لا",
                 "wrong", "not me", "wrong number", "wrong person"]
    return any(w in lower for w in neg_words)


def detect_lang(text: str):
    lower = text.lower()
    if any(w in lower for w in ["hindi", "हिंदी", "हिन्दी"]):
        return 'hi'
    if any(w in lower for w in ["arabic", "عربي", "arab"]):
        return 'ar'
    return 'en'


def add_bot_msg(text: str):
    st.session_state.messages.append({'role': 'bot', 'text': text})


def add_user_msg(text: str):
    st.session_state.messages.append({'role': 'user', 'text': text})


# ─────────────────────────────────────────────
# UI RENDERERS
# ─────────────────────────────────────────────

def render_status():
    phase = st.session_state.phase
    dot_map = {
        'setup':     ('dot-idle',   'Ready to start'),
        'speaking':  ('dot-active', 'Aisha is speaking...'),
        'listening': ('dot-listen', '🎙️ Your turn — record your answer below'),
        'done':      ('dot-idle',   'Call completed ✅'),
    }
    dot, text = dot_map.get(phase, ('dot-idle', ''))
    lang_label = LANG_FLAGS.get(st.session_state.call_lang, '')
    return f'''<div class="status-bar">
        <span class="{dot}"></span>
        <span>{text}</span>
        <span class="lang-badge">{lang_label}</span>
    </div>'''


def render_progress():
    step = st.session_state.step
    dots = ''.join(
        f'<div class="step-dot {"done" if i < step else "active" if i == step else ""}"></div>'
        for i in range(9)
    )
    return f'<div class="step-progress">{dots}</div>'


def render_chat():
    html = '<div class="chat-container" id="chat-bottom">'
    for msg in st.session_state.messages:
        if msg['role'] == 'bot':
            html += f'''<div class="msg-bot">
                <div class="avatar">🤖</div>
                <div class="bubble"><div class="label">AISHA</div>{msg["text"]}</div>
            </div>'''
        else:
            html += f'''<div class="msg-user">
                <div class="avatar">👤</div>
                <div class="bubble"><div class="label">YOU</div>{msg["text"]}</div>
            </div>'''
    html += '</div>'
    return html


def render_summary():
    rows = ''.join(
        f'<div class="summary-row"><span class="summary-key">{k}</span>'
        f'<span class="summary-val">{v}</span></div>'
        for k, v in st.session_state.collected.items()
    )
    return f'<div class="summary-card"><h3>📋 Call Summary</h3>{rows}</div>'


def play_tts(text: str):
    """Render TTS audio player — browser autoplays it."""
    lang = st.session_state.call_lang
    audio_bytes = make_tts(text, lang)
    # Encode to base64 for inline autoplay HTML
    b64 = base64.b64encode(audio_bytes).decode()
    autoplay_html = f"""
    <audio autoplay style="display:none">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(autoplay_html, unsafe_allow_html=True)
    # Also show a visible player as fallback
    st.audio(audio_bytes, format="audio/mp3")


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <div class="badge">🛡️ PLATINUM INSURANCE BROKER</div>
    <h1>Aisha Voice Assistant</h1>
    <p>AI-powered insurance customer care · English · हिंदी · العربية</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN APP FLOW
# ─────────────────────────────────────────────

# ── PHASE: SETUP ── enter name, then start
if st.session_state.phase == 'setup':
    st.markdown(render_status(), unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        entered_name = st.text_input(
            "👤 Person's name to call",
            value=st.session_state.caller_name,
            placeholder="e.g. Alia, Riya, Sara...",
            max_chars=40,
        )
        st.session_state.caller_name = entered_name.strip()

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        name_ready = bool(st.session_state.caller_name)
        if st.button("📞 Start Call", use_container_width=True, disabled=not name_ready):
            # Prepare first question
            q = get_question_text(0)
            add_bot_msg(q)
            st.session_state.phase = 'speaking'
            st.session_state.current_question = q
            st.rerun()

    if not st.session_state.caller_name:
        st.markdown(
            '<p style="color:#8b949e;font-size:0.82rem;margin-top:4px;">'
            '⬆️ Enter a name to enable the call button.</p>',
            unsafe_allow_html=True
        )

# ── PHASE: SPEAKING — Aisha speaks, then we wait for user mic input
elif st.session_state.phase == 'speaking':
    st.markdown(render_status(), unsafe_allow_html=True)
    if st.session_state.messages:
        st.markdown(render_progress(), unsafe_allow_html=True)
        st.markdown(render_chat(), unsafe_allow_html=True)

    # Play current question TTS
    q = st.session_state.current_question
    if q:
        st.markdown("**🔊 Aisha says:**")
        play_tts(q)

    st.markdown("""
    <div class="instruction-box">
        🎧 Listen to Aisha above, then click <strong>▶ Move to recording</strong> when ready to speak.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎙️ Ready — Record my answer", use_container_width=True):
            st.session_state.phase = 'listening'
            st.rerun()
    with col2:
        if st.button("📵 End Call", use_container_width=True):
            lang = st.session_state.call_lang
            farewell = FAREWELL[lang]
            add_bot_msg(farewell)
            st.session_state.phase = 'done'
            st.session_state.finished = True
            st.rerun()

# ── PHASE: LISTENING — user records via st.audio_input
elif st.session_state.phase == 'listening':
    st.markdown(render_status(), unsafe_allow_html=True)
    if st.session_state.messages:
        st.markdown(render_progress(), unsafe_allow_html=True)
        st.markdown(render_chat(), unsafe_allow_html=True)

    st.markdown("""
    <div class="instruction-box">
        🎙️ Click the mic below, speak your answer clearly, then click <strong>Stop</strong>.
        Hit <strong>Submit Answer</strong> when done.
    </div>
    """, unsafe_allow_html=True)

    audio = st.audio_input("🎤 Record your answer")

    col1, col2 = st.columns(2)

    with col1:
        submit_disabled = audio is None
        if st.button("✅ Submit Answer", use_container_width=True, disabled=submit_disabled):
            step = st.session_state.step
            lang = st.session_state.call_lang

            # Transcribe with Gemini
            with st.spinner("Transcribing with Gemini..."):
                audio_bytes = audio.read()
                transcript = transcribe_with_gemini(audio_bytes, lang)

            if not transcript:
                # Retry prompt — stay in listening phase
                sorry = SORRY[lang]
                add_bot_msg(sorry)
                st.session_state.current_question = sorry
                st.session_state.phase = 'speaking'
                st.rerun()
            else:
                add_user_msg(transcript)

                # ── Q0: Wrong person check ──
                if step == 0 and is_negative(transcript):
                    wrong_msg = WRONG_PERSON[lang].replace(
                        "{name}", st.session_state.caller_name or "the person"
                    )
                    add_bot_msg(wrong_msg)
                    st.session_state.collected["Name Confirmed"] = "No — Wrong person"
                    st.session_state.phase = 'done'
                    st.session_state.finished = True
                    st.session_state.current_question = wrong_msg
                    st.rerun()

                # ── Q2: Detect preferred language ──
                if step == 2:
                    st.session_state.call_lang = detect_lang(transcript)
                    lang = st.session_state.call_lang

                # Save answer
                st.session_state.collected[QUESTION_LABELS[step]] = transcript

                # Acknowledge
                ack = QUICK_ACK[lang]
                add_bot_msg(ack)

                # Advance step
                next_step = step + 1
                st.session_state.step = next_step

                if next_step >= 9:
                    # All questions done
                    farewell = FAREWELL[lang]
                    add_bot_msg(farewell)
                    st.session_state.current_question = farewell
                    st.session_state.phase = 'done'
                    st.session_state.finished = True
                else:
                    # Next question
                    next_q = get_question_text(next_step)
                    add_bot_msg(next_q)
                    st.session_state.current_question = next_q
                    st.session_state.phase = 'speaking'

                st.rerun()

    with col2:
        if st.button("📵 End Call", use_container_width=True):
            lang = st.session_state.call_lang
            farewell = FAREWELL[lang]
            add_bot_msg(farewell)
            st.session_state.current_question = farewell
            st.session_state.phase = 'done'
            st.session_state.finished = True
            st.rerun()

# ── PHASE: DONE
elif st.session_state.phase == 'done':
    st.markdown(render_status(), unsafe_allow_html=True)
    if st.session_state.messages:
        st.markdown(render_progress(), unsafe_allow_html=True)
        st.markdown(render_chat(), unsafe_allow_html=True)

    # Play final TTS (farewell or wrong-person)
    final_msg = st.session_state.current_question
    if final_msg:
        st.markdown("**🔊 Aisha says:**")
        play_tts(final_msg)

    st.markdown(render_summary(), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Start New Call", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
