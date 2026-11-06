# Buildathon2_social_eagle

# 🤖 AI Customer Support Automation Desk

An intelligent, multi-agent customer support automation system built using the **AutoGen** framework and **Streamlit**. Designed to streamline customer service operations by automating triage, policy retrieval, response drafting, audit logging, and intelligent human escalation for **ShopEase**.

A multi-agent customer support workflow built using the **AutoGen** framework and **Streamlit**.

## Features
- **Query Triage**: Analyzes customer category, urgency, sentiment[cite: 1].
- **Knowledge Retrieval**: Searches markdown policy files (`shipping_policy.md`, `refund_policy.md`, etc.)[cite: 1, 2, 3, 4].
- **Automated Resolution**: Drafts customer replies backed by policy facts.
- **Smart Escalation & Logging**: Automatically flags high-urgency, angry, or complex tickets for human review and records every session to `logs/tickets.csv`.

## Setup & Running
1. Install dependencies:
   ```bash
   pip install -r requirements.txt

---

## 🏗️ Architecture & Multi-Agent Workflow

The system coordinates specialized AI agents dynamically using AutoGen's **GroupChat** orchestration and semantic retrieval:

```text
               ┌───────────────────────┐
               │    Customer Complaint │
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │  Customer Query Agent │ ──► Detects language, category, urgency, & sentiment
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │ Knowledge Base Agent  │ ──► ChromaDB semantic vector search over policy docs
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │   Resolution Agent    │ ──► Drafts polite reply in the customer's native language
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │       Log Agent       │ ──► Evaluates escalation rules & records audit log
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │ Streamlit UI / Metrics│ ──► Analytics dashboard, status badges, & CSV export
               └───────────┬───────────┘
```

### Agent Roles & Responsibilities

1. **Customer Query Agent**: Analyzes the raw customer complaint text to detect the customer's language, category, urgency level, sentiment, and core summary.
2. **Knowledge Base Agent**: Queries internal company documentation (`shipping_policy.md`, `refund_policy.md`, `account_and_login.md`, `product_faq.md`) using **ChromaDB** semantic vector embeddings to retrieve relevant passages.
3. **Resolution Agent**: Synthesizes verified vector store facts to draft clear, professional responses in the customer's exact native language.
4. **Log Agent**: Audits the ticket lifecycle against strict business rules, handles escalation decisions, and records the session into `logs/tickets.csv`.
5. **Human Supervisor (UserProxyAgent)**: Prompts human-in-the-loop review and approval for escalated tickets.

---

## 🚀 Key Features Added

* **ChromaDB Semantic Search**: Replaced keyword matching with persistent vector store embeddings (`chroma_db/`) for accurate policy retrieval.
* **Dynamic GroupChat Orchestration**: Utilizes AutoGen's `GroupChat` and `GroupChatManager` with autonomous speaker selection.
* **Human-in-the-Loop Supervision**: Integrated `UserProxyAgent` to review and approve escalated support replies.
* **Multilingual Support**: Automatic language detection (Spanish, French, German, Hindi, etc.) with responses generated in the customer's native tongue.
* **Operational Analytics Dashboard**: Real-time Streamlit metric cards and category bar charts tracking ticket volumes, resolution rates, and escalation statistics.

---

## 🚨 Escalation Rules

Tickets are automatically marked as **Escalated** and routed for human supervision when *any* of the following conditions are met:

* **High Urgency**: Customer requests require immediate intervention.
* **Very Angry Sentiment**: Customer expression is extremely frustrated or furious.
* **Missing Knowledge Base Documentation**: ChromaDB returns no semantic matches.
* **Legal Threats or Fraud/Payment Disputes**: Mentions of lawsuits, consumer courts, legal action, or credit card fraud.
* **Low Confidence**: The Resolution Agent lacks sufficient verified policy facts.

---

## 📁 Repository Structure

```text
├── app.py                  # Streamlit dashboard & analytics view
├── agents/
│   ├── query_agent.py      # Multilingual Triage Agent
│   ├── knowledge_agent.py  # ChromaDB Vector Store & semantic search tool
│   ├── resolution_agent.py # Multilingual Resolution Agent
│   └── log_agent.py        # Audit Logger Agent + tool
├── team.py                 # AutoGen GroupChat workflow & human-in-the-loop logic
├── knowledge_base/         # Company policy & FAQ markdown files
├── chroma_db/              # Persistent ChromaDB vector store directory
├── logs/
│   └── tickets.csv         # Automatically generated ticket audit log
├── screenshots/            # UI screenshots for documentation
├── .env.example            # Environment variable template
├── .gitignore
├── requirements.txt        # Project dependencies (including chromadb)
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone or Open the Repository

Ensure you are in your project workspace folder in your terminal (e.g., VS Code).

### 2. Install Dependencies

Install all required Python packages (`pyautogen`, `streamlit`, `pandas`, `python-dotenv`, `chromadb`):

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to create a local `.env` file:

```bash
cp .env.example .env
```

Open `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your-actual-openai-api-key-here
```

---

## 🚀 How to Run the Application

Launch the Streamlit web dashboard locally:

```bash
streamlit run app.py
```

Streamlit will automatically open a browser window at `http://localhost:8501`.

1. Review live metrics in the **Operational Analytics Dashboard** at the top.
2. Enter customer details and a complaint (in English or any foreign language).
3. Click **Submit & Run Multi-Agent Team** to watch the agents collaborate via semantic search and group chat.
4. Review the timeline, final response badge (**Resolved** or **Escalated** with human supervisor sign-off), and download the CSV audit log.