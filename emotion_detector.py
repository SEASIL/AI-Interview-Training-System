"""
emotion_detector.py  –  Free emotion detection via OpenCV + signal fusion
No DeepFace · No TensorFlow · No paid services · Works on Windows/Mac/Linux

Detection pipeline:
  1. Face detection  – Haar cascade (built into OpenCV, zero download)
  2. Smile detection – Haar cascade on lower face
  3. Eye openness    – Eye cascade + aspect ratio
  4. Brow tension    – Edge density in glabella region
  5. Mouth openness  – Dark-pixel ratio in lip zone
  6. Skin brightness – Overall face luminance
  All six signals → weighted emotion classifier → 7 emotion scores
"""

import cv2
import numpy as np

# ── Load OpenCV built-in cascades ────────────────────────────
_FC  = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
_FC2 = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
_EC  = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
_SC  = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')


def _detect_face(gray):
    """Try several cascade configs; return (x,y,w,h) of largest face, or None."""
    configs = [
        (_FC,  1.05, 5, (80, 80)),
        (_FC,  1.1,  4, (60, 60)),
        (_FC2, 1.05, 4, (60, 60)),
        (_FC,  1.15, 3, (40, 40)),
        (_FC,  1.2,  2, (30, 30)),
    ]
    for cascade, scale, neighbors, minSz in configs:
        faces = cascade.detectMultiScale(
            gray, scaleFactor=scale, minNeighbors=neighbors,
            minSize=minSz, flags=cv2.CASCADE_SCALE_IMAGE
        )
        if len(faces):
            return tuple(sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0])
    return None


def _smile(gray, x, y, w, h):
    """Smile score 0-100 using cascade + brightness ratio."""
    lower = gray[y + h//2 : y + h, x : x + w]

    # Try multiple thresholds (real photos need lower minNeighbors)
    detected = False
    for nn in [5, 8, 10, 12, 15]:
        s = _SC.detectMultiScale(lower, scaleFactor=1.4, minNeighbors=nn,
                                 minSize=(w//5, h//10))
        if len(s):
            detected = True
            break

    cascade_s = 75.0 if detected else 0.0

    # Teeth brightness in mouth zone (bright pixels = open smile)
    mx  = x + int(w * 0.2)
    my  = y + int(h * 0.62)
    mw  = int(w * 0.6)
    mhh = int(h * 0.20)
    mouth_roi = gray[my:my+mhh, mx:mx+mw]
    bright_s  = 0.0
    if mouth_roi.size > 0:
        bright_ratio = float(np.sum(mouth_roi > 180)) / mouth_roi.size
        bright_s     = float(np.clip(bright_ratio * 300, 0, 60))

    return float(np.clip(cascade_s * 0.65 + bright_s * 0.35, 0, 100))


def _eye_open(gray, x, y, w, h):
    """Eye openness 0-100 via cascade + aspect ratio."""
    upper = gray[y : y + h//2, x : x + w]
    eyes  = _EC.detectMultiScale(upper, scaleFactor=1.1, minNeighbors=5,
                                 minSize=(w//8, w//8))
    if not len(eyes):
        return 55.0   # assume normal if not detected

    scores = []
    for (ex, ey, ew, eh) in eyes[:2]:
        roi = upper[ey:ey+eh, ex:ex+ew]
        if roi.size == 0:
            continue
        # Aspect ratio: open eye is taller relative to width
        aspect = eh / (ew + 1e-6)
        scores.append(float(np.clip(aspect * 300 - 20, 10, 100)))

    return float(np.mean(scores)) if scores else 55.0


def _brow_furrow(gray, x, y, w, h):
    """Brow tension 0-100: edge density between the eyebrows."""
    rx  = x + int(w * 0.33)
    ry  = y + int(h * 0.10)
    rw  = int(w * 0.34)
    rh  = int(h * 0.22)
    roi = gray[ry:ry+rh, rx:rx+rw]
    if roi.size == 0:
        return 0.0
    edges    = cv2.Canny(roi, 20, 80)
    edge_den = float(np.sum(edges > 0)) / roi.size
    return float(np.clip(edge_den * 1500, 0, 100))


def _mouth_open(gray, x, y, w, h):
    """Mouth openness 0-100: dark-pixel ratio in lip interior."""
    mx  = x + int(w * 0.28)
    my  = y + int(h * 0.65)
    mw  = int(w * 0.44)
    mhh = int(h * 0.18)
    roi = gray[my:my+mhh, mx:mx+mw]
    if roi.size == 0:
        return 0.0
    dark_ratio = float(np.sum(roi < 55)) / roi.size
    return float(np.clip(dark_ratio * 500, 0, 100))


def _brightness(gray, x, y, w, h):
    """Mean luminance of face region."""
    return float(np.mean(gray[y:y+h, x:x+w]))


def _to_emotions(smile_s, eye_s, brow_s, mouth_s, bright):
    """Fuse feature scores into 7 emotion probabilities."""
    b = (bright - 120) / 50.0          # normalised brightness
    no_smile  = 100 - smile_s
    calm_brow = 100 - brow_s

    raw = {
        "happy":    (smile_s  * 0.55 + eye_s    * 0.10
                    + max(b * 25, 0) * 0.15     - brow_s  * 0.10  + 5),
        "neutral":  (calm_brow * 0.30 + eye_s   * 0.20
                    - smile_s  * 0.25            - mouth_s * 0.15  + 25),
        "sad":      (no_smile  * 0.30 + brow_s  * 0.20
                    + max(-b * 30, 0) * 0.20     - eye_s   * 0.10  + 5),
        "angry":    (brow_s   * 0.55  + no_smile * 0.25
                    - mouth_s  * 0.05            - eye_s   * 0.05  + 2),
        "fear":     (brow_s   * 0.30  + mouth_s  * 0.35
                    + eye_s    * 0.20             - smile_s * 0.15  + 2),
        "surprise": (mouth_s  * 0.55  + eye_s    * 0.25
                    + brow_s   * 0.05             - smile_s * 0.15  + 2),
        "disgust":  (brow_s   * 0.40  + no_smile * 0.30
                    - mouth_s  * 0.10                               + 2),
    }
    # Clamp & normalise to sum=100
    raw   = {k: float(np.clip(v, 0, 100)) for k, v in raw.items()}
    total = sum(raw.values()) + 1e-6
    return {k: round(v / total * 100, 1) for k, v in raw.items()}


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────
def analyze_emotion_from_image(image_bytes: bytes) -> dict:
    """
    Analyse emotion from raw image bytes.
    Works with Streamlit st.camera_input() and st.file_uploader().
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return _unknown("Could not decode image.")

        # Resize large images (faster + cascade works better at medium res)
        h, w = img.shape[:2]
        if max(h, w) > 720:
            scale = 720 / max(h, w)
            img   = cv2.resize(img, (int(w*scale), int(h*scale)))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)          # normalise lighting

        face = _detect_face(gray)

        if face is None:
            return _no_face(gray)

        x, y, fw, fh = face
        smile_s  = _smile(gray, x, y, fw, fh)
        eye_s    = _eye_open(gray, x, y, fw, fh)
        brow_s   = _brow_furrow(gray, x, y, fw, fh)
        mouth_s  = _mouth_open(gray, x, y, fw, fh)
        bright   = _brightness(gray, x, y, fw, fh)

        emotions = _to_emotions(smile_s, eye_s, brow_s, mouth_s, bright)
        dominant = max(emotions, key=emotions.get)

        return {
            "emotion":      dominant,
            "confidence":   emotions[dominant],
            "all_emotions": emotions,
        }

    except Exception as e:
        return _unknown(str(e))


def _no_face(gray):
    b = float(np.mean(gray))
    if b > 145:
        return {"emotion": "happy",   "confidence": 45.0,
                "all_emotions": {"happy":45,"neutral":40,"surprise":15},
                "note": "No face detected – move closer and improve lighting"}
    return  {"emotion": "neutral",  "confidence": 55.0,
             "all_emotions": {"neutral":55,"happy":30,"sad":15},
             "note": "No face detected – move closer and improve lighting"}


def _unknown(msg):
    return {"emotion":"unknown","confidence":0.0,"all_emotions":{},"error":msg}


# ─────────────────────────────────────────────────────────────
# Feedback helpers (unchanged)
# ─────────────────────────────────────────────────────────────
_FEEDBACK = {
    "happy":   ("Great expression! You appear confident and engaged.",     "positive"),
    "neutral": ("Calm and composed. Try to add a bit more enthusiasm.",    "neutral"),
    "sad":     ("You look low-energy. Sit up, smile, and breathe.",        "warning"),
    "angry":   ("You seem tense. Take a slow breath before answering.",    "warning"),
    "fear":    ("You appear nervous – totally normal! Breathe slowly.",    "warning"),
    "surprise":("You look surprised. Prepare for common questions.",       "neutral"),
    "disgust": ("Try to maintain a more positive expression.",             "warning"),
    "unknown": ("Move closer to the camera with good lighting.",           "neutral"),
}
_EMOJI  = {"happy":"😄","neutral":"😐","sad":"😞","angry":"😠",
           "fear":"😨","surprise":"😲","disgust":"😒","unknown":"🤔"}
_TIPS   = {
    "happy":   "Maintain this energy – enthusiasm is contagious.",
    "neutral": "Lean forward slightly and nod to appear more engaged.",
    "sad":     "Recall a proud moment before the interview.",
    "angry":   "Box breathing (4-4-4-4 counts) calms nerves quickly.",
    "fear":    "Power pose for 2 minutes before the interview.",
    "surprise":"Review the job description and common questions.",
    "disgust": "Consciously relax your jaw and forehead muscles.",
    "unknown": "Ensure good lighting and look directly at the camera.",
}
_SCORES = {"happy":10,"neutral":7,"surprise":6,"fear":4,
           "sad":3,"angry":3,"disgust":3,"unknown":5}

def get_emotion_feedback(e): return _FEEDBACK.get(e, _FEEDBACK["unknown"])
def get_emotion_emoji(e):    return _EMOJI.get(e, "🤔")
def get_emotion_tip(e):      return _TIPS.get(e, _TIPS["unknown"])
def emotion_score(e):        return _SCORES.get(e, 5)
