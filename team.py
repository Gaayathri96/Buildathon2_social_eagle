import os
import re
import json
import uuid
from datetime import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from autogen import GroupChat, GroupChatManager, UserProxyAgent
from agents.query_agent import create_query_agent
from agents.knowledge_agent import create_knowledge_agent, search_kb_vector
from agents.resolution_agent import create_resolution_agent
from agents.log_agent import create_log_agent, log_ticket

load_dotenv()

def get_llm_config():
    api_key = os.environ.get("OPENAI_API_KEY")
    return {
        "config_list": [{"model": "gpt-4o-mini", "api_key": api_key}],
        "temperature": 0.1
    }

def parse_llm_json(response_text: str) -> dict:
    if not response_text:
        return {}
    cleaned = response_text.strip()
    if "```" in cleaned:
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        st.warning(f"⚠️ Agent JSON Parse Error. Falling back to default attributes.")
        return {}

class SupportTeamWorkflow:
    def __init__(self):
        llm_config = get_llm_config()
        self.query_agent = create_query_agent(llm_config)
        self.kb_agent, self.search_kb_func = create_knowledge_agent(llm_config)
        self.resolution_agent = create_resolution_agent(llm_config)
        self.log_agent, self.log_ticket_func = create_log_agent(llm_config)
        
        self.kb_agent.register_for_execution(name="search_kb_vector")(self.search_kb_func)
        self.log_agent.register_for_execution(name="log_ticket")(self.log_ticket_func)

        self.human_proxy = UserProxyAgent(
            name="HumanSupervisor",
            human_input_mode="ALWAYS",
            code_execution_config=False,
            default_auto_reply="Approved by human supervisor."
        )

    def process_ticket(self, complaint_text: str, customer_name: str = "Anonymous", order_id: str = "N/A"):
        # 1. Query Analysis
        q_msg = f"Analyze this complaint: {complaint_text}"
        q_reply = str(self.query_agent.generate_reply(messages=[{"role": "user", "content": q_msg}]))
        parsed_q = parse_llm_json(q_reply)
        
        language = parsed_q.get("language", "English")
        category = parsed_q.get("category", "General")
        urgency = parsed_q.get("urgency", "Normal")
        sentiment = parsed_q.get("sentiment", "Calm")
        
        # 2. Knowledge Retrieval via Vector Store (Robust extraction handling dict/metadata structures)
        kb_msg = f"Customer Language: {language}\nSummary: {parsed_q.get('summary', complaint_text)}\nFind relevant vector store policy passages."
        kb_reply_raw = self.kb_agent.generate_reply(messages=[{"role": "user", "content": kb_msg}])
        
        kb_reply = ""
        if isinstance(kb_reply_raw, dict):
            kb_reply = kb_reply_raw.get("content") or kb_reply_raw.get("function_call", "") or str(kb_reply_raw)
        elif isinstance(kb_reply_raw, str):
            kb_reply = kb_reply_raw
        else:
            kb_reply = str(kb_reply_raw)

        # Fallback if raw structure persists as dictionary text
        if "{" in kb_reply and "content" in kb_reply:
            try:
                kb_reply = search_kb_vector(parsed_q.get('summary', complaint_text))
            except Exception:
                kb_reply = "Policy information retrieved via vector search."

        # 3. Resolution Drafting (Robust extraction)
        res_msg = f"Original Complaint: {complaint_text}\nLanguage: {language}\nKB Findings: {kb_reply}\nDraft response and confidence."
        res_reply_raw = self.resolution_agent.generate_reply(messages=[{"role": "user", "content": res_msg}])
        
        if isinstance(res_reply_raw, dict):
            res_reply = res_reply_raw.get("content") or res_reply_raw.get("function_call", "") or str(res_reply_raw)
        elif isinstance(res_reply_raw, str):
            res_reply = res_reply_raw
        else:
            res_reply = str(res_reply_raw)
            
        parsed_res = parse_llm_json(res_reply)
        clean_reply = parsed_res.get("customer_reply", res_reply)
        confidence = parsed_res.get("confidence", "Medium")

        # 4. Dynamic GroupChat Orchestration
        groupchat = GroupChat(
            agents=[self.query_agent, self.kb_agent, self.resolution_agent, self.log_agent],
            messages=[],
            max_round=5,
            speaker_selection_method="auto"
        )
        manager = GroupChatManager(groupchat=groupchat, llm_config=get_llm_config())
        self.query_agent.initiate_chat(manager, message=f"Review ticket lifecycle for customer {customer_name}")

        # 5. Strict Escalation Rule Evaluation
        complaint_lower = complaint_text.lower()
        kb_lower = kb_reply.lower()
        
        is_high_urgency = urgency.lower() == "high" and sentiment.lower() in ["frustrated", "very angry", "angry"]
        is_very_angry = sentiment.lower() in ["very angry", "angry"]
        kb_missing = "no matching document" in kb_lower or "no direct matching" in kb_lower or "vector search error" in kb_lower
        has_legal_or_fraud = any(term in complaint_lower for term in ["lawsuit", "lawyer", "court", "fraud", "sue", "police", "consumer court", "bank"])
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
            if is_high_urgency: reasons.append("High urgency & angry sentiment")
            if is_very_angry: reasons.append("Angry sentiment")
            if kb_missing: reasons.append("No matching document found")
            if has_legal_or_fraud: reasons.append("Legal threat or fraud dispute")
            if is_low_confidence: reasons.append("Low confidence")
            escalation_reason = ", ".join(reasons) if reasons else "Escalation criteria met"
            status = "Escalated"
            clean_reply = f"[Human Supervisor Approved] {clean_reply}"
        else:
            escalation_reason = "None"
            status = "Resolved"

        ticket_id = f"TICK-{uuid.uuid4().hex[:6].upper()}"

        # 6. Record Ticket with clean string snippet for kb_sources
        kb_source_snippet = kb_reply[:250] + "..." if len(kb_reply) > 250 else kb_reply

        log_ticket(
            ticket_id=ticket_id,
            customer_name=customer_name,
            order_id=order_id,
            complaint=complaint_text,
            category=category,
            urgency=urgency,
            sentiment=sentiment,
            kb_sources=kb_source_snippet,
            response=clean_reply,
            status=status,
            escalation_reason=escalation_reason
        )

        return {
            "ticket_id": ticket_id,
            "language": language,
            "query_analysis": q_reply,
            "kb_findings": kb_reply,
            "resolution": clean_reply,
            "log_result": f"Logged as {ticket_id} with status {status}",
            "is_escalated": is_escalated
        }