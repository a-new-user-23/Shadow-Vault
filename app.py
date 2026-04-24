import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
from PIL import Image
import io
import os

# --- LOGIC: ENCRYPTION ---
def process_encryption(uploaded_file, carrier_img_path):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(uploaded_file.read())
    img = Image.open(carrier_img_path).convert("RGB") 
    stego_img = lsb.hide(img, encrypted_data.decode('latin-1'))
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")
    return buf.getvalue(), key.decode()

# --- LOGIC: RECOVERY ---
def process_recovery(stego_image, master_key):
    try:
        # 1. Extract from pixels
        img = Image.open(stego_image).convert("RGB")
        hidden_data = lsb.reveal(img)
        
        # 2. Decrypt with key
        cipher = Fernet(master_key.encode())
        decrypted_data = cipher.decrypt(hidden_data.encode('latin-1'))
        return decrypted_data
    except Exception:
        return None

# --- INITIALIZE STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'vault_created' not in st.session_state:
    st.session_state.vault_created = False

def reset_and_clear():
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

# --- PAGE: CONVERT (Kept exactly as you liked) ---
elif st.session_state.page == 'convert':
    st.title("📤 Secure a File")
    u_file = st.file_uploader("Browse and upload your secret file", type=['pdf', 'zip', 'docx', 'txt'], key="file_input")
    
    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT", use_container_width=True, type="primary"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking data..."):
                    st.session_state.final_img, st.session_state.m_key = process_encryption(u_file, "vault_1.png")
                    st.session_state.vault_created = True
                    st.rerun()
            else:
                st.error("System Error: 'vault_1.png' missing.")

    if st.session_state.vault_created:
        st.success("✅ Vault Created!")
        st.warning("⚠️ CRITICAL: Copy your key before finishing!")
        st.code(st.session_state.m_key, language="text")
        st.download_button("📥 DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png", "image/png", use_container_width=True)
        st.divider()
        if st.button("WIPE SESSION & START OVER", use_container_width=True):
            reset_and_clear()

    if st.button("← Back to Menu"):
        reset_and_clear()

# --- PAGE: RECOVER (Full Logic Added) ---
elif st.session_state.page == 'recover':
    st.title("📥 Recover Data")
    
    r_img = st.file_uploader("Step 1: Upload your Vault Image", type=['png'])
    r_key = st.text_input("Step 2: Paste Master Key", type="password")

    if r_img and r_key:
        if st.button("EXTRACT FILE", use_container_width=True, type="primary"):
            with st.spinner("Decrypting..."):
                recovered_bytes = process_recovery(r_img, r_key)
                
                if recovered_bytes:
                    st.success("✅ File Successfully Extracted!")
                    # We provide a generic 'recovered_file' name since extensions are encrypted
                    st.download_button(
                        label="📥 DOWNLOAD RECOVERED FILE",
                        data=recovered_bytes,
                        file_name="recovered_secret_file", 
                        use_container_width=True
                    )
                else:
                    st.error("❌ Recovery Failed. Incorrect key or damaged image.")

    st.divider()
    if st.button("← Back to Main Menu"):
        reset_and_clear()
