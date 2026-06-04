from tools import toolkit, db, llm
from langchain_community.agent_toolkits import create_sql_agent

print("Agent oluşturuluyor...")

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="tool-calling"
)

soru = "Veritabanında toplam kaç adet müşteri (customers) var? Sadece sayıyı söyle."
print(f"Patronun Sorusu: {soru}\n" + "-"*30)

# Sistemin çalışması (Ateşleme)
cevap = agent_executor.invoke({"input": soru})

print("\n" + "="*30)
print(f"Ajanın Final Cevabı: {cevap['output']}")