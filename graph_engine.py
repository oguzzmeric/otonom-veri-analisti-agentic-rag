from typing import TypedDict
from langgraph.graph import StateGraph, END
from tools import llm, db

class AgentState(TypedDict):
    question: str
    sql_query: str
    answer: str   #veritabanı sonucu veya hatlar burda birikir

def sql_yazan(state:AgentState) -> dict:
    # SQL sorgusu oluşturmak için LLM'yi kullan
    
    question = state['question']
    sema = db.get_table_info()

    onceki_hata = state.get('answer', '')  # Önceki hatayı al
    hata_uyarisi = ""
    if "hata" in onceki_hata.lower() or "error" in onceki_hata.lower():
        print("Önceki adımda bir hata oluştu. LLM'ye hata bilgisini iletiyorum.")
        hata_uyarisi = f"Önceki adımda şu hata oluştu: {onceki_hata}. Lütfen bu hatayı göz önünde bulundurarak yeni bir SQL sorgusu oluştur."

    prompt = f"""Sen kıdemli bir SQLite veri analistisin.
    Aşağıdaki veritabanı şemasına bakarak yöneticinin sorusunu cevaplayacak SADECE çalıştırılabilir bir SQL kodu yaz.
    Asla açıklama yapma. Asla markdown (```sql) formatı kullanma. Sadece saf SQL kodunu ver.
    {hata_uyarisi}
    
    Şema:
    {sema}

    Soru: {question}
    SQL Kodu: """
    cevap = llm.invoke(prompt)
    temiz_sql = cevap.content.replace("```sql", "").replace("```", "").strip().strip('"').strip("'")  # Çıktıyı temizle
    return {"sql_query": temiz_sql}

def sql_calistiran(state:AgentState) -> dict:
    sql_kodu = state['sql_query']
    print(f"Çalıştırılacak SQL: {sql_kodu}")

    try:
        sonuc = db.run(sql_kodu)
        print(f"SQL Sonucu: {sonuc}")
    except Exception as e:
        print(f"SQL çalıştırılırken hata oluştu: {e}")
        sonuc = f"Hata: {str(e)}"
    return {"answer": sonuc}

def hata_kontrol(state:AgentState) -> str:
    sonuc = state['answer']
    if "hata" in sonuc.lower() or "error" in sonuc.lower():
        return "hata"
    else:
        print("SQL sorgusu başarıyla çalıştırıldı, sonuç alındı.")
        return "basarili"
    
##workflow 
workflow = StateGraph(AgentState)
workflow.add_node(sql_yazan, "sql_yazan")
workflow.add_node(sql_calistiran, "sql_calistiran")

workflow.set_entry_point("sql_yazan")
workflow.add_edge("sql_yazan", "sql_calistiran")
workflow.add_conditional_edges(
    "sql_calistiran",
    hata_kontrol,
    {
        "hata": "sql_yazan",  # Eğer hata varsa, SQL yazma adımına geri dön
        "basarili": END,      # Eğer başarılıysa, süreci sonlandır
    }
)

app = workflow.compile()

if __name__ == "__main__":
    test = {"question": "Hangi müşteri en çok alışveriş yaptı?"}
    final = app.invoke(test)
    print("\n" + "="*30)
    print(f"Final Sonuç: {final}")
    print("="*30)