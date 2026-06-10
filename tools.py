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

# 🔥 SOTA HAMLE V2: Tablolar arası köprüleri ve ilişkileri (Ontoloji) ajana öğretiyoruz
custom_hints = {
    "customers": """CREATE TABLE customers (
        customer_id TEXT,
        customer_unique_id TEXT,
        customer_zip_code_prefix INTEGER,
        customer_city TEXT,
        customer_state TEXT
    );
    /* ⚠️ MÜHENDİSLİK NOTU:
    Müşterilerin şehir (customer_city) bilgilerini ödemeler veya sipariş kalemleriyle bağlamak için DOĞRUDAN 'orders' tablosunu kullanmalısınız.
    İlişki: customers.customer_id = orders.customer_id
    */""",

    "orders": """CREATE TABLE orders (
        order_id TEXT,
        customer_id TEXT,
        order_status TEXT,
        order_purchase_timestamp TEXT
    );
    /* ⚠️ MÜHENDİSLİK NOTU (KONTROL KÖPRÜSÜ):
    Bu tablo veritabanının merkez köprüsüdür!
    1. Şehir bazlı ödeme analizlerinde (Örn: Rio'dan verilen siparişler nasıl ödenmiş?):
       customers -> orders -> order_payments tablolarını sırasıyla JOIN yapmalısınız.
       Bağlantı: customers.customer_id = orders.customer_id AND orders.order_id = order_payments.order_id
    */""",

    "order_items": """CREATE TABLE order_items (
        order_id TEXT,
        order_item_id INTEGER,
        product_id TEXT,
        seller_id TEXT,
        price REAL,
        freight_value REAL
    );
    /* ⚠️ KRİTİK ANALİZ KURALLARI:
    1. Satıcıların (seller_id) elde ettiği toplam GELİR hesaplanırken BU tablodaki 'price' sütunu toplanmalıdır -> SUM(price).
    2. Satıcı bazlı ciro analizlerinde ASLA 'order_payments' tablosunu kullanmayın.
    */""",
    
    "order_payments": """CREATE TABLE order_payments (
        order_id TEXT,
        payment_sequential INTEGER,
        payment_type TEXT,
        payment_installments INTEGER,
        payment_value REAL
    );
    /* ⚠️ KRİTİK ANALİZ KURALLARI:
    1. Bu tablo siparişlerin ödeme yöntemlerini (payment_type) içerir.
    2. Şehir bazlı ödeme sorgularında 'orders' ve 'customers' tablolarıyla 'order_id' üzerinden JOIN yapılarak kullanılmalıdır.
    */"""
}

# köprü oluşturma
db = SQLDatabase.from_uri(
    f"sqlite:///{FULL_DB_PATH}", 
    custom_table_info=custom_hints
)

# creativity istemediğimiz için temperature 0 yapıyoruz
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

## llm ve db'yi burada bağlayarak bir toolkit oluşturuyoruz
toolkit = SQLDatabaseToolkit(llm=llm, db=db, top_k=5) 
tools = toolkit.get_tools()