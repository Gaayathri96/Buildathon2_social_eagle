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
st.markdown("Multilingual support triage, ChromaDB vector retrieval, dynamic agent orchestration, and operational analytics.")

@st.cache_resource
def load_workflow():
    return SupportTeamWorkflow()

try:
    workflow = load_workflow()
except Exception as e:
    st.error(f"Error initializing workflow: {e}")

with st.sidebar:
    st.header("About the Team")
    st.markdown("1. **Customer Query Agent**: Tries to understand urgency, sentiment & language.")
    st.markdown("2. **Knowledge Base Agent**: ChromaDB semantic vector search.")
    st.markdown("3. **Resolution Agent**: Multilingual response drafting.")
    st.markdown("4. **Log Agent**: Escalation evaluation & CSV logging.")

# --- Ticket Submission Form ---
with st.form("complaint_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name", "Carlos Gomez")
    with col2:
        order_id = st.text_input("Order ID", "SE-88214")
        
    raw_complaint = st.text_area(
        "Raw Complaint Text (Supports multiple languages e.g., Spanish, French, German)",
        placeholder="¿Dónde está mi pedido? Se suponía que llegaría ayer.",
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
                
                with st.expander("1. 🔍 Customer Query Agent (Triage & Language Detection)", expanded=False):
                    st.write(f"**Detected Language:** {results['language']}")
                    st.write(results["query_analysis"])
                    
                with st.expander("2. 📚 Knowledge Base Agent (ChromaDB Vector Search)", expanded=False):
                    st.write(results["kb_findings"])
                    
                with st.expander("3. ✍️ Resolution Agent (Multilingual Draft Reply)", expanded=False):
                    st.write(results["resolution"])
                    
                with st.expander("4. 📋 Log Agent (Audit & Record)", expanded=False):
                    st.write(results["log_result"])
                
                is_escalated = results["is_escalated"]
                
                st.markdown("---")
                st.subheader("🎯 Final Customer Response & Status")
                
                if is_escalated:
                    st.error("⚠️ Status Badge: **ESCALATED** (Human supervisor review applied)")
                else:
                    st.success("✅ Status Badge: **RESOLVED**")
                
                st.info(results["resolution"])
                
            except Exception as e:
                st.error(f"Error during execution: {e}")

st.markdown("---")
st.subheader("📁 Ticket Audit Log Table")

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

st.markdown("---")

# --- Conditional Operational Analytics Dashboard Section at the Bottom ---
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

if st.button("📈 Show Operational Analytics Dashboard"):
    st.session_state.show_dashboard = not st.session_state.show_dashboard

if st.session_state.show_dashboard:
    st.subheader("📊 Operational Analytics Dashboard")
    if os.path.exists(log_path):
        df_logs = pd.read_csv(log_path)
        if not df_logs.empty:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            total_tickets = len(df_logs)
            resolved_count = len(df_logs[df_logs["status"] == "Resolved"])
            escalated_count = len(df_logs[df_logs["status"] == "Escalated"])
            
            col_m1.metric("Total Tickets", total_tickets)
            col_m2.metric("Resolved", resolved_count)
            col_m3.metric("Escalated", escalated_count)
            col_m4.metric("Escalation Rate", f"{(escalated_count/total_tickets)*100:.1f}%" if total_tickets > 0 else "0%")

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("**Tickets per Category**")
                category_counts = df_logs["category"].value_counts()
                st.bar_chart(category_counts)
            with col_c2:
                st.markdown("**Status Breakdown**")
                status_counts = df_logs["status"].value_counts()
                st.bar_chart(status_counts)
        else:
            st.info("No ticket metrics available yet.")
    else:
        st.info("Analytics dashboard will populate once tickets are submitted.")