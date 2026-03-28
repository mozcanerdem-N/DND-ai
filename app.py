import streamlit as st
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- 1. SAYFA VE CSS AYARLARI ---
st.set_page_config(page_title="MEB Asistanı", page_icon="🎓", layout="wide")

# Kutunun çizgilerini netleştiren ve tasarımı sabitleyen CSS
st.markdown("""
    <style>
    .main-border {
        border: 2px solid #555; 
        border-radius: 15px; 
        padding: 25px;
        margin-top: 10px;
        background-color: #1e1e1e;
    }
    .stChatFloatingInputContainer {padding-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI YÜKLEME (CACHE) ---
@st.cache_resource
def load_data():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory="./okul_asistani_db", embedding_function=embeddings)
    return vector_db

# --- 3. SOL KENAR ÇUBUĞU (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 📋 MENÜ")
    # Sayfa geçiş butonları
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.page = "Chat"
    if st.button("📊 İstatistikler", use_container_width=True):
        st.session_state.page = "İstatistikler"
    if st.button("📜 Hikaye Özeti", use_container_width=True):
        st.session_state.page = "Hikaye Özeti"
    if st.button("🎒 Çanta", use_container_width=True):
        st.session_state.page = "Çanta"
    
    st.divider()

    st.markdown("### 🔑 API ANAHTARI")
    api_key = st.text_input("Groq API Key", type="password", label_visibility="collapsed").strip()
    
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

# API Anahtarı yoksa sistemi durdur
if not api_key:
    st.info("👈 Lütfen sol taraftan Groq API anahtarınızı girin.")
    st.stop()

# Nesneleri başlat
client = Groq(api_key=api_key)
vector_db = load_data()

# --- 4. SORGULAMA FONKSİYONU ---
def okul_asistani_sorgula(soru):
    docs = vector_db.similarity_search(soru, k=5)
    baglam = "\n\n".join([doc.page_content for doc in docs])

    # [Daha önce paylaştığın tüm kuralları içeren prompt buraya gelecek]
    system_prompt = f"Sen MEB uzmanısın. Kurallara uy. Bağlam: {baglam}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": soru}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 5. ANA EKRAN (LAYOUT) ---
if 'page' not in st.session_state:
    st.session_state.page = "Chat"
if 'messages' not in st.session_state:
    st.session_state.messages = []

# BURASI ÖNEMLİ: Mesajların içine yazılacağı konteynırı en başta tanımlıyoruz
with st.container():
    # Görseldeki kutu yapısını başlatıyoruz
    st.markdown(f'<div class="main-border">', unsafe_allow_html=True)
    st.subheader(f"LAYOUT ({st.session_state.page.upper()})")
    
    # Mesajların basılacağı alan
    chat_area = st.container()
    
    with chat_area:
        if st.session_state.page == "Chat":
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        else:
            st.write(f"Şu an {st.session_state.page} sayfasındasınız.")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. CHAT INPUT ---
if prompt := st.chat_input("Yönetmelik hakkında bir soru sorun..."):
    if st.session_state.page == "Chat":
        # Mesajı listeye ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Cevap üret ve listeye ekle
        cevap = okul_asistani_sorgula(prompt)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        
        # Sayfayı hemen yenileyerek yeni mesajları kutu içine bas
        st.rerun()
