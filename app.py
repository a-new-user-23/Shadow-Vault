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

# Enhanced CSS for centering and professional alignment
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* Center headings */
    h1, h2, h3 { text-align: center !important; }
    
    /* Professional Button Styling */
    .stButton>button { 
        width: 100%; 
        max-width: 350px; 
        margin: 10px auto; 
        display: block;
        border-radius: 8px; 
        height: 3.5em; 
        font-weight: 600; 
        transition: all 0.3s ease;
    }
    
    .stDownloadButton>button { 
        width: 100%; 
        max-width: 350px;
        margin: 10px auto;
        display: block;
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #28a745 !important; 
        color: white !important; 
    }

    /* Hero Section Gradient */
    .hero-text { 
        text-align: center; 
        padding: 3rem 1rem; 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        color: white; 
        border-radius: 15px; 
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Feature Cards */
    .feature-card { 
        background: white; 
        padding: 2rem; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        height: 100%; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    /* Fix for column alignment */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        align-items: center;
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
    except Exception:
        return None, None

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'vault_created' not in st.session_state:
    st.session_state.vault_created = False

def reset_and_clear():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("## 🛡️ Shadow-Vault")
    st.caption("Secure Pixel-Vault Technology")
    st.markdown("---")
    if st.button("🏠 Home Dashboard"): 
        st.session_state.page = 'home'
        st.rerun()
    if st.button("📤 Secure a File"): 
        st.session_state.page = 'convert'
        st.rerun()
    if st.button("📥 Recover Data"): 
        st.session_state.page = 'recover'
        st.rerun()
    st.markdown("---")
    if st.button("🗑️ Reset Application"): reset_and_clear()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.markdown("""
        <div class='hero-text'>
            <h1>SHADOW-VAULT</h1>
            <p>Enterprise-grade file concealment using Advanced Steganography</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature Section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='feature-card'><h3>🔒</h3><h4>AES-256 Encryption</h4><p>Data is encrypted before pixel-injection using military-grade Fernet standards.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='feature-card'><h3>📦</h3><h4>Zero Data Loss</h4><p>Internal JSON payload preserves original filenames and metadata perfectly.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='feature-card'><h3>🕵️</h3><h4>Stealth Mode</h4><p>The output file is a 100% valid PNG image, undetectable by standard scans.</p></div>", unsafe_allow_html=True)

    st.markdown("<br><br><h3>Select Operation</h3>", unsafe_allow_html=True)
    
    # CENTERING BUTTONS
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button("START ENCRYPTION", type="primary"):
            st.session_state.page = 'convert'
            st.rerun()
        if st.button("START RECOVERY"):
            st.session_state.page = 'recover'
            st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.markdown("## 📤 Secure Your Data")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.info("**Requirements:**\n\n1. Target file < 10MB\n2. 'vault_1.png' must exist in root.\n3. Keep the Master Key safe—it cannot be recovered.")
        u_file = st.file_uploader("Upload Secret File", type=['pdf', 'zip', 'docx', 'txt'])

    with col2:
        if u_file:
            file_size = len(u_file.getvalue())
            if file_size > 10 * 1024 * 1024:
                st.error("File size exceeds 10MB limit.")
            elif not st.session_state.vault_created:
                st.success(f"Ready to process: {u_file.name}")
                if st.button("GENERATE VAULT", type="primary"):
                    if os.path.exists("vault_1.png"):
                        with st.spinner("Executing Cryptographic Injection..."):
                            final_img, master_key = process_encryption(u_file, "vault_1.png")
                            st.session_state.final_img = final_img
                            st.session_state.m_key = master_key.encode()
                            st.session_state.vault_created = True
                            st.rerun()
                    else: st.error("Carrier 'vault_1.png' missing.")

        if st.session_state.vault_created:
            st.success("✅ VAULT SECURED")
            st.download_button("🔑 DOWNLOAD MASTER KEY", st.session_state.m_key, "master_key.key")
            st.download_button("📥 DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png")
            if st.button("New Session"): reset_and_clear()

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.markdown("## 📥 Recovery Portal")
    
    col1, col2 = st.columns(2)
    with col1:
        r_img = st.file_uploader("1. Upload Vault Image", type=['png'])
        r_key_file = st.file_uploader("2. Upload Master Key", type=['key', 'txt'])
    
    with col2:
        if r_img and r_key_file:
            if st.button("EXTRACT SECURE DATA", type="primary"):
                with st.spinner("Extracting..."):
                    master_key = r_key_file.read().decode().strip()
                    recovered_bytes, metadata = process_recovery(r_img, master_key)

                    if recovered_bytes:
                        st.balloons()
                        st.markdown("#### ✅ Extraction Successful")
                        st.json(metadata)
                        st.download_button("📥 SAVE RECOVERED FILE", recovered_bytes, metadata["filename"])
                    else:
                        st.error("Verification failed. Invalid Key or Image.")
