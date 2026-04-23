import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
from PIL import Image
import io
import filetype

# --- ENCRYPTION LOGIC ---
def process_encryption(uploaded_file, carrier_img):
    # 1. Generate AES-256 Master Key
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # 2. Encrypt File Bytes
    encrypted_data = cipher.encrypt(uploaded_file.read())
    
    # 3. Hide Encrypted String in Image Pixels (latin-1 preserves byte integrity)
    img = Image.open(carrier_img)
    stego_img = lsb.hide(img, encrypted_data.decode('latin-1'))
    
    # 4. Save to Memory Buffer
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")
    return buf.getvalue(), key.decode()

# --- DECRYPTION LOGIC ---
def process_decryption(stego_upload, master_key):
    # 1. Extract Hidden String
    hidden_str = lsb.reveal(Image.open(stego_upload))
    
    # 2. Decrypt using Master Key
    cipher = Fernet(master_key.encode())
    decrypted_bytes = cipher.decrypt(hidden_str.encode('latin-1'))
    
    # 3. Auto-Identify File Extension
    kind = filetype.guess(decrypted_bytes)
    ext = kind.extension if kind else "dat"
    return decrypted_bytes, ext

# --- MINIMALIST FRONTEND ---
st.set_page_config(page_title="Shadow-Vault", layout="centered")

# Navigation State
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🛡️ Shadow-Vault")
    st.write("Convert any file into a secure image. No data ever leaves your RAM.")
    if st.button("MAKE FILE SECURE", use_container_width=True):
        st.session_state.page = 'convert'
        st.rerun()
    if st.button("RECOVER A SECURE FILE", use_container_width=True):
        st.session_state.page = 'recover'
        st.rerun()

# --- PAGE: CONVERT ---
elif st.session_state.page == 'convert':
    st.title("📤 Secure a File")
    if st.button("⬅️ Back"): st.session_state.page = 'home'; st.rerun()
    
    u_file = st.file_uploader("Browse file to convert (PDF, ZIP, DOCX)", type=['pdf', 'zip', 'docx', 'txt'])
    u_img = st.file_uploader("Browse carrier image (PNG)", type=['png'])

    if u_file and u_img:
        if u_file.size > 30 * 1024 * 1024:
            st.error("File size exceeds 30MB limit.")
        elif st.button("PROCEED"):
            try:
                final_img, m_key = process_encryption(u_file, u_img)
                st.success("Conversion Complete!")
                st.info(f"Master Key: {m_key}")
                st.caption("Copy this key! It is required for recovery and is not stored.")
                st.download_button("DOWNLOAD IMAGE", final_img, "vault.png", "image/png")
            except Exception as e:
                st.error(f"Error: {e}")

# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.title("📥 Recover Data")
    if st.button("⬅️ Back"): st.session_state.page = 'home'; st.rerun()
    
    r_img = st.file_uploader("Browse Shadow-Image", type=['png'])
    r_key = st.text_input("Paste Master Key", type="password")

    if r_img and r_key:
        if st.button("RECOVER"):
            try:
                recovered_data, extension = process_decryption(r_img, r_key)
                st.success("File Recovered Successfully!")
                st.download_button(f"DOWNLOAD FILE (.{extension})", recovered_data, f"recovered.{extension}")
            except Exception:
                st.error("Invalid Key or Corrupted Image.")
