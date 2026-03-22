# ==========================================
# 🤖 DEEPAN AI (IRON MAN JARVIS STYLE)
# ==========================================

import streamlit as st
import fitz
from pptx import Presentation
from docx import Document
import matplotlib.pyplot as plt
import re
import os
import numpy as np

from sentence_transformers import SentenceTransformer
from duckduckgo_search import DDGS

# ==========================================
# 🧠 MODEL
# ==========================================

model = SentenceTransformer('all-MiniLM-L6-v2')

# ==========================================
# 🎨 IRON MAN UI
# ==========================================

st.set_page_config(page_title="Deepan AI", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0a0f1c;
    color: white;
}
.title {
    font-size: 40px;
    color: #00e6ff;
    text-align: center;
    text-shadow: 0px 0px 15px #00e6ff;
}
.chat-user {
    background: linear-gradient(90deg,#007cf0,#00dfd8);
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: right;
}
.chat-ai {
    background: #111827;
    border: 1px solid #00e6ff;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🤖 DEEPAN AI</div>", unsafe_allow_html=True)

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

def semantic_search(question, chunks, embeddings):
    q_emb = model.encode([question])[0]
    scores = np.dot(embeddings, q_emb)
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
# 🤖 JARVIS ANSWER
# ==========================================

def get_answer(q, chunks, emb):

    doc = " ".join(semantic_search(q, chunks, emb))
    web = web_search(q)

    return f"""
🤖 **Deepan AI Response**

📄 From Notes:
{doc[:400]}

🌐 From Internet:
{web[:400]}
"""

# ==========================================
# 🗺 MINDMAP
# ==========================================

def create_mindmap(topics):
    if not topics:
        return None

    fig, ax = plt.subplots(figsize=(8,6))
    ax.set_facecolor("#0a0f1c")

    root = topics[0]
    ax.text(0.5, 0.9, root, ha='center',
            bbox=dict(boxstyle="round", fc="#00e6ff"))

    spacing = 0.8 / max(1, len(topics)-1)

    for i, t in enumerate(topics[1:]):
        x = 0.1 + i * spacing
        ax.text(x, 0.6, t, ha='center',
                bbox=dict(boxstyle="round", fc="#007cf0"))

        ax.annotate("", xy=(0.5,0.85), xytext=(x,0.65),
                    arrowprops=dict(arrowstyle="->", color="#00e6ff"))

    ax.axis('off')

    path = "mindmap.png"
    plt.savefig(path, bbox_inches='tight', facecolor="#0a0f1c")
    plt.close()

    return path

# ==========================================
# 🎤 VOICE (BROWSER)
# ==========================================

def voice_ui():
    st.components.v1.html("""
    <button onclick="start()">🎤 Speak</button>
    <p id="out"></p>

    <script>
    function start(){
        var r = new webkitSpeechRecognition();
        r.onresult = function(e){
            document.getElementById("out").innerText =
            e.results[0][0].transcript;
        };
        r.start();
    }
    </script>
    """, height=150)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("⚙️ Control Panel")

file = st.sidebar.file_uploader("Upload File", type=["pdf","pptx","docx","txt"])

# ==========================================
# MAIN
# ==========================================

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

    # Mindmap
    topics = list(set(re.findall(r'\b[A-Z][a-zA-Z]{4,}\b', text)))[:8]
    st.subheader("🗺 Mind Map")
    st.image(create_mindmap(topics))

    # Voice
    st.subheader("🎤 Voice Assistant")
    voice_ui()

    # Chat
    st.subheader("💬 Chat")

    for q,a in st.session_state.chat:
        st.markdown(f"<div class='chat-user'>🧑 {q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-ai'>{a}</div>", unsafe_allow_html=True)

    user = st.chat_input("Ask anything...")

    if user:
        ans = get_answer(user, chunks, st.session_state.emb)
        st.session_state.chat.append((user, ans))
        st.rerun()

else:
    st.info("Upload file to activate Deepan AI 🚀")
