import streamlit as st
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(page_title="MEB Asistanı", page_icon="🎓", layout="wide")

# CSS: Beyaz borderları kaldırdık, sadece hizalama bıraktık
st.markdown("""
    <style>
    .main-layout {
        padding: 10px;
        margin-bottom: 20px;
    }
    .stChatFloatingInputContainer {padding-bottom: 20px;}
    /* Sidebar butonlarını daha şık yapalım */
    .stButton>button {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI VE MODEL HAZIRLIĞI (CACHE) ---
@st.cache_resource
def load_data():
    # Embedding modelini yüklüyoruz
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Veri tabanını klasörden yüklüyoruz (Klasör adının doğruluğundan emin ol)
    vector_db = Chroma(persist_directory="./okul_asistani_db", embedding_function=embeddings)
    return vector_db

# --- 3. SOL KENAR ÇUBUĞU (SIDEBAR) ---
with st.sidebar:
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

    # Sohbeti temizleme butonu (opsiyonel ama faydalı)
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# API Key kontrolü
if not api_key:
    st.info("👈 Lütfen sol taraftaki panelden Groq API anahtarınızı girerek başlayın.")
    st.stop()

# Gerekli nesneleri başlat
client = Groq(api_key=api_key)
vector_db = load_data()

# --- 4. SORGULAMA FONKSİYONU (SENİN ÖZEL KURALLARIN) ---
def okul_asistani_sorgula(soru):
    docs = vector_db.similarity_search(soru, k=5)
    baglam = "\n\n".join([doc.page_content for doc in docs])

    # Senin paylaştığın o uzun ve detaylı sistem promptu
    system_prompt = f"""Sen MEB Ortaöğretim Kurumları Yönetmeliği konusunda uzman, teknik ve resmi bir asistansın.
    Kritik Kurallar:
    1. SADECE sana verilen 'Bağlam' içindeki bilgileri kullan.
    2. Eğer cevap bağlamda yoksa, 'Bu konuyla ilgili yönetmelikte net bir bilgi bulamadım' de.
    3. Cevaplarını maddeler halinde ve resmi bir dille ver.
    [... Diğer tüm kuralların buraya dahil edildiğini varsayıyoruz ...]
    Bağlam:
    {baglam}
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
        return f"Hata: {str(e)}"

# --- 5. ANA EKRAN VE MESAJ YÖNETİMİ ---
if 'page' not in st.session_state:
    st.session_state.page = "Chat"
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Ana Konteynır (Beyaz çizgisiz, temiz layout)
main_container = st.container()

with main_container:
    st.markdown(f'<div class="main-layout"><h3>LAYOUT ({st.session_state.page.upper()})</h3>', unsafe_allow_html=True)
    
    # Mesajların basılacağı alan
    chat_placeholder = st.container()
    
    with chat_placeholder:
        if st.session_state.page == "Chat":
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        else:
            st.info(f"{st.session_state.page} sayfası şu an geliştirme aşamasında.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. CHAT INPUT (MESAJ GİRİŞİ) ---
if prompt := st.chat_input("Yönetmelik hakkında bir soru sorun..."):
    if st.session_state.page == "Chat":
        # Kullanıcı mesajını kaydet
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Cevap üret ve kaydet
        cevap = okul_asistani_sorgula(prompt)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        
        # Sayfayı yenileyerek her şeyi LAYOUT başlığı altına diz
        st.rerun()

st.caption("⚠️ MEB Asistanı | Veritabanı: Ortaöğretim Kurumları Yönetmeliği")
