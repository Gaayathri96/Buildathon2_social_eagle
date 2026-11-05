import os
import pandas as pd
import streamlit as st
from team import SupportTeamWorkflow

st.set_page_config(
    page_title="AI Customer Support Desk",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Customer Support Automation Desk")
st.markdown("Automated support triage, knowledge retrieval, resolution drafting, and logging powered by ShopEase policies.")

@st.cache_resource
def load_workflow():
    return SupportTeamWorkflow()

try:
    workflow = load_workflow()
except Exception as e:
    st.error(f"Error initializing workflow: {e}")

with st.sidebar:
    st.header("About the Team")
    st.markdown("1. **Customer Query Agent**: Tries to understand urgency and sentiment.")
    st.markdown("2. **Knowledge Base Agent**: Queries Markdown policies.")
    st.markdown("3. **Resolution Agent**: Drafts polite solutions.")
    st.markdown("4. **Log Agent**: Evaluates escalation rules & records audit logs.")

with st.form("complaint_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name", "Ananya Verma")
    with col2:
        order_id = st.text_input("Order ID", "SE-55412")
        
    raw_complaint = st.text_area(
        "Raw Complaint Text",
        placeholder="Type the customer's complaint here (e.g., damaged package received, shipping delay, refund status)...",
        height=130
    )
    submit_btn = st.form_submit_button("Submit & Run Multi-Agent Team")

if submit_btn:
    if not raw_complaint.strip():
        st.warning("Please enter a complaint before submitting.")
    else:
        with st.spinner("🤖 Multi-agent team collaborating on ticket..."):
            try:
                results = workflow.process_ticket(raw_complaint, customer_name, order_id)
                
                st.subheader("📋 Step-by-Step Agent Execution Timeline")
                
                with st.expander("1. 🔍 Customer Query Agent (Triage)", expanded=False):
                    st.write(results["query_analysis"])
                    
                with st.expander("2. 📚 Knowledge Base Agent (Search)", expanded=False):
                    st.write(results["kb_findings"])
                    
                with st.expander("3. ✍️ Resolution Agent (Draft Reply)", expanded=False):
                    st.write(results["resolution"])
                    
                with st.expander("4. 📋 Log Agent (Audit & Record)", expanded=False):
                    st.write(results["log_result"])
                
                is_escalated = results["is_escalated"]
                
                st.markdown("---")
                st.subheader("🎯 Final Customer Response & Status")
                
                if is_escalated:
                    st.error("⚠️ Status Badge: **ESCALATED** (Handed over to human support)")
                else:
                    st.success("✅ Status Badge: **RESOLVED**")
                
                st.info(results["resolution"])
                
            except Exception as e:
                st.error(f"Error during execution: {e}")

st.markdown("---")
st.subheader("📊 Ticket Audit Log Table")

log_path = os.path.join("logs", "tickets.csv")
if os.path.exists(log_path):
    df_logs = pd.read_csv(log_path)
    st.dataframe(df_logs, use_container_width=True)
    
    with open(log_path, "rb") as f:
        st.download_button(
            label="📥 Download Ticket Log (CSV)",
            data=f,
            file_name="tickets.csv",
            mime="text/csv"
        )
else:
    st.info("No tickets logged yet.")