"""
Aisha — Platinum Insurance Voice Assistant
Streamlit Cloud compatible — FULLY AUTOMATIC, zero clicks during the call.

Flow per question:
  1. TTS plays automatically in the browser (gTTS → base64 → HTML audio autoplay)
  2. After TTS ends, mic recording starts automatically for RECORD_SECONDS
  3. Recorded audio sent back to Python via Streamlit component value
  4. Gemini transcribes → answer processed → next question triggers automatically

Deploy on Streamlit Cloud:
  - Add GEMINI_API_KEY to App Settings → Secrets
  - requirements.txt needs: streamlit, google-genai, gTTS
"""

import io, base64, os
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from gtts import gTTS

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aisha — Platinum Insurance",
    page_icon="🛡️",
    layout="centered",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:#0d1117;color:#e6edf3;}
.stApp{background:linear-gradient(135deg,#0d1117 0%,#161b22 50%,#0d1117 100%);}
.header-box{background:linear-gradient(135deg,#1a2332,#1e3a5f);border:1px solid #30363d;border-radius:16px;padding:28px 32px;margin-bottom:24px;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,0.4);}
.header-box h1{font-family:'DM Serif Display',serif;font-size:2.2rem;color:#e6edf3;margin:0 0 6px 0;}
.header-box p{color:#8b949e;font-size:0.95rem;margin:0;}
.badge{display:inline-block;background:#1f6feb22;border:1px solid #1f6feb66;color:#58a6ff;font-size:0.75rem;padding:3px 10px;border-radius:20px;margin-bottom:12px;font-weight:500;}
.status-bar{display:flex;align-items:center;gap:10px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:12px 18px;margin-bottom:20px;font-size:0.9rem;}
.dot-idle{width:10px;height:10px;border-radius:50%;background:#8b949e;display:inline-block;}
.dot-active{width:10px;height:10px;border-radius:50%;background:#3fb950;display:inline-block;animation:pulse 1.2s infinite;}
.dot-listen{width:10px;height:10px;border-radius:50%;background:#f78166;display:inline-block;animation:pulse 0.7s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.chat-container{background:#0d1117;border:1px solid #21262d;border-radius:14px;padding:20px;min-height:320px;max-height:460px;overflow-y:auto;margin-bottom:20px;}
.msg-bot{display:flex;align-items:flex-start;gap:12px;margin-bottom:16px;}
.msg-bot .avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#1f6feb,#388bfd);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;}
.msg-bot .bubble{background:#1c2128;border:1px solid #30363d;border-radius:4px 14px 14px 14px;padding:10px 14px;max-width:80%;font-size:0.92rem;line-height:1.5;color:#e6edf3;}
.msg-bot .label{font-size:0.72rem;color:#58a6ff;font-weight:600;margin-bottom:4px;}
.msg-user{display:flex;align-items:flex-start;gap:12px;margin-bottom:16px;flex-direction:row-reverse;}
.msg-user .avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#238636,#3fb950);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;}
.msg-user .bubble{background:#132d0e;border:1px solid #238636;border-radius:14px 4px 14px 14px;padding:10px 14px;max-width:80%;font-size:0.92rem;line-height:1.5;color:#e6edf3;}
.msg-user .label{font-size:0.72rem;color:#3fb950;font-weight:600;margin-bottom:4px;text-align:right;}
.step-progress{display:flex;gap:6px;margin-bottom:20px;justify-content:center;}
.step-dot{width:8px;height:8px;border-radius:50%;background:#21262d;transition:all .3s;}
.step-dot.done{background:#3fb950;}
.step-dot.active{background:#58a6ff;transform:scale(1.3);}
.lang-badge{display:inline-block;background:#1f6feb22;border:1px solid #1f6feb44;color:#79c0ff;font-size:0.75rem;padding:2px 8px;border-radius:12px;margin-left:8px;}
.summary-card{background:linear-gradient(135deg,#161b22,#1c2128);border:1px solid #30363d;border-radius:14px;padding:24px;margin-top:20px;}
.summary-card h3{font-family:'DM Serif Display',serif;color:#e6edf3;margin:0 0 18px 0;font-size:1.3rem;}
.summary-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #21262d;font-size:0.9rem;}
.summary-row:last-child{border-bottom:none;}
.summary-key{color:#8b949e;font-weight:500;}
.summary-val{color:#e6edf3;font-weight:400;text-align:right;max-width:55%;}
.stButton>button{background:linear-gradient(135deg,#1f6feb,#388bfd)!important;color:white!important;border:none!important;border-radius:10px!important;padding:14px 28px!important;font-size:1rem!important;font-weight:600!important;width:100%!important;box-shadow:0 4px 15px rgba(31,111,235,.3)!important;}
.stButton>button:disabled{background:#21262d!important;color:#8b949e!important;box-shadow:none!important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# API KEY  (set in Streamlit Cloud → Settings → Secrets as GEMINI_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY missing. Add it to Streamlit Cloud → App Settings → Secrets.")
    st.stop()

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

RECORD_SECONDS = 5   # seconds of mic recording per turn

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT
# ─────────────────────────────────────────────────────────────────────────────
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
    0:"Name Confirmed", 1:"Good Time to Talk", 2:"Preferred Language",
    3:"Age", 4:"City", 5:"Has Insurance",
    6:"Insurance Company", 7:"Policy Expiry", 8:"Looking for New Plan"
}
FAREWELL = {
    'en': "Thank you for your time. Our advisor will contact you shortly. Have a great day!",
    'hi': "आपके समय के लिए धन्यवाद। हमारे advisor जल्द संपर्क करेंगे। शुभ दिन!",
    'ar': "شكراً على وقتك. سيتواصل معك مستشارنا قريباً. يوماً سعيداً!"
}
WRONG_PERSON = {
    'en': "I'm sorry to bother you. I was looking for {name}. Have a great day, goodbye!",
    'hi': "माफ करें आपको परेशान किया। मैं {name} से बात करना चाहती थी। शुभ दिन!",
    'ar': "آسف على الإزعاج. كنت أبحث عن {name}. يوماً سعيداً، مع السلامة!"
}
SORRY     = {'en':"Sorry, could you repeat that?",'hi':"माफ करें, दोबारा बोलें?",'ar':"آسفة، هل يمكنك الإعادة؟"}
QUICK_ACK = {'en':"Got it, thank you.",'hi':"समझ गई, धन्यवाद।",'ar':"فهمت، شكراً."}
LANG_FLAGS = {'en':'🇬🇧 English','hi':'🇮🇳 Hindi','ar':'🇦🇪 Arabic'}
LANG_RETRY = {
    'en': "Sorry, I didn't catch that. Please say English, Hindi, or Arabic.",
    'hi': "माफ करें, मुझे समझ नहीं आया। कृपया English, Hindi, या Arabic बोलें।",
    'ar': "آسفة، لم أفهم. يرجى قول English أو Hindi أو Arabic."
}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
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
        'retry_count': 0,
        'component_key': 0,          # incremented each turn to force re-render
        'retry_tts_text': '',        # text spoken on retry turns
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def make_tts_b64(text: str, lang: str) -> str:
    """Convert text to gTTS MP3 and return as base64 string."""
    clean = (text.replace("*","").replace("#","").replace("`","")
                 .replace("\n"," ").replace("  "," ").strip())
    buf = io.BytesIO()
    gTTS(text=clean, lang=lang, slow=False).write_to_fp(buf)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def transcribe(audio_b64: str, lang: str) -> str:
    """Send base64 audio to Gemini and return transcript."""
    lang_hint = {'en':'English','hi':'Hindi','ar':'Arabic'}.get(lang,'English')
    prompt = (
        f"The user is speaking in {lang_hint}. "
        "Transcribe exactly as spoken. Return ONLY the transcript text. "
        "If silent or inaudible, return an empty string."
    )
    audio_bytes = base64.b64decode(audio_b64)
    audio_part  = types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm")
    try:
        r = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, audio_part],
        )
        t = r.text.strip()
        return "" if len(t) < 2 or t.lower().startswith("i cannot") else t
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return ""

def detect_lang(text: str):
    lo = text.lower()
    if any(w in lo for w in ["hindi","हिंदी","हिन्दी","हिंदि","هندي","ہندی"]): return 'hi'
    if any(w in lo for w in ["arabic","arab","عربي","عربية","عرب"]):            return 'ar'
    if any(w in lo for w in ["english","eng","अंग्रेजी","انجليزي","إنجليزي"]): return 'en'
    return None

def add_bot(text):  st.session_state.messages.append({'role':'bot', 'text':text})
def add_user(text): st.session_state.messages.append({'role':'user','text':text})

def play_once(text: str, lang: str):
    """Play TTS without recording — used for ack/farewell between steps."""
    b64 = make_tts_b64(text, lang)
    components.html(
        f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>',
        height=0,
    )

# ─────────────────────────────────────────────────────────────────────────────
# UI RENDERERS
# ─────────────────────────────────────────────────────────────────────────────
def render_status():
    dot = {'idle':'dot-idle','speaking':'dot-active','listening':'dot-listen',
           'processing':'dot-active'}.get(st.session_state.status, 'dot-idle')
    lang_label = LANG_FLAGS.get(st.session_state.call_lang, '')
    return (f'<div class="status-bar">'
            f'<span class="{dot}"></span>'
            f'<span>{st.session_state.status_text}</span>'
            f'<span class="lang-badge">{lang_label}</span>'
            f'</div>')

def render_progress():
    s = st.session_state.step
    dots = ''.join(
        f'<div class="step-dot {"done" if i<s else "active" if i==s else ""}"></div>'
        for i in range(9))
    return f'<div class="step-progress">{dots}</div>'

def render_chat():
    html = '<div class="chat-container" id="chatbox">'
    for m in st.session_state.messages:
        if m['role'] == 'bot':
            html += (f'<div class="msg-bot">'
                     f'<div class="avatar">🤖</div>'
                     f'<div class="bubble"><div class="label">AISHA</div>{m["text"]}</div>'
                     f'</div>')
        else:
            html += (f'<div class="msg-user">'
                     f'<div class="avatar">👤</div>'
                     f'<div class="bubble"><div class="label">YOU</div>{m["text"]}</div>'
                     f'</div>')
    html += ('</div>'
             '<script>var c=document.getElementById("chatbox");'
             'if(c)c.scrollTop=c.scrollHeight;</script>')
    return html

def render_summary():
    rows = ''.join(
        f'<div class="summary-row">'
        f'<span class="summary-key">{k}</span>'
        f'<span class="summary-val">{v}</span>'
        f'</div>'
        for k, v in st.session_state.collected.items())
    return f'<div class="summary-card"><h3>📋 Call Summary</h3>{rows}</div>'

# ─────────────────────────────────────────────────────────────────────────────
# CORE AUTO VOICE COMPONENT
# ─────────────────────────────────────────────────────────────────────────────
def auto_voice_turn(tts_audio_b64: str, record_seconds: int, key: int):
    """
    Renders a self-contained HTML component that:
      1. Autoplays TTS audio
      2. After TTS ends, automatically records mic for `record_seconds`
      3. Returns the recorded audio as a base64 string via Streamlit component value

    The component communicates back via window.parent.postMessage with
    type='streamlit:setComponentValue', which is Streamlit's official
    bi-directional component protocol.
    """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: transparent;
    padding: 8px 0;
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
  }}
  #panel {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  #dot {{
    width: 12px; height: 12px;
    border-radius: 50%;
    background: #58a6ff;
    flex-shrink: 0;
    animation: blink 1.2s infinite;
  }}
  @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.2}} }}
  #lbl {{ color: #e6edf3; font-size: 0.85rem; flex: 1; }}
  #bar {{
    width: 120px; height: 5px;
    background: #21262d;
    border-radius: 3px;
    overflow: hidden;
    flex-shrink: 0;
  }}
  #fill {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #1f6feb, #3fb950);
    border-radius: 3px;
    transition: width 0.15s linear;
  }}
</style>
</head>
<body>
<div id="panel">
  <div id="dot"></div>
  <div id="lbl">🔊 Aisha is speaking...</div>
  <div id="bar"><div id="fill"></div></div>
</div>

<script>
const RECORD_MS = {record_seconds * 1000};
const TTS_B64   = `{tts_audio_b64}`;

const lbl  = document.getElementById('lbl');
const dot  = document.getElementById('dot');
const fill = document.getElementById('fill');

// ── Send audio back to Streamlit Python ──────────────────────────────────────
function returnValue(b64) {{
  window.parent.postMessage({{
    isStreamlitMessage: true,
    type: 'streamlit:setComponentValue',
    value: b64,
  }}, '*');
}}

// ── Record mic for RECORD_MS then return base64 ──────────────────────────────
async function recordMic() {{
  dot.style.background  = '#f78166';
  dot.style.animation   = 'blink 0.7s infinite';
  lbl.textContent       = '🎙️ Listening... speak now';
  fill.style.width      = '0%';

  let stream;
  try {{
    stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
  }} catch (err) {{
    lbl.textContent      = '❌ Microphone access denied — please allow in browser settings';
    dot.style.background = '#ff6b6b';
    dot.style.animation  = 'none';
    return;
  }}

  const recorder = new MediaRecorder(stream, {{ mimeType: 'audio/webm' }});
  const chunks   = [];
  recorder.ondataavailable = e => {{ if (e.data.size > 0) chunks.push(e.data); }};

  recorder.onstop = () => {{
    stream.getTracks().forEach(t => t.stop());
    const blob   = new Blob(chunks, {{ type: 'audio/webm' }});
    const reader = new FileReader();
    reader.onload = () => {{
      const b64 = reader.result.split(',')[1];
      lbl.textContent      = '⏳ Processing your response...';
      dot.style.background = '#58a6ff';
      dot.style.animation  = 'blink 1.2s infinite';
      fill.style.width     = '100%';
      returnValue(b64);
    }};
    reader.readAsDataURL(blob);
  }};

  recorder.start(200);

  // Countdown progress bar
  const t0 = Date.now();
  const timer = setInterval(() => {{
    const elapsed = Date.now() - t0;
    const pct     = Math.min((elapsed / RECORD_MS) * 100, 100);
    fill.style.width = pct + '%';
    const rem = Math.max(0, Math.ceil((RECORD_MS - elapsed) / 1000));
    lbl.textContent  = `🎙️ Listening... ${{rem}}s`;
    if (elapsed >= RECORD_MS) {{
      clearInterval(timer);
      recorder.stop();
    }}
  }}, 150);
}}

// ── Play TTS then record ──────────────────────────────────────────────────────
async function run() {{
  // Signal Streamlit we're alive (value=null means "not done yet")
  window.parent.postMessage({{
    isStreamlitMessage: true,
    type: 'streamlit:setComponentValue',
    value: null,
  }}, '*');

  if (TTS_B64) {{
    const audio = new Audio('data:audio/mp3;base64,' + TTS_B64);
    dot.style.background = '#3fb950';
    lbl.textContent      = '🔊 Aisha is speaking...';

    await new Promise(resolve => {{
      audio.onended = resolve;
      audio.onerror = resolve;
      // Some browsers block autoplay — retry with user-gesture unlock
      const playPromise = audio.play();
      if (playPromise !== undefined) {{
        playPromise.catch(() => {{
          // If blocked, show a tap-to-play note (only happens first load)
          lbl.textContent = '🔊 Tap anywhere to unmute and hear Aisha...';
          document.addEventListener('click', () => {{ audio.play(); }}, {{ once: true }});
        }});
      }}
    }});
  }}

  await recordMic();
}}

run();
</script>
</body>
</html>
"""
    # The component returns a value when JS calls setComponentValue
    # key= forces a full re-render each new turn
    return components.html(html, height=72, key=f"voice_turn_{key}")


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <div class="badge">🛡️ PLATINUM INSURANCE BROKER</div>
  <h1>Aisha Voice Assistant</h1>
  <p>AI-powered insurance customer care · English · हिंदी · العربية</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLACEHOLDERS
# ─────────────────────────────────────────────────────────────────────────────
status_ph   = st.empty()
progress_ph = st.empty()
chat_ph     = st.empty()
summary_ph  = st.empty()

# Always show current state
status_ph.markdown(render_status(), unsafe_allow_html=True)
if st.session_state.messages:
    progress_ph.markdown(render_progress(), unsafe_allow_html=True)
    chat_ph.markdown(render_chat(),         unsafe_allow_html=True)
if st.session_state.finished:
    summary_ph.markdown(render_summary(), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONTROLS  (name input / start / end call)
# ─────────────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    if not st.session_state.started and not st.session_state.finished:
        name_in = st.text_input(
            "👤 Person's name to call",
            value=st.session_state.caller_name,
            placeholder="e.g. Alia, Riya, Sara...",
            max_chars=40,
        )
        st.session_state.caller_name = name_in.strip()
        ready = bool(st.session_state.caller_name)

        if st.button("📞 Start Call", use_container_width=True, disabled=not ready):
            st.session_state.started       = True
            st.session_state.step          = 0
            st.session_state.retry_count   = 0
            st.session_state.component_key = 0
            st.rerun()

        if not ready:
            st.caption("⬆️ Enter a name above to enable the call.")

    elif st.session_state.finished:
        if st.button("🔄 Start New Call", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

with col2:
    if st.session_state.started and not st.session_state.finished:
        if st.button("📵 End Call", use_container_width=True):
            lang     = st.session_state.call_lang
            farewell = FAREWELL[lang]
            add_bot(farewell)
            st.session_state.finished    = True
            st.session_state.status      = 'idle'
            st.session_state.status_text = 'Call ended by user'
            status_ph.markdown(render_status(),   unsafe_allow_html=True)
            chat_ph.markdown(render_chat(),        unsafe_allow_html=True)
            summary_ph.markdown(render_summary(), unsafe_allow_html=True)
            play_once(farewell, lang)
            st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CALL LOOP
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.started or st.session_state.finished:
    st.stop()

step = st.session_state.step
lang = st.session_state.call_lang

# ── All questions answered ─────────────────────────────────────────────────
if step >= 9:
    farewell = FAREWELL[lang]
    add_bot(farewell)
    st.session_state.finished    = True
    st.session_state.status      = 'idle'
    st.session_state.status_text = 'Call completed ✅'
    status_ph.markdown(render_status(),   unsafe_allow_html=True)
    progress_ph.markdown(render_progress(), unsafe_allow_html=True)
    chat_ph.markdown(render_chat(),        unsafe_allow_html=True)
    summary_ph.markdown(render_summary(), unsafe_allow_html=True)
    play_once(farewell, lang)
    st.stop()

# ── Decide what to speak this turn ────────────────────────────────────────
if st.session_state.retry_count == 0:
    # Fresh question
    speak_text = QUESTIONS[lang][step].replace(
        "{name}", st.session_state.caller_name or "you"
    )
    if not any(m['text'] == speak_text for m in reversed(st.session_state.messages[-2:])):
        add_bot(speak_text)
else:
    # Retry — speak the retry/sorry message stored in state
    speak_text = st.session_state.retry_tts_text

# ── Update status bar ────────────────────────────────────────────────────
st.session_state.status      = 'listening'
st.session_state.status_text = f'🎙️ Auto-listening after Aisha speaks... (Q{step+1}/9)'
status_ph.markdown(render_status(),   unsafe_allow_html=True)
progress_ph.markdown(render_progress(), unsafe_allow_html=True)
chat_ph.markdown(render_chat(),        unsafe_allow_html=True)

# ── Render the auto-speak + auto-record component ─────────────────────────
tts_b64_str = make_tts_b64(speak_text, lang)
received    = auto_voice_turn(
    tts_audio_b64=tts_b64_str,
    record_seconds=RECORD_SECONDS,
    key=st.session_state.component_key,
)

# ── Process returned audio ─────────────────────────────────────────────────
# received is None until JS calls setComponentValue with the base64 audio
if not received or not isinstance(received, str) or len(received) < 200:
    # Still waiting for audio — Streamlit will rerun when value arrives
    st.stop()

# ── Transcribe ────────────────────────────────────────────────────────────
st.session_state.status      = 'speaking'
st.session_state.status_text = 'Processing your response...'
status_ph.markdown(render_status(), unsafe_allow_html=True)

user_input = transcribe(received, lang)

# ── STEP 2: Language preference ───────────────────────────────────────────
if step == 2:
    detected = detect_lang(user_input) if user_input else None
    if detected is None:
        if user_input: add_user(user_input)
        retry_msg = LANG_RETRY[lang]
        add_bot(retry_msg)
        st.session_state.retry_count   += 1
        st.session_state.retry_tts_text = retry_msg
        st.session_state.component_key += 1
        st.rerun()
    else:
        if user_input: add_user(user_input)
        st.session_state.call_lang = detected
        st.session_state.collected[QUESTION_LABELS[step]] = LANG_FLAGS[detected]
        ack = QUICK_ACK[detected]
        add_bot(ack)
        play_once(ack, detected)
        st.session_state.step          += 1
        st.session_state.retry_count    = 0
        st.session_state.component_key += 1
        st.rerun()

# ── STEP 0: Wrong person check ────────────────────────────────────────────
elif step == 0 and user_input:
    neg = ["no","nope","nahi","nahin","नहीं","نه","لا",
           "wrong","not me","wrong number","wrong person"]
    if any(w in user_input.lower() for w in neg):
        add_user(user_input)
        wrong = WRONG_PERSON[lang].replace(
            "{name}", st.session_state.caller_name or "the person"
        )
        add_bot(wrong)
        st.session_state.collected["Name Confirmed"] = "No — Wrong person"
        st.session_state.finished    = True
        st.session_state.status      = 'idle'
        st.session_state.status_text = 'Call ended — wrong person'
        status_ph.markdown(render_status(),   unsafe_allow_html=True)
        chat_ph.markdown(render_chat(),        unsafe_allow_html=True)
        summary_ph.markdown(render_summary(), unsafe_allow_html=True)
        play_once(wrong, lang)
        st.stop()
    else:
        add_user(user_input)
        st.session_state.collected[QUESTION_LABELS[step]] = user_input
        ack = QUICK_ACK[lang]
        add_bot(ack)
        play_once(ack, lang)
        st.session_state.step          += 1
        st.session_state.retry_count    = 0
        st.session_state.component_key += 1
        st.rerun()

# ── All other steps ───────────────────────────────────────────────────────
else:
    if not user_input:
        if st.session_state.retry_count < 1:
            sorry = SORRY[lang]
            add_bot(sorry)
            st.session_state.retry_count   += 1
            st.session_state.retry_tts_text = sorry
            st.session_state.component_key += 1
            st.rerun()
        else:
            # Give up on this question, move on
            st.session_state.collected[QUESTION_LABELS[step]] = "—"
            st.session_state.step          += 1
            st.session_state.retry_count    = 0
            st.session_state.component_key += 1
            st.rerun()
    else:
        add_user(user_input)
        st.session_state.collected[QUESTION_LABELS[step]] = user_input
        ack = QUICK_ACK[lang]
        add_bot(ack)
        play_once(ack, lang)
        st.session_state.step          += 1
        st.session_state.retry_count    = 0
        st.session_state.component_key += 1
        st.rerun()
