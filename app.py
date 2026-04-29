import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
from datetime import datetime

# --- CONFIGURATION & SOPHISTICATED UI STYLING ---
st.set_page_config(
    page_title="Shadow-Vault",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    /* 1. NORDIC NEUTRAL BASE */
    .stApp {
        background-color: #F5F7F9;
        color: #334155;
    }

    /* Seamless Header Integration */
    header[data-testid="stHeader"] {
        background-color: #F5F7F9 !important;
        border-bottom: 1px solid #E2E8F0;
    }

    /* 2. SIDEBAR: CLEAN & ALIGNED */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Perfect vertical alignment with main content */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 2.5rem !important;
    }

    section[data-testid="stSidebar"] .stButton>button {
        background-color: transparent !important;
        color: #64748B !important;
        border: none !important;
        text-align: left;
        font-weight: 500;
        border-radius: 8px;
        transition: 0.2s;
        padding: 0.5rem 1rem;
    }

    section[data-testid="stSidebar"] .stButton>button:hover {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }

    /* 3. HERO SECTION - SUBTLE DEPTH */
    .hero-container {
        padding: 5rem 1rem;
        text-align: center;
        background: linear-gradient(180deg, #FFFFFF 0%, #F5F7F9 100%);
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 4rem;
    }

    .main-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: -0.025em !important;
        margin-bottom: 0.75rem !important;
    }

    .sub-title {
        color: #64748B !important;
        font-size: 1.1rem !important;
        max-width: 600px;
        margin: 0 auto;
    }

    /* 4. FEATURE CARDS - ELEVATED WHITE TILES */
    .feature-card {
        background: #FFFFFF;
        padding: 2.5rem;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        text-align: center;
        min-height: 300px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* 5. PRIMARY BUTTONS - SLATE BLUE ACCENT */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: 600;
        background-color: #475569 !important; /* Elegant Slate Blue */
        color: white !important;
        border: none;
        transition: all 0.2s;
    }

    .stButton>button:hover {
        background-color: #1E293B !important;
        box-shadow: 0 4px 12px rgba(71, 85, 105, 0.2);
    }

    /* File Uploader Customization */
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
    }

    .success-text { color: #10B981; font-weight: 600; }
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

# --- STATE MANAGEMENT ---
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
    st.markdown("<h2 style='color: #0F172A; font-weight: 800;'>Shadow Vault</h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    if st.button("🏠 Dashboard"):
        st.session_state.page = "home"; st.rerun()
    if st.button("📤 Secure a File"):
        st.session_state.page = "convert"; st.rerun()
    if st.button("📥 Recover Data"):
        st.session_state.page = "recover"; st.rerun()
    
    st.markdown("<div style='height: 40vh;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Reset Session"):
        reset_and_clear()

# --- MAIN DASHBOARD ---
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-container'>
        <h1 class='main-title'>Shield your data.</h1>
        <p class='sub-title'>Professional-grade steganography with AES-256 encryption. Hide any file inside an image in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='feature-card'>
        <h3 style='color:#475569;'>Encryption</h3>
        <p style='color:#64748B; font-size: 0.95rem;'>Military-grade AES-256 Fernet encryption ensures your data is unreadable without the master key.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='feature-card'>
        <h3 style='color:#475569;'>Steganography</h3>
        <p style='color:#64748B; font-size: 0.95rem;'>Advanced LSB pixel manipulation hides data within image layers without visual distortion.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='feature-card'>
        <h3 style='color:#475569;'>Zero-Trace</h3>
        <p style='color:#64748B; font-size: 0.95rem;'>All processing happens in volatile session memory. No files ever touch a hard drive or server.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    _, btn1, gap, btn2, _ = st.columns([2, 3, 0.5, 3, 2])
    with btn1:
        if st.button("SECURE A FILE NOW"):
            st.session_state.page = "convert"; st.rerun()
    with btn2:
        if st.button("OPEN RECOVERY PORTAL"):
            st.session_state.page = "recover"; st.rerun()

# --- CONTENT PAGES ---
elif st.session_state.page == "convert":
    st.markdown("<h2 style='font-weight:800;'>Secure a File</h2>", unsafe_allow_html=True)
    u_file = st.file_uploader("Upload the document you want to hide", type=["pdf", "zip", "docx", "txt"])
    
    if u_file and not st.session_state.vault_created:
        _, mid, _ = st.columns([3, 2, 3])
        with mid:
            if st.button("Generate Vault"):
                if os.path.exists("vault_1.png"):
                    with st.spinner("Processing..."):
                        final_img, m_key = process_encryption(u_file, "vault_1.png")
                        st.session_state.final_img = final_img
                        st.session_state.m_key = m_key.encode()
                        st.session_state.vault_created = True
                        st.rerun()
                else: st.error("Carrier image 'vault_1.png' not found in directory.")

    if st.session_state.vault_created:
        st.markdown("<p class='success-text'>✅ Vault successfully generated.</p>", unsafe_allow_html=True)
        st.download_button("📥 Download Vault Image", st.session_state.final_img, "vault.png")
        st.download_button("🔑 Download Master Key", st.session_state.m_key, "master_key.key")

elif st.session_state.page == "recover":
    st.markdown("<h2 style='font-weight:800;'>Recover Hidden Data</h2>", unsafe_allow_html=True)
    r_img = st.file_uploader("Upload the Vault PNG", type=["png"])
    r_key = st.file_uploader("Upload your Master Key", type=["key", "txt"])

    if r_img and r_key:
        _, mid, _ = st.columns([3, 2, 3])
        with mid:
            if st.button("Decrypt & Extract"):
                bytes_data, meta = process_recovery(r_img, r_key.read().decode().strip())
                if bytes_data:
                    st.balloons()
                    st.write("### File Found")
                    st.json(meta)
                    st.download_button("💾 Save Recovered File", bytes_data, meta["filename"])
                else:
                    st.error("Recovery failed. The key is incorrect or the image has been altered.")
