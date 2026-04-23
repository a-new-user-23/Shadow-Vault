import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
from PIL import Image
import io
import filetype
import os

# --- LOGIC ---
def process_encryption(uploaded_file, carrier_img_path):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(uploaded_file.read())
    
    # Open the pre-selected gallery image
    img = Image.open(carrier_img_path)
    stego_img = lsb.hide(img, encrypted_data.decode('latin-1'))
    
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")
    return buf.getvalue(), key.decode()

# --- UI CONFIG ---
st.set_page_config(page_title="Shadow-Vault", layout="centered")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Reset Function
def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🛡️ Shadow-Vault")
    st.info("Stateless. Secure. Invisible.")
    if st.button("MAKE FILE SECURE", use_container_width=True):
        st.session_state.page = 'convert'
        st.rerun()
    if st.button("RECOVER A SECURE FILE", use_container_width=True):
        st.session_state.page = 'recover'
        st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.title("📤 Secure a File")
    
    # 1. Select Secret File
    u_file = st.file_uploader("Step 1: Choose secret file", type=['pdf', 'zip', 'docx', 'txt'])
    
    # 2. Select Gallery Image (Addressing Issue #4)
    st.write("Step 2: Select a Vault Image")
    col1, col2, col3 = st.columns(3)
    
    # Note: These images must exist in your GitHub repo
    selection = None
    with col1:
        st.image("vault_1.png", caption="Galaxy (Large Capacity)")
        if st.button("Use Galaxy"): selection = "vault_1.png"
    with col2:
        st.image("vault_2.png", caption="Forest (High Texture)")
        if st.button("Use Forest"): selection = "vault_2.png"
    with col3:
        st.image("vault_3.png", caption="Abstract (Deep Mask)")
        if st.button("Use Abstract"): selection = "vault_3.png"

    if u_file and selection:
        if st.button("GENERATE SECURE IMAGE"):
            with st.spinner("Encrypting..."):
                final_img, m_key = process_encryption(u_file, selection)
                st.success("Vault Created!")
                
                # Addressing Issue #1: Copyable Key
                st.code(m_key, language="text")
                st.caption("Copy the Master Key above.")
                
                st.download_button("DOWNLOAD VAULT IMAGE", final_img, "vault.png", "image/png")
                
                # Addressing Issue #3: Reset Button
                if st.button("FINISH & ERASE SESSION"):
                    reset_app()

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.title("📥 Recover Data")
    r_img = st.file_uploader("Upload Shadow-Image", type=['png'])
    r_key = st.text_input("Paste Master Key", type="password")

    if r_img and r_key:
        if st.button("RECOVER"):
            # ... (Recovery logic remains the same)
            st.button("FINISH", on_click=reset_app)
