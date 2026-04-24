import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
from PIL import Image
import io
import os

# --- ENCRYPTION LOGIC ---
def process_encryption(uploaded_file, carrier_img_path):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(uploaded_file.read())
    
    img = Image.open(carrier_img_path).convert("RGB") 
    stego_img = lsb.hide(img, encrypted_data.decode('latin-1'))
    
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")
    return buf.getvalue(), key.decode()

# --- INITIALIZE STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'vault_created' not in st.session_state:
    st.session_state.vault_created = False

def reset_and_clear():
    # This wipes everything and forces a fresh start
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🛡️ Shadow-Vault")
    if st.button("MAKE FILE SECURE", use_container_width=True, type="primary"):
        st.session_state.page = 'convert'
        st.rerun()
    if st.button("RECOVER A SECURE FILE", use_container_width=True):
        st.session_state.page = 'recover'
        st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.title("📤 Secure a File")
    
    # We use a key for the uploader so we can clear it programmatically
    u_file = st.file_uploader("Browse and upload your secret file", type=['pdf', 'zip', 'docx', 'txt'], key="file_input")
    
    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT", use_container_width=True, type="primary"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking data..."):
                    # Store results in session state so they don't vanish
                    st.session_state.final_img, st.session_state.m_key = process_encryption(u_file, "vault_1.png")
                    st.session_state.vault_created = True
                    st.rerun()
            else:
                st.error("System Error: 'vault_1.png' missing.")

    # Show results only after generation
    if st.session_state.vault_created:
        st.success("✅ Vault Created!")
        
        st.warning("⚠️ CRITICAL: Copy your key before finishing!")
        st.code(st.session_state.m_key, language="text")
        
        st.download_button(
            label="📥 DOWNLOAD VAULT IMAGE",
            data=st.session_state.final_img,
            file_name="vault.png",
            mime="image/png",
            use_container_width=True
        )
        
        st.divider()
        # This button solves both your problems: it clears the PDF and the Key
        if st.button("WIPE SESSION & START OVER", use_container_width=True):
            reset_and_clear()

    if st.button("← Back to Menu"):
        reset_and_clear()

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.title("📥 Recover Data")
    # ... (Keep recovery code simple as before)
    if st.button("← Back to Menu"):
        reset_and_clear()
