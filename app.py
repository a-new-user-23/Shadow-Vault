import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
import filetype
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Shadow Vault",
    page_icon="🛡️",
    layout="centered",
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.block-container{
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 820px;
}

.main-card{
    background: white;
    border-radius: 18px;
    padding: 32px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    border: 1px solid #e6eef8;
    margin-bottom: 20px;
}

.hero-title{
    color:#0b1f4d;
    font-size:38px;
    font-weight:800;
    margin-bottom:0;
    text-align:center;
}

.hero-sub{
    color:#35507a;
    font-size:18px;
    text-align:center;
    margin-top:4px;
    margin-bottom:6px;
}

.hero-mini{
    color:#60708f;
    font-size:15px;
    text-align:center;
    margin-bottom:10px;
}

.feature-strip{
    text-align:center;
    color:#0b1f4d;
    font-weight:600;
    margin-top:10px;
}

.meta-box{
    background:#f7faff;
    border-left:5px solid #0b1f4d;
    padding:18px;
    border-radius:12px;
    margin-top:15px;
    color:#102443;
}

.footer{
    text-align:center;
    color:#7d8ca5;
    margin-top:30px;
    font-size:14px;
}

.stButton > button{
    border-radius:12px !important;
    height:52px !important;
    font-weight:700 !important;
    font-size:16px !important;
}

@media (max-width: 640px){
    .hero-title{
        font-size:28px;
    }
    .hero-sub{
        font-size:15px;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------------- ENCRYPTION ----------------
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


# ---------------- RECOVERY ----------------
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


# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "vault_created" not in st.session_state:
    st.session_state.vault_created = False


def reset_and_clear():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# ---------------- HOME ----------------
if st.session_state.page == "home":

    st.markdown("""
    <div class="main-card">
        <div class="hero-title">🛡 SHADOW VAULT</div>
        <div class="hero-sub">Advanced Encryption & Steganographic Storage</div>
        <div class="hero-mini">Secure • Conceal • Recover</div>
        <div class="feature-strip">
            AES Encryption | Unique Master Key | Hidden Vault Security
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔒 Secure File", use_container_width=True, type="primary"):
            st.session_state.page = "convert"
            st.rerun()

    with c2:
        if st.button("📂 Recover File", use_container_width=True):
            st.session_state.page = "recover"
            st.rerun()

    st.markdown('<div class="footer">Built for secure confidential file protection</div>', unsafe_allow_html=True)


# ---------------- CONVERT ----------------
elif st.session_state.page == "convert":

    st.markdown("""
    <div class="main-card">
        <div class="hero-title" style="font-size:30px;">📤 Secure a File</div>
        <div class="hero-sub">Upload confidential file (Max: 10 MB)</div>
    </div>
    """, unsafe_allow_html=True)

    u_file = st.file_uploader(
        "Browse and upload your secret file",
        type=["pdf", "zip", "docx", "txt"],
        key="file_input"
    )

    # 10 MB CHECK
    if u_file is not None:
        file_size = len(u_file.getvalue())
        max_size = 10 * 1024 * 1024

        if file_size > max_size:
            st.error("❌ File size too large. Maximum allowed size is 10 MB.")
            st.stop()

    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT", use_container_width=True, type="primary"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking data securely..."):
                    final_img, master_key = process_encryption(u_file, "vault_1.png")

                    st.session_state.final_img = final_img
                    st.session_state.m_key = master_key.encode()
                    st.session_state.vault_created = True
                    st.rerun()
            else:
                st.error("System Error: vault_1.png missing.")

    if st.session_state.vault_created:
        st.success("✅ Secure Vault Created Successfully")

        st.download_button(
            "🔑 DOWNLOAD MASTER KEY",
            st.session_state.m_key,
            "master_key.key",
            "application/octet-stream",
            use_container_width=True
        )

        st.download_button(
            "📥 DOWNLOAD VAULT IMAGE",
            st.session_state.final_img,
            "vault.png",
            "image/png",
            use_container_width=True
        )

        st.divider()

        if st.button("🗑 WIPE SESSION & START OVER", use_container_width=True):
            reset_and_clear()

    if st.button("← Back to Menu"):
        reset_and_clear()


# ---------------- RECOVER ----------------
elif st.session_state.page == "recover":

    st.markdown("""
    <div class="main-card">
        <div class="hero-title" style="font-size:30px;">📥 Recover Data</div>
        <div class="hero-sub">Upload vault image and master key</div>
    </div>
    """, unsafe_allow_html=True)

    r_img = st.file_uploader(
        "Step 1: Upload Vault Image",
        type=["png"]
    )

    r_key_file = st.file_uploader(
        "Step 2: Upload Master Key",
        type=["key", "txt"]
    )

    if r_img and r_key_file:
        if st.button("EXTRACT FILE", use_container_width=True, type="primary"):
            with st.spinner("Decrypting vault..."):

                master_key = r_key_file.read().decode().strip()

                recovered_bytes, metadata = process_recovery(
                    r_img,
                    master_key
                )

                if recovered_bytes:
                    kind = filetype.guess(recovered_bytes)

                    ext = kind.extension if kind else "bin"
                    mime = kind.mime if kind else "application/octet-stream"

                    st.success("✅ File Successfully Extracted")

                    st.markdown(f"""
                    <div class="meta-box">
                        <h4 style="margin-top:0;">📄 File Metadata</h4>
                        <b>File Name:</b> {metadata['filename']}<br><br>
                        <b>File Type:</b> {ext.upper()}<br><br>
                        <b>File Size:</b> {round(metadata['size']/1024,2)} KB<br><br>
                        <b>Vault Created:</b> {metadata['created_at']}<br><br>
                        <b>Status:</b> Verified
                    </div>
                    """, unsafe_allow_html=True)

                    st.download_button(
                        "📥 DOWNLOAD RECOVERED FILE",
                        recovered_bytes,
                        metadata["filename"],
                        mime,
                        use_container_width=True
                    )

                else:
                    st.error("❌ Recovery Failed. Incorrect key or damaged vault.")

    st.divider()

    if st.button("← Back to Main Menu"):
        reset_and_clear()
