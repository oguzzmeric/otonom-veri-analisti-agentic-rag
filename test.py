from tools import toolkit, db, llm
from langchain_community.agent_toolkits import create_sql_agent

print("Agent oluşturuluyor...")

agent_executor = create_sql_agent(
    llm=llm,#zeka modeli
    toolkit=toolkit,#toolkit, SQL sorgularını oluşturmak ve yorumlamak için kullanılan araç seti
    verbose=True,#ajanın her adımını ayrıntılı olarak gösterir
    agent_type="tool-calling"#önce tool çağırır sonra cevaba döner
)


soru = "en çok sipariş hangi şehirden verildi?"
print(f"Patronun Sorusu: {soru}\n" + "-"*30)

# Sistemin çalışması (Ateşleme)
cevap = agent_executor.invoke({"input": soru})

print("\n" + "="*30)
print(f"Ajanın Final Cevabı: {cevap['output']}")