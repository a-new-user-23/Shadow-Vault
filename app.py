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
st.set_page_config(
    page_title="Shadow-Vault | Professional Steganography",
    page_icon="🛡️",
    layout="wide"
)

# Dark Theme CSS
st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background-color: #0f172a;
        color: #f8f9fa;
    }

    /* Titles and Text */
    h1, h2, h3, h4, p, label {
        text-align: center !important;
        font-family: 'Inter', sans-serif;
        color: #f8f9fa !important;
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }

    /* Hero Section */
    .hero-text {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #334155;
    }

    /* Feature Cards - Dark Mode */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }

    [data-testid="stVerticalBlock"] {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }

    .feature-card {
        background-color: #1e293b;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
        text-align: center;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* File Uploader Box */
    [data-testid="stFileUploadDropzone"] {
        background-color: #1e293b !important;
        border: 1px dashed #475569 !important;
    }

    /* Action Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 4em;
        font-weight: 700;
        background-color: #ff4b4b !important;
        color: white !important;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }

    .stButton>button:hover {
        background-color: #ff3333 !important;
        transform: translateY(-2px);
    }

    /* Success/Download Buttons */
    .stDownloadButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #10b981 !important;
        color: white !important;
        border: none;
    }

    /* Metadata JSON styling */
    pre {
        background-color: #1e293b !important;
        color: #10b981 !important;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)


# --- LOGIC ---
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


def reset_and_clear():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🛡️ Shadow-Vault")
    st.markdown("---")

    if st.button("🏠 Home Dashboard"):
        st.session_state.page = "home"
        st.rerun()

    if st.button("📤 Secure a File"):
        st.session_state.page = "convert"
        st.rerun()

    if st.button("📥 Recover Data"):
        st.session_state.page = "recover"
        st.rerun()

    st.markdown("---")

    with st.expander("📖 About This Tool"):
        st.markdown("""
        <div style='color: #94a3b8;'>
        <b>Capabilities</b><br>
        - Hide PDF, ZIP, DOCX, TXT inside PNG pixels<br>
        - Max File Size: 10MB<br><br>
        <b>Privacy</b><br>
        - No storage<br>
        - RAM-only processing<br>
        - Session wiped on reset
        </div>
        """, unsafe_allow_html=True)

    if st.button("🗑️ Reset Session"):
        reset_and_clear()


# --- HOME PAGE ---
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-text'>
        <h1>SHADOW-VAULT</h1>
        <p>Professional Steganography & Encryption Suite</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='font-size: 3rem;'>🔐</h3>
        <h4>Encryption</h4>
        <p style='color: #94a3b8 !important;'>Your file is encrypted with AES-standard security before hiding.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='font-size: 3rem;'>🖼️</h3>
        <h4>Steganography</h4>
        <p style='color: #94a3b8 !important;'>Data is embedded into image pixels invisibly to the naked eye.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='font-size: 3rem;'>🔑</h3>
        <h4>Unique Master Key</h4>
        <p style='color: #94a3b8 !important;'>Every vault requires a specific cryptographic key for recovery.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left_space, btn1, gap, btn2, right_space = st.columns([2, 3, 0.5, 3, 2])

    with btn1:
        if st.button("START ENCRYPTION"):
            st.session_state.page = "convert"
            st.rerun()

    with btn2:
        if st.button("START RECOVERY"):
            st.session_state.page = "recover"
            st.rerun()


# --- CONVERT PAGE ---
elif st.session_state.page == "convert":
    st.markdown("### 📤 Secure Your Data")
    u_file = st.file_uploader(
        "Upload Secret File",
        type=["pdf", "zip", "docx", "txt"]
    )

    if u_file and not st.session_state.vault_created:
        left, mid, right = st.columns([3, 4, 3])
        with mid:
            if st.button("GENERATE VAULT"):
                if os.path.exists("vault_1.png"):
                    with st.spinner("Locking Vault..."):
                        final_img, m_key = process_encryption(u_file, "vault_1.png")
                        st.session_state.final_img = final_img
                        st.session_state.m_key = m_key.encode()
                        st.session_state.vault_created = True
                        st.rerun()
                else:
                    st.error("Carrier 'vault_1.png' not found.")

    if st.session_state.vault_created:
        st.success("✅ Vault Created Successfully")
        st.download_button("🔑 DOWNLOAD MASTER KEY", st.session_state.m_key, "master_key.key")
        st.download_button("📥 DOWNLOAD VAULT IMAGE", st.session_state.final_img, "vault.png")
        if st.button("← Back To Home"):
            reset_and_clear()


# --- RECOVER PAGE ---
elif st.session_state.page == "recover":
    st.markdown("### 📥 Recovery Portal")
    r_img = st.file_uploader("Upload Vault Image", type=["png"])
    r_key = st.file_uploader("Upload Master Key", type=["key", "txt"])

    if r_img and r_key:
        left, mid, right = st.columns([3, 4, 3])
        with mid:
            if st.button("EXTRACT SECURE DATA"):
                bytes_data, meta = process_recovery(r_img, r_key.read().decode().strip())
                if bytes_data:
                    st.balloons()
                    kind = filetype.guess(bytes_data)
                    file_type = kind.extension.upper() if kind else "Unknown"

                    clean_meta = {
                        "File Name": meta["filename"],
                        "File Type": file_type,
                        "File Size": f'{meta["size"]} bytes',
                        "Stored Date": meta["created_at"]
                    }

                    st.subheader("📄 File Metadata")
                    st.json(clean_meta)
                    st.download_button("📥 SAVE RECOVERED FILE", bytes_data, meta["filename"])
                else:
                    st.error("Verification failed. Incorrect key or corrupted image.")
