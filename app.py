import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Shadow-Vault | Professional Steganography",
    page_icon="🛡️",
    layout="wide"
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (ONLY FOR ENCRYPTION)

# --- STYLING (UNCHANGED) ---
st.markdown("""
<style>
header[data-testid="stHeader"] {
    background-color: rgba(15, 23, 42, 0.95) !important;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #334155;
}

.stApp {
    background-color: #0f172a;
    color: #f8f9fa;
}

.hero-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
    padding: 5rem 2rem;
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    text-align: center;
    margin-bottom: 3.5rem;
}

.main-title {
    font-size: 4rem;
    font-weight: 900;
    color: white;
}

.sub-title {
    color: #94a3b8;
    letter-spacing: 5px;
}

/* SYMMETRY FIX */
.feature-card {
    background: rgba(30, 41, 59, 0.5);
    padding: 2.5rem;
    border-radius: 20px;
    min-height: 360px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.stButton>button {
    width: 100%;
    height: 4.5em;
    font-weight: 700;
    background-color: #ff4b4b !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# --- CORE LOGIC ---
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

    encrypted_data = cipher.encrypt(json.dumps(payload).encode())

    stego_img = lsb.hide(
        carrier_img_path,
        encrypted_data.decode("latin-1")
    )

    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")

    return buf.getvalue(), key.decode()


def process_recovery(stego_image, master_key):
    try:
        hidden_data = lsb.reveal(stego_image)

        cipher = Fernet(master_key.encode())
        decrypted_json = cipher.decrypt(
            hidden_data.encode("latin-1")
        ).decode()

        payload = json.loads(decrypted_json)
        recovered_bytes = base64.b64decode(payload["filedata"])

        return recovered_bytes, payload

    except:
        return None, None


# --- STATE ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "vault_created" not in st.session_state:
    st.session_state.vault_created = False


def reset():
    st.session_state.clear()
    st.rerun()


# --- HOME ---
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-container'>
        <h1 class='main-title'>SHADOW-VAULT</h1>
        <p class='sub-title'>SECURE STEGANOGRAPHY SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class='feature-card'>
        <h2>🔐 ENCRYPTION</h2>
        <p>AES + Fernet security layer</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='feature-card'>
        <h2>🖼️ STEGANOGRAPHY</h2>
        <p>Hidden inside image pixels</p>
        </div>
        """, unsafe_allow_html=True)

    b1, b2 = st.columns([1, 1], gap="large")

    with b1:
        if st.button("START ENCRYPTION"):
            st.session_state.page = "convert"
            st.rerun()

    with b2:
        if st.button("START RECOVERY"):
            st.session_state.page = "recover"
            st.rerun()


# --- ENCRYPT ---
elif st.session_state.page == "convert":
    st.title("📤 Secure File")

    u_file = st.file_uploader("Upload file (MAX 10MB)", type=["pdf", "zip", "docx", "txt"])

    # ONLY ENCRYPTION LIMIT CHECK
    if u_file:
        file_bytes = u_file.getvalue()
        if len(file_bytes) > MAX_FILE_SIZE:
            st.error("❌ File too large (Max 10MB allowed for encryption)")
            st.stop()

    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT"):
            final_img, key = process_encryption(u_file, "vault_1.png")

            st.session_state.final_img = final_img
            st.session_state.key = key.encode()
            st.session_state.vault_created = True
            st.rerun()

    if st.session_state.vault_created:
        st.success("Vault Created")

        st.download_button("DOWNLOAD KEY", st.session_state.key, "master.key")
        st.download_button("DOWNLOAD VAULT", st.session_state.final_img, "vault.png")

        if st.button("BACK HOME"):
            reset()


# --- RECOVERY (NO SIZE LIMIT HERE) ---
elif st.session_state.page == "recover":
    st.title("📥 Recover File")

    r_img = st.file_uploader("Upload Vault Image", type=["png"])
    r_key = st.file_uploader("Upload Key", type=["key", "txt"])

    if r_img and r_key:
        if st.button("EXTRACT SECURE DATA"):
            data, meta = process_recovery(r_img, r_key.read().decode().strip())

            if data:
                st.success("Recovery Successful")

                # ONLY META DATA (NO FULL FILE DISPLAY)
                st.json({
                    "filename": meta["filename"],
                    "size": meta["size"],
                    "created_at": meta["created_at"]
                })

                st.download_button("DOWNLOAD FILE", data, meta["filename"])

            else:
                st.error("Invalid key or corrupted vault")

    if st.button("BACK HOME"):
        reset()
