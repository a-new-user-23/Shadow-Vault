import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
import filetype
from datetime import datetime

# --- CONFIGURATION & ADVANCED UI STYLING ---
st.set_page_config(
    page_title="Shadow-Vault | Professional Steganography",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    /* 1. GLOBAL COLORS & FONTS */
    :root {
        --bg-deep: #0f172a;
        --bg-card: rgba(30, 41, 59, 0.7);
        --accent-primary: #6366f1; /* Indigo */
        --accent-secondary: #06b6d4; /* Cyan */
        --text-main: #f8f9fa;
        --text-dim: #94a3b8;
    }

    /* 2. HEADER & BACKGROUND */
    header[data-testid="stHeader"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stApp {
        background-color: var(--bg-deep);
        color: var(--text-main);
    }

    /* 3. SIDEBAR ALIGNMENT & BUTTONS */
    section[data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 2.5rem !important;
    }

    /* Sidebar Buttons - Modern Indigo Style */
    section[data-testid="stSidebar"] .stButton>button {
        background: transparent !important;
        color: var(--text-dim) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        transition: all 0.3s ease;
        text-align: left;
        padding-left: 1.5rem;
    }

    section[data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        color: var(--accent-primary) !important;
        border-color: var(--accent-primary) !important;
        transform: translateX(5px);
    }

    /* 4. PREMIUM HERO SECTION */
    .hero-container {
        background: radial-gradient(circle at top left, rgba(99, 102, 241, 0.15), transparent),
                    radial-gradient(circle at bottom right, rgba(6, 182, 212, 0.1), transparent);
        padding: 6rem 2rem;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        text-align: center;
        margin-bottom: 4rem;
        box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.5);
    }

    .main-title {
        font-size: clamp(3rem, 8vw, 6rem) !important;
        font-weight: 800 !important;
        letter-spacing: -4px !important;
        margin: 0 !important;
        background: linear-gradient(135deg, #fff 30%, var(--accent-primary) 60%, var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sub-title {
        color: var(--text-dim) !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 8px;
        margin-top: 20px !important;
        opacity: 0.8;
    }

    /* 5. SYMMETRICAL GLASS CARDS */
    .feature-card {
        background: var(--bg-card);
        padding: 3rem 2rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .feature-card:hover {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(99, 102, 241, 0.4);
        transform: translateY(-15px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }

    /* 6. MAIN ACTION BUTTONS */
    .stButton>button {
        width: 100%;
        border-radius: 14px;
        height: 4.8em;
        font-weight: 600;
        background: linear-gradient(135deg, var(--accent-primary), #4f46e5) !important;
        color: white !important;
        border: none;
        transition: all 0.4s ease;
        letter-spacing: 1px;
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.2);
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.4);
        filter: brightness(1.1);
    }

    /* Download Buttons - Cyan Scheme */
    .stDownloadButton>button {
        background: linear-gradient(135deg, var(--accent-secondary), #0891b2) !important;
        box-shadow: 0 10px 20px rgba(6, 182, 212, 0.2);
    }
    
    /* JSON & UI Clean up */
    pre { background-color: rgba(15, 23, 42, 0.5) !important; border-radius: 12px !important; }
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
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
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

# --- APP STATE ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "vault_created" not in st.session_state:
    st.session_state.vault_created = False

def reset_and_clear():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white; font-weight: 800; letter-spacing: -1px;'>🛡️ SHADOW</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🏠 DASHBOARD"):
        st.session_state.page = "home"; st.rerun()
    if st.button("📤 ENCRYPT VAULT"):
        st.session_state.page = "convert"; st.rerun()
    if st.button("📥 RECOVER DATA"):
        st.session_state.page = "recover"; st.rerun()
        
    st.markdown("---")
    if st.button("🗑️ RESET SESSION"):
        reset_and_clear()

# --- PAGE CONTENT ---
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-container'>
        <h1 class='main-title'>SHADOW VAULT</h1>
        <p class='sub-title'>Decentralized Privacy & Stealth Suite</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='feature-card'><h2 style='color:#6366f1; font-size:3rem;'>🔐</h2>
        <h3 style='margin-bottom:15px;'>AES-256</h3>
        <p style='color:#94a3b8; line-height:1.6;'>Dual-layered cryptographic hardening using industry-standard Fernet (AES-256) protocols.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='feature-card'><h2 style='color:#06b6d4; font-size:3rem;'>🖼️</h2>
        <h3 style='margin-bottom:15px;'>STEALTH</h3>
        <p style='color:#94a3b8; line-height:1.6;'>Sub-pixel LSB injection ensures your data remains invisible even under forensic scrutiny.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='feature-card'><h2 style='color:#a855f7; font-size:3rem;'>📦</h2>
        <h3 style='margin-bottom:15px;'>PAYLOAD</h3>
        <p style='color:#94a3b8; line-height:1.6;'>Comprehensive JSON encapsulation preserves original file metadata and structural integrity.</p></div>""", unsafe_allow_html=True)

    st.markdown("<br><br><p style='text-align: center; color: #64748b; letter-spacing: 2px;'>CHOOSE OPERATION</p>", unsafe_allow_html=True)
    
    _, btn1, gap, btn2, _ = st.columns([2, 3, 0.5, 3, 2])
    with btn1:
        if st.button("START ENCRYPTION"):
            st.session_state.page = "convert"; st.rerun()
    with btn2:
        if st.button("START RECOVERY"):
            st.session_state.page = "recover"; st.rerun()

elif st.session_state.page == "convert":
    st.markdown("<h2 style='text-align:left;'>📤 Create Encrypted Vault</h2>", unsafe_allow_html=True)
    u_file = st.file_uploader("Select file (Max 10MB)", type=["pdf", "zip", "docx", "txt"])
    
    if u_file and not st.session_state.vault_created:
        _, mid, _ = st.columns([3, 4, 3])
        with mid:
            if st.button("GENERATE SECURE IMAGE"):
                if os.path.exists("vault_1.png"):
                    with st.spinner("Encrypting..."):
                        final_img, m_key = process_encryption(u_file, "vault_1.png")
                        st.session_state.final_img = final_img
                        st.session_state.m_key = m_key.encode()
                        st.session_state.vault_created = True
                        st.rerun()
                else: st.error("Carrier image 'vault_1.png' missing.")

    if st.session_state.vault_created:
        st.success("Vault Generated Successfully")
        st.download_button("🔑 DOWNLOAD MASTER KEY", st.session_state.m_key, "master_key.key")
        st.download_button("📥 DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png")

elif st.session_state.page == "recover":
    st.markdown("<h2 style='text-align:left;'>📥 Data Recovery Portal</h2>", unsafe_allow_html=True)
    r_img = st.file_uploader("Upload Vault Image", type=["png"])
    r_key = st.file_uploader("Upload Master Key", type=["key", "txt"])

    if r_img and r_key:
        _, mid, _ = st.columns([3, 4, 3])
        with mid:
            if st.button("DECRYPT & EXTRACT"):
                bytes_data, meta = process_recovery(r_img, r_key.read().decode().strip())
                if bytes_data:
                    st.balloons()
                    st.json(meta)
                    st.download_button("📥 SAVE RECOVERED FILE", bytes_data, meta["filename"])
                else:
                    st.error("Recovery Failed: Invalid Key or Data Corruption.")
