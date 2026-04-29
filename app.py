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

MAX_FILE_SIZE = 10 * 1024 * 1024


# ---------- CORE LOGIC ----------
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

    try:
        stego_img = lsb.hide(
            carrier_img_path,
            encrypted_data.decode("latin-1")
        )
    except Exception as e:
        raise Exception("Carrier image too small. Use larger image.") from e

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


# ---------- STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "vault_created" not in st.session_state:
    st.session_state.vault_created = False


def reset_and_clear():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<h2 style='text-align:left;'>🛡️ Shadow-Vault</h2>", unsafe_allow_html=True)
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

    if st.button("🗑️ Reset Session"):
        reset_and_clear()


# ---------- HOME ----------
if st.session_state.page == "home":

    st.markdown("""
    <div class='hero-container'>
        <h1 class='main-title'>SHADOW-VAULT</h1>
        <p class='sub-title'>Military-Grade Steganography</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='feature-card'>🔐 Encryption</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='feature-card'>🖼️ Steganography</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='feature-card'>🔑 Master Key</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("START ENCRYPTION"):
            st.session_state.page = "convert"
            st.rerun()

    with c2:
        if st.button("START RECOVERY"):
            st.session_state.page = "recover"
            st.rerun()


# ---------- ENCRYPT ----------
elif st.session_state.page == "convert":

    st.header("Encrypt File")

    u_file = st.file_uploader("Upload File")

    if u_file:
        if len(u_file.getvalue()) > MAX_FILE_SIZE:
            st.error("File too large (Max 10MB)")
            st.stop()

    if u_file and st.button("Generate Vault"):

        try:
            img, key = process_encryption(u_file, "vault_1.png")

            st.session_state.vault_created = True
            st.session_state.img = img
            st.session_state.key = key.encode()

            st.success("Vault Created")

        except Exception as e:
            st.error(str(e))


    if st.session_state.vault_created:
        st.download_button("Download Key", st.session_state.key, "key.key")
        st.download_button("Download Vault", st.session_state.img, "vault.png")

        if st.button("Back"):
            reset_and_clear()


# ---------- RECOVER ----------
elif st.session_state.page == "recover":

    st.header("Recover File")

    img = st.file_uploader("Upload Vault", type=["png"])
    key = st.file_uploader("Upload Key")

    if img and key and st.button("Extract"):

        data, meta = process_recovery(img, key.read().decode().strip())

        if data:
            st.json({
                "filename": meta["filename"],
                "size": meta["size"],
                "created_at": meta["created_at"]
            })

            st.download_button("Download File", data, meta["filename"])

        else:
            st.error("Invalid key or corrupted file")
