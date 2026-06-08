from typing import TypedDict
from langgraph.graph import StateGraph, END
from tools import llm, db

class AgentState(TypedDict):
    question : str
    sql_query : str
    answer : str
    final_report : str

def sql_yazan(state:AgentState) -> dict:
    question = state["question"]
    sema = db.get_table_info()
    
    onceki_hata = state.get("answer","")
    hata_uyarisi = ""
    
    if "hata" in onceki_hata.lower() or "error" in onceki_hata.lower():
        print("önceki sql sorgu hatası bulundu düzeltiliyor")

    
    prompt = f"""Sen kıdemli bir SQLite veri analistisin.
    Aşağıdaki veritabanı şemasına bakarak yöneticinin sorusunu cevaplayacak SADECE çalıştırılabilir bir SQL kodu yaz.
    Asla açıklama yapma. Asla markdown (```sql) formatı kullanma. Sadece saf SQL kodunu ver.
    {hata_uyarisi}
    Şema:
    {sema}
    Soru: {question}
    SQL Kodu: """
    
    cevap = llm.invoke(prompt)
    temiz_sql = cevap.content.replace("```sql", "").replace("```", "").strip().strip('"').strip("'")
    return {"sql_query" : temiz_sql}

def sql_calistiran(state:AgentState) -> dict:
    sql_kodu = state["sql_query"]
    print(f"\nDenenen SQL sorgusu: \n{sql_kodu}")

    try:
        sonuc = db.run(sql_kodu)
        print("sql kodu döndü")
    except Exception as e:
        print("hata")
        sonuc = f"Hata : {str(e)}"
    
    return{"answer" : str(sonuc)}

def raporlayici(state:AgentState) -> dict:
    print("raporlayıcı çalışıyor")
    soru = state["question"]
    ham_veri = state["answer"]

    prompt = f"""Sen profesyonel bir veri analistisin.
    Yöneticin sana şu soruyu sordu: "{soru}"
    Veritabanından gelen ham sonuç şu: "{ham_veri}"
    
    Lütfen bu ham sonucu yöneticinin kolayca anlayabileceği, net ve profesyonel bir Türkçe cümleye çevir.
    Sadece cevabı ver, ekstra açıklama yapma."""

    cevap = llm.invoke(prompt)
    return {"final_report" : cevap.content}

def hata_kontrol(state:AgentState) ->str:
    sonuc = state["answer"]
    if "hata" in sonuc.lower() or "error" in sonuc.lower():
        print("sonuç işleniyor")
        return "hatali_dondu"
    else:
        print("kod temiz")
        return "basarili"
    
workflow = StateGraph(AgentState)
workflow.add_node("sql_yazan", sql_yazan)
workflow.add_node("sql_calistiran", sql_calistiran)
workflow.add_node("raporlayici", raporlayici) # Yeni departmanı şirkete kaydettik

workflow.set_entry_point("sql_yazan")
workflow.add_edge("sql_yazan", "sql_calistiran")
workflow.add_conditional_edges(
    "sql_calistiran",
    hata_kontrol, 
    {
        "hatali_dondu": "sql_yazan",
        "basarili": "raporlayici" # Başarılıysa END yerine artık raporlayıcıya gidiyor
    }
)

# Raporlayıcı işini bitirince süreç tamamlanır
workflow.add_edge("raporlayici", END)

app = workflow.compile()

if __name__ == "__main__":
    test = {"question": "en çok hangi ürünler alındı?"}
    print("\nWorkflow çalıştırılıyor...\n" + "-"*30)
    
    final = app.invoke(test)

    print("\n" + "="*50)
    print("PATRONUN GÖRECEĞİ VİTRİN RAPORU:")
    print(final["final_report"])
    print("="*50)