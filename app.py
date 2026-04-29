import streamlit as st
from stegano import lsb
from cryptography.fernet import Fernet
from PIL import Image
import io
import os
import filetype

# --- LOGIC: ENCRYPTION ---
def process_encryption(uploaded_file, carrier_img_path):
    key = Fernet.generate_key()  # Unique key for every file
    cipher = Fernet(key)

    encrypted_data = cipher.encrypt(uploaded_file.read())

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
        img = Image.open(stego_image).convert("RGB")
        hidden_data = lsb.reveal(img)

        # Decrypt using uploaded key
        cipher = Fernet(master_key.encode())
        decrypted_data = cipher.decrypt(hidden_data.encode("latin-1"))

        return decrypted_data

    except Exception:
        return None


# --- INITIALIZE STATE ---
if "page" not in st.session_state:
    st.session_state.page = "home"

if "vault_created" not in st.session_state:
    st.session_state.vault_created = False


# --- RESET FUNCTION ---
def reset_and_clear():
    st.session_state.clear()
    st.rerun()


# --- PAGE: HOME ---
if st.session_state.page == "home":
    st.title("🛡️ Shadow-Vault")

    if st.button("MAKE FILE SECURE", use_container_width=True, type="primary"):
        st.session_state.page = "convert"
        st.rerun()

    if st.button("RECOVER A SECURE FILE", use_container_width=True):
        st.session_state.page = "recover"
        st.rerun()


# --- PAGE: CONVERT ---
elif st.session_state.page == "convert":
    st.title("📤 Secure a File")

    u_file = st.file_uploader(
        "Browse and upload your secret file",
        type=["pdf", "zip", "docx", "txt"],
        key="file_input"
    )

    if u_file and not st.session_state.vault_created:
        if st.button("GENERATE VAULT", use_container_width=True, type="primary"):
            if os.path.exists("vault_1.png"):
                with st.spinner("Locking data securely..."):
                    final_img, m_key = process_encryption(u_file, "vault_1.png")

                    st.session_state.final_img = final_img
                    st.session_state.m_key = m_key
                    st.session_state.vault_created = True

                    st.rerun()
            else:
                st.error("System Error: 'vault_1.png' missing.")


    if st.session_state.vault_created:
        st.success("✅ Vault Created Successfully!")
        st.info("🔐 Download and store your Master Key safely. It is required for recovery.")

        # Download Master Key
        st.download_button(
            label="🔑 DOWNLOAD MASTER KEY",
            data=st.session_state.m_key,
            file_name="master_key.key",
            mime="text/plain",
            use_container_width=True
        )

        # Download Vault Image
        st.download_button(
            label="📥 DOWNLOAD VAULT IMAGE",
            data=st.session_state.final_img,
            file_name="vault.png",
            mime="image/png",
            use_container_width=True
        )

        st.divider()

        if st.button("WIPE SESSION & START OVER", use_container_width=True):
            reset_and_clear()

    if st.button("← Back to Menu"):
        reset_and_clear()


# --- PAGE: RECOVER ---
elif st.session_state.page == "recover":
    st.title("📥 Recover Data")

    r_img = st.file_uploader(
        "Step 1: Upload your Vault Image",
        type=["png"]
    )

    r_key_file = st.file_uploader(
        "Step 2: Upload Master Key",
        type=["key", "txt"]
    )

    if r_img and r_key_file:
        if st.button("EXTRACT FILE", use_container_width=True, type="primary"):
            with st.spinner("Decrypting securely..."):

                master_key = r_key_file.read().decode().strip()

                recovered_bytes = process_recovery(r_img, master_key)

                if recovered_bytes:
                    kind = filetype.guess(recovered_bytes)

                    ext = kind.extension if kind else "bin"
                    mime = kind.mime if kind else "application/octet-stream"

                    st.success(f"✅ {ext.upper()} File Successfully Extracted!")

                    st.download_button(
                        label="📥 DOWNLOAD RECOVERED FILE",
                        data=recovered_bytes,
                        file_name=f"decrypted_vault_file.{ext}",
                        mime=mime,
                        use_container_width=True
                    )

                else:
                    st.error("❌ Recovery Failed. Wrong key or damaged vault image.")

    st.divider()

    if st.button("← Back to Main Menu"):
        reset_and_clear()
