import streamlit as st
from groq import Groq
import random

# --- SAYFA ---
st.set_page_config(layout="wide")

# --- SESSION ---
if "page" not in st.session_state:
    st.session_state.page = "chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# --- CSS (görünüm) ---
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}
.left-panel {
    border-right: 2px solid #ccc;
    padding: 10px;
}
.menu-btn {
    width: 100%;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

# --- LAYOUT ---
left, right = st.columns([1, 4])

# =========================
# 📌 SOL PANEL
# =========================
with left:
    st.markdown("### API ANAHTARI")
    api = st.text_input("Groq API Key", type="password")

    if api:
        st.session_state.api_key = api

    st.markdown("---")
    st.markdown("### OYUN DOSYASI")
    st.file_uploader("Yükle", type=["json"])

    st.markdown("### SAVE DOSYASI")
    st.file_uploader("Yükle", type=["json"], key="save")

    st.markdown("---")
    st.markdown("### MENÜ")

    if st.button("💬 Chat", use_container_width=True):
        st.session_state.page = "chat"

    if st.button("📊 İstatistikler", use_container_width=True):
        st.session_state.page = "stats"

    if st.button("📜 Hikaye Özeti", use_container_width=True):
        st.session_state.page = "story"

    if st.button("🎒 Çanta", use_container_width=True):
        st.session_state.page = "inventory"

# =========================
# 📌 SAĞ PANEL (DEĞİŞEN)
# =========================
with right:

    # 🔹 CHAT EKRANI
    if st.session_state.page == "chat":

        st.markdown("## 💬 Chat")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        prompt = st.chat_input("Mesaj yaz...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Düşünüyor..."):

                    if not st.session_state.api_key:
                        cevap = "API key girmen lazım 😄"
                    else:
                        client = Groq(api_key=st.session_state.api_key)

                        cevap = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": "Sen bir RPG oyun anlatıcısısın."},
                                {"role": "user", "content": prompt}
                            ],
                            model="llama-3.1-8b-instant"
                        ).choices[0].message.content

                    st.write(cevap)
                    st.session_state.messages.append({"role": "assistant", "content": cevap})

    # 🔹 İSTATİSTİK
    elif st.session_state.page == "stats":
        st.markdown("## 📊 İstatistikler")
        st.write("HP: 30")
        st.write("Strength: 5")

    # 🔹 HİKAYE ÖZETİ
    elif st.session_state.page == "story":
        st.markdown("## 📜 Hikaye Özeti")
        st.write("Henüz kayıtlı bir olay yok.")

    # 🔹 ENVANTER
    elif st.session_state.page == "inventory":
        st.markdown("## 🎒 Çanta")
        st.write("- Kılıç")
        st.write("- İksir")
