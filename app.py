import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
from datetime import datetime

# --- CONFIGURATION & ADVANCED UI STYLING ---
st.set_page_config(
    page_title="Shadow-Vault | Professional Steganography",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    header[data-testid="stHeader"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #334155;
    }

    header[data-testid="stHeader"] svg {
        fill: #f8f9fa !important;
    }

    .stApp {
        background-color: #0f172a;
        color: #f8f9fa;
    }

    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
        padding: 5rem 2rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        text-align: center;
        margin-bottom: 3.5rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    .main-title {
        font-size: clamp(3rem, 8vw, 5.5rem) !important;
        font-weight: 900 !important;
        letter-spacing: -3px !important;
        margin: 0 !important;
        background: linear-gradient(to right, #ffffff 20%, #ff4b4b 40%, #ff4b4b 60%, #ffffff 80%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 6s linear infinite;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    .sub-title {
        color: #94a3b8 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase;
        letter-spacing: 6px;
        margin-top: 15px !important;
        font-weight: 500;
    }

    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }

    [data-testid="stVerticalBlock"] {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }

    .feature-card {
        background: rgba(30, 41, 59, 0.5);
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .feature-card:hover {
        border: 1px solid rgba(255, 75, 75, 0.5);
        transform: translateY(-12px);
        background: rgba(30, 41, 59, 0.8);
        box-shadow: 0 15px 35px rgba(255, 75, 75, 0.1);
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 4.5em;
        font-weight: 700;
        background-color: #ff4b4b !important;
        color: white !important;
        border: none;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button:hover {
        background-color: #ff3333 !important;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.4);
        transform: scale(1.02);
    }

    section[data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid #1e293b;
    }

    .stDownloadButton>button {
        background-color: #10b981 !important;
        height: 3.5em;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


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

    stego_img = lsb.hide(
        carrier_img_path,
        encrypted_data.decode("latin-1")
    )

    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")

    return buf.getvalue(), key.decode()


def process_recovery(stego_image, master_key):
    try:
        hidden_data = lsb.reveal(stego_image)

        cipher = Fernet(master_key.encode())
        decrypted_json = cipher.decrypt(
            hidden_data.encode("latin-1")
        ).decode()

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


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:left !important;'>🛡️ Shadow-Vault</h2>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🏠 Home Dashboard"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("📤 Secure a File"):
        st.session_state.page = "convert"
        st.rerun()

    if st.button("📥 Recover Data"):
        st.session_state.page = "recover"
        st.rerun()

    st.markdown("---")

    with st.expander("📖 About This Tool"):
        st.info(
            "Hide encrypted PDF, ZIP, DOCX, or TXT files inside PNG images.\n"
            "Max size 10MB.\n"
            "No data is ever stored on our servers."
        )

    if st.button("🗑️ Reset Session"):
        reset_and_clear()


# --- HOME ---
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-container'>
        <h1 class='main-title'>SHADOW-VAULT</h1>
        <p class='sub-title'>Military-Grade Steganography</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='feature-card'>
        <h2 style='font-size:3rem;'>🔐</h2>
        <h3>AES-256</h3>
        <p style='color:#94a3b8;'>Your files are double-locked using Fernet encryption before pixel injection.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='feature-card'>
        <h2 style='font-size:3rem;'>🖼️</h2>
        <h3>Stealth Mode</h3>
        <p style='color:#94a3b8;'>Data is hidden in PNG pixels, making it undetectable.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='feature-card'>
        <h2 style='font-size:3rem;'>📦</h2>
        <h3>Full Meta</h3>
        <p style='color:#94a3b8;'>Original filename, size and timestamp preserved.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br><h3 style='text-align:center;'>Select Operation</h3>", unsafe_allow_html=True)

    l, b1, g, b2, r = st.columns([6, 3, 0.5, 3, 5])

    with b1:
        if st.button("START ENCRYPTION"):
            st.session_state.page = "convert"
            st.rerun()

    with b2:
        if st.button("START RECOVERY"):
            st.session_state.page = "recover"
            st.rerun()


# --- ENCRYPT PAGE ---
elif st.session_state.page == "convert":
    st.markdown("### 📤 Create a Secure Vault")

    u_file = st.file_uploader(
        "Upload File to Hide",
        type=["pdf", "zip", "docx", "txt"]
    )

    if u_file:
        if u_file.size > MAX_FILE_SIZE:
            st.error("❌ File size too large. Maximum allowed size is 10 MB.")
            st.stop()

    if u_file and not st.session_state.vault_created:
        _, mid, _ = st.columns([3, 4, 3])

        with mid:
            if st.button("GENERATE VAULT"):
                with st.spinner("Locking Vault..."):
                    final_img, m_key = process_encryption(
                        u_file,
                        "vault_1.png"
                    )

                    st.session_state.final_img = final_img
                    st.session_state.m_key = m_key.encode()
                    st.session_state.vault_created = True
                    st.rerun()

    if st.session_state.vault_created:
        st.success("✅ Vault Successfully Created")

        st.download_button(
            "🔑 DOWNLOAD MASTER KEY",
            st.session_state.m_key,
            "master_key.key"
        )

        st.download_button(
            "📥 DOWNLOAD VAULT IMAGE",
            st.session_state.final_img,
            "vault.png"
        )

        if st.button("← Back To Home"):
            reset_and_clear()


# --- RECOVER PAGE ---
elif st.session_state.page == "recover":
    st.markdown("### 📥 Extract Hidden Data")

    r_img = st.file_uploader(
        "Upload Vault Image",
        type=["png"]
    )

    r_key = st.file_uploader(
        "Upload Master Key",
        type=["key", "txt"]
    )

    if r_img and r_key:
        _, mid, _ = st.columns([3, 4, 3])

        with mid:
            if st.button("EXTRACT SECURE DATA"):
                bytes_data, meta = process_recovery(
                    r_img,
                    r_key.read().decode().strip()
                )

                if bytes_data:
                    st.balloons()

                    clean_meta = {
                        "filename": meta["filename"],
                        "size_bytes": meta["size"],
                        "created_at": meta["created_at"]
                    }

                    st.json(clean_meta)

                    st.download_button(
                        "📥 SAVE RECOVERED FILE",
                        bytes_data,
                        meta["filename"]
                    )

                    if st.button("← Back To Home"):
                        reset_and_clear()

                else:
                    st.error("Verification failed. Incorrect key or corrupt image.")
