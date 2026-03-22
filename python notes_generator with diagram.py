# ==========================================
# 🤖 DEEPAN AI - JARVIS FINAL VERSION
# ==========================================

import streamlit as st
import fitz
from pptx import Presentation
from docx import Document
import matplotlib.pyplot as plt
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from duckduckgo_search import DDGS

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ==========================================
# 🧠 MODEL
# ==========================================

model = SentenceTransformer('all-MiniLM-L6-v2')

# ==========================================
# 🎨 UI (IRON MAN STYLE)
# ==========================================

st.set_page_config(page_title="Deepan AI", layout="wide")

st.markdown("""
<style>
body {background:#0a0f1c;color:white;}
.title {font-size:40px;color:#00e6ff;text-align:center;text-shadow:0 0 15px #00e6ff;}
.chat-user {background:#007cf0;padding:10px;border-radius:10px;margin:5px;text-align:right;}
.chat-ai {background:#111827;border:1px solid #00e6ff;padding:10px;border-radius:10px;margin:5px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🤖 DEEPAN AI </div>", unsafe_allow_html=True)

# ==========================================
# 📄 FILE READERS
# ==========================================

def read_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

def read_ppt(file):
    text = ""
    prs = Presentation(file)
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text

def read_docx(file):
    return "\n".join([p.text for p in Document(file).paragraphs])

def read_txt(file):
    return file.read().decode("utf-8")

# ==========================================
# 🧠 PROCESSING
# ==========================================

def split_text(text):
    return [c.strip() for c in text.split(".") if len(c) > 40]

def embed_chunks(chunks):
    return model.encode(chunks)

def semantic_search(q, chunks, emb):
    q_emb = model.encode([q])[0]
    scores = np.dot(emb, q_emb)
    top = np.argsort(scores)[-5:][::-1]
    return [chunks[i] for i in top]

# ==========================================
# 🌐 WEB SEARCH
# ==========================================

def web_search(query):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            results.append(r["body"])
    return " ".join(results)

# ==========================================
# 🤖 SMART ANSWER (JARVIS STYLE)
# ==========================================

def get_answer(q, chunks, emb):

    doc = " ".join(semantic_search(q, chunks, emb))
    web = web_search(q)

    return f"""
Here’s a clear explanation:

📘 From your notes:
{doc[:500]}

🌐 Additional info:
{web[:500]}
"""

# ==========================================
# 🎤 VOICE (INPUT + OUTPUT)
# ==========================================

def voice_system():
    st.components.v1.html("""
    <button onclick="start()">🎤 Speak</button>
    <p id="text"></p>

    <script>
    function start(){
        var rec = new webkitSpeechRecognition();
        rec.onresult = function(e){
            let txt = e.results[0][0].transcript;
            document.getElementById("text").innerText = txt;
            window.parent.postMessage(txt, "*");
        };
        rec.start();
    }

    window.addEventListener("message", (e)=>{
        let speech = new SpeechSynthesisUtterance(e.data);
        speech.rate = 0.9;
        speech.pitch = 0.8;
        speech.lang = "en-US";
        speechSynthesis.speak(speech);
    });
    </script>
    """, height=200)

# ==========================================
# 📅 STUDY PLAN
# ==========================================

def generate_plan(topics, days):
    per_day = max(1, len(topics)//days)
    plan = []

    for i in range(days):
        plan.append(f"Day {i+1}: {', '.join(topics[i*per_day:(i+1)*per_day])} + Revision")

    return "\n".join(plan)

# ==========================================
# 🗺 MINDMAP
# ==========================================

def create_mindmap(topics):
    fig, ax = plt.subplots(figsize=(8,6))
    ax.set_facecolor("#0a0f1c")

    ax.text(0.5,0.9,topics[0],ha='center',bbox=dict(boxstyle="round",fc="#00e6ff"))

    for i,t in enumerate(topics[1:]):
        x = 0.1 + i*(0.8/max(1,len(topics)-1))
        ax.text(x,0.6,t,ha='center',bbox=dict(boxstyle="round",fc="#007cf0"))
        ax.annotate("",xy=(0.5,0.85),xytext=(x,0.65),
                    arrowprops=dict(arrowstyle="->",color="#00e6ff"))

    ax.axis('off')
    plt.savefig("mindmap.png",bbox_inches='tight',facecolor="#0a0f1c")
    plt.close()

    return "mindmap.png"

# ==========================================
# 📤 PDF EXPORT (FORMATTED)
# ==========================================

def export_pdf(topics, plan):
    doc = SimpleDocTemplate("Deepan_AI_Notes.pdf")
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("<b>Deepan AI Study Notes</b>", styles["Title"]))
    content.append(Spacer(1,10))

    content.append(Paragraph("<b>Topics:</b>", styles["Heading2"]))
    for t in topics:
        content.append(Paragraph(t, styles["Normal"]))

    content.append(Spacer(1,10))

    content.append(Paragraph("<b>Study Plan:</b>", styles["Heading2"]))
    for p in plan.split("\n"):
        content.append(Paragraph(p, styles["Normal"]))

    doc.build(content)

    return "Deepan_AI_Notes.pdf"

# ==========================================
# MAIN
# ==========================================

file = st.sidebar.file_uploader("Upload File", type=["pdf","pptx","docx","txt"])
days = st.sidebar.slider("Study Days",1,30,5)

if file:

    if file.name.endswith(".pdf"):
        text = read_pdf(file)
    elif file.name.endswith(".pptx"):
        text = read_ppt(file)
    elif file.name.endswith(".docx"):
        text = read_docx(file)
    else:
        text = read_txt(file)

    chunks = split_text(text)

    if "emb" not in st.session_state:
        st.session_state.emb = embed_chunks(chunks)

    if "chat" not in st.session_state:
        st.session_state.chat = []

    topics = list(set(re.findall(r'\b[A-Z][a-zA-Z]{4,}\b', text)))[:10]

    st.image(create_mindmap(topics))

    plan = generate_plan(topics, days)
    st.subheader("📅 Study Plan")
    st.write(plan)

    voice_system()

    for q,a in st.session_state.chat:
        st.markdown(f"<div class='chat-user'>{q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-ai'>{a}</div>", unsafe_allow_html=True)

    user = st.chat_input("Ask anything...")

    if user:
        ans = get_answer(user, chunks, st.session_state.emb)
        st.session_state.chat.append((user, ans))
        st.rerun()

    pdf = export_pdf(topics, plan)

    with open(pdf, "rb") as f:
        st.download_button("📤 Download Notes", f, pdf)

else:
    st.info("Upload file to activate Deepan AI 🚀")
