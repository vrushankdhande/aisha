import streamlit as st
import io
import time
import tempfile
import os
import numpy as np
from google import genai
from google.genai import types
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
.info-box {
    background:#1c2128;border:1px solid #1f6feb44;border-radius:10px;
    padding:14px 18px;margin-bottom:16px;font-size:0.88rem;color:#79c0ff;line-height:1.6;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIG — API key from Streamlit secrets
# ─────────────────────────────────────────────
# In Streamlit Cloud: add GEMINI_API_KEY to Settings → Secrets
# Locally: create .streamlit/secrets.toml with  GEMINI_API_KEY = "your-key"
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = ""

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# ─────────────────────────────────────────────
# CONSTANTS
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

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        'started': False,
        'finished': False,
        'step': 0,
        'call_lang': 'en',
        'messages': [],
        'collected': {},
        'status': 'idle',
        'status_text': 'Ready to start',
        'caller_name': '',
        'awaiting_upload': False,   # True when we need the user to upload audio
        'pending_step': 0,          # which step is waiting for audio
        'tts_audio': None,          # bytes of latest TTS to play
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# AUDIO HELPERS  (cloud-safe: no sounddevice / winsound)
# ─────────────────────────────────────────────

def text_to_speech_bytes(text: str, lang: str) -> bytes:
    """Return MP3 bytes for the given text using gTTS."""
    clean = (text.replace("*", "").replace("#", "").replace("`", "")
             .replace("\n", " ").replace("  ", " ").strip())
    buf = io.BytesIO()
    tts = gTTS(text=clean, lang=lang, slow=False)
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def transcribe_with_gemini(audio_bytes: bytes, mime_type: str, lang: str) -> str:
    """Transcribe uploaded audio via Gemini Flash."""
    if gemini_client is None:
        return ""
    lang_hint = {'en': 'English', 'hi': 'Hindi', 'ar': 'Arabic'}.get(lang, 'English')
    prompt = (
        f"The user is speaking in {lang_hint}. "
        "Transcribe the audio exactly as spoken. "
        "Return ONLY the transcript text with no extra commentary. "
        "If the audio is silent or inaudible return an empty string."
    )
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    try:
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash",          # correct stable model name
            contents=[prompt, audio_part],
        )
        transcript = response.text.strip()
        if len(transcript) < 2 or transcript.lower().startswith("i cannot"):
            return ""
        return transcript
    except Exception as e:
        st.error(f"Gemini transcription error: {e}")
        return ""


# ─────────────────────────────────────────────
# UI RENDERERS
# ─────────────────────────────────────────────

def render_status():
    s = st.session_state.status
    dot = {'idle': 'dot-idle', 'speaking': 'dot-active', 'listening': 'dot-listen'}.get(s, 'dot-idle')
    lang_label = LANG_FLAGS.get(st.session_state.call_lang, '')
    return f'''<div class="status-bar">
        <span class="{dot}"></span>
        <span>{st.session_state.status_text}</span>
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
    html = '<div class="chat-container">'
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


# ─────────────────────────────────────────────
# STEP PROCESSOR  (called after audio uploaded)
# ─────────────────────────────────────────────

def process_step(step: int, user_input: str):
    """Apply business logic for a completed step."""
    lang = st.session_state.call_lang

    if user_input:
        st.session_state.messages.append({'role': 'user', 'text': user_input})

        # Q0 — wrong person?
        if step == 0:
            lower = user_input.lower()
            negative_words = [
                "no", "nope", "nahi", "nahin", "नहीं", "نه", "لا",
                "wrong", "not me", "wrong number", "wrong person"
            ]
            if any(w in lower for w in negative_words):
                wrong_msg = WRONG_PERSON[lang].replace(
                    "{name}", st.session_state.caller_name or 'the person'
                )
                st.session_state.messages.append({'role': 'bot', 'text': wrong_msg})
                st.session_state.collected["Name Confirmed"] = "No — Wrong person"
                st.session_state.tts_audio = text_to_speech_bytes(wrong_msg, lang)
                st.session_state.finished = True
                st.session_state.status = 'idle'
                st.session_state.status_text = 'Call ended — wrong person'
                return

        # Q2 — language preference
        if step == 2:
            lower = user_input.lower()
            if any(w in lower for w in ["hindi", "हिंदी", "हिन्दी"]):
                st.session_state.call_lang = 'hi'
            elif any(w in lower for w in ["arabic", "عربي", "arab"]):
                st.session_state.call_lang = 'ar'
            else:
                st.session_state.call_lang = 'en'
            lang = st.session_state.call_lang

        st.session_state.collected[QUESTION_LABELS[step]] = user_input
        ack = QUICK_ACK[lang]
        st.session_state.messages.append({'role': 'bot', 'text': ack})
    else:
        st.session_state.collected[QUESTION_LABELS[step]] = "—"

    # Advance to next step
    next_step = step + 1
    st.session_state.step = next_step

    if next_step >= 9:
        # Farewell
        farewell = FAREWELL[st.session_state.call_lang]
        st.session_state.messages.append({'role': 'bot', 'text': farewell})
        st.session_state.tts_audio = text_to_speech_bytes(farewell, st.session_state.call_lang)
        st.session_state.finished = True
        st.session_state.status = 'idle'
        st.session_state.status_text = 'Call completed ✅'
        st.session_state.awaiting_upload = False
    else:
        # Prepare next question TTS
        next_q = QUESTIONS[st.session_state.call_lang][next_step].replace(
            "{name}", st.session_state.caller_name or 'you'
        )
        st.session_state.messages.append({'role': 'bot', 'text': next_q})
        st.session_state.tts_audio = text_to_speech_bytes(next_q, st.session_state.call_lang)
        st.session_state.awaiting_upload = True
        st.session_state.pending_step = next_step
        st.session_state.status = 'listening'
        st.session_state.status_text = f'🎙️ Upload your response for Q{next_step + 1}/9'


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
# MISSING API KEY WARNING
# ─────────────────────────────────────────────
if not GEMINI_API_KEY:
    st.warning(
        "⚠️ **GEMINI_API_KEY not found.** "
        "Add it in **Streamlit Cloud → Settings → Secrets** as:\n\n"
        "```toml\nGEMINI_API_KEY = \"your-key-here\"\n```"
    )

# ─────────────────────────────────────────────
# STATUS + PROGRESS + CHAT
# ─────────────────────────────────────────────
st.markdown(render_status(), unsafe_allow_html=True)

if st.session_state.started:
    st.markdown(render_progress(), unsafe_allow_html=True)
    st.markdown(render_chat(), unsafe_allow_html=True)

# ── Play latest TTS audio ──
if st.session_state.tts_audio:
    st.audio(st.session_state.tts_audio, format="audio/mp3", autoplay=True)

# ─────────────────────────────────────────────
# CALL CONTROLS
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # ── Pre-call ──
    if not st.session_state.started and not st.session_state.finished:
        entered_name = st.text_input(
            "👤 Person's name to call",
            value=st.session_state.caller_name,
            placeholder="e.g. Alia, Riya, Sara...",
            max_chars=40,
        )
        st.session_state.caller_name = entered_name.strip()
        name_ready = bool(st.session_state.caller_name)

        if st.button("📞 Start Call", disabled=not name_ready, use_container_width=True):
            if not GEMINI_API_KEY:
                st.error("Please add your GEMINI_API_KEY in Streamlit secrets first.")
            else:
                st.session_state.started = True
                st.session_state.step = 0
                # Ask Q0
                q0 = QUESTIONS['en'][0].replace("{name}", st.session_state.caller_name)
                st.session_state.messages.append({'role': 'bot', 'text': q0})
                st.session_state.tts_audio = text_to_speech_bytes(q0, 'en')
                st.session_state.awaiting_upload = True
                st.session_state.pending_step = 0
                st.session_state.status = 'listening'
                st.session_state.status_text = '🎙️ Upload your response for Q1/9'
                st.rerun()

        if not name_ready:
            st.markdown(
                '<p style="color:#8b949e;font-size:0.82rem;margin-top:6px;">'
                '⬆️ Enter a name above to enable the call button.</p>',
                unsafe_allow_html=True,
            )

    # ── Post-call ──
    elif st.session_state.finished:
        st.markdown(render_summary(), unsafe_allow_html=True)
        if st.button("🔄 Start New Call", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

with col2:
    if st.session_state.started and not st.session_state.finished:
        if st.button("📵 End Call", use_container_width=True):
            farewell = FAREWELL[st.session_state.call_lang]
            st.session_state.messages.append({'role': 'bot', 'text': farewell})
            st.session_state.tts_audio = text_to_speech_bytes(farewell, st.session_state.call_lang)
            st.session_state.finished = True
            st.session_state.awaiting_upload = False
            st.session_state.status = 'idle'
            st.session_state.status_text = 'Call ended by user'
            st.rerun()

# ─────────────────────────────────────────────
# AUDIO UPLOAD PANEL  (replaces microphone)
# ─────────────────────────────────────────────
if st.session_state.awaiting_upload and not st.session_state.finished:
    step = st.session_state.pending_step
    st.markdown(
        f'<div class="info-box">'
        f'🎙️ <strong>Your turn — Q{step + 1}/9</strong><br>'
        f'Record your voice on your device, then upload the file below.<br>'
        f'Accepted formats: <code>mp3 · wav · ogg · webm · m4a</code>'
        f'</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload your recorded response",
        type=["mp3", "wav", "ogg", "webm", "m4a"],
        key=f"upload_step_{step}",
    )

    if uploaded is not None:
        audio_bytes = uploaded.read()
        # Detect MIME type from extension
        ext = uploaded.name.rsplit(".", 1)[-1].lower()
        mime_map = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "webm": "audio/webm",
            "m4a": "audio/mp4",
        }
        mime_type = mime_map.get(ext, "audio/wav")

        with st.spinner("Transcribing your response…"):
            transcript = transcribe_with_gemini(audio_bytes, mime_type, st.session_state.call_lang)

        if not transcript:
            # One retry hint
            st.warning("Couldn't understand the audio. Please upload again or type your answer below.")
            typed = st.text_input("Or type your answer:", key=f"typed_{step}")
            if st.button("Submit typed answer", key=f"submit_typed_{step}"):
                st.session_state.tts_audio = None
                process_step(step, typed)
                st.rerun()
        else:
            st.success(f"Heard: *{transcript}*")
            st.session_state.tts_audio = None
            process_step(step, transcript)
            st.rerun()
