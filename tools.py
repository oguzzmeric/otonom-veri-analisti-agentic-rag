import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

#key upload
load_dotenv()

# 🔥 KANKA DEĞİŞİKLİK BURADA: Bulut ve lokal uyumluluğu için mutlak yol (Absolute Path) hesabı
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FULL_DB_PATH = os.path.join(BASE_DIR, "database", "olist.db")

#köprü oluşturma (Başına f ve 3 adet / koyarak tam mutlak yolu enjekte ediyoruz)
db = SQLDatabase.from_uri(f"sqlite:///{FULL_DB_PATH}") #SQLDatabase, bir SQL veritabanına bağlanmak ve sorgular çalıştırma

#creativity istemediğimiz için temperature 0 yapıyoruz
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

##llm ve db'yi burada bağlayarak bir toolkit oluşturuyoruz
toolkit = SQLDatabaseToolkit(llm=llm, db=db, top_k=5) 
tools = toolkit.get_tools()

#sqldatabase parametreleri şunlardır:
#llm: SQL sorgularını oluşturmak ve yorumlamak için kullanılan dil modeli.
#db: veritabanı bağlantısı.
#top_k: SQL sorgularını oluştururken dikkate alınacak en fazla sorgu sayısı    tools budur