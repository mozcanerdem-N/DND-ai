import streamlit as st
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- 1. SAYFA AYARLARI VE CSS ---
st.set_page_config(page_title="MEB Asistanı", page_icon="🎓", layout="wide")

# Görseldeki siyah çerçeve stilini korumak için basit bir dokunuş
st.markdown("""
    <style>
    .stChatFloatingInputContainer {padding-bottom: 20px;}
    .block-container {padding-top: 2rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI VE MODEL HAZIRLIĞI ---
@st.cache_resource
def load_data():
    # Embedding modelini yüklüyoruz
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Veri tabanını klasörden yüklüyoruz
    vector_db = Chroma(persist_directory="./okul_asistani_db", embedding_function=embeddings)
    return vector_db

# --- 3. SOL KENAR ÇUBUĞU (SIDEBAR) ---
with st.sidebar:
    # MENÜ (En üstte)
    st.markdown("### 📋 MENÜ")
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.page = "Chat"
    if st.button("📊 İstatistikler", use_container_width=True):
        st.session_state.page = "İstatistikler"
    if st.button("📜 Hikaye Özeti", use_container_width=True):
        st.session_state.page = "Hikaye Özeti"
    if st.button("🎒 Çanta", use_container_width=True):
        st.session_state.page = "Çanta"
    
    st.divider()

    # API ANAHTARI
    st.markdown("### 🔑 API ANAHTARI")
    api_key = st.text_input("Groq API Key", type="password", label_visibility="collapsed").strip()
    
    # OYUN & SAVE DOSYASI (Görseldeki butonlar)
    st.markdown("### 🎮 OYUN DOSYASI")
    c1, c2, c3 = st.columns(3)
    c1.button("🟥", key="g1")
    c2.button("⬆️", key="g2")
    c3.button("⬇️", key="g3")

    st.markdown("### 💾 SAVE DOSYASI")
    s1, s2, s3 = st.columns(3)
    s1.button("🟥", key="s1")
    s2.button("⬆️", key="s2")
    s3.button("⬇️", key="s3")

# API Key kontrolü
if not api_key:
    st.info("👈 Lütfen sol taraftaki panelden Groq API anahtarınızı girerek başlayın.")
    st.stop()

# Gerekli nesneleri başlat
client = Groq(api_key=api_key)
vector_db = load_data()

# --- 4. SORGULAMA MANTIĞI ---
def okul_asistani_sorgula(soru):
    docs = vector_db.similarity_search(soru, k=5)
    baglam = "\n\n".join([doc.page_content for doc in docs])

    system_prompt = f"""Sen MEB Ortaöğretim Kurumları Yönetmeliği konusunda uzmansın.
    [BURAYA SENİN PAYLAŞTIĞIN TÜM KRİTİK KURALLAR VE EK BİLGİLER GELECEK - Kısalık için özetlendi]
    Bağlam: {baglam}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Soru: {soru}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=1000
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

# --- 5. ANA EKRAN (LAYOUT) ---
if 'page' not in st.session_state:
    st.session_state.page = "Chat"

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Layout Çerçevesi
with st.container(border=True):
    st.subheader(f"LAYOUT ({st.session_state.page.upper()})")
    
    if st.session_state.page == "Chat":
        # Mesaj geçmişini göster
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    else:
        st.write(f"{st.session_state.page} sayfası henüz yapım aşamasında.")

# Alt kısımdaki Chat Input
if prompt := st.chat_input("Yönetmelik hakkında bir soru sorun..."):
    if st.session_state.page == "Chat":
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Ekranı anlık güncellemek için st.rerun() kullanılabilir veya direkt mesaj yazdırılabilir
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Yönetmelik taranıyor..."):
                cevap = okul_asistani_sorgula(prompt)
                st.write(cevap)
                st.session_state.messages.append({"role": "assistant", "content": cevap})
    else:
        st.warning("Lütfen soru sormak için MENÜ'den Chat sayfasını seçin.")

st.caption("⚠️ MEB Asistanı | Veritabanı: Ortaöğretim Kurumları Yönetmeliği")
