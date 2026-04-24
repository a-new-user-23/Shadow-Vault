import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
from PIL import Image
import io
import os

# --- LOGIC ---
def process_encryption(uploaded_file, carrier_img_path):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(uploaded_file.read())
    
    # Open the pre-selected gallery image
    img = Image.open(carrier_img_path)
    # We convert to RGB to ensure compatibility with Stegano
    img = img.convert("RGB") 
    stego_img = lsb.hide(img, encrypted_data.decode('latin-1'))
    
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")
    return buf.getvalue(), key.decode()

# --- UI CONFIG ---
st.set_page_config(page_title="Shadow-Vault", layout="centered")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🛡️ Shadow-Vault")
    st.info("Stateless. Secure. Invisible. Your files, hidden in plain sight.")
    if st.button("MAKE FILE SECURE", use_container_width=True):
        st.session_state.page = 'convert'
        st.rerun()
    if st.button("RECOVER A SECURE FILE", use_container_width=True):
        st.session_state.page = 'recover'
        st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.title("📤 Secure a File")
    
    u_file = st.file_uploader("Step 1: Choose secret file", type=['pdf', 'zip', 'docx', 'txt'])
    
    st.write("Step 2: Select a Vault Image")
    col1, col2, col3 = st.columns(3)
    
    selection = None
    
    with col1:
        if os.path.exists("vault_1.png"):
            st.image("vault_1.png", caption="Galaxy Vault (Active)")
            if st.button("Use Galaxy"): 
                selection = "vault_1.png"
        else:
            st.error("vault_1.png not found in repo")

    with col2:
        st.info("Vault 2\n\n(Coming Soon)")
    
    with col3:
        st.info("Vault 3\n\n(Coming Soon)")

    if u_file and selection:
        if st.button("GENERATE SECURE IMAGE", type="primary"):
            with st.spinner("Locking your file inside the stars..."):
                try:
                    final_img, m_key = process_encryption(u_file, selection)
                    st.success("Vault Created Successfully!")
                    
                    st.write("### 🔑 Your Master Key")
                    st.code(m_key, language="text")
                    st.caption("Copy this key. You cannot recover your file without it.")
                    
                    st.download_button("📥 DOWNLOAD VAULT IMAGE", final_img, "vault.png", "image/png", use_container_width=True)
                    
                    if st.button("FINISH & ERASE SESSION"):
                        reset_app()
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    if st.button("← Back"):
        st.session_state.page = 'home'
        st.rerun()

# --- PAGE: RECOVER (Keep existing logic) ---
elif st.session_state.page == 'recover':
    st.title("📥 Recover Data")
    # ... (Your recovery code here)
    if st.button("← Back"):
        st.session_state.page = 'home'
        st.rerun()
