from autogen import ConversableAgent

def create_resolution_agent(llm_config):
    return ConversableAgent(
        name="ResolutionAgent",
        system_message="""You are a polite, professional customer support resolution writer.
Using ONLY the facts found and provided by the Knowledge Base Agent, write a clear, polite reply that solves the problem.
Also evaluate your confidence in solving the issue completely using the KB facts (High, Medium, Low).
Output a JSON object containing:
- "customer_reply": The drafted polite response message.
- "confidence": (High, Medium, Low)
Return ONLY valid JSON.""",
        llm_config=llm_config,
        human_input_mode="NEVER"
    )