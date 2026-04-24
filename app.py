import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
from PIL import Image
import io
import os

# --- ENCRYPTION LOGIC ---
def process_encryption(uploaded_file, carrier_img_path):
    # Generate Encryption Key
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # Encrypt the uploaded file data
    encrypted_data = cipher.encrypt(uploaded_file.read())
    
    # Hide encrypted data in the default vault_1.png
    img = Image.open(carrier_img_path)
    img = img.convert("RGB") 
    stego_img = lsb.hide(img, encrypted_data.decode('latin-1'))
    
    # Save to memory
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")
    return buf.getvalue(), key.decode()

# --- UI CONFIG ---
st.set_page_config(page_title="Shadow-Vault", layout="centered")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🛡️ Shadow-Vault")
    st.write("Secure files inside the stars. No traces left behind.")
    
    if st.button("MAKE FILE SECURE", use_container_width=True, type="primary"):
        st.session_state.page = 'convert'
        st.rerun()
        
    if st.button("RECOVER A SECURE FILE", use_container_width=True):
        st.session_state.page = 'recover'
        st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.title("📤 Secure a File")
    
    # 1. BROWSE AND UPLOAD
    u_file = st.file_uploader("Browse and upload your secret file", type=['pdf', 'zip', 'docx', 'txt'])
    
    # 2. THE BIG SECURE BUTTON
    if u_file:
        if st.button("GENERATE VAULT", use_container_width=True, type="primary"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking your data..."):
                    final_img, m_key = process_encryption(u_file, "vault_1.png")
                    
                    st.success("Vault Created!")
                    
                    # OUTPUT 1: Copy Master Key
                    st.write("### 🔑 Step 1: Copy Master Key")
                    st.code(m_key, language="text")
                    
                    # OUTPUT 2: Download Button
                    st.write("### 📥 Step 2: Download Vault")
                    st.download_button(
                        label="DOWNLOAD SECURE IMAGE",
                        data=final_img,
                        file_name="vault.png",
                        mime="image/png",
                        use_container_width=True
                    )
            else:
                st.error("System Error: 'vault_1.png' is missing from the repository.")

    # 3. BACK BUTTON
    st.divider()
    if st.button("← Back to Menu"):
        st.session_state.page = 'home'
        st.rerun()

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.title("📥 Recover Data")
    r_img = st.file_uploader("Upload your Vault Image", type=['png'])
    r_key = st.text_input("Paste Master Key", type="password")

    if r_img and r_key:
        if st.button("RECOVER ORIGINAL FILE", use_container_width=True, type="primary"):
            st.info("Decrypting and extracting data...")
            # Recovery logic would execute here
            
    if st.button("← Back to Menu"):
        st.session_state.page = 'home'
        st.rerun()
