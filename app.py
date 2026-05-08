"""
app.py  –  AI Interview Training System
Webcam: auto-captures every 4 seconds while answering (no manual snapshot)
"""

import os
import time
import base64
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import plotly.express as px

from questions        import get_questions, get_keywords, get_all_roles
from feedback_engine  import analyze_answer
from emotion_detector import (
    analyze_emotion_from_image,
    get_emotion_feedback,
    get_emotion_emoji,
    get_emotion_tip,
    emotion_score,
)

st.set_page_config(
    page_title="AI Interview Trainer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* ... Animated Gradient Background remains same ... */

    /* Green Glowing AI Title */
    .ai-title {
        font-size: 3.5rem !important;
        font-weight: 800;
        background: linear-gradient(to right, #00ff88, #00ff41, #00ff88);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: shine 3s linear infinite;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        margin-bottom: 0;
        text-align: center;
    }
    
    /* Green Glowing Header Line */
    .glow-line {
        height: 4px;
        width: 100%;
        max-width: 750px;
        background: linear-gradient(90deg, #00ff88, #00ff41, #00ff88);
        background-size: 200% auto;
        animation: shine 3s linear infinite;
        margin: 15px auto 30px auto;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.7), 0 0 30px rgba(0, 255, 128, 0.4);
    }

    /* NEW: Red Divider Class */
    .red-divider {
        height: 2px;
        width: 100%;
        background: #ff3333; /* Pure Red */
        margin: 15px 0 25px 0;
        box-shadow: 0 0 12px rgba(255, 51, 51, 0.5);
        border-radius: 2px;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* Futuristic Text Area */
    [data-testid="stTextArea"] textarea {
        background: rgba(20, 25, 45, 0.6) !important;
        border: 1px solid rgba(0, 243, 255, 0.3) !important;
        color: #00f3ff !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.5), 0 0 10px rgba(0, 243, 255, 0.1) !important;
        transition: all 0.3s ease;
    }
    [data-testid="stTextArea"] textarea:focus {
        border: 1px solid #b5179e !important;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.5), 0 0 20px rgba(181, 23, 158, 0.4) !important;
    }
    
    /* Next-Gen Landing Cards */
    .landing-card {
        background: rgba(20, 25, 45, 0.4);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 30px;
        height: 100%;
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
        color: #e0e0e0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .landing-card::before {
        content: '';
        position: absolute;
        top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
        transform: skewX(-25deg);
        transition: 0.5s;
    }
    .landing-card:hover::before {
        left: 125%;
    }
    .landing-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
    }
    .card-1 { border-left: 2px solid #00f2fe; box-shadow: 0 0 15px rgba(0, 242, 254, 0.1); }
    .card-2 { border-left: 2px solid #b5179e; box-shadow: 0 0 15px rgba(181, 23, 158, 0.1); }
    .card-3 { border-left: 2px solid #f72585; box-shadow: 0 0 15px rgba(247, 37, 133, 0.1); }
    .card-4 { border-left: 2px solid #4cc9f0; box-shadow: 0 0 15px rgba(76, 201, 240, 0.1); }

    .landing-card h3 {
        margin-top: 0;
        font-size: 1.25rem;
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .landing-card p {
        font-size: 0.95rem;
        color: #a0a5b5;
        line-height: 1.5;
        margin-bottom: 0;
    }

    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #00f3ff 0%, #0077ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(0, 119, 255, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 243, 255, 0.6);
        color: white;
        border: none;
    }
    
    /* Tip Box / Glassmorphism */
    .tip-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-left: 4px solid #00f3ff;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        color: #e0e0e0 !important;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #00f3ff;
        font-weight: 800;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    }
    
    /* Emotion Live */
    .emotion-live {
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        margin: 6px 0;
        font-size: 1.15rem;
        font-weight: 600;
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Custom Error Alert */
    .custom-error-box {
        background: rgba(255, 50, 50, 0.1);
        border: 1px solid rgba(255, 50, 50, 0.5);
        border-left: 5px solid #ff3333;
        padding: 15px 20px;
        border-radius: 8px;
        color: #ffcccc;
        font-size: 1.05rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
        box-shadow: 0 0 15px rgba(255, 50, 50, 0.2);
        animation: pulseAlert 2s infinite;
    }
    @keyframes pulseAlert {
        0% { box-shadow: 0 0 10px rgba(255, 50, 50, 0.2); }
        50% { box-shadow: 0 0 20px rgba(255, 50, 50, 0.5); }
        100% { box-shadow: 0 0 10px rgba(255, 50, 50, 0.2); }
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Live webcam component
# Streams webcam in browser, auto-captures every N seconds,
# sends base64 frame to Streamlit via a hidden text input.
# ─────────────────────────────────────────────────────────────
def live_webcam_component(key: str, capture_interval: int = 4) -> str | None:
    """
    Shows a live webcam feed.
    Auto-captures a frame every `capture_interval` seconds.
    Returns the latest base64-encoded JPEG frame, or None.
    """
    html = f"""
    <div id="webcam_container_{key}" style="position:relative; width:100%;">

      <video id="video_{key}" autoplay playsinline muted
        style="width:100%; border-radius:12px; border:3px solid transparent;
               background: linear-gradient(#000, #000) padding-box, linear-gradient(45deg, #00f3ff, #b5179e) border-box;
               box-shadow: 0 0 25px rgba(0, 243, 255, 0.4); max-height:220px; object-fit:cover;">
      </video>

      <canvas id="canvas_{key}" style="display:none;"></canvas>

      <div id="status_{key}"
        style="position:absolute; top:8px; left:8px;
               background:rgba(0,0,0,0.6); color:#fff;
               font-size:12px; padding:3px 8px; border-radius:12px;
               font-family:sans-serif;">
        Starting camera...
      </div>

      <div id="emotion_overlay_{key}"
        style="position:absolute; bottom:8px; left:0; right:0;
               text-align:center; font-family:sans-serif;">
      </div>

      <input type="hidden" id="frame_data_{key}" value="">
    </div>

    <script>
    (function() {{
      const video   = document.getElementById('video_{key}');
      const canvas  = document.getElementById('canvas_{key}');
      const status  = document.getElementById('status_{key}');
      const overlay = document.getElementById('emotion_overlay_{key}');
      const frameInput = document.getElementById('frame_data_{key}');
      let stream = null;
      let captureTimer = null;
      let frameCount = 0;

      async function startCamera() {{
        try {{
          stream = await navigator.mediaDevices.getUserMedia({{
            video: {{ width: 320, height: 240, facingMode: 'user' }}
          }});
          video.srcObject = stream;
          status.textContent = '🟢 Live — analysing every {capture_interval}s';
          status.style.background = 'rgba(0,120,0,0.7)';
          scheduleCature();
        }} catch(err) {{
          status.textContent = '❌ Camera blocked: ' + err.message;
          status.style.background = 'rgba(180,0,0,0.7)';
        }}
      }}

      function captureFrame() {{
        if (!stream || !video.videoWidth) return;
        canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.7);
        const b64 = dataUrl.split(',')[1];
        frameCount++;

        // Send to Streamlit via postMessage
        window.parent.postMessage({{
          type: 'streamlit:setComponentValue',
          value: b64
        }}, '*');

        overlay.innerHTML = '<span style="background:rgba(0,0,0,0.55);color:#fff;'
          + 'padding:2px 10px;border-radius:10px;font-size:12px;">'
          + '📸 Frame ' + frameCount + ' captured</span>';

        setTimeout(() => {{ overlay.innerHTML = ''; }}, 1500);
      }}

      function scheduleCature() {{
        captureTimer = setInterval(captureFrame, {capture_interval * 1000});
      }}

      startCamera();

      // Cleanup on page hide
      document.addEventListener('visibilitychange', () => {{
        if (document.hidden && captureTimer) {{
          clearInterval(captureTimer);
        }} else if (!document.hidden && stream) {{
          scheduleCature();
        }}
      }});
    }})();
    </script>
    """
    frame_b64 = components.html(html, height=250, scrolling=False)
    return frame_b64


def voice_input_component(key: str):
    html_code = f"""
    <style>
      @keyframes pulseMicReady {{
         0% {{ box-shadow: 0 0 10px rgba(0,243,255,0.2); transform: scale(1); }}
         50% {{ box-shadow: 0 0 25px rgba(0,243,255,0.5); transform: scale(1.02); }}
         100% {{ box-shadow: 0 0 10px rgba(0,243,255,0.2); transform: scale(1); }}
      }}
      @keyframes pulseMicRec {{
         0% {{ box-shadow: 0 0 15px rgba(255,50,50,0.4); transform: scale(1); }}
         50% {{ box-shadow: 0 0 35px rgba(255,50,50,0.8); transform: scale(1.05); }}
         100% {{ box-shadow: 0 0 15px rgba(255,50,50,0.4); transform: scale(1); }}
      }}
      .mic-btn-ready {{
          padding: 14px 28px; font-size: 16px; font-weight: 700; border-radius: 50px;
          border: 2px solid #00f3ff; background: rgba(0,243,255,0.1); color: #00f3ff;
          cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: 0.3s;
          text-transform: uppercase; margin: 10px 0; animation: pulseMicReady 2.5s infinite; width: 220px;
          box-shadow: inset 0 0 10px rgba(0,243,255,0.1);
      }}
      .mic-btn-recording {{
          padding: 14px 28px; font-size: 16px; font-weight: 700; border-radius: 50px;
          border: 2px solid #ff3333; background: rgba(255,50,50,0.2); color: #ffcccc;
          cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: 0.3s;
          text-transform: uppercase; margin: 10px 0; animation: pulseMicRec 1s infinite; width: 220px;
          box-shadow: inset 0 0 15px rgba(255,50,50,0.2);
      }}
    </style>
    <div style="font-family:sans-serif;padding:4px 0; text-align:left;">
      <button id="micBtn_{key}" onclick="toggleMic_{key}()" class="mic-btn-ready">
        🎙️ <span id="micLabel_{key}">START SPEAKING</span>
      </button>
    </div>
    <script>
    (function() {{
      let rec_{key}=null, on_{key}=false;
      if(!('webkitSpeechRecognition' in window)&&!('SpeechRecognition' in window)) return;
      const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
      rec_{key}=new SR();
      rec_{key}.continuous=true; rec_{key}.interimResults=true; rec_{key}.lang='en-US';
      let fin_{key}='';

      function updateStreamlitTextarea(text) {{
          const parentDoc = window.parent.document;
          const textAreas = parentDoc.querySelectorAll('textarea[aria-label="Your spoken answer:"]');
          if (textAreas.length > 0) {{
              const stTextArea = textAreas[textAreas.length - 1]; 
              const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
              nativeInputValueSetter.call(stTextArea, text);
              stTextArea.dispatchEvent(new Event('input', {{ bubbles: true }}));
          }}
      }}

      rec_{key}.onresult=function(e){{
        let interim='';
        for(let i=e.resultIndex;i<e.results.length;++i){{
          if(e.results[i].isFinal) fin_{key}+=e.results[i][0].transcript+' ';
          else interim+=e.results[i][0].transcript;
        }}
        updateStreamlitTextarea(fin_{key} + interim);
      }};
      rec_{key}.onend=function(){{ if(on_{key}) rec_{key}.start(); }};
      window['toggleMic_{key}']=function(){{
        const btn = document.getElementById('micBtn_{key}');
        const lbl = document.getElementById('micLabel_{key}');
        if(!on_{key}){{
          fin_{key}=''; rec_{key}.start(); on_{key}=true;
          lbl.textContent='STOP RECORDING';
          btn.className='mic-btn-recording';
        }}else{{
          rec_{key}.stop(); on_{key}=false;
          lbl.textContent='START SPEAKING';
          btn.className='mic-btn-ready';
        }}
      }};
    }})();
    </script>
    """
    components.html(html_code, height=90, scrolling=False)
    
    # --- THIS IS THE GAP FOR THE RED BOX ---
    err_slot = st.empty() 
    
    transcribed = st.text_area(
        "Your spoken answer:", 
        height=150, 
        placeholder="Click 'Start speaking' and your words will appear here instantly...",
        key=f"voice_auto_{key}"
    )
    return transcribed.strip(), err_slot


# ─────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────
_DEFAULTS = {
    "started":          False,
    "questions":        [],
    "current_q":        0,
    "answers":          [],
    "feedbacks":        [],
    "emotions":         [],
    "role":             "Software Developer",
    "api_key_set":      False,
    "latest_emotion":   None,
    "emotion_history":  [],
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c5/Target_Corporation_logo_%28vector%29.svg", width=50)
    st.markdown("<h2 style='margin-top:-10px; color:white;'>Interview Trainer</h2>", unsafe_allow_html=True)
    st.divider()

    st.header("⚙️ Setup")
    role  = st.selectbox("Target role:", get_all_roles(), index=0)
    num_q = st.slider("Number of questions:", min_value=3, max_value=8, value=5)

    use_emotion = st.checkbox("Enable auto webcam emotion detection", value=True)
    use_ai      = st.checkbox("Enable AI model answers (Claude)", value=True)

    capture_interval = st.slider(
        "Emotion capture every (seconds):",
        min_value=3, max_value=10, value=5,
        help="How often to auto-capture your expression during answering"
    ) if use_emotion else 5

    use_ai = st.checkbox("Enable AI model answers (Gemini)", value=True)

    # ... (capture_interval logic stays the same) ...

    if use_ai:
        api_key = st.text_input("Gemini API key:",
                                help="Get yours at aistudio.google.com")
        if api_key:
            # Gemini's SDK looks for the GOOGLE_API_KEY environment variable
            os.environ["GOOGLE_API_KEY"] = api_key
            st.session_state.api_key_set = True
            st.success("API key saved ✓", icon="🔑")
    st.divider()
    if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
        st.session_state.update({
            "questions":       get_questions(role, num_q),
            "current_q":       0,
            "answers":         [],
            "feedbacks":       [],
            "emotions":        [],
            "started":         True,
            "role":            role,
            "latest_emotion":  None,
            "emotion_history": [],
        })
        st.rerun()

    if st.session_state.started:
        st.divider()
        total_q = len(st.session_state.questions)
        done_q  = st.session_state.current_q
        st.progress(done_q / total_q if total_q else 0)
        st.caption(f"Question {done_q} / {total_q} complete")

        # Live emotion display in sidebar
        if st.session_state.latest_emotion:
            em = st.session_state.latest_emotion
            emoji = get_emotion_emoji(em.get("emotion", "unknown"))
            st.divider()
            st.markdown("**Live emotion:**")
            st.markdown(f"## {emoji} {em.get('emotion','').title()}")
            conf = em.get("confidence", 0)
            st.progress(min(int(conf), 100))
            st.caption(f"{conf:.0f}% confidence")


# ─────────────────────────────────────────────────────────────
# Landing page
# ─────────────────────────────────────────────────────────────
if not st.session_state.started:
    st.markdown("<h1 class='ai-title'>AI Interview Training System</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#e0e0e0; font-size:1.05rem; margin-top:-10px;'>"
        "Practice real interviews with <b>AI feedback</b>, <b>automatic webcam emotion detection</b>, "
        "and <b>model answers</b> powered by AI.</p>", unsafe_allow_html=True
    )
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="landing-card card-1">
            <h3>🎤 Voice & Text Input</h3>
            <p>Provide responses seamlessly via your browser microphone or by typing.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="landing-card card-2">
            <h3>📸 Automated Emotion Tracking</h3>
            <p>Continuous webcam analysis to evaluate your emotional expressions.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="landing-card card-3">
            <h3>🧠 Intelligent Feedback</h3>
            <p>Comprehensive evaluation utilizing advanced NLP and keyword analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="landing-card card-4">
            <h3>📊 Performance Analytics</h3>
            <p>Detailed dashboard providing a complete breakdown of your scores.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:white; font-weight:600;'>How to start: <span style='font-weight:400;'>Choose your role in the sidebar, then press <b>Start Interview</b>.</span></p>", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Active interview
# ─────────────────────────────────────────────────────────────
questions = st.session_state.questions
q_idx     = st.session_state.current_q

if q_idx < len(questions):
    question = questions[q_idx]
    total    = len(questions)
    role     = st.session_state.role

    # Use the Green Glowing Header
    st.markdown("<h1 class='ai-title'>AI Interview Trainer</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)
    
    st.progress(q_idx / total)
    st.caption(f"**{role}**  ·  Question {q_idx + 1} of {total}")
    
    # Use the Red Divider instead of st.divider()
    st.markdown("<div class='red-divider'></div>", unsafe_allow_html=True)

    col_main, col_cam = st.columns([3, 1])

    # ── Webcam panel (always visible while answering) ─────────
    with col_cam:
        if use_emotion:
            st.markdown("**📸 Live Emotion Detection**")
            st.caption(f"Auto-analysing every {capture_interval}s")

            # Placeholders that update as frames arrive
            emotion_display   = st.empty()
            emotion_bar       = st.empty()
            emotion_tip_area  = st.empty()

            # Render the live webcam component
            # Note: Streamlit components can't directly return async values,
            # so we use a manual capture fallback below the live feed.
            live_webcam_component(key=f"live_{q_idx}", capture_interval=capture_interval)

            st.caption("─── or manual snapshot ───")
            cam_snap = st.camera_input(
                "Take a snapshot now",
                key=f"snap_{q_idx}",
                label_visibility="visible",
            )

            if cam_snap is not None:
                with st.spinner("Analysing…"):
                    result = analyze_emotion_from_image(cam_snap.getvalue())
                st.session_state.latest_emotion = result
                st.session_state.emotion_history.append(result)

                emotion  = result.get("emotion", "unknown")
                conf     = result.get("confidence", 0)
                msg, mood = get_emotion_feedback(emotion)
                emoji    = get_emotion_emoji(emotion)

                with emotion_display.container():
                    st.markdown(f"### {emoji} {emotion.title()}")
                    st.caption(f"{conf:.0f}% confidence")

                if mood == "positive":
                    emotion_bar.success(msg)
                elif mood == "warning":
                    emotion_bar.warning(msg)
                else:
                    emotion_bar.info(msg)

                emotion_tip_area.caption(f"💡 {get_emotion_tip(emotion)}")

                # Emotion bar chart
                all_e = result.get("all_emotions", {})
                if all_e:
                    e_df = pd.DataFrame(
                        list(all_e.items()), columns=["Emotion", "Score"]
                    ).set_index("Emotion").sort_values("Score", ascending=False)
                    st.bar_chart(e_df, height=150)

        else:
            st.info("Webcam emotion detection is off.\nEnable it in the sidebar.")

    # ── Answer input ─────────────────────────────────────────
    with col_main:
        st.markdown(f"### ❓ {question}")
        st.markdown(" ")

        # 1. Update the call to receive both text and the placeholder
        answer_text, error_box = voice_input_component(key=str(q_idx))

        submitted = st.button(
            "✅ Submit Answer",
            use_container_width=True,
            type="primary",
            key=f"submit_{q_idx}",
        )

  # ── Process submission ────────────────────────────────────
    if submitted:
        if not answer_text.strip():
            error_box.markdown(
                """<div class="custom-error-box">
                   🚨 <div style="display: flex; flex-direction: column; gap: 5px;">
                        <span style="font-weight: 800;">Action Required:</span>
                        <span style="font-size: 0.95rem; font-weight: 400;">1. You cannot submit an empty answer.</span>
                        <span style="font-size: 0.95rem; font-weight: 400;">2. Don't forget to put a full stop at the end of your answer.</span>
                      </div>
                   </div>""", 
                unsafe_allow_html=True
            )
            st.stop()

        keywords = get_keywords(role)
        feedback = analyze_answer(answer_text, question, keywords)

        # Use dominant emotion from history, or latest snapshot
        emotion_result = st.session_state.latest_emotion
        if st.session_state.emotion_history:
            # Pick most frequent emotion across all captures this question
            from collections import Counter
            emotion_counts = Counter(
                e.get("emotion", "unknown")
                for e in st.session_state.emotion_history
                if e
            )
            dominant_emotion_str = emotion_counts.most_common(1)[0][0]
            # Find the entry with that emotion and highest confidence
            best = max(
                (e for e in st.session_state.emotion_history
                 if e and e.get("emotion") == dominant_emotion_str),
                key=lambda x: x.get("confidence", 0),
                default=emotion_result
            )
            emotion_result = best

        st.session_state.answers.append(answer_text)
        st.session_state.feedbacks.append(feedback)
        st.session_state.emotions.append(emotion_result)
        # Reset emotion history for next question
        st.session_state.emotion_history = []
        st.session_state.latest_emotion  = None

        score = feedback["overall_score"]
        grade = feedback["grade"]
        if score >= 8:
            st.success(f"🌟 **{grade}!**  Score: {score}/10")
        elif score >= 6:
            st.warning(f"👍 **{grade}.**  Score: {score}/10")
        else:
            st.error(f"📈 **{grade}.**  Score: {score}/10 – keep practising!")

        with st.expander("📊 Detailed Feedback", expanded=True):
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Length",     f"{feedback['length_score']}/10")
            mc2.metric("Confidence", f"{feedback['sentiment_score']}/10")
            mc3.metric("Keywords",   f"{feedback['keyword_score']}/10")
            mc4.metric("Structure",  f"{feedback['structure_score']}/10")

            st.divider()
            st.markdown(f"**Length:** {feedback['length_msg']}")
            st.markdown(f"**Tone:** {feedback['sentiment_msg']}")

            if feedback["matched_topics"]:
                st.success("✅ Topics covered: " + ", ".join(feedback["matched_topics"]))
            else:
                st.error("❌ No strong domain keywords detected.")

            # Show emotion summary if available
            if emotion_result:
                st.divider()
                em_str = emotion_result.get("emotion", "unknown")
                em_emoji = get_emotion_emoji(em_str)
                em_msg, _ = get_emotion_feedback(em_str)
                st.markdown(f"**{em_emoji} Dominant expression during answer:** {em_str.title()}")
                st.caption(em_msg)

            st.divider()
            st.markdown("**💡 Improvement Tips:**")
            for tip in feedback["tips"]:
                st.warning(f"💡 {tip}")

        if use_ai and st.session_state.api_key_set:
            with st.expander("🧠 AI Model Answer (Gemini)", expanded=False):
                with st.spinner("Generating ideal answer…"):
                    try:
                        from model_answer import get_model_answer
                        model_ans = get_model_answer(question, role, answer_text)
                        st.markdown(model_ans)
                    except Exception as exc:
                        st.error(f"Gemini API error: {exc}")

        time.sleep(0.6)
        st.session_state.current_q += 1
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────
else:
    st.balloons()
    st.title("📊 Interview Complete – Your Results")
    role      = st.session_state.role
    feedbacks = st.session_state.feedbacks
    questions = st.session_state.questions
    answers   = st.session_state.answers
    emotions  = st.session_state.emotions

    if not feedbacks:
        st.warning("No answers recorded.")
        st.stop()

    scores = [f["overall_score"] for f in feedbacks]
    avg    = round(sum(scores) / len(scores), 1)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏆 Overall Score",  f"{avg}/10")
    col2.metric("✅ Questions Done", len(scores))
    col3.metric("🎯 Best",    f"Q{scores.index(max(scores))+1} ({max(scores)}/10)")
    col4.metric("📉 Weakest", f"Q{scores.index(min(scores))+1} ({min(scores)}/10)")

    # Emotion summary across session
    all_emotions_session = [
        e.get("emotion", "unknown") for e in emotions if e
    ]
    if all_emotions_session:
        from collections import Counter
        top_emotion = Counter(all_emotions_session).most_common(1)[0][0]
        em_emoji = get_emotion_emoji(top_emotion)
        st.info(f"{em_emoji} **Overall expression during interview:** {top_emotion.title()} — {get_emotion_feedback(top_emotion)[0]}")

    st.divider()
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.subheader("📊 Score per Question")
        chart_df = pd.DataFrame(
            {"Score": scores},
            index=[f"Q{i+1}" for i in range(len(scores))]
        )
        st.bar_chart(chart_df, height=300)

    with c_chart2:
        st.subheader("🧩 Average Score Breakdown")
        if feedbacks:
            avg_len = sum(f["length_score"] for f in feedbacks) / len(feedbacks)
            avg_conf = sum(f["sentiment_score"] for f in feedbacks) / len(feedbacks)
            avg_key = sum(f["keyword_score"] for f in feedbacks) / len(feedbacks)
            avg_struct = sum(f["structure_score"] for f in feedbacks) / len(feedbacks)
            
            pie_data = pd.DataFrame({
                "Metric": ["Length", "Confidence", "Keywords", "Structure"],
                "Average Score": [avg_len, avg_conf, avg_key, avg_struct]
            })
            
            fig = px.pie(pie_data, values="Average Score", names="Metric", hole=0.4,
                         color_discrete_sequence=["#00f3ff", "#0077ff", "#b5179e", "#4cc9f0"])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                template="plotly_dark", 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📝 Detailed Review")
    for i, (q, ans, fb, em) in enumerate(zip(questions, answers, feedbacks, emotions)):
        with st.expander(
            f"Q{i+1}: {q[:65]}{'…' if len(q)>65 else ''}  —  "
            f"{fb['grade']}  ({fb['overall_score']}/10)"
        ):
            st.markdown(f"**Your answer:**  {ans}")
            if em:
                emoji_str = get_emotion_emoji(em.get("emotion","unknown"))
                st.caption(f"Expression: {emoji_str} {em.get('emotion','unknown').title()} ({em.get('confidence',0):.0f}%)")
            st.markdown("---")
            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Length",     fb["length_score"])
            rc2.metric("Confidence", fb["sentiment_score"])
            rc3.metric("Keywords",   fb["keyword_score"])
            rc4.metric("Structure",  fb["structure_score"])
            st.markdown(f"- {fb['length_msg']}")
            st.markdown(f"- {fb['sentiment_msg']}")
            st.markdown("**💡 Tips:**")
            for tip in fb["tips"]:
                st.warning(f"💡 {tip}")

    if use_ai and st.session_state.api_key_set:
        st.divider()
        st.subheader("🧠 AI Coaching Report")
        with st.spinner("Generating personalised coaching report…"):
            try:
                from model_answer import get_overall_coaching
                report = get_overall_coaching(role, questions, answers, scores)
                st.markdown(report)
            except Exception as exc:
                st.warning(f"Could not generate report: {exc}")

    st.divider()
    st.subheader("🎯 Top Improvement Areas")
    all_tips    = [tip for fb in feedbacks for tip in fb["tips"]]
    unique_tips = list(dict.fromkeys(all_tips))[:5]
    for tip in unique_tips:
        st.warning(f"💡 {tip}")

    st.divider()
    if st.button("🔄 Start New Interview", use_container_width=True, type="primary"):
        for key in list(_DEFAULTS.keys()):
            st.session_state[key] = _DEFAULTS[key]
        st.rerun()