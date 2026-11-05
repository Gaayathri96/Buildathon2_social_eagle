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

The system coordinates four specialized AI agents in a sequential pipeline (`Query → Knowledge → Resolution → Log`):

```text
               ┌───────────────────────┐
               │    Customer Complaint │
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │  Customer Query Agent │ ──► Analyzes category, urgency, & sentiment
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │ Knowledge Base Agent  │ ──► Searches local markdown policy docs
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │   Resolution Agent    │ ──► Drafts polite reply & calculates confidence
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │       Log Agent       │ ──► Evaluates escalation rules & records audit log
               └───────────┬───────────┘
                           ▼
               ┌───────────────────────┐
               │ Streamlit UI / CSV Log│ ──► Displays status badges, reply, & downloadable log
               └───────────────────────┘
```

### Agent Roles & Responsibilities
1. **Customer Query Agent**: Analyzes the raw customer complaint text to extract category, urgency level, customer sentiment, and a concise one-sentence summary.
2. **Knowledge Base Agent**: Queries internal company documentation (`shipping_policy.md`, `refund_policy.md`, `account_and_login.md`, `product_faq.md`) to retrieve exact matching passages and source filenames.
3. **Resolution Agent**: Synthesizes verified facts from the Knowledge Base Agent to draft clear, professional responses and rates its confidence level.
4. **Log Agent**: Audits the entire ticket lifecycle against strict business rules, handles escalation decisions, and records the session into `logs/tickets.csv` with exact schema attributes.

---

## 🚨 Escalation Rules

Tickets are automatically marked as **Escalated** and handed over to human support when *any* of the following conditions are met:
- **High Urgency**: Customer requests require immediate intervention (e.g., `Urgency = High`).
- **Very Angry Sentiment**: Customer expression is extremely frustrated or furious (`Sentiment = Very Angry`).
- **Missing Knowledge Base Documentation**: The Knowledge Base Agent cannot find a matching document or policy in the store.
- **Legal Threats or Fraud/Payment Disputes**: Mentions of lawsuits, consumer courts, legal action, payment disputes, or fraudulent credit card charges.
- **Low Confidence**: The Resolution Agent lacks sufficient verified policy facts to fully resolve the issue.

---

## 📁 Repository Structure

```text
├── app.py                  # Streamlit UI dashboard
├── agents/
│   ├── query_agent.py      # Customer Query Agent
│   ├── knowledge_agent.py  # Knowledge Base Agent + search_kb tool
│   ├── resolution_agent.py # Resolution Agent
│   └── log_agent.py        # Log Agent + log_ticket tool
├── team.py                 # Wires agents into the sequential AutoGen workflow
├── knowledge_base/         # Company policy & FAQ markdown files
│   ├── shipping_policy.md
│   ├── refund_policy.md
│   ├── account_and_login.md
│   └── product_faq.md
├── logs/
│   └── tickets.csv         # Automatically generated ticket audit log
├── screenshots/            # UI screenshots for documentation
├── .env.example            # Environment variable template
├── .gitignore
├── requirements.txt        # Project dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone or Open the Repository
Ensure you are in your project workspace folder in your terminal (e.g., VS Code).

### 2. Install Dependencies
Install all required Python packages (`pyautogen`, `streamlit`, `pandas`, `python-dotenv`):
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

1. Enter the customer's name and order ID.
2. Type or paste a complaint into the text area.
3. Click **Submit & Run Multi-Agent Team** to watch the agents process the ticket step-by-step through the pipeline.
4. Review the expandable agent timeline, final response badge (**Resolved** or **Escalated**), and the live audit table at the bottom with CSV export functionality.

---

## 📷 Screenshots & Explanations

### 1. Dashboard Interface & Triage View
> *This view shows the input form where users submit a customer complaint along with optional details like name and Order ID. Once submitted, the expanders reveal the sequential output from each agent.*
> *(Example screenshot path: `screenshots/dashboard_view.png`)*

### 2. Resolved vs. Escalated Tickets Audit Table
> *This table at the bottom tracks all processed records with columns: `ticket_id`, `timestamp`, `customer_name`, `order_id`, `complaint`, `category`, `urgency`, `sentiment`, `kb_sources`, `response`, `status`, and `escalation_reason`. Users can download this file instantly as a CSV.*
> *(Example screenshot path: `screenshots/audit_log.png`)*