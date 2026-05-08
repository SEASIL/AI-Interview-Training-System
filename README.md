# 🎯 AI Interview Training System

> An AI-powered interview preparation platform with real-time NLP feedback, live webcam emotion detection, and Google Gemini AI coaching.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)](https://streamlit.io)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9+-green?logo=opencv)](https://opencv.org)
[![Gemini](https://img.shields.io/badge/Google_Gemini-Free_Tier-orange?logo=google)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---


## 🚀 What It Does

Practice job interviews with instant AI feedback — no human coach needed.

- **4 Job Roles:** Software Developer, HR Manager, Data Scientist, Product Manager
- **40+ Interview Questions** curated per role
- **NLP Scoring** across 4 dimensions: length, confidence, keywords, structure (STAR)
- **Live Webcam Emotion Detection** using OpenCV (happy, neutral, nervous, angry, etc.)
- **Voice Input** via browser mic (Chrome/Edge)
- **AI Model Answers** powered by Google Gemini (free tier)
- **Session Dashboard** with scores, charts, and coaching report

---

## 🖥️ Screenshots

### Phase 1: Setup & Landing
> **Customizable Interview Environment:** Configure target roles, toggle AI engines, and set emotion capture intervals.
![Landing Page](assets/landing_page.png)

### Phase 2: Live Interview Session
> **Real-Time Interaction:** Integrated voice-to-text input with a live webcam feed for automated emotion tracking using OpenCV.
![Main Dashboard](assets/main_dashboard.jpg)

### Phase 3: Analytics & Feedback
> **NLP Scoring Dashboard:** Comprehensive breakdown of performance metrics including Confidence, Structure (STAR), and Length analysis.
![Results Page](assets/results_page.png)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| NLP Analysis | NLTK, TextBlob |
| Emotion Detection | OpenCV (Haar Cascades) |
| AI Coaching | Google Gemini 1.5 Flash |
| Voice Input | Web Speech API (JavaScript) |
| Data Processing | Pandas, NumPy |
| Deployment | Local or Google Colab |

---

## ⚡ Quick Start (Local)

### Prerequisites
- Python 3.11 → [Download here](https://python.org/downloads/release/python-3119)
- Chrome or Edge (for voice input)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-interview-training-system.git
cd ai-interview-training-system

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt_tab')"

# 6. Run the app
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## ☁️ Run on Google Colab (No Installation)

1. Upload all `.py` files to your Colab session
2. Run in a cell:
```python
!python launch_colab.py
```
3. Click the public URL that appears

---

## 🔑 Google Gemini API Key (Free)

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with Google → Create API Key → Copy it
3. Paste it in the app sidebar under **Gemini API key**

> Free tier: 1,500 requests/day — more than enough for daily practice.

---

## 📁 Project Structure

```
ai-interview-training-system/
│
├── app.py                  # Main Streamlit application
├── questions.py            # Question bank & keyword dictionaries
├── feedback_engine.py      # NLP scoring engine
├── emotion_detector.py     # OpenCV emotion detection
├── model_answer.py         # Google Gemini AI integration
├── launch_colab.py         # Google Colab deployment launcher
└── requirements.txt        # Python dependencies
```

---

## 📊 Scoring System

Each answer is scored across 4 dimensions:

| Dimension | Weight | What It Measures |
|---|---|---|
| Keyword Coverage | 30% | Domain-specific terminology |
| Answer Length | 25% | Completeness (optimal: 80–180 words) |
| Confidence Tone | 25% | Assertive vs. hedging language |
| Structure (STAR) | 20% | Example + result detection |

**Grades:** Excellent (≥8.5) · Good (≥7.0) · Average (≥5.0) · Needs Work (<5.0)

---

## ✨ Features

- [x] Role-based question selection (4 roles, 40+ questions)
- [x] Real-time NLP feedback on answer quality
- [x] Live webcam emotion detection (no TensorFlow needed)
- [x] Browser mic voice input (Chrome/Edge)
- [x] AI model answers via Google Gemini (free)
- [x] Session analytics dashboard with bar charts
- [x] AI coaching report after session
- [x] Works fully offline (NLP + emotion detection)
- [x] Google Colab deployment with free tunnel
- [x] No data stored — 100% private

---

## 🔧 Troubleshooting

| Error | Fix |
|---|---|
| `streamlit not recognized` | Run `venv\Scripts\activate` first |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Camera not working | Allow camera permission in browser |
| Gemini API error | Check API key in sidebar |
| Port 8501 in use | Add `--server.port 8502` to run command |

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

Built with: [Streamlit](https://streamlit.io) · [OpenCV](https://opencv.org) · [NLTK](https://nltk.org) · [TextBlob](https://textblob.readthedocs.io) · [Google Gemini](https://ai.google.dev)

