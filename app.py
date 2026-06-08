import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import json
from groq import Groq
from supabase import create_client
from fpdf import FPDF  # Make sure to run 'pip install fpdf2' in your terminal

# ─── CONFIG ───────────────────────────────────────────────────
st.set_page_config(page_title="Analytics AI", page_icon="📊", layout="wide")

for k, v in [("msgs", []), ("df", None), ("lang", "English"), ("analyzed", False), ("ai_insight_text", "")]:
    st.session_state.setdefault(k, v)

# ─── KEYS (nee keys ikkada pettukko) ──────────────────────────
SUPABASE_URL = "https://maregfdgkglquibpcbeu.supabase.co"
SUPABASE_KEY = "nee_supabase_anon_key"
GROQ_API_KEY = "nee_groq_api_key"

db  = create_client(SUPABASE_URL, SUPABASE_KEY)
llm = Groq(api_key=GROQ_API_KEY)
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# ─── STYLES ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #f8fafc; }
.main-header {
    background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
    padding: 28px 32px; border-radius: 18px; color: white;
    margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.main-header h1 { margin: 0; font-size: 28px; font-weight: 700; }
.main-header p  { margin: 6px 0 0; opacity: 0.75; font-size: 14px; }
.kpi-card {
    background: white; border-radius: 14px; padding: 20px;
    text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    border-top: 4px solid #2d6a9f;
}
.kpi-val  { font-size: 32px; font-weight: 700; color: #1e3a5f; }
.kpi-lbl  { font-size: 13px; color: #64748b; margin-top: 4px; }
.chat-box {
    background: white; border-radius: 16px; padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-top: 16px;
    max-height: 420px; overflow-y: auto;
}
.umsg {
    background: #1e3a5f; color: white;
    padding: 10px 16px; border-radius: 18px 18px 4px 18px;
    max-width: 75%; margin: 8px 0 8px auto; font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.amsg {
    background: #f0f4f8; color: #1e3a5f;
    padding: 10px 16px; border-radius: 18px 18px 18px 4px;
    max-width: 75%; margin: 8px 0; font-size: 14px;
    border-left: 4px solid #2d6a9f;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.section-title {
    font-size: 18px; font-weight: 600; color: #1e3a5f;
    margin: 24px 0 12px; border-left: 4px solid #2d6a9f;
    padding-left: 12px;
}
.stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #2d6a9f) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 10px 24px !important;
    font-weight: 600 !important; transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
.stTextInput input {
    border-radius: 12px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 10px 16px !important;
}
.stTextInput input:focus { border-color: #2d6a9f !important; }
div[data-testid="metric-container"] {
    background: white; border-radius: 12px; padding: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR & FILTERS ────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.session_state.lang = st.selectbox(
        "🌐 Language",
        ["English", "Telugu", "Hindi", "Tamil", "Spanish"]
    )
    st.markdown("---")
    st.markdown("### 📂 Upload Data")
    uploaded = st.file_uploader("Upload CSV file", type=["csv"], label_visibility="collapsed")
    
    if uploaded:
        if st.session_state.df is None:
            st.session_state.df = pd.read_csv(uploaded)
            st.session_state.ai_insight_text = ""
            st.session_state.analyzed = False
        st.success(f"✅ {uploaded.name}")
        st.caption(f"{st.session_state.df.shape[0]} rows × {st.session_state.df.shape[1]} cols")

    main_df = st.session_state.df
    
    if main_df is not None:
        st.markdown("---")
        st.markdown("### 🔍 Dynamic Filters")
        categorical_cols = main_df.select_dtypes(include='object').columns.tolist()
        
        for col_name in categorical_cols[:3]: 
            unique_vals = ["All"] + list(st.session_state.df[col_name].dropna().unique())
            user_choice = st.selectbox(f"Select {col_name}", unique_vals, key=f"sidebar_filter_{col_name}")
            if user_choice != "All":
                main_df = main_df[main_df[col_name] == user_choice]
        
        st.info(f"Active Rows: {main_df.shape[0]}")

    st.markdown("---")
    st.markdown("### 💬 Chat History")
    st.metric("Messages", len(st.session_state.msgs))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.msgs = []
            st.session_state.df = None
            st.session_state.ai_insight_text = ""
            st.session_state.analyzed = False
            st.rerun()
    with col2:
        if st.button("📥 Export", use_container_width=True) and st.session_state.msgs:
            txt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.msgs])
            b64 = base64.b64encode(txt.encode()).decode()
            st.markdown(f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">⬇️ Download</a>', unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📊 Analytics AI Dashboard</h1>
    <p>Upload your CSV → Instant charts + AI-powered insights</p>
</div>
""", unsafe_allow_html=True)

# ─── DASHBOARD WORKFLOW ───────────────────────────────────────
if main_df is not None:
    nc = main_df.select_dtypes(include='number').columns.tolist()
    cc = main_df.select_dtypes(include='object').columns.tolist()

    # KPI Cards Block
    st.markdown('<div class="section-title">📈 Overview</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{main_df.shape[0]:,}</div><div class="kpi-lbl">📋 Filtered Rows</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{main_df.shape[1]}</div><div class="kpi-lbl">📊 Columns</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{len(nc)}</div><div class="kpi-lbl">🔢 Numeric</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{len(cc)}</div><div class="kpi-lbl">🔤 Text</div></div>', unsafe_allow_html=True)
    with k5:
        missing = int(main_df.isnull().sum().sum())
        st.markdown(f'<div class="kpi-card"><div class="kpi-val">{missing}</div><div class="kpi-lbl">❌ Missing</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("🔍 Preview Active Data (Top 50)", expanded=False):
        st.dataframe(main_df.head(50), use_container_width=True)

    # Plotly Premium Charts
    if nc:
        st.markdown('<div class="section-title">📊 Visualizations</div>', unsafe_allow_html=True)
        chart_tabs = st.tabs(["📊 Bar", "📈 Line", "🥧 Pie", "🔵 Scatter", "🔥 Correlation", "📦 Box", "📉 Histogram"])
        
        PC = px.colors.qualitative.G10 
        LAYOUT = dict(
            template="plotly_white", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1e3a5f", size=12),
            margin=dict(t=40, b=40, l=40, r=20), hovermode="closest"
        )

        with chart_tabs[0]:
            c1, c2 = st.columns([1, 3])
            with c1:
                col = st.selectbox("Y-Axis", nc, key="bar_y")
                grp = st.selectbox("Group by", ["None"] + cc, key="bar_g")
            with c2:
                fig = px.bar(main_df, x=cc[0] if cc else main_df.index, y=col, color=None if grp == "None" else grp, color_discrete_sequence=PC, barmode="group", title=f"Distribution of {col}")
                fig.update_layout(**LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[1]:
            c1, c2 = st.columns([1, 3])
            with c1:
                col = st.selectbox("Column", nc, key="line_y")
                multi = st.multiselect("Extra Lines", [x for x in nc if x != col], key="line_m")
            with c2:
                cols_to_plot = [col] + multi
                fig = px.line(main_df, y=cols_to_plot, color_discrete_sequence=PC, title="Trend Analysis Line Chart")
                fig.update_layout(**LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[2]:
            if cc:
                c1, c2 = st.columns([1, 3])
                with c1:
                    cat = st.selectbox("Category", cc, key="pie_c")
                    val = st.selectbox("Value", nc, key="pie_v")
                with c2:
                    pie_df = main_df.groupby(cat)[val].sum().reset_index()
                    fig = px.pie(pie_df, names=cat, values=val, color_discrete_sequence=PC, hole=0.4, title=f"Share of {val} by {cat}")
                    fig.update_layout(**LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[3]:
            if len(nc) >= 2:
                c1, c2 = st.columns([1, 3])
                with c1:
                    x = st.selectbox("X", nc, key="sc_x")
                    y = st.selectbox("Y", nc, index=1, key="sc_y")
                    sz = st.selectbox("Size", ["None"] + nc, key="sc_s")
                    clr = st.selectbox("Color", ["None"] + cc, key="sc_c")
                with c2:
                    fig = px.scatter(main_df, x=x, y=y, size=None if sz == "None" else sz, color=None if clr == "None" else clr, color_discrete_sequence=PC, opacity=0.8, title=f"Relationship between {x} and {y}")
                    fig.update_layout(**LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[4]:
            if len(nc) >= 2:
                corr = main_df[nc].corr()
                fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", title="Correlation Heatmap Matrix", aspect="auto")
                fig.update_layout(**LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[5]:
            c1, c2 = st.columns([1, 3])
            with c1:
                col = st.selectbox("Column", nc, key="box_c")
                grp = st.selectbox("Group by", ["None"] + cc, key="box_g")
            with c2:
                fig = px.box(main_df, x=None if grp == "None" else grp, y=col, color=None if grp == "None" else grp, color_discrete_sequence=PC, title=f"Outlier & Spread Analysis for {col}")
                fig.update_layout(**LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

        with chart_tabs[6]:
            c1, c2 = st.columns([1, 3])
            with c1:
                col = st.selectbox("Column", nc, key="hist_c")
                bins = st.slider("Bins", 5, 100, 20)
            with c2:
                fig = px.histogram(main_df, x=col, nbins=bins, color_discrete_sequence=PC, title=f"Frequency Distribution of {col}")
                fig.update_layout(**LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

    # ─── AI AUTO ANALYZE & EXPORT REPORT ──────────────────────────
    st.markdown('<div class="section-title">🤖 AI Auto Analysis & Reports</div>', unsafe_allow_html=True)
    
    if st.button("✨ Analyze My Data with AI", use_container_width=True):
        with st.spinner("AI analyzing your data..."):
            try:
                prompt = f"""Dataset Summary:
- Shape: {main_df.shape[0]} rows × {main_df.shape[1]} columns
- Columns: {list(main_df.columns)}
- Numeric columns: {nc}
- Text columns: {cc}
- Statistics:
{main_df.describe().to_string()}

Provide: key insights, trends, and 3 actionable recommendations."""

                r = llm.chat.completions.create(
                    model=MODEL, max_tokens=1500,
                    messages=[
                        {"role": "system", "content": f"You are an expert data analyst. Respond in {st.session_state.lang}. Be concise, clear, and insightful."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.session_state.ai_insight_text = r.choices[0].message.content
                st.session_state.analyzed = True
                try:
                    db.table("chat_history").insert({"role": "assistant", "message": st.session_state.ai_insight_text}).execute()
                except:
                    pass
                st.rerun()
            except Exception as e:
                st.error(f"AI Error: {e}")

    if st.session_state.analyzed and st.session_state.ai_insight_text:
        st.markdown(f'<div class="amsg">🤖 {st.session_state.ai_insight_text}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 📋 Export AI Executive Summary")
        
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.cell(200, 10, txt="AI Executive Data Analysis Report", ln=1, align="C")
            pdf.ln(10)
            
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.cell(200, 10, txt=f"- Total Active Filtered Rows: {main_df.shape[0]}", ln=1)
            pdf.ln(5)
            
            clean_text = st.session_state.ai_insight_text.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 6, txt=clean_text)
            
            # FIXED: Output converted explicitly to bytes string object for streamlit
            pdf_bytes = bytes(pdf.output())
            
            st.download_button(
                label="📥 Download Executive PDF Report",
                data=pdf_bytes,
                file_name="AI_Data_Executive_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.warning(f"Note on PDF mapping: {pdf_err}")

else:
    st.markdown("""
    <div style="background:white; border-radius:20px; padding:60px; text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.08); margin-top:20px;">
        <div style="font-size:64px; margin-bottom:16px;">📂</div>
        <h2 style="color:#1e3a5f; margin:0 0 10px;">Upload a CSV to get started</h2>
        <p style="color:#888; font-size:15px;">Use the sidebar to upload your data file</p>
    </div>
    """, unsafe_allow_html=True)


# ─── GLOBAL AI CHAT CONTEXT ───────────────────────────────────
st.markdown('<div class="section-title">💬 Chat with AI</div>', unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    if st.session_state.msgs:
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for m in st.session_state.msgs:
            if m["role"] == "user":
                st.markdown(f'<div class="umsg">👤 {m["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="amsg">🤖 {m["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:white; border-radius:12px; padding:20px; text-align:center; color:#aaa;">
            💬 Ask anything about your data or any topic!
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns([5, 1])
lang_placeholders = {
    "Telugu": "మీ డేటా గురించి అడగండి...", "Hindi":  "अपने डेटा के बारे में पूछें...", "Tamil":  "உங்கள் தரவைப் பற்றி கேளுங்கள்...",
}
placeholder = lang_placeholders.get(st.session_state.lang, "Ask about your data or anything...")

with c1:
    user_input = st.text_input("", placeholder=placeholder, label_visibility="collapsed", key="chat_input")
with c2:
    send = st.button("Send 🚀", use_container_width=True)

if send and user_input:
    st.session_state.msgs.append({"role": "user", "content": user_input})
    
    ctx = ""
    if main_df is not None:
        ctx = f"\n\nDataset context: {main_df.shape[0]} rows, columns: {list(main_df.columns)}\nStats:\n{main_df.describe().to_string()}"

    with st.spinner("Thinking..."):
        try:
            r = llm.chat.completions.create(
                model=MODEL, max_tokens=1024,
                messages=[
                    {"role": "system", "content": f"You are an expert data analyst and AI assistant. Respond in {st.session_state.lang}. Be helpful, clear, and concise.{ctx}"},
                    *st.session_state.msgs[-10:]
                ]
            )
            reply = r.choices[0].message.content
        except Exception as e:
            reply = f"Error: {e}"

    st.session_state.msgs.append({"role": "assistant", "content": reply})

    try:
        db.table("chat_history").insert({"role": "user", "message": user_input}).execute()
        db.table("chat_history").insert({"role": "assistant", "message": reply}).execute()
    except:
        pass

    st.rerun()
