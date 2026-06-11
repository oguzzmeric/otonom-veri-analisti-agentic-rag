# 📊 Autonomous Data Analyst: Self-Healing SQL Agent with LangGraph

An advanced, enterprise-grade Autonomous Text-to-SQL Data Analyst Agent built on top of **LangGraph**'s cyclical state-machine architecture. Unlike traditional linear pipelines (e.g., vanilla LangChain) that crash upon encountering syntax or logical database runtime errors, this system utilizes a **State-Driven Self-Healing Loop** to dynamically debug, rewrite, and re-execute complex SQL queries.

The architecture is fully stress-tested against the **Olist Brazilian E-Commerce Dataset**, managing an active relational database of over **1,200,000 operational rows**.

---

## 🧠 Core Cognitive Architecture & Features

* **State-Driven Self-Healing Loop:** If the database engine throws a runtime or syntax error, the raw traceback log is captured and injected back into the graph's `State`. The agent autonomously reasons over the error log, identifies the failure point, and rewrites the query within a configurable `Recursion Limit (15)`.
* **Autonomous Conditional Aggregation:** Optimizes database execution paths by synthesizing complex analytical queries using high-level constructs like `SUM(CASE WHEN...)` or `AVG(CASE WHEN...)` in a single execution pass.
* **Semantic Multi-Join Routing:** Resolves missing direct relationships between disjointed tables by parsing an ontological semantic layer injected into the table schemas, enabling flawless multi-table mapping (e.g., bridging `customers -> orders -> order_items -> order_payments`).
* **Deterministic Guardrails:** Configured with zero LLM temperature to prevent hallucinations, ensuring that any query outside the schema's boundary or historical scope safely terminates with an explicit data-absence report rather than arbitrary code generation.

---

## 🛠️ Tech Stack

* **Orchestration & State Management:** LangGraph
* **Agentic Toolkits:** LangChain SQLDatabaseToolkit
* **Inference Engine:** OpenAI GPT-4o-Mini (`temperature=0`)
* **Database Engine:** SQLite (OLAP emulation)
* **Frontend UI:** Streamlit (Wide-mode Operational Dashboard)

---

## 📂 Project Structure

```text
├── database/
│   └── olist.db             # Relational database containing 1.2M rows
├── app.py                   # Streamlit UI & LangGraph compilation loop
├── tools.py                 # Semantic knowledge layer & SQL toolkit configuration
├── .env.example             # Template for environment variables
└── requirements.txt         # Dependency tree
