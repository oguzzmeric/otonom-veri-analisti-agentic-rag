import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

# key upload
load_dotenv()

# Bulut ve lokal uyumluluğu için mutlak yol (Absolute Path) hesabı
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FULL_DB_PATH = os.path.join(BASE_DIR, "database", "olist.db")

# 🔥 SOTA HAMLE: Ajanın labirentte kaybolmasını engelleyen özel şema ipuçları (Data Catalog)
custom_hints = {
    "order_items": """CREATE TABLE order_items (
        order_id TEXT,
        order_item_id INTEGER,
        product_id TEXT,
        seller_id TEXT,
        shipping_limit_date TEXT,
        price REAL,
        freight_value REAL
    );
    /* ⚠️ KRİTİK ANALİZ KURALLARI (MÜHENDİSLİK NOTU):
    1. Satıcıların (seller_id) elde ettiği toplam GELİR, CİRO veya KAZANÇ hesaplanırken BU tablodaki 'price' sütunu toplanmalıdır -> SUM(price).
    2. Bir satıcının yaptığı "en çok satış" veya "sipariş adedi", bu tablodaki satır sayısıdır -> COUNT(order_id).
    3. Satıcı bazlı ciro analizlerinde ASLA 'order_payments' tablosunu kullanmayın ve onunla JOIN yapmayın. 'order_payments' tablosu mükerrer (duplicate) sonuçlar üretir ve hesaplamayı patlatır.
    */""",
    
    "order_payments": """CREATE TABLE order_payments (
        order_id TEXT,
        payment_sequential INTEGER,
        payment_type TEXT,
        payment_installments INTEGER,
        payment_value REAL
    );
    /* ⚠️ KRİTİK ANALİZ KURALLARI (MÜHENDİSLİK NOTU):
    1. Bu tablo sadece genel sipariş ödemelerini içerir. 
    2. SATICI (seller_id) bazlı ciro, kazanç veya gelir hesaplamalarında BU TABLOYU KULLANMAYIN. Satıcı cirosu sadece 'order_items' tablosundaki 'price' sütunundan hesaplanır.
    */"""
}

# köprü oluşturma (Özel ipuçlarını veritabanı motoruna bağlıyoruz)
db = SQLDatabase.from_uri(
    f"sqlite:///{FULL_DB_PATH}", 
    custom_table_info=custom_hints
)

# creativity istemediğimiz için temperature 0 yapıyoruz
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

## llm ve db'yi burada bağlayarak bir toolkit oluşturuyoruz
toolkit = SQLDatabaseToolkit(llm=llm, db=db, top_k=5) 
tools = toolkit.get_tools()