import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

#key upload
load_dotenv()

#köprü oluşturma
db_path = "sqlite:///database/olist.db"
db = SQLDatabase.from_uri(db_path) #SQLDatabase, bir SQL veritabanına bağlanmak ve sorgular çalıştırma

#creativity istemediğimiz için temperature 0 yapıyoruz
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

##llm ve db'yi burada bağlayarak bir toolkit oluşturuyoruz
toolkit = SQLDatabaseToolkit(llm=llm, db=db, top_k=5) 
tools = toolkit.get_tools()

#sqldatabase parametreleri şunlardır:
#llm: SQL sorgularını oluşturmak ve yorumlamak için kullanılan dil modeli.
#db: veritabanı bağlantısı.
#top_k: SQL sorgularını oluştururken dikkate alınacak en fazla sorgu sayısı