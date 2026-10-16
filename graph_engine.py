from typing import TypedDict
from langgraph.graph import StateGraph, END
from tools import llm, db
from prompts import SQL_YAZAN_PROMPT, HATA_UYARISI, RAPORLAYICI_PROMPT

MAX_DENEME = 3  # SQL en fazla bu kadar kez yazılıp denenir


class AgentState(TypedDict, total=False):
    question: str
    sql_query: str
    answer: str
    error: str          # son denemenin hata mesajı, hata yoksa ""
    attempts: int       # kaç kez SQL yazıldı
    final_report: str


def sadece_okuma_mi(sql: str) -> bool:
    """LLM'in ürettiği SQL'in veriyi değiştirmediğinden emin ol."""
    temiz = sql.strip().rstrip(";").strip()
    if ";" in temiz:  # birden fazla ifade çalıştırılmasın
        return False
    ilk_kelime = temiz.split(None, 1)[0].upper() if temiz else ""
    return ilk_kelime in ("SELECT", "WITH")


def sql_yazan(state: AgentState) -> dict:
    question = state["question"]
    sema = db.get_table_info()

    hata_uyarisi = ""
    if state.get("error"):
        print("önceki sql sorgu hatası bulundu, hata LLM'e geri veriliyor")
        hata_uyarisi = HATA_UYARISI.format(
            onceki_sql=state.get("sql_query", ""), hata=state["error"]
        )

    prompt = SQL_YAZAN_PROMPT.format(hata_uyarisi=hata_uyarisi, sema=sema, question=question)
    cevap = llm.invoke(prompt)
    temiz_sql = cevap.content.replace("```sql", "").replace("```", "").strip().strip('"').strip("'")
    return {"sql_query": temiz_sql, "attempts": state.get("attempts", 0) + 1}


def sql_calistiran(state: AgentState) -> dict:
    sql_kodu = state["sql_query"]
    print(f"\nDenenen SQL sorgusu (deneme {state.get('attempts', 1)}): \n{sql_kodu}")

    if sql_kodu == "YAPILAMAZ":
        print("veri yokluğu tespit ettik sql sorgusu iptal edildi")
        return {"answer": "VERİ_YOK: istenilen bilgi veritabanında bulunmuyor.", "error": ""}

    if not sadece_okuma_mi(sql_kodu):
        return {"answer": "", "error": "Güvenlik: yalnızca tek bir SELECT/WITH sorgusu çalıştırılabilir."}

    try:
        sonuc = db.run(sql_kodu)
        print("sql kodu döndü")
        return {"answer": str(sonuc), "error": ""}
    except Exception as e:
        print("hata")
        return {"answer": "", "error": str(e)}


def raporlayici(state: AgentState) -> dict:
    print("raporlayıcı çalışıyor")
    if state.get("error"):  # deneme hakkı bitti, hâlâ hata var
        return {"final_report": (
            f"Sorgu {state.get('attempts', 0)} denemede düzeltilemedi. "
            f"Son hata: {state['error']}"
        )}

    prompt = RAPORLAYICI_PROMPT.format(soru=state["question"], ham_veri=state["answer"])
    cevap = llm.invoke(prompt)
    return {"final_report": cevap.content}


def hata_kontrol(state: AgentState) -> str:
    if state.get("error"):
        if state.get("attempts", 0) < MAX_DENEME:
            print("hata var, sql yeniden yazılacak")
            return "hatali_dondu"
        print("deneme hakkı bitti")
        return "basarili"
    print("kod temiz")
    return "basarili"


workflow = StateGraph(AgentState)
workflow.add_node("sql_yazan", sql_yazan)
workflow.add_node("sql_calistiran", sql_calistiran)
workflow.add_node("raporlayici", raporlayici)

workflow.set_entry_point("sql_yazan")
workflow.add_edge("sql_yazan", "sql_calistiran")
workflow.add_conditional_edges(
    "sql_calistiran",
    hata_kontrol,
    {
        "hatali_dondu": "sql_yazan",
        "basarili": "raporlayici",
    },
)
workflow.add_edge("raporlayici", END)

app = workflow.compile()

if __name__ == "__main__":
    test = {"question": "Sistemdeki Drone siparişlerini teslim eden kargo kuryelerinin (couriers) isimlerini ve taşıdıkları toplam paket sayılarını listele."}
    print("\nWorkflow çalıştırılıyor...\n" + "-" * 30)

    final = app.invoke(test)

    print("\n" + "=" * 50)
    print("RAPOR:")
    print(final["final_report"])
    print("=" * 50)
