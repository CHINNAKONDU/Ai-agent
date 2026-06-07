import streamlit as st
import pandas as pd
import os
from groq import Groq

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

st.set_page_config(page_title="🤖 AI Agent Dashboard", layout="wide")
st.title("🤖 AI Agent Dashboard")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found! .env file lo GROQ_API_KEY=your_key_here add cheyyi")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

tab1, tab2 = st.tabs(["📊 CSV Analysis", "💬 Chat"])

with tab1:
    st.header("📊 CSV Analysis")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Data Preview")
        st.dataframe(df, use_container_width=True)

        st.subheader("📈 Statistics")
        st.write(df.describe())

        numeric_cols = [c for c in df.select_dtypes(include='number').columns]
        if len(numeric_cols) >= 1:
            st.subheader("📊 Chart")
            first_col = df.columns[0]
            chart_cols = [c for c in numeric_cols if c != first_col]
            if chart_cols:
                try:
                    st.bar_chart(df.set_index(first_col)[chart_cols])
                except Exception:
                    st.bar_chart(df[chart_cols])
            else:
                st.bar_chart(df[numeric_cols])

        st.subheader("🤖 AI Insights")
        if st.button("📊 AI Insights చెప్పు (Telugu లో)"):
            with st.spinner("Analyzing..."):
                csv_summary = df.describe().to_string()
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a data analyst. Always respond in Telugu language."},
                        {"role": "user", "content": f"Ee CSV data analyze cheyyi Telugu lo insights cheppu:\n{csv_summary}"}
                    ]
                )
                st.success(response.choices[0].message.content)

with tab2:
    st.header("💬 Chat (Telugu AI)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Emi adugutavu?")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant. Always respond in Telugu language."},
                        *st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})