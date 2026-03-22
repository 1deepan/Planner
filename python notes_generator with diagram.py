# ==========================================
# 🤖 DEEPAN AI - STABLE JARVIS VERSION
# ==========================================

import streamlit as st
import os
import fitz
import numpy as np
import re
import matplotlib.pyplot as plt

from sentence_transformers import SentenceTransformer
from duckduckgo_search import DDGS
from gtts import gTTS
import base64

# ==========================================
# 🔐 OPENAI SETUP
# ==========================================

from openai import OpenAI

client = None
api_key = os.getenv("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")

if api_key:
    client = OpenAI(api_key=api_key)

# ==========================================
# 🧠 MODEL
# ==========================================

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# ==========================================
# 🎨 UI
# ==========================================

st.set_page_config(page_title="Deepan AI", layout="wide")

st.markdown("""
<style>
body { background-color:#0a0f1c; color:white; }

.title {
    text-align:center;
    font-size:40px;
    color:#00e6ff;
    text-shadow:0 0 15px #00e6ff;
}

.chat-user {
    background:#007cf0;
    padding:10px;
    border-radius:10px;
    margin:5px;
    text-align:right;
}

.chat-ai {
    background:#111827;
    border:1px solid #00e6ff;
    padding:10px;
    border-radius:10px;
    margin:5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🤖 DEEPAN AI</div>", unsafe_allow_html=True)

# ==========================================
# 📄 FILE READER
# ==========================================

def read_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

# ==========================================
# 🧠 PROCESSING
# ==========================================

def split_text(text):
    return [c.strip() for c in text.split(".") if len(c) > 40]

def embed_chunks(chunks):
    return embed_model.encode(chunks)

def search_chunks(query, chunks, emb):
    q_emb = embed_model.encode([query])[0]
    scores = np.dot(emb, q_emb)
    top = np.argsort(scores)[-5:][::-1]
    return [chunks[i] for i in top]

# ==========================================
# 🌐 WEB SEARCH
# ==========================================

def web_search(query):
    try:
        with DDGS() as ddgs:
            results = [r["body"] for r in ddgs.text(query, max_results=3)]
        return " ".join(results)
    except:
        return ""

# ==========================================
# 🤖 AI RESPONSE
# ==========================================

def get_response(query, chunks, emb, history):

    doc_context = " ".join(search_chunks(query, chunks, emb))
    web_context = web_search(query)

    if client:
        messages = [{"role": "system", "content": "You are Deepan AI assistant."}]

        for u, a in history[-5:]:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})

        messages.append({
            "role": "user",
            "content": f"""
Document:
{doc_context}

Web:
{web_context}

Question:
{query}
"""
        })

        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"⚠️ AI Error: {str(e)}"

    return "⚠️ API Key Missing"

# ==========================================
# 🔊 VOICE OUTPUT
# ==========================================

def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("voice.mp3")

        audio = open("voice.mp3", "rb").read()
        b64 = base64.b64encode(audio).decode()

        st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}">
        </audio>
        """, unsafe_allow_html=True)
    except:
        pass

# ==========================================
# 📅 STUDY PLAN
# ==========================================

def study_plan(topics, days):
    per_day = max(1, len(topics)//days)
    plan = []

    for i in range(days):
        plan.append(f"Day {i+1}: {', '.join(topics[i*per_day:(i+1)*per_day])}")

    return "\n".join(plan)

# ==========================================
# 🗺 MINDMAP
# ==========================================

def mindmap(topics):
    fig, ax = plt.subplots()

    if topics:
        ax.text(0.5, 0.9, topics[0], ha='center')

    for i, t in enumerate(topics[1:5]):
        ax.text(0.2+i*0.2, 0.5, t, ha='center')

    ax.axis('off')
    return fig

# ==========================================
# SESSION MEMORY
# ==========================================

if "chat" not in st.session_state:
    st.session_state.chat = []

# ==========================================
# INPUT
# ==========================================

file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
days = st.sidebar.slider("Study Days", 1, 10, 5)

# ==========================================
# MAIN
# ==========================================

if file:

    text = read_pdf(file)
    chunks = split_text(text)
    emb = embed_chunks(chunks)

    topics = list(set(re.findall(r'\b[A-Z][a-zA-Z]{4,}\b', text)))[:10]

    st.subheader("🗺 Mindmap")
    st.pyplot(mindmap(topics))

    st.subheader("📅 Study Plan")
    st.write(study_plan(topics, days))

    st.subheader("💬 Chat")

    for q, a in st.session_state.chat:
        st.markdown(f"<div class='chat-user'>{q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-ai'>{a}</div>", unsafe_allow_html=True)

    user = st.chat_input("Ask anything...")

    if user:
        ans = get_response(user, chunks, emb, st.session_state.chat)
        st.session_state.chat.append((user, ans))

        speak(ans)
        st.rerun()

else:
    st.info("📂 Upload a PDF to start Deepan AI")
