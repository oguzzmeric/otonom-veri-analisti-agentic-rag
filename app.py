import streamlit as st
from graph_engine import app as agent_app
from tools import db  # Veritabanı şemasını sol panele çekmek için ekledik

# 1. Sayfa Ayarları ve Görsel Tema (Wide moda geçtik)
st.set_page_config(
    page_title="Otonom Veri Analisti", 
    page_icon="📊", 
    layout="wide"  
)

# 2. Sol Panel (Sidebar) - Data Catalog
st.sidebar.title("Data catalog")
st.sidebar.write("Olist.db aktif tablolar")
st.sidebar.write("1.200.000 veri")

try:
    # LangChain SQLDatabase nesnesinden veritabanındaki tüm tabloları dinamik çekiyoruz
    tablolar = db.get_usable_table_names()
    for tablo in tablolar:
        # Her tabloyu tıklanabilir akordiyon (expander) içine alıyoruz
        with st.sidebar.expander(f"📦 {tablo}"):
            # Tablonun CREATE TABLE şemasını ve ilk 3 satır örneğini SQL kodu olarak basıyoruz
            tablo_semasi = db.get_table_info([tablo])
            st.code(tablo_semasi, language="sql")
except Exception as e:
    st.sidebar.error(f"Şema yüklenirken hata oluştu: {str(e)}")

st.sidebar.write("---")
st.sidebar.caption("Powered by LangGraph & Streamlit")

# 3. Ana Ekran Başlıkları
st.title("📊 Olist Veri Analisti")
st.caption("LangGraph & SOTA Döngüsel Mimari ile Kendi Kendini İyileştiren SQL Ajanı")
st.write("---")

# 4. Sohbet Hafızasını (Session State) Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba patron! Sol taraftaki 1.200.000 veri ile ilgili tüm soruların için buradayım."}
    ]

# 5. Geçmiş Mesajları Ekrana Çizme
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Kullanıcı Girdisi ve Ajanın Tetiklenmesi
if user_query := st.chat_input("Örn: São Paulo şehrindeki en karlı 3 kategori nedir?"):
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
        
    with st.chat_message("assistant"):
        with st.spinner("Ajan departmanları çalışıyor: Şema okunuyor, SQL yazılıyor ve test ediliyor..."):
            try:
                inputs = {"question": user_query}
                config = {"recursion_limit": 15}
                result = agent_app.invoke(inputs, config=config)
                
                cevap = result.get("final_report") or result.get("final_rapor") or "Rapor üretilirken sistemsel bir hata oluştu."
                
            except Exception as e:
                cevap = f"Şantiyede beklenmedik bir arıza oluştu: {str(e)}"
        
        # Ajanın ürettiği Türkçe cevabı ekrana basıyoruz
        st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        
        # 7. Kaputun Altı (SQL Sorgusunu Gösterme Modülü)
        if "result" in locals() and isinstance(result, dict):
            with st.expander("Çalıştırılan SQL Sorgusu"):
                if "messages" in result:
                    sql_bulundu = False
                    for msg in result["messages"]:
                        icerik = str(msg.content)
                        if "SELECT" in icerik.upper() and "FROM" in icerik.upper():
                            st.code(icerik, language="sql")
                            sql_bulundu = True
                    
                    if not sql_bulundu:
                        st.info("Bu adımda bir SQL sorgusu yakalanamadı veya işlem LLM içinde çözüldü.")
                else:
                    st.json(result)