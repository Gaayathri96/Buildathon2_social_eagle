import os
import uuid
from datetime import datetime
import pandas as pd
from autogen import ConversableAgent

def log_ticket(
    customer_name: str,
    order_id: str,
    complaint: str,
    category: str,
    urgency: str,
    sentiment: str,
    kb_sources: str,
    response: str,
    status: str,
    escalation_reason: str,
    ticket_id: str = None
) -> str:
    """Records the ticket to logs/tickets.csv using the exact required columns."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "tickets.csv")
    
    # Generate automatic ID and timestamp if not provided
    if not ticket_id:
        ticket_id = f"TICK-{uuid.uuid4().hex[:6].upper()}"
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_row = pd.DataFrame([{
        "ticket_id": ticket_id,
        "timestamp": current_timestamp,
        "customer_name": customer_name,
        "order_id": order_id,
        "complaint": complaint,
        "category": category,
        "urgency": urgency,
        "sentiment": sentiment,
        "kb_sources": kb_sources,
        "response": response,
        "status": status,
        "escalation_reason": escalation_reason
    }])
    
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
        
    df.to_csv(log_file, index=False)
    return f"Ticket {ticket_id} successfully logged with status: {status}."

def create_log_agent(llm_config):
    agent = ConversableAgent(
        name="LogAgent",
        system_message="""You are an administrative logging agent.
Review the ticket lifecycle and apply Escalation Rules:
Escalate to human support if:
- Urgency is High
- Sentiment is Very Angry
- KB found no matching documents
- Issue involves legal threats, fraud, or payment disputes
- Resolution confidence is Low

Record every ticket using the `log_ticket` tool.""",
        llm_config=llm_config,
        human_input_mode="NEVER"
    )
    agent.register_for_llm(name="log_ticket", description="Record ticket to CSV log.")(log_ticket)
    return agent, log_ticket