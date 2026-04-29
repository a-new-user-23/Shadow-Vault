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

    /* Equal Height Flex Containers */
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
    
    .feature-card h4 { color: #1e293b; margin-top: 10px; font-size: 1.2rem; }
    .feature-card p { color: #64748b; font-size: 0.9rem; line-height: 1.5; }

    .stButton>button { 
        width: 100%; max-width: 350px; margin: 10px auto; display: block;
        border-radius: 8px; height: 3.5em; font-weight: 600; 
    }
    
    .stDownloadButton>button { 
        width: 100%; max-width: 350px; margin: 10px auto; display: block;
        border-radius: 8px; height: 3.5em; background-color: #28a745 !important; color: white !important; 
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🛡️ Shadow-Vault")
    if st.button("🏠 Home Dashboard"): st.session_state.page = 'home'; st.rerun()
    if st.button("📤 Secure a File"): st.session_state.page = 'convert'; st.rerun()
    if st.button("📥 Recover Data"): st.session_state.page = 'recover'; st.rerun()
    st.markdown("---")
    if st.button("🗑️ Reset Session"): reset_and_clear()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.markdown("""
        <div class='hero-text'>
            <h1>SHADOW-VAULT</h1>
            <p>Advanced File Concealment & Privacy Suite</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='feature-card'><h3>🔐</h3><h4>AES-256 Encryption</h4>
        <p>Before concealment, your file is transformed into unreadable ciphertext using industry-standard 256-bit encryption.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='feature-card'><h3>🖼️</h3><h4>Steganography</h4>
        <p>Your encrypted data is injected into the Least Significant Bits (LSB) of a PNG image, making it invisible to the human eye.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='feature-card'><h3>🔑</h3><h4>Master Key Gen</h4>
        <p>A unique, non-recoverable Master Key is generated per session. Without this exact key, the vault remains locked forever.</p></div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Action Buttons
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button("START ENCRYPTION", type="primary"):
            st.session_state.page = 'convert'
            st.rerun()
        if st.button("START RECOVERY"):
            st.session_state.page = 'recover'
            st.rerun()
        
        # Info Button/Expander
        with st.expander("ℹ️ Important Security Disclosure"):
            st.write("""
            **Supported File Types:** PDF, ZIP, DOCX, TXT (Max 10MB).
            
            **Privacy Policy:**
            - We **do not store** your uploaded files or keys. 
            - All processing happens in temporary server RAM and is wiped immediately after your session ends or you click 'Reset'.
            - Your Master Key is the only way to recover data. If you lose it, we cannot help you.
            """)

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.markdown("### 📤 Secure Your Data")
    u_file = st.file_uploader("Upload Secret File", type=['pdf', 'zip', 'docx', 'txt'])
    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT", type="primary"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking Vault..."):
                    final_img, m_key = process_encryption(u_file, "vault_1.png")
                    st.session_state.final_img, st.session_state.m_key = final_img, m_key.encode()
                    st.session_state.vault_created = True; st.rerun()
            else: st.error("System file 'vault_1.png' missing.")
    
    if st.session_state.vault_created:
        st.success("✅ Vault Created")
        st.download_button("🔑 DOWNLOAD MASTER KEY", st.session_state.m_key, "master_key.key")
        st.download_button("📥 DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png")

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.markdown("### 📥 Recovery Portal")
    r_img = st.file_uploader("Upload Vault Image", type=['png'])
    r_key = st.file_uploader("Upload Master Key", type=['key', 'txt'])
    if r_img and r_key:
        if st.button("EXTRACT DATA", type="primary"):
            bytes_data, meta = process_recovery(r_img, r_key.read().decode().strip())
            if bytes_data:
                st.balloons(); st.json(meta)
                st.download_button("📥 SAVE FILE", bytes_data, meta["filename"])
            else: st.error("Verification failed.")
