import streamlit as st
from groq import Groq
import random

# --- SAYFA AYARI ---
st.set_page_config(layout="wide")

# --- SESSION ---
if "page" not in st.session_state:
    st.session_state.page = "chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# --- CSS FIXLER ---
st.markdown("""
<style>

/* ÜST BOŞLUK FIX */
.block-container {
    padding-top: 0.5rem !important;
}

/* BAŞLIK FIX */
h1, h2, h3 {
    margin-top: 0px !important;
    padding-top: 0px !important;
}

/* SOL PANEL ÜSTE YAPIŞTIR */
section[data-testid="column"] > div {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

/* CHAT CONTAINER */
.chat-container {
    height: 70vh;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #444;
    border-radius: 10px;
}

/* BUTON FULL WIDTH */
button {
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# --- LAYOUT ---
left, right = st.columns([1, 4])

# =========================
# 📌 SOL PANEL
# =========================
with left:
    st.markdown("### 🔑 API ANAHTARI")
    api = st.text_input("Groq API Key", type="password")

    if api:
        st.session_state.api_key = api

    st.markdown("---")

    st.markdown("### 📂 OYUN DOSYASI")
    st.file_uploader("Yükle", type=["json"])

    st.markdown("### 💾 SAVE DOSYASI")
    st.file_uploader("Yükle", type=["json"], key="save")

    st.markdown("---")

    st.markdown("### 📌 MENÜ")

    if st.button("💬 Chat"):
        st.session_state.page = "chat"

    if st.button("📊 İstatistikler"):
        st.session_state.page = "stats"

    if st.button("📜 Hikaye Özeti"):
        st.session_state.page = "story"

    if st.button("🎒 Çanta"):
        st.session_state.page = "inventory"

# =========================
# 📌 SAĞ PANEL
# =========================
with right:

    # 💬 CHAT
    if st.session_state.page == "chat":

        st.markdown("## 💬 Chat")

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        st.markdown('</div>', unsafe_allow_html=True)

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
                                {"role": "system", "content": "Sen bir DND oyun anlatıcısısın. Oyuncunun eylemlerine göre sahneyi anlat."},
                                {"role": "user", "content": prompt}
                            ],
                            model="llama-3.1-8b-instant"
                        ).choices[0].message.content

                    st.write(cevap)
                    st.session_state.messages.append({"role": "assistant", "content": cevap})

    # 📊 İSTATİSTİK
    elif st.session_state.page == "stats":
        st.markdown("## 📊 İstatistikler")
        st.write("HP: 30")
        st.write("Strength: 5")
        st.write("Intelligence: 3")

    # 📜 HİKAYE
    elif st.session_state.page == "story":
        st.markdown("## 📜 Hikaye Özeti")
        st.write("Henüz olay yok...")

    # 🎒 ENVANTER
    elif st.session_state.page == "inventory":
        st.markdown("## 🎒 Çanta")
        st.write("- Kılıç")
        st.write("- İksir")
