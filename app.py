import streamlit as st, pandas as pd, plotly.express as px, base64
from groq import Groq
from supabase import create_client

# CONFIG
st.set_page_config("📊 Analytics AI", "📊", layout="wide")
[st.session_state.setdefault(k,v) for k,v in [("msgs",[]),("dark",False),("df",None),("lang","English")]]

db  = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
llm = Groq(api_key=st.secrets["GROQ_API_KEY"])

# THEME
D = st.session_state.dark
BG,CARD,TXT = ("#0d1117","#161b22","#e6edf3") if D else ("#f6f8fa","#ffffff","#24292f")

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
*{{font-family:'DM Sans',sans-serif}}
.stApp{{background:{BG}}}
.hdr{{background:linear-gradient(135deg,#0a2540,#1a4a7a);padding:22px 28px;border-radius:16px;color:white;margin-bottom:20px}}
.kpi{{background:{CARD};border:1px solid {'#30363d' if D else '#e1e4e8'};border-radius:12px;padding:18px;text-align:center}}
.umsg{{background:#0a2540;color:white;padding:10px 16px;border-radius:16px 16px 4px 16px;max-width:72%;margin:5px 0 5px auto;font-size:14px}}
.amsg{{background:{CARD};color:{TXT};padding:10px 16px;border-radius:16px 16px 16px 4px;max-width:72%;margin:5px 0;border-left:3px solid #1a4a7a;font-size:14px}}
.stButton>button{{background:#0a2540!important;color:white!important;border-radius:20px!important;border:none!important;padding:8px 20px!important}}
.stTextInput input{{border-radius:20px!important;border:1.5px solid #1a4a7a!important;background:{CARD}!important;color:{TXT}!important}}
div[data-testid="metric-container"]{{background:{CARD};border:1px solid {'#30363d' if D else '#e1e4e8'};border-radius:12px;padding:12px}}
</style>""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.session_state.dark = st.toggle("🌙 Dark Mode", D)
    st.session_state.lang = st.selectbox("🌐 Lang", ["English","Telugu","Hindi","Tamil","Spanish"])
    st.markdown("---")
    f = st.file_uploader("📂 Upload CSV", type=["csv"])
    if f:
        st.session_state.df = pd.read_csv(f)
        st.success(f"✅ {f.name} • {st.session_state.df.shape[0]}R × {st.session_state.df.shape[1]}C")
    st.markdown("---")
    if st.button("📄 Export Chat") and st.session_state.msgs:
        b = base64.b64encode("\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.msgs]).encode()).decode()
        st.markdown(f'<a href="data:file/txt;base64,{b}" download="chat.txt">⬇️ Download</a>', unsafe_allow_html=True)
    st.metric("💬 Messages", len(st.session_state.msgs))
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.msgs = []; st.rerun()

# HEADER
st.markdown("""<div class="hdr"><h2 style="margin:0">📊 Analytics AI Dashboard</h2>
<small style="opacity:.7">Upload CSV → Auto Charts + AI Insights</small></div>""", unsafe_allow_html=True)

df = st.session_state.df

# DASHBOARD
if df is not None:
    nc = df.select_dtypes(include='number').columns.tolist()
    cc = df.select_dtypes(include='object').columns.tolist()

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📋 Rows", df.shape[0])
    c2.metric("📊 Columns", df.shape[1])
    c3.metric("🔢 Numeric", len(nc))
    c4.metric("❌ Missing", int(df.isnull().sum().sum()))

    # Charts
    if nc:
        t1,t2,t3,t4,t5,t6 = st.tabs(["📊 Bar","📈 Line","🥧 Pie","🔵 Scatter","🔥 Heatmap","📦 Box"])
        PC = px.colors.qualitative.Set2
        L = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color=TXT)

        with t1:
            col=st.selectbox("Column",nc,key="b")
            fig=px.bar(df,x=cc[0] if cc else None,y=col,color=cc[0] if cc else None,color_discrete_sequence=PC)
            fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)

        with t2:
            col=st.selectbox("Column",nc,key="l")
            fig=px.line(df,y=col,color_discrete_sequence=["#1a4a7a"])
            fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)

        with t3:
            if cc:
                cat=st.selectbox("Category",cc,key="p"); val=st.selectbox("Value",nc,key="pv")
                fig=px.pie(df.groupby(cat)[val].sum().reset_index(),names=cat,values=val,color_discrete_sequence=PC)
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("Need a text/category column")

        with t4:
            if len(nc)>=2:
                x=st.selectbox("X",nc,key="sx"); y=st.selectbox("Y",nc,index=1,key="sy")
                c=st.selectbox("Color",["None"]+cc,key="sc")
                fig=px.scatter(df,x=x,y=y,color=None if c=="None" else c,color_discrete_sequence=PC)
                fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
            else: st.info("Need 2+ numeric columns")

        with t5:
            if len(nc)>=2:
                fig=px.imshow(df[nc].corr(),text_auto=True,color_continuous_scale="Blues",title="Correlation Matrix")
                fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
            else: st.info("Need 2+ numeric columns")

        with t6:
            col=st.selectbox("Column",nc,key="bx")
            fig=px.box(df,x=cc[0] if cc else None,y=col,color=cc[0] if cc else None,color_discrete_sequence=PC)
            fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)

    # AI Auto Analyze
    st.markdown("---")
    if st.button("🤖 AI Auto Analyze My Data ✨", use_container_width=True):
        with st.spinner("Analyzing..."):
            try:
                r = llm.chat.completions.create(model="llama3-8b-8192", max_tokens=1024, messages=[
                    {"role":"system","content":f"Expert data analyst. Respond in {st.session_state.lang}. Give insights, trends, anomalies, recommendations."},
                    {"role":"user","content":f"Dataset: {df.shape[0]} rows, cols:{list(df.columns)}\nStats:\n{df.describe().to_string()}\nMissing:{df.isnull().sum().to_dict()}"}
                ])
                ins = r.choices[0].message.content
                st.markdown(f'<div class="amsg">🤖 {ins}</div>', unsafe_allow_html=True)
                try: db.table("chat_history").insert({"role":"assistant","message":ins}).execute()
                except: pass
            except Exception as e: st.error(f"Error: {e}")
else:
    st.markdown(f"""<div style="background:{'#161b22' if D else '#0a2540'};border-radius:16px;
    padding:60px;text-align:center;color:white">
    <h2>📂 Upload a CSV to get started</h2>
    <p style="opacity:.6">← Use sidebar to upload • Auto charts + AI analysis</p></div>""", unsafe_allow_html=True)

# CHAT
st.markdown("---")
st.markdown("### 💬 Chat with AI")
for m in st.session_state.msgs:
    css,ic = ("umsg","👤") if m["role"]=="user" else ("amsg","🤖")
    st.markdown(f'<div class="{css}">{ic} {m["content"]}</div>', unsafe_allow_html=True)

c1,c2 = st.columns([5,1])
ph = {"Telugu":"డేటా గురించి అడగండి...","Hindi":"डेटा पूछें..."}.get(st.session_state.lang,"Ask about your data...")
with c1: inp = st.text_input("",placeholder=ph,label_visibility="collapsed")
with c2: send = st.button("Send 🚀",use_container_width=True)

if send and inp:
    st.session_state.msgs.append({"role":"user","content":inp})
    ctx = f"\nData: {df.shape}, cols:{list(df.columns)}\n{df.describe().to_string()}" if df is not None else ""
    with st.spinner("..."):
        try:
            r = llm.chat.completions.create(model="llama3-8b-8192", max_tokens=1024, messages=[
                {"role":"system","content":f"Expert data analyst. Respond in {st.session_state.lang}.{ctx}"},
                *st.session_state.msgs
            ])
            rep = r.choices[0].message.content
        except Exception as e: rep = f"Error: {e}"
    st.session_state.msgs.append({"role":"assistant","content":rep})
    try:
        db.table("chat_history").insert({"role":"user","message":inp}).execute()
        db.table("chat_history").insert({"role":"assistant","message":rep}).execute()
    except: pass
    st.rerun()
