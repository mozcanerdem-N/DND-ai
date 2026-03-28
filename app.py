import streamlit as st

# Sayfa Genişliği Ayarı
st.set_page_config(layout="wide")

# --- SOL KENAR ÇUBUĞU (SIDEBAR) ---
with st.sidebar:
    # 1. MENÜ KISMI (İsteğin üzerine en üstte)
    st.markdown("### MENÜ")
    if st.button("Chat", use_container_width=True):
        st.session_state.page = "Chat"
    if st.button("İstatistikler", use_container_width=True):
        st.session_state.page = "İstatistikler"
    if st.button("Hikaye Özeti (Geçmiş)", use_container_width=True):
        st.session_state.page = "Hikaye Özeti"
    if st.button("Çanta", use_container_width=True):
        st.session_state.page = "Çanta"
    
    st.divider() # Görsel ayrım için

    # 2. API ANAHTARI
    st.markdown("### API ANAHTARI")
    api_key = st.text_input("Anahtarınızı girin", type="password", label_visibility="collapsed")

    # 3. OYUN DOSYASI
    st.markdown("### OYUN DOSYASI")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("🗑️", key="game_stop")
    with col2:
        st.button("⬆️", key="game_up")
    with col3:
        st.button("⬇️", key="game_down")

    # 4. SAVE DOSYASI
    st.markdown("### SAVE DOSYASI")
    scol1, scol2, scol3 = st.columns(3)
    with scol1:
        st.button("🗑️", key="save_stop")
    with scol2:
        st.button("⬆️", key="save_up")
    with scol3:
        st.button("⬇️", key="save_down")

# --- ANA İÇERİK ALANI (LAYOUT - DEĞİŞEN KISIM) ---

# Sayfa durumu kontrolü (Başlangıçta 'Chat' açık gelsin)
if 'page' not in st.session_state:
    st.session_state.page = "Chat"

# Dinamik içerik çerçevesi
with st.container(border=True):
    st.subheader(f"LAYOUT ({st.session_state.page.upper()})")
    
    # Burası sayfa içeriğine göre değişen kısımdır
    st.write(f"Şu an {st.session_state.page} sayfasındasınız.")
    
    # Görseldeki alt boşluk (placeholder)
    for _ in range(15):
        st.write("")

# Alt kısımdaki giriş alanı (Input + Ok butonu)
footer_col1, footer_col2 = st.columns([0.9, 0.1])
with footer_col1:
    user_input = st.text_input("Mesajınızı yazın...", label_visibility="collapsed")
with footer_col2:
    st.button("➡️")
