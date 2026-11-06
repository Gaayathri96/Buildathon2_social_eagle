from autogen import ConversableAgent

def create_resolution_agent(llm_config):
    return ConversableAgent(
        name="ResolutionAgent",
        system_message="""You are a polite, professional customer support resolution writer.
Using ONLY verified facts from the Knowledge Base Agent, draft a clear, professional response solving the customer's problem.
CRITICAL: Detect the customer's language from the query analysis and draft the `customer_reply` in that EXACT same language.
Output a JSON object containing:
- "customer_reply": The drafted response in the customer's language.
- "confidence": (High, Medium, Low)
Return ONLY valid JSON.""",
        llm_config=llm_config,
        human_input_mode="NEVER"
    )