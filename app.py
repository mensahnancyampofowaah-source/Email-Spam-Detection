"""
Email Spam Detector — Streamlit App
Run:  streamlit run app.py
"""

import os
import re
import pickle
import streamlit as st

# ── page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Email Spam Detector",
    page_icon=" ",
    layout="centered",
)

# ── custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:      #0d0f14;
    --surface: #13161d;
    --border:  #232733;
    --accent:  #00e5c0;
    --danger:  #ff4c6a;
    --safe:    #00e5c0;
    --muted:   #5a6275;
    --text:    #e8eaf0;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Syne', sans-serif;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

/* ── hero ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-icon {
    font-size: 3.5rem;
    display: block;
    margin-bottom: .6rem;
    filter: drop-shadow(0 0 18px #00e5c0aa);
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #00e5c0 0%, #7b9fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 .4rem;
}
.hero p {
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: .85rem;
    letter-spacing: .05em;
    margin: 0;
}

/* ── card ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,.4);
}

/* ── textarea ── */
textarea {
    background: #0d0f14 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: .88rem !important;
    resize: vertical !important;
}
textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px #00e5c030 !important; }

/* ── button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #00e5c0 0%, #00b89f 100%) !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: .04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .8rem 2rem !important;
    transition: opacity .2s, transform .15s !important;
    cursor: pointer !important;
}
.stButton > button:hover { opacity: .9 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── result cards ── */
.result-spam {
    background: linear-gradient(135deg, #1f0d12, #2a0e17);
    border: 1px solid #ff4c6a55;
    border-radius: 14px;
    padding: 1.8rem 2rem;
    text-align: center;
    box-shadow: 0 0 40px #ff4c6a22;
}
.result-ham {
    background: linear-gradient(135deg, #051a15, #071f1a);
    border: 1px solid #00e5c055;
    border-radius: 14px;
    padding: 1.8rem 2rem;
    text-align: center;
    box-shadow: 0 0 40px #00e5c022;
}
.result-icon { font-size: 3rem; display: block; margin-bottom: .6rem; }
.result-label {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -.5px;
    margin: 0 0 .4rem;
}
.result-sublabel {
    font-family: 'DM Mono', monospace;
    font-size: .8rem;
    letter-spacing: .08em;
}

/* ── confidence bar ── */
.conf-wrap { margin-top: 1.4rem; }
.conf-label {
    font-family: 'DM Mono', monospace;
    font-size: .75rem;
    color: var(--muted);
    display: flex;
    justify-content: space-between;
    margin-bottom: .4rem;
}
.conf-track {
    height: 8px;
    background: var(--border);
    border-radius: 99px;
    overflow: hidden;
}
.conf-fill-spam {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #ff4c6a, #ff8a9b);
    transition: width .6s cubic-bezier(.4,0,.2,1);
}
.conf-fill-ham {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #00e5c0, #7b9fff);
    transition: width .6s cubic-bezier(.4,0,.2,1);
}

/* ── stat badge ── */
.badge-row {
    display: flex;
    gap: .7rem;
    justify-content: center;
    margin-top: 1rem;
    flex-wrap: wrap;
}
.badge {
    background: var(--border);
    border-radius: 99px;
    padding: .25rem .85rem;
    font-family: 'DM Mono', monospace;
    font-size: .72rem;
    color: var(--muted);
    letter-spacing: .05em;
}

/* ── examples ── */
.example-btn {
    background: var(--border);
    border: 1px solid #2e3444;
    border-radius: 8px;
    padding: .4rem .9rem;
    font-family: 'DM Mono', monospace;
    font-size: .74rem;
    color: var(--muted);
    cursor: pointer;
    transition: border-color .2s, color .2s;
    display: inline-block;
    margin: .2rem;
}
.example-btn:hover { border-color: var(--accent); color: var(--accent); }

/* misc */
label, .stTextArea label { color: var(--muted) !important; font-size: .8rem !important; letter-spacing: .06em !important; font-family: 'DM Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ── stopwords (no external dependency) ──────────────────────────────────────
STOPWORDS = {
    "a","about","above","after","again","against","all","am","an","and",
    "any","are","aren't","as","at","be","because","been","before","being",
    "below","between","both","but","by","can't","cannot","could","couldn't",
    "did","didn't","do","does","doesn't","doing","don't","down","during",
    "each","few","for","from","further","get","got","had","hadn't","has",
    "hasn't","have","haven't","having","he","he'd","he'll","he's","her",
    "here","here's","hers","herself","him","himself","his","how","how's",
    "i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it",
    "it's","its","itself","let's","me","more","most","mustn't","my",
    "myself","no","nor","not","of","off","on","once","only","or","other",
    "ought","our","ours","ourselves","out","over","own","same","shan't",
    "she","she'd","she'll","she's","should","shouldn't","so","some","such",
    "than","that","that's","the","their","theirs","them","themselves","then",
    "there","there's","these","they","they'd","they'll","they're","they've",
    "this","those","through","to","too","under","until","up","very","was",
    "wasn't","we","we'd","we'll","we're","we've","were","weren't","what",
    "what's","when","when's","where","where's","which","while","who","who's",
    "whom","why","why's","will","with","won't","would","wouldn't","you",
    "you'd","you'll","you're","you've","your","yours","yourself","yourselves",
}

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " url ", text)
    text = re.sub(r"\d+", " num ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = [t for t in text.split() if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)


@st.cache_resource(show_spinner=False)
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "models", "spam_model.pkl")
    vec_path   = os.path.join(os.path.dirname(__file__), "models", "tfidf_vectorizer.pkl")
    acc_path   = os.path.join(os.path.dirname(__file__), "models", "accuracy.txt")

    if not os.path.exists(model_path):
        return None, None, None

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(vec_path, "rb") as f:
        vectorizer = pickle.load(f)
    acc = None
    if os.path.exists(acc_path):
        with open(acc_path) as f:
            acc = float(f.read().strip())
    return model, vectorizer, acc


def predict(text: str, model, vectorizer):
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])
    label = model.predict(vec)[0]
    proba = model.predict_proba(vec)[0]
    return label, proba


# ────────────────────────────────────────────────────────────────────────────
# UI
# ────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
  <span class="hero-icon"> </span>
  <h1>Email Spam Detector</h1>
  <p>NAIVE BAYES · TF-IDF · SMS SPAM COLLECTION DATASET</p>
</div>
""", unsafe_allow_html=True)

model, vectorizer, accuracy = load_model()

if model is None:
    st.error(" Model not found. Run `python train_model.py` first to train and save the model.")
    st.stop()

# ── model info strip ─────────────────────────────────────────────────────────
acc_pct = f"{accuracy*100:.1f}%" if accuracy else "N/A"
st.markdown(f"""
<div style="display:flex; gap:.7rem; justify-content:center; margin-bottom:2rem; flex-wrap:wrap;">
  <div class="badge"> Model: Multinomial Naive Bayes</div>
  <div class="badge"> Features: TF-IDF bigrams</div>
  <div class="badge"> Test Accuracy: {acc_pct}</div>
</div>
""", unsafe_allow_html=True)

# ── example messages ─────────────────────────────────────────────────────────
EXAMPLES = {
    "Spam — Prize": "Congratulations! You've won a $1000 Walmart gift card. Click here now to claim your prize before it expires! http://free-prize.win",
    "Spam — Urgent": "URGENT: Your account will be suspended. Verify your details immediately at http://secure-login.xyz or lose access.",
    "Ham — Meeting": "Hi Sarah, just checking if you're free for the team meeting tomorrow at 3pm. Let me know!",
    "Ham — Casual": "Hey, are you coming to the party on Friday? I can pick you up if you need a ride.",
}

st.markdown('<p style="color:var(--muted); font-family:\'DM Mono\',monospace; font-size:.75rem; letter-spacing:.06em; margin-bottom:.5rem;">TRY AN EXAMPLE</p>', unsafe_allow_html=True)

cols = st.columns(len(EXAMPLES))
for col, (label, text) in zip(cols, EXAMPLES.items()):
    if col.button(label, key=label):
        st.session_state["email_input"] = text

# ── input ────────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)

email_text = st.text_area(
    "EMAIL / MESSAGE CONTENT",
    value=st.session_state.get("email_input", ""),
    height=180,
    placeholder="Paste or type an email message here…",
    key="email_input",
    label_visibility="visible",
)

check = st.button(" Analyse Message", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── result ───────────────────────────────────────────────────────────────────
if check:
    if not email_text.strip():
        st.warning("Please enter a message to analyse.")
    else:
        with st.spinner("Analysing…"):
            label, proba = predict(email_text, model, vectorizer)

        is_spam     = bool(label)
        spam_pct    = round(proba[1] * 100, 1)
        ham_pct     = round(proba[0] * 100, 1)
        conf        = spam_pct if is_spam else ham_pct
        css_class   = "result-spam" if is_spam else "result-ham"
        icon        = " " if is_spam else " "
        verdict     = "SPAM" if is_spam else "NOT SPAM"
        sub         = "This message looks suspicious." if is_spam else "This message appears legitimate."
        label_color = "#ff4c6a" if is_spam else "#00e5c0"
        fill_class  = "conf-fill-spam" if is_spam else "conf-fill-ham"
        bar_label   = "Spam probability" if is_spam else "Ham probability"
        bar_pct     = spam_pct if is_spam else ham_pct

        st.markdown(f"""
        <div class="{css_class}">
          <span class="result-icon">{icon}</span>
          <div class="result-label" style="color:{label_color}">{verdict}</div>
          <div class="result-sublabel" style="color:{label_color}88">{sub}</div>

          <div class="conf-wrap">
            <div class="conf-label">
              <span>{bar_label}</span>
              <span>{bar_pct}%</span>
            </div>
            <div class="conf-track">
              <div class="{fill_class}" style="width:{bar_pct}%"></div>
            </div>
          </div>

          <div class="badge-row">
            <div class="badge"> Spam score: {spam_pct}%</div>
            <div class="badge"> Ham score: {ham_pct}%</div>
            <div class="badge"> Confidence: {conf}%</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # word count debug strip
        word_count = len(email_text.split())
        char_count = len(email_text)
        st.markdown(f"""
        <div style="margin-top:1rem; text-align:center;">
          <span class="badge"> {word_count} words</span>
          <span class="badge"> {char_count} characters</span>
          <span class="badge"> Cleaned: {len(clean_text(email_text).split())} tokens</span>
        </div>
        """, unsafe_allow_html=True)

# ── footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem;
            border-top:1px solid var(--border); color:var(--muted);
            font-family:'DM Mono',monospace; font-size:.72rem; letter-spacing:.05em;">
  Trained on the UCI SMS Spam Collection dataset · 5,574 messages · Naive Bayes classifier
</div>
""", unsafe_allow_html=True)
