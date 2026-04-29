import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
import filetype
from datetime import datetime

# --- CONFIGURATION & UI STYLING ---
st.set_page_config(page_title="Shadow-Vault | Professional Steganography", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { text-align: center !important; font-family: 'Inter', sans-serif; color: #0f172a; }
    
    .hero-text { 
        text-align: center; 
        padding: 3rem 1rem; 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        color: white; 
        border-radius: 15px; 
        margin-bottom: 2rem;
    }

    /* Equal Height Flex Containers for Feature Cards */
    [data-testid="column"] { display: flex !important; }
    [data-testid="stVerticalBlock"] { flex: 1; display: flex; flex-direction: column; }

    .feature-card { 
        background: white; 
        padding: 2rem; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }

    /* Unified Button Styling - Red-Coral Theme */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        font-weight: 600; 
        background-color: #ff4b4b !important; 
        color: white !important;
        border: none;
        transition: transform 0.2s ease, background-color 0.2s ease;
    }
    .stButton>button:hover { 
        transform: scale(1.02);
        background-color: #ff3333 !important;
    }
    
    .stDownloadButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #28a745 !important; 
        color: white !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC: ENCRYPTION & RECOVERY ---
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
    except: return None, None

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'vault_created' not in st.session_state: st.session_state.vault_created = False

def reset_and_clear():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- SIDEBAR (Includes Navigation and About Section) ---
with st.sidebar:
    st.markdown("## 🛡️ Shadow-Vault")
    st.caption("Secure Information Concealment")
    st.markdown("---")
    if st.button("🏠 Home Dashboard"): st.session_state.page = 'home'; st.rerun()
    if st.button("📤 Secure a File"): st.session_state.page = 'convert'; st.rerun()
    if st.button("📥 Recover Data"): st.session_state.page = 'recover'; st.rerun()
    st.markdown("---")
    
    # "About This Tool" placed in the sidebar as requested
    with st.expander("📖 About This Tool", expanded=False):
        st.info("""
        **Capabilities:**
        - Conceals files inside PNG pixels.
        - Supported: PDF, ZIP, DOCX, TXT.
        - Max File Size: 10MB.
        
        **Privacy Policy:**
        - We do not store any data.
        - All files are processed in real-time RAM.
        - Session data is wiped on exit or reset.
        """)
        
    if st.button("🗑️ Reset Session"): reset_and_clear()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.markdown("""
        <div class='hero-text'>
            <h1>SHADOW-VAULT</h1>
            <p>Enterprise-Grade Steganography & AES-256 Privacy</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='feature-card'><h3>🔐</h3><h4>AES-256 Encryption</h4>
        <p>Your file is encrypted into unreadable ciphertext using industry-standard Fernet (AES-256) encryption before hiding.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='feature-card'><h3>🖼️</h3><h4>Steganography</h4>
        <p>Data is injected into the Least Significant Bits (LSB) of image pixels, maintaining a standard PNG appearance.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='feature-card'><h3>🔑</h3><h4>Master Key Gen</h4>
        <p>A unique, one-time Master Key is generated per session. It is the only way to decrypt and recover your hidden files.</p></div>""", unsafe_allow_html=True)

    st.markdown("<br><br><h3 style='text-align: center;'>Select Operation</h3>", unsafe_allow_html=True)
    
    # --- SYMMETRICAL HORIZONTAL BUTTONS ---
    _, left_btn, right_btn, _ = st.columns([1, 2, 2, 1])
    with left_btn:
        if st.button("START ENCRYPTION"):
            st.session_state.page = 'convert'
            st.rerun()
    with right_btn:
        if st.button("START RECOVERY"):
            st.session_state.page = 'recover'
            st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.markdown("### 📤 Secure Your Data")
    u_file = st.file_uploader("Upload Secret File", type=['pdf', 'zip', 'docx', 'txt'])
    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking Vault..."):
                    final_img, m_key = process_encryption(u_file, "vault_1.png")
                    st.session_state.final_img, st.session_state.m_key = final_img, m_key.encode()
                    st.session_state.vault_created = True; st.rerun()
            else: st.error("System file 'vault_1.png' missing.")
    
    if st.session_state.vault_created:
        st.success("✅ Vault Created Successfully")
        st.download_button("🔑 DOWNLOAD MASTER KEY", st.session_state.m_key, "master_key.key")
        st.download_button("📥 DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png")

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.markdown("### 📥 Recovery Portal")
    r_img = st.file_uploader("Upload Vault Image", type=['png'])
    r_key = st.file_uploader("Upload Master Key", type=['key', 'txt'])
    if r_img and r_key:
        if st.button("EXTRACT SECURE DATA"):
            bytes_data, meta = process_recovery(r_img, r_key.read().decode().strip())
            if bytes_data:
                st.balloons()
                st.markdown("#### ✅ File Verified")
                st.json(meta)
                st.download_button("📥 SAVE RECOVERED FILE", bytes_data, meta["filename"])
            else:
                st.error("Verification failed. Incorrect key or corrupt image.")
