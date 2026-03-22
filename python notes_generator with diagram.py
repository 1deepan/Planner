# ==========================================
# 🔥 GOD LEVEL AI STUDY APP
# ==========================================

import streamlit as st
import fitz
from pptx import Presentation
from docx import Document
import matplotlib.pyplot as plt
import re
import os
import speech_recognition as sr
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
# 🧠 SMART TOPICS + IMPORTANCE
# ==========================================

def extract_topics(text):
    lines = text.split("\n")
    topics = []

    for line in lines:
        line = line.strip()
        if 5 < len(line) < 80:
            if line.istitle() or ":" in line:
                topics.append(line)

    words = re.findall(r'\b[A-Z][a-zA-Z]{4,}\b', text)
    topics += list(set(words))

    return list(set(topics))[:10]

def highlight_important(text):
    keywords = ["definition", "algorithm", "formula", "theorem", "step"]
    important = []

    for line in text.split("\n"):
        for k in keywords:
            if k.lower() in line.lower():
                important.append(line)

    return important[:8]

# ==========================================
# 🗺 FLOWCHART GENERATOR
# ==========================================

def create_flowchart(steps):
    if len(steps) < 2:
        return None

    fig, ax = plt.subplots(figsize=(6, len(steps)))

    for i, step in enumerate(steps):
        y = len(steps) - i

        ax.text(
            0.5, y,
            step[:40],
            ha='center',
            bbox=dict(boxstyle="round", fc="lightblue")
        )

        if i < len(steps)-1:
            ax.annotate(
                "",
                xy=(0.5, y-1),
                xytext=(0.5, y-0.2),
                arrowprops=dict(arrowstyle="->")
            )

    ax.axis('off')

    path = "flowchart.png"
    plt.savefig(path)
    plt.close()

    return path

# ==========================================
# 💬 CHATBOT (BETTER RAG)
# ==========================================

def split_text(text):
    return [chunk for chunk in text.split(".") if len(chunk) > 40]

def get_answer(question, chunks):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(chunks + [question])

    sim = cosine_similarity(vectors[-1], vectors[:-1])
    top_indices = sim[0].argsort()[-3:][::-1]

    context = " ".join([chunks[i] for i in top_indices])

    if USE_AI:
        try:
            res = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{
                    "role": "user",
                    "content": f"""
Answer clearly like a tutor.

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

    return f"📌 Answer from document:\n{context}"

# ==========================================
# 🎤 VOICE INPUT
# ==========================================

def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak now...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return "Could not understand"

# ==========================================
# 🎨 UI
# ==========================================

st.set_page_config(page_title="AI Study Pro", layout="wide")

st.title("🔥 AI Study Assistant (Pro Version)")

uploaded_file = st.file_uploader("Upload file", type=["pdf","pptx","docx","txt"])
days = st.number_input("Study days", 1, 30, 3)

if uploaded_file:

    if uploaded_file.name.endswith(".pdf"):
        text = read_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".pptx"):
        text = read_ppt(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        text = read_docx(uploaded_file)
    else:
        text = read_txt(uploaded_file)

    st.session_state["chunks"] = split_text(text)

    st.subheader("📄 Preview")
    st.write(text[:1500])

    # IMPORTANT TOPICS
    st.subheader("🔥 Important Exam Topics")
    important = highlight_important(text)
    for i in important:
        st.write("⭐", i)

    # FLOWCHART
    st.subheader("🗺 Flowchart")
    steps = extract_topics(text)
    flow = create_flowchart(steps)
    if flow:
        st.image(flow)

    # CHAT
    st.subheader("💬 Chat")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    col1, col2 = st.columns([4,1])

    with col1:
        user_input = st.text_input("Ask anything from your notes")

    with col2:
        if st.button("🎤 Speak"):
            user_input = voice_input()

    if user_input:
        answer = get_answer(user_input, st.session_state["chunks"])

        st.session_state.chat.append(("You", user_input))
        st.session_state.chat.append(("AI", answer))

    for role, msg in st.session_state.chat:
        if role == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")
# streamlit run "c:\Users\karun\Downloads\generate_image\python notes_generator with diagram.py"