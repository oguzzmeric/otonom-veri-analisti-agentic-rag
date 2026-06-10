import streamlit as st
from graph_engine import app as agent_app

# 1. Sayfa Ayarları ve Görsel Tema
st.set_page_config(
    page_title="Otonom Veri Analisti", 
    page_icon="📊", 
    layout="centered"
)

st.title("📊 Otonom Veri Analisti")
st.caption("LangGraph & SOTA Döngüsel Mimari ile Kendi Kendini İyileştiren SQL Ajanı")
st.write("---")

# 2. Sohbet Hafızasını (Session State) Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba patron! Veritabanındaki tablolarla ilgili neyi analiz etmemi istersin?"}
    ]

# 3. Geçmiş Mesajları Ekrana Çizme
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Kullanıcı Girdisi ve Ajanın Tetiklenmesi
if user_query := st.chat_input("Örn: São Paulo şehrindeki en karlı 3 kategori nedir?"):
    
    # Kullanıcı mesajını hafızaya ekle ve ekrana bas
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # Asistan rolünde spinner (yükleniyor animasyonu) başlat
    with st.chat_message("assistant"):
        with st.spinner("Ajan departmanları çalışıyor: Şema okunuyor, SQL yazılıyor ve test ediliyor..."):
            try:
                inputs = {"question": user_query}
                
                # RECURSION LIMIT: Ajanın en fazla 5 kere döngüye girmesine izin veriyoruz.
                # Bu sınır, ajanın kendini tamir etmesi (Self-Healing) için yeterli alanı tanırken, 
                # hata döngüsüne girip 429 token limitini patlatmasını kesin olarak engeller.
                config = {"recursion_limit": 5}
                
                # Arka plandaki LangGraph motoruna soruyu ve güvenlik ayarını kargoluyoruz
                result = agent_app.invoke(inputs, config=config)
                
                # KORUMA KÖPRÜSÜ: Çantadan veri çekerken hem 'final_report' hem de 'final_rapor' 
                # anahtarlarını kontrol ederek isim uyuşmazlığı riskini sıfıra indiriyoruz.
                cevap = result.get("final_report") or result.get("final_rapor") or "Rapor üretilirken sistemsel bir hata oluştu."
                
            except Exception as e:
                cevap = f"Şantiyede beklenmedik bir arıza oluştu: {str(e)}"
        
        # Temizlenen cevabı ekrana bas ve hafızaya mühürle
        st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})