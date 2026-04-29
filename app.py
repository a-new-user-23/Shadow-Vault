import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
import io
import os
import json
import base64
import filetype
from datetime import datetime

# --- LOGIC: ENCRYPTION ---
def process_encryption(uploaded_file, carrier_img_path):
    key = Fernet.generate_key()
    cipher = Fernet(key)

    # Read original file bytes
    original_bytes = uploaded_file.read()

    # Collect metadata
    payload = {
        "filename": uploaded_file.name,
        "size": len(original_bytes),
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "filedata": base64.b64encode(original_bytes).decode("utf-8")
    }

    # Convert payload to JSON string
    payload_json = json.dumps(payload)

    # Encrypt payload
    encrypted_data = cipher.encrypt(payload_json.encode())

    # Hide encrypted payload in image
    stego_img = lsb.hide(
        carrier_img_path,
        encrypted_data.decode("latin-1")
    )

    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")

    return buf.getvalue(), key.decode()


# --- LOGIC: RECOVERY ---
def process_recovery(stego_image, master_key):
    try:
        # Extract hidden encrypted data
        hidden_data = lsb.reveal(stego_image)

        # Decrypt
        cipher = Fernet(master_key.encode())
        decrypted_json = cipher.decrypt(hidden_data.encode("latin-1")).decode()

        # Parse JSON payload
        payload = json.loads(decrypted_json)

        # Recover original bytes
        recovered_bytes = base64.b64decode(payload["filedata"])

        return recovered_bytes, payload

    except Exception:
        return None, None


# --- INITIALIZE STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'vault_created' not in st.session_state:
    st.session_state.vault_created = False


def reset_and_clear():
    for key in list(st.session_state.keys()):
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

    u_file = st.file_uploader(
        "Browse and upload your secret file",
        type=['pdf', 'zip', 'docx', 'txt'],
        key="file_input"
    )

    # -------- 10 MB CHECK --------
    if u_file is not None:
        file_size = len(u_file.getvalue())
        max_size = 10 * 1024 * 1024

        if file_size > max_size:
            st.error("❌ File size too large. Maximum allowed size is 10 MB.")
            st.stop()
    # -----------------------------

    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT", use_container_width=True, type="primary"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking data..."):
                    final_img, master_key = process_encryption(u_file, "vault_1.png")

                    st.session_state.final_img = final_img
                    st.session_state.m_key = master_key.encode()
                    st.session_state.vault_created = True
                    st.rerun()
            else:
                st.error("System Error: 'vault_1.png' missing.")

    if st.session_state.vault_created:
        st.success("✅ Vault Created!")

        # Download key file
        st.download_button(
            "🔑 DOWNLOAD MASTER KEY",
            st.session_state.m_key,
            "master_key.key",
            "application/octet-stream",
            use_container_width=True
        )

        # Download vault image
        st.download_button(
            "📥 DOWNLOAD VAULT IMAGE",
            st.session_state.final_img,
            "vault.png",
            "image/png",
            use_container_width=True
        )

        st.divider()

        if st.button("WIPE SESSION & START OVER", use_container_width=True):
            reset_and_clear()

    if st.button("← Back to Menu"):
        reset_and_clear()


# --- PAGE: RECOVER ---
elif st.session_state.page == 'recover':
    st.title("📥 Recover Data")

    r_img = st.file_uploader(
        "Step 1: Upload your Vault Image",
        type=['png']
    )

    r_key_file = st.file_uploader(
        "Step 2: Upload Master Key",
        type=['key', 'txt']
    )

    if r_img and r_key_file:
        if st.button("EXTRACT FILE", use_container_width=True, type="primary"):
            with st.spinner("Decrypting..."):
                master_key = r_key_file.read().decode().strip()

                recovered_bytes, metadata = process_recovery(
                    r_img,
                    master_key
                )

                if recovered_bytes:
                    kind = filetype.guess(recovered_bytes)

                    ext = kind.extension if kind else "bin"
                    mime = kind.mime if kind else "application/octet-stream"

                    st.success("✅ File Successfully Extracted!")

                    # -------- METADATA --------
                    st.subheader("📄 File Metadata")
                    st.info(
                        f"""
**File Name:** {metadata['filename']}

**File Type:** {ext.upper()}

**File Size:** {round(metadata['size'] / 1024, 2)} KB

**Vault Created:** {metadata['created_at']}

**Status:** Verified
"""
                    )
                    # --------------------------

                    st.download_button(
                        "📥 DOWNLOAD RECOVERED FILE",
                        recovered_bytes,
                        metadata["filename"],
                        mime,
                        use_container_width=True
                    )

                else:
                    st.error("❌ Recovery Failed. Incorrect key or damaged image.")

    st.divider()

    if st.button("← Back to Main Menu"):
        reset_and_clear()
