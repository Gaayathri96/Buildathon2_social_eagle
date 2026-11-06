from autogen import ConversableAgent

def create_query_agent(llm_config):
    return ConversableAgent(
        name="CustomerQueryAgent",
        system_message="""You are an expert multilingual customer service triage agent.
Analyze the raw complaint text and output a valid JSON object containing:
- "language": Detected language of the customer (e.g., English, Spanish, French, German, Hindi)
- "category": (e.g., Shipping, Refunds, Account, FAQ, Billing)
- "urgency": (Low, Medium, High)
- "sentiment": (Calm, Frustrated, Very Angry)
- "summary": A concise 1-sentence summary of the core issue.
- "legal_or_fraud": true/false (Set to true if legal threats, lawsuits, fraud, or unauthorized payment disputes are present).
Return ONLY valid JSON.""",
        llm_config=llm_config,
        human_input_mode="NEVER"
    )