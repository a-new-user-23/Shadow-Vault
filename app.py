import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
from datetime import datetime

# --- CONFIGURATION & LUXURY UI STYLING ---
st.set_page_config(
    page_title="Shadow-Vault",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    /* 1. THE FOUNDATION: MATTE BLACK & MONOCHROME */
    :root {
        --bg-black: #0A0A0A;
        --card-gray: #141414;
        --accent-gold: #D4AF37;
        --text-off-white: #E5E5E5;
        --border-dim: #262626;
    }

    /* Hide Streamlit Header & Integrate Top Bar */
    header[data-testid="stHeader"] {
        background-color: var(--bg-black) !important;
        border-bottom: 1px solid var(--border-dim);
    }
    
    .stApp {
        background-color: var(--bg-black);
        color: var(--text-off-white);
    }

    /* 2. SIDEBAR: ALIGNED & ULTRA-CLEAN */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid var(--border-dim);
    }
    
    /* Pushes sidebar content down to match main page heading level */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 4.5rem !important;
    }

    /* Minimalist Sidebar Buttons */
    section[data-testid="stSidebar"] .stButton>button {
        background: transparent !important;
        color: #737373 !important;
        border: none !important;
        border-radius: 0px;
        border-left: 2px solid transparent !important;
        text-align: left;
        padding-left: 1rem;
        transition: 0.2s;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.75rem;
    }

    section[data-testid="stSidebar"] .stButton>button:hover {
        color: var(--accent-gold) !important;
        border-left: 2px solid var(--accent-gold) !important;
    }

    /* 3. HERO SECTION: TYPOGRAPHY FOCUS */
    .hero-container {
        padding: 8rem 0rem 4rem 0rem;
        text-align: center;
        border-bottom: 1px solid var(--border-dim);
        margin-bottom: 4rem;
    }

    .main-title {
        font-size: 4.5rem !important;
        font-weight: 300 !important; /* Elegant thin weight */
        letter-spacing: 20px !important;
        color: var(--text-off-white) !important;
        text-transform: uppercase;
        margin: 0 !important;
    }

    .sub-title {
        color: #525252 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 6px;
        margin-top: 1.5rem !important;
    }

    /* 4. FEATURE CARDS: SHARP & STRUCTURED */
    .feature-card {
        background: var(--card-gray);
        padding: 3rem;
        border: 1px solid var(--border-dim);
        border-radius: 0px; /* Sharp corners */
        text-align: left;
        min-height: 320px;
        transition: 0.3s;
    }

    .feature-card:hover {
        border-color: var(--accent-gold);
    }

    .card-icon {
        color: var(--accent-gold);
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    /* 5. MAIN BUTTONS: HIGH CONTRAST */
    .stButton>button {
        width: 100%;
        border-radius: 0px; /* Sharp edges */
        height: 3.5em;
        font-weight: 500;
        background-color: var(--accent-gold) !important;
        color: black !important;
        border: none;
        letter-spacing: 2px;
        text-transform: uppercase;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #F9E076 !important;
        transform: translateY(-2px);
    }
    
    /* Code/JSON block styling */
    pre { background-color: #000 !important; border: 1px solid #262626 !important; }
    </style>
""", unsafe_allow_html=True)

# --- CORE LOGIC ---
def process_encryption(uploaded_file, carrier_img_path):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    original_bytes = uploaded_file.read()
    payload = {
        "filename": uploaded_file.name,
        "size": len(original_bytes),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "filedata": base64.b64encode(original_bytes).decode("utf-8")
    }
    payload_json = json.dumps(payload)
    encrypted_data = cipher.encrypt(payload_json.encode())
    stego_img = lsb.hide(carrier_img_path, encrypted_data.decode("latin-1"))
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")
    return buf.getvalue(), key.decode()

def process_recovery(stego_image, master_key):
    try:
        hidden_data = lsb.reveal(stego_image)
        cipher = Fernet(master_key.encode())
        decrypted_json = cipher.decrypt(hidden_data.encode("latin-1")).decode()
        payload = json.loads(decrypted_json)
        recovered_bytes = base64.b64decode(payload["filedata"])
        return recovered_bytes, payload
    except:
        return None, None

# --- SESSION MGMT ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "vault_created" not in st.session_state:
    st.session_state.vault_created = False

def reset_and_clear():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='letter-spacing: 5px; color: white; font-weight: 400;'>S-VAULT</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("01. DASHBOARD"):
        st.session_state.page = "home"; st.rerun()
    if st.button("02. SECURE FILE"):
        st.session_state.page = "convert"; st.rerun()
    if st.button("03. RECOVER DATA"):
        st.session_state.page = "recover"; st.rerun()
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("X. RESET SESSION"):
        reset_and_clear()

# --- MAIN INTERFACE ---
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-container'>
        <h1 class='main-title'>SHADOW VAULT</h1>
        <p class='sub-title'>High-Level Steganographic Protocol</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='feature-card'>
        <div class='card-icon'>[ 01 ]</div>
        <h4 style='letter-spacing:2px;'>ENCRYPTION</h4>
        <p style='color:#737373; font-size:0.9rem; margin-top:1rem;'>AES-256 Fernet hardening applied to raw binary before injection.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='feature-card'>
        <div class='card-icon'>[ 02 ]</div>
        <h4 style='letter-spacing:2px;'>STEALTH</h4>
        <p style='color:#737373; font-size:0.9rem; margin-top:1rem;'>Least Significant Bit (LSB) manipulation within PNG architecture.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='feature-card'>
        <div class='card-icon'>[ 03 ]</div>
        <h4 style='letter-spacing:2px;'>INTEGRITY</h4>
        <p style='color:#737373; font-size:0.9rem; margin-top:1rem;'>Zero-loss payload preservation including original metadata.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    _, btn1, gap, btn2, _ = st.columns([2, 3, 0.5, 3, 2])
    with btn1:
        if st.button("SECURE A FILE"):
            st.session_state.page = "convert"; st.rerun()
    with btn2:
        if st.button("RECOVER DATA"):
            st.session_state.page = "recover"; st.rerun()

elif st.session_state.page == "convert":
    st.markdown("<h3 style='letter-spacing:3px;'>[ INITIALIZE ENCRYPTION ]</h3>", unsafe_allow_html=True)
    u_file = st.file_uploader("Select Target File", type=["pdf", "zip", "docx", "txt"])
    
    if u_file and not st.session_state.vault_created:
        _, mid, _ = st.columns([3, 4, 3])
        with mid:
            if st.button("EXECUTE"):
                if os.path.exists("vault_1.png"):
                    with st.spinner("Processing..."):
                        final_img, m_key = process_encryption(u_file, "vault_1.png")
                        st.session_state.final_img = final_img
                        st.session_state.m_key = m_key.encode()
                        st.session_state.vault_created = True
                        st.rerun()
                else: st.error("ERR: CARRIER_MISSING")

    if st.session_state.vault_created:
        st.success("PROTOCOL COMPLETE")
        st.download_button("DOWNLOAD MASTER KEY", st.session_state.m_key, "master_key.key")
        st.download_button("DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png")

elif st.session_state.page == "recover":
    st.markdown("<h3 style='letter-spacing:3px;'>[ INITIALIZE RECOVERY ]</h3>", unsafe_allow_html=True)
    r_img = st.file_uploader("Upload Vault PNG", type=["png"])
    r_key = st.file_uploader("Upload Master Key", type=["key", "txt"])

    if r_img and r_key:
        _, mid, _ = st.columns([3, 4, 3])
        with mid:
            if st.button("DECRYPT"):
                bytes_data, meta = process_recovery(r_img, r_key.read().decode().strip())
                if bytes_data:
                    st.balloons()
                    st.json(meta)
                    st.download_button("SAVE RECOVERED FILE", bytes_data, meta["filename"])
                else:
                    st.error("ERR: AUTHENTICATION_FAILED")
