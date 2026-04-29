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

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: 600; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745 !important; color: white !important; }
    .hero-text { text-align: center; padding: 2rem 0rem; }
    .feature-card { background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e9ecef; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_index=True)

# --- LOGIC: ENCRYPTION & RECOVERY (Core logic remains same for stability) ---
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

# --- NAVIGATION ---
with st.sidebar:
    st.title("🛡️ Shadow-Vault")
    st.markdown("---")
    if st.button("🏠 Dashboard"): st.session_state.page = 'home'; st.rerun()
    if st.button("📤 Secure File"): st.session_state.page = 'convert'; st.rerun()
    if st.button("📥 Recover File"): st.session_state.page = 'recover'; st.rerun()
    st.markdown("---")
    st.caption("v2.1.0 | Enterprise Steganography")

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.markdown("<div class='hero-text'><h1>Shadow-Vault</h1><p>Advanced AES-256 File Steganography</p></div>", unsafe_allow_index=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='feature-card'><h3>🔒 Military Grade</h3><p>Files are encrypted using Fernet (AES-256) before being embedded into pixels.</p></div>", unsafe_allow_index=True)
    with col2:
        st.markdown("<div class='feature-card'><h3>📦 Metadata Preservation</h3><p>Original filenames, timestamps, and extensions are securely stored within the vault.</p></div>", unsafe_allow_index=True)
    with col3:
        st.markdown("<div class='feature-card'><h3>🕵️ Invisible</h3><p>The resulting 'Vault Image' looks like a standard PNG, undetectable to the naked eye.</p></div>", unsafe_allow_index=True)

    st.markdown("<br>", unsafe_allow_index=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("GET STARTED: ENCRYPT", type="primary"):
            st.session_state.page = 'convert'
            st.rerun()
    with c2:
        if st.button("RECOVER DATA"):
            st.session_state.page = 'recover'
            st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.subheader("📤 Secure a New File")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.info("**Guidelines:**\n* Max Size: 10MB\n* Supported: PDF, ZIP, DOCX, TXT\n* Requires: `vault_1.png` in root.")
        u_file = st.file_uploader("Upload Secret File", type=['pdf', 'zip', 'docx', 'txt'])

    with col2:
        if u_file:
            file_size = len(u_file.getvalue())
            if file_size > 10 * 1024 * 1024:
                st.error("File exceeds 10MB limit.")
            elif not st.session_state.vault_created:
                st.write(f"**Ready to secure:** {u_file.name}")
                if st.button("LOCK INTO VAULT", type="primary"):
                    if os.path.exists("vault_1.png"):
                        with st.spinner("Executing cryptographic embedding..."):
                            final_img, master_key = process_encryption(u_file, "vault_1.png")
                            st.session_state.final_img = final_img
                            st.session_state.m_key = master_key.encode()
                            st.session_state.vault_created = True
                            st.rerun()
                    else: st.error("Carrier image 'vault_1.png' not found.")

        if st.session_state.vault_created:
            st.success("Encryption Complete.")
            st.download_button("🔑 DOWNLOAD MASTER KEY", st.session_state.m_key, "master_key.key")
            st.download_button("📥 DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png")
            if st.button("Start New Session"): reset_and_clear()

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.subheader("📥 Recover Data from Vault")
    
    col1, col2 = st.columns(2)
    with col1:
        r_img = st.file_uploader("1. Upload Vault Image", type=['png'])
        r_key_file = st.file_uploader("2. Upload Master Key", type=['key', 'txt'])
    
    with col2:
        if r_img and r_key_file:
            if st.button("DECRYPT & EXTRACT", type="primary"):
                with st.spinner("Recovering..."):
                    master_key = r_key_file.read().decode().strip()
                    recovered_bytes, metadata = process_recovery(r_img, master_key)

                    if recovered_bytes:
                        kind = filetype.guess(recovered_bytes)
                        ext = kind.extension if kind else "bin"
                        
                        st.markdown("### 📄 Recovery Successful")
                        st.json({
                            "Filename": metadata['filename'],
                            "Size": f"{round(metadata['size'] / 1024, 2)} KB",
                            "Created": metadata['created_at']
                        })
                        
                        st.download_button("📥 SAVE RECOVERED FILE", recovered_bytes, metadata["filename"])
                    else:
                        st.error("Decryption failed. Check your key.")
