import streamlit as st
import requests
import os
import html
import re
import asyncio
import tempfile
from datetime import datetime

import edge_tts

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="KrishiMitra AI | Smart Farming Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "diagnosis" not in st.session_state:
    st.session_state.diagnosis = None

if "diagnosis_image" not in st.session_state:
    st.session_state.diagnosis_image = None

if "disease_guidance" not in st.session_state:
    st.session_state.disease_guidance = {}

if "disease_audio" not in st.session_state:
    st.session_state.disease_audio = {}

if "last_disease_input_id" not in st.session_state:
    st.session_state.last_disease_input_id = None

# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* GLOBAL */

.stApp {
    background: #f7faf8;
    color: #172b22;
}

.block-container {
    max-width: 1320px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

h1, h2, h3, h4 {
    color: #173c2a !important;
}

p {
    line-height: 1.7;
}

/* HEADER */

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
}

.brand-icon {
    font-size: 38px;
}

.brand-name {
    font-size: 28px;
    font-weight: 800;
    color: #166534;
    letter-spacing: -1px;
}

.brand-subtitle {
    font-size: 10px;
    letter-spacing: 2px;
    color: #64748b;
    font-weight: 700;
}

/* NAVIGATION */

div[data-testid="stButton"] button {
    border-radius: 12px;
    font-weight: 650;
    min-height: 43px;
    transition: 0.2s ease;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: #16a34a;
    color: white;
    border: 1px solid #16a34a;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #15803d;
    border-color: #15803d;
}

div[data-testid="stButton"] button[kind="secondary"] {
    background: white;
    color: #24523a;
    border: 1px solid #dbe8df;
}

div[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #16a34a;
    color: #166534;
}

/* HERO */

.hero {
    background:
        radial-gradient(
            circle at 90% 20%,
            rgba(134, 239, 172, 0.22),
            transparent 35%
        ),
        linear-gradient(
            125deg,
            #102f23 0%,
            #166534 58%,
            #15803d 100%
        );

    border-radius: 26px;
    padding: 65px 58px;
    color: white;
    margin-top: 30px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.22);
    color: #dcfce7;
    padding: 10px 18px;
    border-radius: 50px;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 1px;
    margin-bottom: 25px;
}

.hero-title {
    font-size: clamp(36px, 5vw, 64px);
    font-weight: 850;
    line-height: 1.13;
    letter-spacing: -2px;
    color: white;
    margin-bottom: 22px;
}

.hero-title span {
    color: #bbf7d0;
}

.hero-description {
    font-size: 17px;
    line-height: 1.9;
    color: #e2f5e8;
    max-width: 700px;
}

.hero-note {
    margin-top: 32px;
    color: #d1fae5;
    font-size: 13px;
}

/* SECTION HEADINGS */

.section-label {
    color: #16a34a;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.section-title {
    color: #173c2a;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 12px;
}

.section-description {
    color: #64748b;
    font-size: 16px;
    margin-bottom: 25px;
}

/* FEATURE CARDS */

.feature-card {
    background: white;
    border: 1px solid #e3ebe5;
    border-radius: 20px;
    padding: 30px;
    min-height: 245px;
    box-shadow: 0 8px 28px rgba(15, 45, 30, 0.035);
}

.feature-icon {
    font-size: 38px;
    margin-bottom: 18px;
}

.feature-title {
    font-size: 20px;
    font-weight: 800;
    color: #173c2a;
    margin-bottom: 12px;
}

.feature-description {
    font-size: 14px;
    color: #64748b;
    line-height: 1.8;
}

/* INFORMATION CARDS */

.info-card {
    background: white;
    border: 1px solid #e2ebe5;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 18px;
}

.info-label {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    margin-bottom: 10px;
}

.info-value {
    font-size: 29px;
    font-weight: 800;
    color: #166534;
    overflow-wrap: anywhere;
}

.info-value.warning {
    color: #b45309;
}

.info-value.danger {
    color: #b91c1c;
}

/* TREATMENT CARDS */

.treatment-card {
    background: white;
    border-radius: 18px;
    padding: 24px;
    margin: 15px 0;
    border: 1px solid #e2e8f0;
}

.treatment-card.organic {
    border-left: 5px solid #16a34a;
}

.treatment-card.chemical {
    border-left: 5px solid #eab308;
}

.treatment-card.prevention {
    border-left: 5px solid #3b82f6;
}

.treatment-title {
    font-size: 19px;
    font-weight: 800;
    color: #173c2a;
    margin-bottom: 12px;
}

.treatment-text {
    font-size: 15px;
    color: #334155;
    line-height: 1.9;
}

/* STEPS */

.step-card {
    background: white;
    border: 1px solid #e2ebe5;
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    min-height: 160px;
}

.step-number {
    font-size: 12px;
    font-weight: 800;
    color: #15803d;
    letter-spacing: 1px;
}

.step-icon {
    font-size: 34px;
    margin: 14px 0;
}

.step-title {
    font-size: 17px;
    font-weight: 750;
    color: #173c2a;
}

/* STATUS */

.status-box {
    border-radius: 14px;
    padding: 15px 20px;
    margin: 20px 0;
    font-size: 14px;
    font-weight: 650;
}

.status-online {
    background: #dcfce7;
    color: #166534;
    border: 1px solid #bbf7d0;
}

.status-offline {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

/* ALERTS */

div[data-testid="stAlert"] {
    border-radius: 14px;
}

div[data-testid="stAlert"] p {
    color: #172b22 !important;
    font-weight: 550;
}

/* METRICS */

div[data-testid="stMetricValue"] {
    color: #166534 !important;
}

div[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

/* CHAT */

.chat-wrapper {
    background: white;
    border: 1px solid #e2ebe5;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
}

.chat-message {
    padding: 16px 20px;
    border-radius: 16px;
    margin-bottom: 14px;
    line-height: 1.8;
    overflow-wrap: anywhere;
}

.chat-user {
    background: #dcfce7;
    color: #14532d;
    margin-left: 12%;
}

.chat-assistant {
    background: #f1f5f9;
    color: #1e293b;
    margin-right: 12%;
}

.chat-role {
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 7px;
}

/* FOOTER */

.site-footer {
    background: linear-gradient(
        125deg,
        #102f23,
        #166534
    );
    color: white;
    padding: 40px;
    border-radius: 22px;
    margin-top: 55px;
    text-align: center;
}

.footer-title {
    font-size: 26px;
    font-weight: 800;
    color: white;
    margin-bottom: 15px;
}

.footer-text {
    font-size: 14px;
    color: #dcfce7;
    line-height: 2;
}

/* INPUTS — force legible controls in light and dark Streamlit themes */

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextArea"] textarea:hover,
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input:focus {
    background-color: #ffffff !important;
    color: #172b22 !important;
    -webkit-text-fill-color: #172b22 !important;
    caret-color: #172b22 !important;
    opacity: 1 !important;
    border-radius: 12px !important;
}
div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}
div[data-testid="stTextArea"] [data-baseweb="textarea"],
div[data-testid="stTextInput"] [data-baseweb="input"] {
    background-color: #ffffff !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #172b22 !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #172b22 !important;
}

/* INPUTS */

textarea,
input {
    border-radius: 12px !important;
}

div[data-testid="stFileUploader"] {
    border-radius: 16px;
}

/* DIVIDERS */

hr {
    border-color: #e2e8f0;
    margin: 28px 0;
}

/* MOBILE */

@media (max-width: 768px) {

    .hero {
        padding: 35px 25px;
    }

    .hero-title {
        font-size: 36px;
        letter-spacing: -1px;
    }

    .hero-description {
        font-size: 14px;
    }

    .section-title {
        font-size: 26px;
    }

    .feature-card {
        min-height: auto;
    }

    .brand-name {
        font-size: 22px;
    }

    .site-footer {
        padding: 30px 20px;
    }
}

</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# HTML COMPONENTS
# ============================================================

# Keep HTML at the start of each line to prevent Streamlit
# from interpreting indented HTML as a code block.


def feature_card(icon, title, description):
    return (
        '<div class="feature-card">'
        f'<div class="feature-icon">{icon}</div>'
        f'<div class="feature-title">{html.escape(title)}</div>'
        f'<div class="feature-description">{html.escape(description)}</div>'
        '</div>'
    )


def info_card(label, value, style=""):
    return (
        '<div class="info-card">'
        f'<div class="info-label">{html.escape(str(label))}</div>'
        f'<div class="info-value {style}">'
        f'{html.escape(str(value))}'
        '</div>'
        '</div>'
    )


def treatment_card(title, text, kind, icon):
    return (
        f'<div class="treatment-card {kind}">'
        f'<div class="treatment-title">{icon} '
        f'{html.escape(title)}</div>'
        f'<div class="treatment-text">'
        f'{html.escape(str(text))}'
        '</div>'
        '</div>'
    )


def step_card(number, icon, title):
    return (
        '<div class="step-card">'
        f'<div class="step-number">STEP {number}</div>'
        f'<div class="step-icon">{icon}</div>'
        f'<div class="step-title">{html.escape(title)}</div>'
        '</div>'
    )


def render(component):
    st.markdown(component, unsafe_allow_html=True)


# ============================================================
# ASSISTANT RESPONSE FORMATTER
# ============================================================

def format_assistant_response(text):
    """Render simple Markdown-like OpenRouter responses as safe HTML.

    Supported:
    - **bold**
    - bullet lists beginning with - or •
    - numbered lists
    - # / ## / ### headings
    - paragraph spacing
    """
    if not text:
        return ""

    # Escape model output first so arbitrary HTML cannot be injected.
    value = html.escape(str(text))
    value = value.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize common model-generated numbered section headings.
    value = re.sub(r"(?mi)^\s*1[.)]\s*(what the result means|result meaning)\s*:?[ \t]*$", r"**What the result means**", value)
    value = re.sub(r"(?mi)^\s*2[.)]\s*(symptoms to check|common symptoms)\s*:?[ \t]*$", r"**Symptoms to check**", value)
    value = re.sub(r"(?mi)^\s*3[.)]\s*(possible causes|causes)\s*:?[ \t]*$", r"**Possible causes**", value)
    value = re.sub(r"(?mi)^\s*4[.)]\s*(what you can do now|what the farmer can do now|management)\s*:?[ \t]*$", r"**What you can do now**", value)
    value = re.sub(r"(?mi)^\s*5[.)]\s*(prevention(?: for)?)\s*:?[ \t]*$", r"**Prevention**", value)

    # Markdown headings.
    value = re.sub(
        r"(?m)^###\s+(.+)$",
        r'<div style="font-size:18px;font-weight:800;color:#173c2a;margin:16px 0 8px;">\1</div>',
        value,
    )
    value = re.sub(
        r"(?m)^##\s+(.+)$",
        r'<div style="font-size:20px;font-weight:800;color:#173c2a;margin:18px 0 9px;">\1</div>',
        value,
    )
    value = re.sub(
        r"(?m)^#\s+(.+)$",
        r'<div style="font-size:22px;font-weight:850;color:#173c2a;margin:20px 0 10px;">\1</div>',
        value,
    )

    # Bold text, e.g. **Leaves:**
    value = re.sub(
        r"\*\*(.+?)\*\*",
        r"<strong>\1</strong>",
        value,
    )

    # Numbered list items.
    value = re.sub(
        r"(?m)^\s*(\d+)\.\s+(.+)$",
        r'<div style="margin:8px 0 8px 10px;line-height:1.8;"><span style="color:#16a34a;font-weight:800;">\1.</span> \2</div>',
        value,
    )

    # Bullet list items.
    value = re.sub(
        r"(?m)^\s*[-•]\s+(.+)$",
        r'<div style="margin:8px 0 8px 10px;line-height:1.8;"><span style="color:#16a34a;font-weight:900;">•</span> \1</div>',
        value,
    )

    # Paragraph gaps and remaining line breaks.
    value = re.sub(
        r"\n\s*\n",
        '<div style="height:10px;"></div>',
        value,
    )
    value = value.replace("\n", "<br>")

    return value


# ============================================================
# BACKEND CONNECTION
# ============================================================

@st.cache_data(ttl=15)
def check_backend():
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


@st.cache_data(ttl=60)
def fetch_supported_classes():
    """Read the actual trained classes from FastAPI, not a hardcoded list."""
    try:
        response = requests.get(f"{API_URL}/disease/classes", timeout=8)
        response.raise_for_status()
        payload = response.json()
        labels = payload.get("classes", [])
        if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
            return []
        return labels
    except (requests.RequestException, ValueError, TypeError):
        return []


def api_error_message(response):
    """Extract a safe, useful FastAPI error message."""
    try:
        detail = response.json().get("detail", "")
        if isinstance(detail, str) and detail:
            return detail
        if isinstance(detail, list):
            return "; ".join(str(x.get("msg", x)) if isinstance(x, dict) else str(x) for x in detail)
    except (ValueError, TypeError, AttributeError):
        pass
    return f"Server returned HTTP {response.status_code}."


def request_error_message(exc):
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return api_error_message(exc.response)
    if isinstance(exc, requests.Timeout):
        return "The request timed out. Please try again."
    if isinstance(exc, requests.ConnectionError):
        return "Cannot reach FastAPI. Check that the backend is running on port 8000."
    return str(exc)


backend_online = check_backend()


# ============================================================
# NAVIGATION
# ============================================================

def navigate(page):
    st.session_state.page = page
    st.rerun()


header_left, header_right = st.columns(
    [1.1, 2.1],
    vertical_alignment="center"
)

with header_left:
    render(
        '<div class="brand">'
        '<div class="brand-icon">🌱</div>'
        '<div>'
        '<div class="brand-name">KrishiMitra AI</div>'
        '<div class="brand-subtitle">'
        'SMART FARMING ASSISTANT'
        '</div>'
        '</div>'
        '</div>'
    )

with header_right:

    nav_cols = st.columns(4)

    pages = [
        "Home",
        "Disease Detection",
        "Farmer Assistant",
        "About"
    ]

    for col, page in zip(nav_cols, pages):
        with col:
            if st.button(
                page,
                key=f"nav_{page}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.page == page
                    else "secondary"
                )
            ):
                navigate(page)


st.divider()


# ============================================================
# HOMEPAGE
# ============================================================

def show_home():

    render(
        '<div class="hero">'
        '<div class="hero-badge">'
        '🌟 AI-POWERED AGRICULTURAL TECHNOLOGY'
        '</div>'
        '<div class="hero-title">'
        'Smarter Farming.<br>'
        '<span>Healthier Crops.</span><br>'
        'Better Tomorrow.'
        '</div>'
        '<div class="hero-description">'
        'Your intelligent farming companion. '
        'Detect possible crop diseases using artificial '
        'intelligence, explore agricultural guidance, '
        'and make informed decisions to protect your harvest.'
        '</div>'
        '<div class="hero-note">'
        '🌾 Built with Indian agriculture in mind '
        '• Initial focus: Rajasthan'
        '</div>'
        '</div>'
    )

    button_left, button_right, spacer = st.columns(
        [1, 1, 1.3]
    )

    with button_left:
        if st.button(
            "🌿 Detect Crop Disease →",
            use_container_width=True,
            type="primary",
            key="home_detect"
        ):
            navigate("Disease Detection")

    with button_right:
        if st.button(
            "💬 Ask Farmer Assistant →",
            use_container_width=True,
            key="home_assistant"
        ):
            navigate("Farmer Assistant")

    st.write("")
    st.write("")

    render(
        '<div class="section-label">OUR FEATURES</div>'
        '<div class="section-title">'
        'Technology for Better Farming'
        '</div>'
        '<div class="section-description">'
        'Explore intelligent tools designed to support '
        'farmers with crop health and agricultural guidance.'
        '</div>'
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        render(
            feature_card(
                "🔬",
                "AI Disease Detection",
                "Upload or capture a crop leaf photograph to receive "
                "a possible disease classification, model "
                "confidence, bilingual guidance, and voice output."
            )
        )

    with c2:
        render(
            feature_card(
                "👨‍🌾",
                "Farmer Assistant",
                "Ask farming questions in English or Hindi "
                "and receive AI-powered agricultural guidance "
                "with a local FAQ fallback."
            )
        )

    with c3:
        render(
            feature_card(
                "🌿",
                "Crop Care Guidance",
                "Explore prevention tips and responsible "
                "crop management recommendations."
            )
        )

    st.write("")
    st.write("")

    render(
        '<div class="section-label">HOW IT WORKS</div>'
        '<div class="section-title">'
        'Crop Health Analysis in Three Steps'
        '</div>'
        '<div class="section-description">'
        'A simple workflow for understanding possible '
        'crop leaf diseases.'
        '</div>'
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        render(
            step_card(
                "01",
                "📷",
                "Upload or Capture a Leaf Photo"
            )
        )

    with s2:
        render(
            step_card(
                "02",
                "🧠",
                "AI Analyzes the Image"
            )
        )

    with s3:
        render(
            step_card(
                "03",
                "🌱",
                "Review Crop Guidance"
            )
        )

    if backend_online:
        render(
            '<div class="status-box status-online">'
            '🟢 AI Backend Connected Successfully'
            '</div>'
        )
    else:
        render(
            '<div class="status-box status-offline">'
            '🔴 Backend Offline — Start the FastAPI server.'
            '</div>'
        )


# ============================================================
# TEXT CLEANING FOR VOICE OUTPUT
# ============================================================

def clean_text_for_speech(text):
    """Remove Markdown/HTML formatting so TTS reads natural sentences."""
    if not text:
        return ""

    value = str(text)

    # Remove HTML tags if any were introduced by formatting.
    value = re.sub(r"<[^>]+>", " ", value)

    # Markdown headings: ### Heading -> Heading.
    value = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", value)

    # Bold / italic markers.
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"__(.*?)__", r"\1", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", value)
    value = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", value)

    # Bullets and numbered list prefixes.
    value = re.sub(r"(?m)^\s*[-•*]\s+", "", value)
    value = re.sub(r"(?m)^\s*\d+[.)]\s+", "", value)

    # Links: [label](url) -> label.
    value = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", value)

    # Backticks and leftover markdown punctuation.
    value = value.replace("`", "")
    value = value.replace("*", "")

    # Make section breaks audible but natural.
    value = re.sub(r"\n\s*\n+", ". ", value)
    value = re.sub(r"\n+", ". ", value)
    value = re.sub(r"\s+", " ", value)

    # Avoid repeated punctuation.
    value = re.sub(r"\.{2,}", ".", value)
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)

    return value.strip()


# ============================================================
# TEXT TO SPEECH
# ============================================================

async def _generate_tts_audio(text, language):
    """Generate Hindi/English speech audio with Edge TTS."""
    voice = "hi-IN-MadhurNeural" if language == "hi" else "en-IN-PrabhatNeural"

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    audio_path = temp_file.name
    temp_file.close()

    speech_text = clean_text_for_speech(text)

    communicate = edge_tts.Communicate(
        text=speech_text,
        voice=voice
    )
    await communicate.save(audio_path)
    return audio_path


def generate_tts_audio(text, language):
    """Synchronous wrapper suitable for Streamlit callbacks."""
    try:
        return asyncio.run(_generate_tts_audio(text, language))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                _generate_tts_audio(text, language)
            )
        finally:
            loop.close()


# ============================================================
# DISEASE DETECTION
# ============================================================

def show_disease_detection():

    render(
        '<div class="section-label">'
        'AI CROP HEALTH ANALYSIS'
        '</div>'
        '<div class="section-title">'
        '🔬 Crop Disease Detection'
        '</div>'
        '<div class="section-description">'
        'Upload or capture a clear crop leaf image to receive '
        'an AI-assisted disease screening report.'
        '</div>'
    )

    if not backend_online:
        st.error(
            "Backend is offline. Start FastAPI before "
            "analyzing an image."
        )

    if backend_online:
        supported_labels = fetch_supported_classes()
        if supported_labels:
            supported_crops = sorted({
                label.split("___", 1)[0].replace("_", " ")
                for label in supported_labels
            })
            with st.expander(
                f"🌾 Supported crops ({len(supported_crops)}) and model classes ({len(supported_labels)})"
            ):
                st.write(", ".join(supported_crops))
                st.caption("Only these trained classes are supported; other crops or conditions may be misclassified.")
        else:
            st.caption("Supported class list is temporarily unavailable.")

    left, right = st.columns(
        [1, 1.15],
        gap="large"
    )

    with left:

        st.subheader("📷 Select Leaf Image")

        image_source = st.selectbox(
            "Choose image source",
            ["📁 Upload Image", "📷 Take Photo"],
            key="disease_image_source"
        )

        leaf_file = None

        if image_source == "📁 Upload Image":
            leaf_file = st.file_uploader(
                "Choose a crop leaf photograph",
                type=["jpg", "jpeg", "png", "webp"],
                help="Use a clear photograph of a single leaf.",
                key="leaf_upload"
            )
        else:
            leaf_file = st.camera_input(
                "Take a clear photo of the affected leaf",
                key="leaf_camera"
            )

        if leaf_file is not None:
            file_bytes = leaf_file.getvalue()
            current_input_id = (
                getattr(leaf_file, "name", "camera_leaf.jpg"),
                len(file_bytes),
                file_bytes[:64]
            )

            if st.session_state.last_disease_input_id != current_input_id:
                st.session_state.diagnosis = None
                st.session_state.disease_guidance = {}
                st.session_state.disease_audio = {}
                st.session_state.last_disease_input_id = current_input_id

            st.image(
                leaf_file,
                caption=(
                    "Captured crop leaf"
                    if image_source == "📷 Take Photo"
                    else "Uploaded crop leaf"
                ),
                use_container_width=True
            )

        if st.button(
            "🌿 Analyze Crop Disease",
            type="primary",
            use_container_width=True,
            disabled=(leaf_file is None or not backend_online),
            key="analyze_button"
        ):
            try:
                with st.spinner("Analyzing the crop leaf..."):
                    file_bytes = leaf_file.getvalue()
                    filename = getattr(leaf_file, "name", "camera_leaf.jpg")
                    mime_type = getattr(leaf_file, "type", "image/jpeg") or "image/jpeg"

                    response = requests.post(
                        f"{API_URL}/disease/predict",
                        files={
                            "file": (filename, file_bytes, mime_type)
                        },
                        timeout=120
                    )
                    response.raise_for_status()
                    result = response.json()

                    st.session_state.diagnosis = result
                    st.session_state.diagnosis_image = filename
                    st.session_state.disease_guidance = {}
                    st.session_state.disease_audio = {}

            except requests.RequestException as exc:
                st.error(
                    f"Disease analysis failed: {request_error_message(exc)}"
                )

        st.info(
            "For better results, photograph the leaf "
            "in natural light and avoid blurry images."
        )

    with right:

        st.subheader("🧪 AI Diagnosis Report")

        result = st.session_state.diagnosis

        if result is None:

            st.info(
                "Upload or capture a leaf image and click "
                "'Analyze Crop Disease' to see results."
            )

        else:

            status = str(
                result.get("status", "")
            ).lower()

            crop = result.get(
                "crop",
                "Unknown"
            )

            disease = result.get(
                "disease",
                "Unknown"
            )

            confidence = result.get(
                "confidence",
                0
            )

            healthy = result.get(
                "healthy",
                False
            )

            # Backend currently returns confidence
            # as a percentage from 0 to 100.
            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = 0.0

            confidence = max(
                0.0,
                min(confidence, 100.0)
            )

            if status == "uncertain":
                st.warning("Analysis completed, but the result is uncertain.")
            else:
                st.success("Analysis completed successfully!")

            st.markdown("### 🌿 Crop Information")

            c1, c2 = st.columns(2)

            with c1:
                render(
                    info_card(
                        "Detected Crop",
                        crop
                    )
                )

            with c2:

                condition = (
                    "Uncertain"
                    if status == "uncertain"
                    else ("Healthy" if healthy else "Possible Disease")
                )

                render(
                    info_card(
                        "Crop Condition",
                        condition
                    )
                )

            st.markdown("### 🔬 Detection Result")

            if status == "uncertain":

                st.warning(
                    "The model is uncertain about this "
                    "image. The predicted class is not a reliable "
                    "diagnosis. Try a clearer photograph and "
                    "consult a local agricultural expert."
                )

            elif healthy:

                st.success(
                    "The model predicts that the "
                    "crop leaf is healthy."
                )

            else:

                st.warning(
                    f"Possible Disease: {disease}"
                )

            st.markdown("### 📊 Model Confidence")

            st.metric(
                "Prediction Confidence",
                f"{confidence:.2f}%"
            )

            st.progress(
                confidence / 100
            )

            st.caption(
                "This percentage represents model "
                "confidence, not a confirmed diagnosis."
            )

            organic = result.get(
                "organic_treatment",
                ""
            )

            chemical = result.get(
                "chemical_treatment",
                ""
            )

            prevention = result.get(
                "prevention",
                ""
            )

            if organic:
                render(
                    treatment_card(
                        "Organic Management",
                        organic,
                        "organic",
                        "🌱"
                    )
                )

            if chemical:
                render(
                    treatment_card(
                        "Chemical Management",
                        chemical,
                        "chemical",
                        "🧪"
                    )
                )

            if prevention:
                render(
                    treatment_card(
                        "Prevention Tips",
                        prevention,
                        "prevention",
                        "🛡️"
                    )
                )

            st.markdown("### 🌐 AI Disease Guidance")

            guidance_language = st.selectbox(
                "Select guidance language",
                ["English", "हिंदी"],
                key="disease_guidance_language"
            )

            guidance_language_code = (
                "hi" if guidance_language == "हिंदी" else "en"
            )

            guidance_key = (
                f"{crop}|{disease}|{confidence:.2f}|{guidance_language_code}"
            )

            guidance_text = st.session_state.disease_guidance.get(guidance_key)

            if not guidance_text:
                button_text = (
                    "🌱 Get Hindi Disease Guidance"
                    if guidance_language_code == "hi"
                    else "🌱 Get English Disease Guidance"
                )

                if st.button(
                    button_text,
                    type="primary",
                    use_container_width=True,
                    key=f"generate_disease_guidance_{guidance_language_code}"
                ):
                    if guidance_language_code == "hi":
                        prompt = f"""
KrishiMitra AI के Crop Disease Detection CNN ने निम्न परिणाम दिया है:

फसल: {crop}
संभावित रोग: {disease}
मॉडल विश्वास स्तर: {confidence:.2f}%
मॉडल स्थिति: {status or 'normal'}

किसान के लिए सरल हिंदी में जानकारी दें।

ठीक इसी संरचना में उत्तर दें और शीर्षकों के आगे 1, 2, 3, 4, 5 न लिखें:

**परिणाम का अर्थ**
एक छोटा स्पष्ट अनुच्छेद।

**लक्षण देखें**
- बिंदुवार लक्षण

**संभावित कारण**
- बिंदुवार कारण

**अभी क्या करें**
- बिंदुवार सुरक्षित उपाय

**रोकथाम**
- बिंदुवार रोकथाम

CNN prediction को निश्चित diagnosis न बताएं।
यदि prediction uncertain है तो यह भी स्पष्ट करें।
"""
                    else:
                        prompt = f"""
KrishiMitra AI's Crop Disease Detection CNN produced the following result:

Crop: {crop}
Possible disease: {disease}
Model confidence: {confidence:.2f}%
Model status: {status or 'normal'}

Explain this result to a farmer in simple English.

Use exactly this structure. Do not number the section headings:

**What the result means**
One short, clear paragraph.

**Symptoms to check**
- Bullet points

**Possible causes**
- Bullet points

**What you can do now**
- Safe, practical bullet points

**Prevention**
- Prevention bullet points

Do not present the CNN prediction as a confirmed diagnosis.
If the prediction is uncertain, make that clear.
"""

                    try:
                        with st.spinner("Generating agricultural guidance..."):
                            assistant_response = requests.post(
                                f"{API_URL}/assistant/ask",
                                json={
                                    "question": prompt,
                                    "language": guidance_language_code
                                },
                                timeout=60
                            )
                            assistant_response.raise_for_status()
                            assistant_data = assistant_response.json()
                            guidance_text = str(
                                assistant_data.get("answer", "")
                            ).strip()

                            if guidance_text:
                                st.session_state.disease_guidance[guidance_key] = guidance_text
                                st.rerun()
                            else:
                                st.warning("No disease guidance was returned.")

                    except requests.RequestException as exc:
                        st.error(
                            "Could not generate disease guidance: "
                            f"{request_error_message(exc)}"
                        )

            guidance_text = st.session_state.disease_guidance.get(guidance_key)

            if guidance_text:
                st.markdown(
                    "### 📝 रोग की जानकारी"
                    if guidance_language_code == "hi"
                    else "### 📝 Disease Information"
                )
                render(format_assistant_response(guidance_text))

                st.markdown(
                    "### 🔊 जानकारी सुनें"
                    if guidance_language_code == "hi"
                    else "### 🔊 Listen to Guidance"
                )

                audio_path = st.session_state.disease_audio.get(guidance_key)

                if not audio_path:
                    if st.button(
                        "🔊 हिंदी में सुनें"
                        if guidance_language_code == "hi"
                        else "🔊 Listen in English",
                        key=f"generate_disease_audio_{guidance_language_code}"
                    ):
                        try:
                            with st.spinner(
                                "आवाज़ तैयार की जा रही है..."
                                if guidance_language_code == "hi"
                                else "Preparing voice..."
                            ):
                                audio_path = generate_tts_audio(
                                    guidance_text,
                                    guidance_language_code
                                )
                                st.session_state.disease_audio[guidance_key] = audio_path
                                st.rerun()
                        except Exception as exc:
                            st.error(f"Voice generation failed: {exc}")

                audio_path = st.session_state.disease_audio.get(guidance_key)
                if audio_path and os.path.exists(audio_path):
                    st.audio(audio_path, format="audio/mp3")

            top_predictions = result.get(
                "top_predictions",
                []
            )

            if top_predictions:

                with st.expander(
                    "View Other Model Predictions"
                ):

                    for item in top_predictions:

                        label = item.get(
                            "label",
                            "Unknown"
                        )

                        score = item.get(
                            "confidence",
                            0
                        )

                        st.write(
                            f"**{label}** — {score}%"
                        )

            st.warning(
                "AI screening is not a substitute "
                "for laboratory diagnosis or advice "
                "from a qualified agricultural expert. "
                "Use only locally registered crop "
                "protection products according to "
                "their labels."
            )


# ============================================================
# FARMER ASSISTANT
# ============================================================

def set_example_question(question):
    """Streamlit callback executes before text_area is instantiated."""
    st.session_state.farmer_question = question


def show_farmer_assistant():

    render(
        '<div class="section-label">'
        'AGRICULTURAL KNOWLEDGE ASSISTANT'
        '</div>'
        '<div class="section-title">'
        '👨‍🌾 Farmer Assistant'
        '</div>'
        '<div class="section-description">'
        'Ask questions about crop health, irrigation, '
        'soil management, and farming practices.'
        '</div>'
    )

    if backend_online:
        render(
            '<div class="status-box status-online">'
            '🟢 Agricultural Assistant Connected'
            '</div>'
        )
    else:
        render(
            '<div class="status-box status-offline">'
            '🔴 Backend Offline'
            '</div>'
        )

    left, right = st.columns(
        [1.6, 1],
        gap="large"
    )

    with left:

        language = st.selectbox(
            "Select Language",
            ["English", "Hindi"],
            key="assistant_language"
        )

        language_code = (
            "hi"
            if language == "Hindi"
            else "en"
        )

        st.markdown("### 💬 Ask Your Question")

        question = st.text_area(
            "Describe your farming problem",
            placeholder=(
                "Example: My tomato leaves are "
                "turning yellow. What should I do?"
            ),
            height=130,
            key="farmer_question"
        )

        if st.button(
            "🌱 Get Agricultural Guidance",
            type="primary",
            use_container_width=True,
            disabled=not backend_online,
            key="ask_button"
        ):

            if not question.strip():

                st.warning(
                    "Please enter your farming question."
                )

            else:

                try:

                    with st.spinner(
                        "Finding agricultural guidance..."
                    ):

                        response = requests.post(
                            f"{API_URL}/assistant/ask",
                            json={
                                "question": question.strip(),
                                "language": language_code
                            },
                            timeout=60
                        )

                        response.raise_for_status()

                        data = response.json()

                        answer = data.get(
                            "answer",
                            ""
                        )

                        if not answer:

                            answer = (
                                "No guidance was returned. "
                                "Please try another question."
                            )

                        st.session_state.chat_history.append(
                            {
                                "role": "user",
                                "content": question.strip()
                            }
                        )

                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                except requests.RequestException as exc:

                    st.error(
                        f"Assistant request failed: {request_error_message(exc)}"
                    )

        st.markdown("### 💬 Conversation")

        if not st.session_state.chat_history:

            st.info(
                "Your conversation will appear here."
            )

        else:

            for message in st.session_state.chat_history:

                role = message["role"]
                raw_content = str(message["content"])

                if role == "user":

                    # User messages remain fully escaped.
                    content = html.escape(raw_content).replace("\n", "<br>")

                    render(
                        '<div class="chat-message chat-user">'
                        '<div class="chat-role">'
                        '👤 You'
                        '</div>'
                        f'{content}'
                        '</div>'
                    )

                else:

                    # Convert the assistant's simple Markdown-style response
                    # into safe, readable HTML.
                    content = format_assistant_response(raw_content)

                    render(
                        '<div class="chat-message chat-assistant">'
                        '<div class="chat-role">'
                        '🌱 KrishiMitra Assistant'
                        '</div>'
                        f'{content}'
                        '</div>'
                    )

            if st.button(
                "🗑️ Clear Conversation",
                key="clear_chat"
            ):

                st.session_state.chat_history = []
                st.rerun()

    with right:

        st.markdown("### 💡 Example Farming Questions")

        examples = [
            "Why are my tomato leaves turning yellow?",
            "How should I irrigate wheat?",
            "What are the symptoms of late blight?",
            "How can I prevent fungal diseases?",
            "How can I improve soil health?"
        ]

        for index, example in enumerate(examples):

            st.button(
                f"🌿 {example}",
                key=f"example_{index}",
                use_container_width=True,
                on_click=set_example_question,
                args=(example,),
            )

        st.write("")

        st.markdown("### 🌾 Farming Tips")

        st.markdown(
            """
            - ✅ Monitor crops regularly.
            - ✅ Use healthy planting material.
            - ✅ Avoid unnecessary pesticide use.
            - ✅ Follow local agricultural advisories.
            - ✅ Seek expert advice for severe symptoms.
            """
        )

        st.info(
            "The assistant uses an OpenRouter-powered agricultural AI "
            "with a local FAQ fallback. Important treatment decisions "
            "should still be verified with a qualified local expert."
        )


# ============================================================
# ABOUT PAGE
# ============================================================

def show_about():

    render(
        '<div class="section-label">'
        'ABOUT THE PROJECT'
        '</div>'
        '<div class="section-title">'
        '🌱 About KrishiMitra AI'
        '</div>'
        '<div class="section-description">'
        'An AI-powered agricultural assistance platform '
        'focused on crop health and accessible farming guidance.'
        '</div>'
    )

    st.markdown("### 🎯 Our Mission")

    st.write(
        "KrishiMitra AI aims to make agricultural "
        "technology more accessible to farmers through "
        "AI-assisted crop disease screening and "
        "easy-to-understand agricultural information."
    )

    st.markdown("### 🧠 Technology Stack")

    c1, c2, c3 = st.columns(3)

    with c1:
        render(
            feature_card(
                "🧠",
                "Machine Learning",
                "TensorFlow-based image classification "
                "for crop disease screening."
            )
        )

    with c2:
        render(
            feature_card(
                "⚡",
                "FastAPI Backend",
                "Python API for disease prediction "
                "and agricultural question answering."
            )
        )

    with c3:
        render(
            feature_card(
                "🌐",
                "Streamlit Frontend",
                "Interactive web interface for "
                "farmers and agricultural users."
            )
        )

    st.write("")

    st.markdown("### 🌍 Project Focus")

    st.write(
        "The initial focus is on agricultural use cases "
        "relevant to Rajasthan, India. "
        "Future development may include additional "
        "crops, stronger field validation, multilingual support, "
        "and a larger verified agricultural knowledge base."
    )

    st.markdown("### ⚠️ Important Disclaimer")

    st.warning(
        "KrishiMitra AI provides informational assistance. "
        "Its predictions and recommendations should not "
        "replace qualified agricultural advice."
    )


# ============================================================
# FOOTER
# ============================================================

def show_footer():

    render(
        '<div class="site-footer">'
        '<div class="footer-title">'
        '🌱 KrishiMitra AI'
        '</div>'
        '<div class="footer-text">'
        'Empowering Indian Agriculture Through '
        'Artificial Intelligence'
        '<br><br>'
        'Smart Farming • Crop Disease Detection • '
        'Agricultural Guidance'
        '<br><br>'
        '© 2026 KrishiMitra AI'
        '</div>'
        '</div>'
    )


# ============================================================
# PAGE ROUTER
# ============================================================

page = st.session_state.page

if page == "Home":

    show_home()

elif page == "Disease Detection":

    show_disease_detection()

elif page == "Farmer Assistant":

    show_farmer_assistant()

elif page == "About":

    show_about()

show_footer()