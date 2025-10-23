import streamlit as st
from parser_engine import parse_statement, StatementData
import os

st.set_page_config(page_title="Credit Card Statement Parser Bot", layout="wide")

if "statement_data" not in st.session_state:
    st.session_state.statement_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "bot", "text": "👋 Hello! Please upload your credit card statement PDF to begin parsing."}]
if "temp_pdf_path" not in st.session_state:
    st.session_state.temp_pdf_path = None

def get_bot_response(query, data: StatementData):
    query_lower = query.lower()
    
    if "balance" in query_lower or "due amount" in query_lower:
        return f"Your **Total Balance Due** is **${data.total_balance_due:,.2f}**."
    
    elif "due date" in query_lower or "when is" in query_lower:
        return f"The **Payment Due Date** is **{data.payment_due_date}**."
    
    elif "statement date" in query_lower or "billing cycle" in query_lower:
        return f"The **Billing Cycle** closed on **{data.billing_cycle_end}**."
    
    elif "last 4" in query_lower or "card number" in query_lower:
        return f"The statement is for a **{data.issuer}** card ending in **{data.card_last_4_digits}**."
    
    elif "transactions" in query_lower or "new charges" in query_lower or "spent" in query_lower:
        return (f"You had **{data.transaction_count}** new transactions, totaling **${data.total_new_charges_amount:,.2f}** "
                f"in the last cycle.")
    
    elif "summary" in query_lower or "all info" in query_lower:
        return (f"**Statement Summary for {data.issuer} (Card ending {data.card_last_4_digits}):**\n"
                f"- Total Balance Due: **${data.total_balance_due:,.2f}**\n"
                f"- Payment Due Date: **{data.payment_due_date}**\n"
                f"- Cycle End Date: **{data.billing_cycle_end}**\n"
                f"- New Charges: **{data.transaction_count}** transactions, totaling **${data.total_new_charges_amount:,.2f}**")

    else:
        return "I can retrieve the Total Balance Due, Payment Due Date, Billing Cycle End Date, Last 4 Digits, and a Transaction Summary. What specific detail are you looking for?"

def handle_upload(uploaded_file):
    if st.session_state.temp_pdf_path and os.path.exists(st.session_state.temp_pdf_path):
        os.remove(st.session_state.temp_pdf_path)

    temp_path = os.path.join("/tmp", uploaded_file.name)
    if not os.path.exists("/tmp"):
        os.makedirs("/tmp")
        
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.session_state.temp_pdf_path = temp_path
    
    st.session_state.chat_history.append({"role": "bot", "text": f"📥 File uploaded successfully. Beginning parsing..."})

    st.session_state.chat_history.append({"role": "bot", "text": "⏳ This may take a moment, especially for large PDFs..."})
    st.rerun()

st.title("💳 Credit Card Statement Parser Chatbot")
st.markdown("---")

with st.sidebar:
    st.header("Upload Statement")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None and st.button("Parse Statement"):
        with st.spinner("Processing..."):
            handle_upload(uploaded_file)

if st.session_state.temp_pdf_path and st.session_state.statement_data is None:
    try:
        data = parse_statement(st.session_state.temp_pdf_path)
        st.session_state.statement_data = data
        st.session_state.chat_history.pop()
        st.session_state.chat_history.pop()
        st.session_state.chat_history.append({
            "role": "bot", 
            "text": f"✅ Parsing Complete! This is a **{data.issuer}** statement. Ask me about the balance, due date, transactions, or card details."
        })
        st.rerun()
    except Exception as e:
        st.session_state.chat_history.append({"role": "bot", "text": f"❌ An error occurred during parsing: {e}"})
        st.session_state.statement_data = None
        st.session_state.temp_pdf_path = None


chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

if st.session_state.statement_data is not None:
    prompt = st.chat_input("Ask about your statement data...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "text": prompt})
        
        response = get_bot_response(prompt, st.session_state.statement_data)
        st.session_state.chat_history.append({"role": "bot", "text": response})
        st.rerun()

elif uploaded_file is None:
    st.info("Please upload a PDF statement in the sidebar to start the chat.")
