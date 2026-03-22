# ==========================================
# 🔥 AI STUDY APP (FINAL PRO MAX)
# ==========================================

import streamlit as st
import fitz
from pptx import Presentation
from docx import Document
import matplotlib.pyplot as plt
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================
# 🔐 OPENAI (OPTIONAL)
# ==========================================

USE_AI = False
try:
    from openai import OpenAI
    if os.getenv("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"):
        client = OpenAI()
        USE_AI = True
except:
    pass

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
# 🧠 TEXT PROCESSING
# ==========================================

def split_text(text):
    return [c for c in text.split(".") if len(c) > 40]

def extract_topics(text):
    words = re.findall(r'\b[A-Z][a-zA-Z]{4,}\b', text)
    return list(set(words))[:8]

# ==========================================
# 💬 CHATBOT (BETTER)
# ==========================================

def get_answer(question, chunks):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(chunks + [question])

    sim = cosine_similarity(vectors[-1], vectors[:-1])[0]
    top = sim.argsort()[-3:][::-1]

    context = " ".join([chunks[i] for i in top])

    if USE_AI:
        try:
            res = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{
                    "role": "user",
                    "content": f"""
Answer like a tutor.

Context:
{context}

Question:
{question}
"""
                }]
            )
            return res.choices[0].message.content
        except:
            pass

    return "📌 " + context

# ==========================================
# 🗺 BEAUTIFUL TREE MINDMAP
# ==========================================

def create_mindmap(topics):
    if not topics:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))

    root = topics[0]
    ax.text(0.5, 0.9, root, ha='center',
            bbox=dict(boxstyle="round", fc="#4CAF50", ec="black"))

    y = 0.6
    spacing = 0.8 / max(1, len(topics)-1)

    for i, t in enumerate(topics[1:]):
        x = 0.1 + i * spacing

        ax.text(x, y, t, ha='center',
                bbox=dict(boxstyle="round", fc="#2196F3", ec="black"))

        ax.annotate("",
                    xy=(0.5, 0.85),
                    xytext=(x, y+0.05),
                    arrowprops=dict(arrowstyle="->", lw=1.5))

    ax.axis('off')

    path = "mindmap.png"
    plt.savefig(path, bbox_inches='tight')
    plt.close()

    return path

# ==========================================
# 🎤 BROWSER VOICE INPUT (JS)
# ==========================================

def voice_input_ui():
    st.components.v1.html("""
    <button onclick="startDictation()">🎤 Speak</button>
    <p id="output"></p>

    <script>
    function startDictation() {
        var recognition = new webkitSpeechRecognition();
        recognition.lang = "en-US";

        recognition.onresult = function(event) {
            document.getElementById("output").innerText =
                event.results[0][0].transcript;
        };

        recognition.start();
    }
    </script>
    """, height=150)

# ==========================================
# 🎨 UI
# ==========================================

st.set_page_config(page_title="AI Study Pro", layout="wide")

st.title("🔥 AI Study Assistant (Final Version)")

file = st.file_uploader("📂 Upload file", type=["pdf","pptx","docx","txt"])
days = st.number_input("📅 Study Days",1,30,3)

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
    st.session_state["chunks"] = chunks

    st.subheader("📄 Preview")
    st.write(text[:1200])

    # Mindmap
    topics = extract_topics(text)
    mind = create_mindmap(topics)

    st.subheader("🗺 Mind Map")
    if mind:
        st.image(mind)

    # Chat
    st.subheader("💬 Chat")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_input = st.text_input("Ask question")

    # Voice UI
    voice_input_ui()

    if user_input:
        ans = get_answer(user_input, chunks)
        st.session_state.chat.append((user_input, ans))

    for q,a in st.session_state.chat:
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 AI:** {a}")
# streamlit run "c:\Users\karun\Downloads\generate_image\python notes_generator with diagram.py"
