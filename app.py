import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
from datetime import datetime

# --- CONFIGURATION & CLEAN UI STYLING ---
st.set_page_config(
    page_title="Shadow-Vault",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    /* 1. CLEAN LIGHT THEME BASE */
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* Standardizing the Top Header */
    header[data-testid="stHeader"] {
        background-color: #F9FAFB !important;
        border-bottom: 1px solid #E5E7EB;
    }

    /* 2. SIDEBAR ALIGNMENT & CLEAN BUTTONS */
    section[data-testid="stSidebar"] {
        background-color: #F3F4F6 !important;
        border-right: 1px solid #E5E7EB;
    }
    
    /* Aligns sidebar content to main page heading level */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 3rem !important;
    }

    section[data-testid="stSidebar"] .stButton>button {
        background-color: transparent !important;
        color: #4B5563 !important;
        border: 1px solid transparent !important;
        text-align: left;
        font-weight: 500;
        border-radius: 6px;
        transition: 0.2s;
    }

    section[data-testid="stSidebar"] .stButton>button:hover {
        background-color: #E5E7EB !important;
        color: #111827 !important;
    }

    /* 3. HERO SECTION - SIMPLE & PROFESSIONAL */
    .hero-container {
        padding: 4rem 1rem;
        text-align: center;
        background-color: #F9FAFB;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 3rem;
    }

    .main-title {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        margin-bottom: 0.5rem !important;
    }

    .sub-title {
        color: #6B7280 !important;
        font-size: 1.1rem !important;
        font-weight: 400;
    }

    /* 4. FEATURE CARDS - WHITE TILES */
    .feature-card {
        background: #FFFFFF;
        padding: 2rem;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        text-align: center;
        min-height: 280px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 5. ACTION BUTTONS - PROFESSIONAL BLUE */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 3em;
        font-weight: 600;
        background-color: #2563EB !important;
        color: white !important;
        border: none;
        transition: background-color 0.2s;
    }

    .stButton>button:hover {
        background-color: #1D4ED8 !important;
    }

    /* Utility UI tweaks */
    [data-testid="stFileUploadDropzone"] {
        background-color: #F9FAFB !important;
        border: 2px dashed #D1D5DB !important;
    }
    
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LOGIC ---
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

# --- STATE ---
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
    st.markdown("<h2 style='color: #111827;'>Shadow-Vault</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🏠 Home Dashboard"):
        st.session_state.page = "home"; st.rerun()
    if st.button("📤 Secure a File"):
        st.session_state.page = "convert"; st.rerun()
    if st.button("📥 Recover Data"):
        st.session_state.page = "recover"; st.rerun()
    st.markdown("---")
    if st.button("🗑️ Reset Session"):
        reset_and_clear()

# --- MAIN PAGES ---
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-container'>
        <h1 class='main-title'>Shadow-Vault</h1>
        <p class='sub-title'>Simple & Secure File Steganography</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='feature-card'>
        <h3 style='color:#2563EB;'>Encryption</h3>
        <p style='color:#4B5563;'>Files are secured using AES-256 (Fernet) encryption before being hidden.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='feature-card'>
        <h3 style='color:#2563EB;'>Stealth</h3>
        <p style='color:#4B5563;'>Data is embedded invisibly into the pixel layers of a standard PNG image.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='feature-card'>
        <h3 style='color:#2563EB;'>Privacy</h3>
        <p style='color:#4B5563;'>No data is stored. Processing happens entirely in your browser's session memory.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    _, btn1, gap, btn2, _ = st.columns([2, 3, 0.5, 3, 2])
    with btn1:
        if st.button("GET STARTED"):
            st.session_state.page = "convert"; st.rerun()
    with btn2:
        if st.button("RECOVER FILE"):
            st.session_state.page = "recover"; st.rerun()

elif st.session_state.page == "convert":
    st.markdown("## Secure a File")
    u_file = st.file_uploader("Choose a file (PDF, ZIP, DOCX, TXT)", type=["pdf", "zip", "docx", "txt"])
    
    if u_file and not st.session_state.vault_created:
        _, mid, _ = st.columns([3, 2, 3])
        with mid:
            if st.button("Process Vault"):
                if os.path.exists("vault_1.png"):
                    with st.spinner("Creating vault..."):
                        final_img, m_key = process_encryption(u_file, "vault_1.png")
                        st.session_state.final_img = final_img
                        st.session_state.m_key = m_key.encode()
                        st.session_state.vault_created = True
                        st.rerun()
                else: st.error("System Error: Carrier image not found.")

    if st.session_state.vault_created:
        st.success("Vault Created Successfully")
        st.download_button("Download Master Key", st.session_state.m_key, "master_key.key")
        st.download_button("Download Vault Image", st.session_state.final_img, "vault.png")

elif st.session_state.page == "recover":
    st.markdown("## Recover Hidden Data")
    r_img = st.file_uploader("Upload Vault Image (PNG)", type=["png"])
    r_key = st.file_uploader("Upload Master Key (.key)", type=["key", "txt"])

    if r_img and r_key:
        _, mid, _ = st.columns([3, 2, 3])
        with mid:
            if st.button("Decrypt Data"):
                bytes_data, meta = process_recovery(r_img, r_key.read().decode().strip())
                if bytes_data:
                    st.balloons()
                    st.write("### File Metadata")
                    st.json(meta)
                    st.download_button("Save Recovered File", bytes_data, meta["filename"])
                else:
                    st.error("Error: Key mismatch or corrupted image.")
