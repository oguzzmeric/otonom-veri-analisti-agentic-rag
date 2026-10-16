# Autonomous Data Analyst: Self-Correcting Text-to-SQL Agent (LangGraph)

Ask a business question in Turkish, get an answer from a 1.2M-row e-commerce database. The agent writes SQL, runs it, and if the database returns an error it feeds the error and the failed query back to the LLM and tries again, up to a fixed number of attempts.

Built with LangGraph, LangChain, GPT-4o-mini and Streamlit on the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (SQLite, ~100k orders, ~1.2M rows across tables).

## How it works

```
question ──► sql_yazan (write SQL) ──► sql_calistiran (run SQL) ──► raporlayici (answer in Turkish)
                 ▲                              │
                 └──── error + failed SQL ──────┘   (max 3 attempts)
```

- **Error-feedback loop:** a LangGraph `StateGraph` keeps the question, the last query, the database error and the attempt count in its state. On error it routes back to the SQL writer with the error message in the prompt.
- **Schema hints:** table schemas are annotated with join paths and business rules (e.g. `customers → orders → order_items / order_payments`, seller revenue = `SUM(order_items.price)`), so multi-table questions join correctly.
- **Out-of-scope questions:** if the schema has nothing that matches the question (e.g. couriers), the agent returns `YAPILAMAZ` and reports that the data does not exist instead of inventing SQL.
- **Read-only guard:** only single `SELECT` / `WITH` statements are executed.
- **Deterministic generation:** GPT-4o-mini with `temperature=0`.

## Example questions

- "En çok sipariş hangi şehirden verildi?"
- "São Paulo şehrindeki en karlı 3 kategori nedir?"
- "Rio de Janeiro'daki müşteriler en çok hangi ödeme yöntemini kullanıyor?"

## Setup

The database (`database/olist.db`, ~113 MB) is stored with **Git LFS**. Install Git LFS before cloning, otherwise you only get a small pointer file.

```bash
git lfs install
git clone https://github.com/oguzzmeric/otonom-veri-analisti-agentic-rag.git
cd otonom-veri-analisti-agentic-rag
git lfs pull                      # downloads olist.db

python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env              # then put your OpenAI key in .env
streamlit run app.py
```

To run the graph from the command line without the UI: `python graph_engine.py`

## Project structure

```text
├── database/olist.db    # SQLite database (Git LFS)
├── app.py               # Streamlit UI: chat, schema browser, executed SQL + attempt count
├── graph_engine.py      # LangGraph state machine: write → run → (retry) → report
├── tools.py             # Database connection, schema hints, LLM config
├── prompts.py           # Prompt templates
├── test.py              # Early prototype with LangChain's create_sql_agent (for comparison)
├── .env.example
└── requirements.txt
```

## Limitations

- Questions and answers are in Turkish; the schema is in English.
- No evaluation set yet: accuracy has not been measured on a fixed list of questions.
- Schema hints cover the four core tables; other tables rely on the raw schema.

## Data license

The Olist dataset is published on Kaggle under CC BY-NC-SA 4.0.
