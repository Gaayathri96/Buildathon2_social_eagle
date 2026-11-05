import os
import json
import uuid
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from agents.query_agent import create_query_agent
from agents.knowledge_agent import create_knowledge_agent
from agents.resolution_agent import create_resolution_agent
from agents.log_agent import create_log_agent, log_ticket

load_dotenv()

def get_llm_config():
    api_key = os.environ.get("OPENAI_API_KEY")
    return {
        "config_list": [{"model": "gpt-4o-mini", "api_key": api_key}],
        "temperature": 0.1
    }

class SupportTeamWorkflow:
    def __init__(self):
        llm_config = get_llm_config()
        self.query_agent = create_query_agent(llm_config)
        self.kb_agent, self.search_kb_func = create_knowledge_agent(llm_config)
        self.resolution_agent = create_resolution_agent(llm_config)
        self.log_agent, self.log_ticket_func = create_log_agent(llm_config)
        
        self.kb_agent.register_for_execution(name="search_kb")(self.search_kb_func)
        self.log_agent.register_for_execution(name="log_ticket")(self.log_ticket_func)

    def process_ticket(self, complaint_text: str, customer_name: str = "Anonymous", order_id: str = "N/A"):
        # 1. Query Agent
        q_msg = f"Analyze this complaint: {complaint_text}"
        q_reply = str(self.query_agent.generate_reply(messages=[{"role": "user", "content": q_msg}]))
        
        # 2. Knowledge Base Agent
        kb_msg = f"Customer Analysis / Summary:\n{q_reply}\nFind relevant passages from documents."
        kb_reply = str(self.kb_agent.generate_reply(messages=[{"role": "user", "content": kb_msg}]))
        
        # 3. Resolution Agent
        res_msg = f"Original Complaint: {complaint_text}\nQuery Analysis: {q_reply}\nKB Findings: {kb_reply}\nWrite a polite response and confidence rating."
        res_reply = str(self.resolution_agent.generate_reply(messages=[{"role": "user", "content": res_msg}]))
        
        # Parse resolution JSON safely
        clean_reply = res_reply
        confidence = "Medium"
        try:
            parsed_res = json.loads(res_reply)
            clean_reply = parsed_res.get("customer_reply", res_reply)
            confidence = parsed_res.get("confidence", "Medium")
        except Exception:
            pass

        # Parse query triage fields safely
        category = "General"
        urgency = "Normal"
        sentiment = "Calm"
        try:
            parsed_q = json.loads(q_reply)
            category = parsed_q.get("category", category)
            urgency = parsed_q.get("urgency", urgency)
            sentiment = parsed_q.get("sentiment", sentiment)
        except Exception:
            pass

        # --- Precise Escalation Rules ---
        complaint_lower = complaint_text.lower()
        kb_lower = kb_reply.lower()
        
        is_high_urgency = urgency.lower() == "high"
        is_very_angry = sentiment.lower() == "very angry" or "furious" in complaint_lower
        kb_missing = "no direct matching document" in kb_lower or "no matching document" in kb_lower
        has_legal_or_fraud = any(term in complaint_lower for term in ["lawsuit", "lawyer", "court", "fraud", "sue", "police", "consumer court"])
        is_low_confidence = confidence.lower() == "low"

        is_escalated = (
            is_high_urgency or 
            is_very_angry or 
            kb_missing or 
            has_legal_or_fraud or 
            is_low_confidence
        )
        
        if is_escalated:
            reasons = []
            if is_high_urgency: reasons.append("High urgency")
            if is_very_angry: reasons.append("Very angry sentiment")
            if kb_missing: reasons.append("No matching document found")
            if has_legal_or_fraud: reasons.append("Legal threat or fraud dispute")
            if is_low_confidence: reasons.append("Low resolution confidence")
            escalation_reason = ", ".join(reasons)
            status = "Escalated"
        else:
            escalation_reason = "None"
            status = "Resolved"

        ticket_id = f"TICK-{uuid.uuid4().hex[:6].upper()}"

        # 5. Log ticket with exact required columns
        log_ticket(
            ticket_id=ticket_id,
            customer_name=customer_name,
            order_id=order_id,
            complaint=complaint_text,
            category=category,
            urgency=urgency,
            sentiment=sentiment,
            kb_sources=kb_reply[:250] + "..." if len(kb_reply) > 250 else kb_reply,
            response=clean_reply,
            status=status,
            escalation_reason=escalation_reason
        )

        return {
            "ticket_id": ticket_id,
            "query_analysis": q_reply,
            "kb_findings": kb_reply,
            "resolution": clean_reply,
            "log_result": f"Logged as {ticket_id} with status {status}",
            "is_escalated": is_escalated
        }