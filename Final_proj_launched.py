import tkinter as tk
from customtkinter import *
import requests
import pyttsx3
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
import os
from tkinter import Toplevel, Text, Scrollbar
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import speech_recognition as sr

# Setup
nltk.download('punkt')
nltk.download('stopwords')
engine = pyttsx3.init()

# API Configuration
TOGETHER_API_KEY = "a2a66a15b60701abe7016e1101f00b53b2f7fdfcab04b43befa264181bc068f9"
LLM_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
LLM_URL = "https://api.together.xyz/v1/chat/completions"

# Context & Urgency
excuse_contexts = {
    "HEALTH ISSUE": "An excuse involving illness or sudden medical problems.",
    "TECHNICAL ISSUE": "An excuse involving software crashes, internet failure, etc.",
    "FAMILY REASON": "An excuse involving family emergencies or responsibilities.",
    "TRANSPORT ISSUE": "An excuse involving traffic or transport breakdowns.",
    "WEATHER ISSUE": "An excuse due to bad weather like storms or flooding.",
    "SOCIAL EVENT": "An excuse involving unexpected social commitments.",
    "ACADEMIC CONFLICT": "An excuse related to school deadlines or class clashes.",
    "WORKLOAD ISSUE": "An excuse involving burnout or overworking.",
    "TIME EXCUSE": "An excuse for poor time management or missed alarms.",
    "DEFAULT": "A general excuse not tied to any specific event."
}

urgency_descriptions = {
    "Low": "Minor delay or minor issue.",
    "Medium": "Significant delay due to important reasons.",
    "High": "Critical emergency or unavoidable circumstance."
}

categories = list(excuse_contexts.keys())
urgencies = list(urgency_descriptions.keys())

# API Request
def generate_llm_response(system_prompt, user_prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    response = requests.post(LLM_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

# Excuse + Proof
def generate_excuse_and_proof(category, urgency):
    context = excuse_contexts.get(category, excuse_contexts["DEFAULT"])
    urgency_desc = urgency_descriptions.get(urgency, "")

    system_prompt = "You are an assistant that creates believable excuses and supporting proofs."
    user_prompt = (
        f"Create a concise and believable excuse for the following:\n"
        f"Category: {category}\nContext: {context}\nUrgency: {urgency} - {urgency_desc}\n\n"
        f"Write the excuse in one sentence.\n"
        f"Then write a supporting proof or explanation (1-2 sentences) that makes the excuse more credible.\n"
        f"Format your response as:\nExcuse: <excuse here>\nProof: <proof here>"
    )

    result_text = generate_llm_response(system_prompt, user_prompt)

    excuse, proof = "", ""
    for line in result_text.split('\n'):
        if line.strip().lower().startswith("excuse:"):
            excuse = line.split(":", 1)[1].strip()
        elif line.strip().lower().startswith("proof:"):
            proof = line.split(":", 1)[1].strip()

    if not excuse:
        excuse = result_text
    if not proof:
        proof = "No proof generated."

    return excuse, proof

# Guilt-Tripping Apology Generator
def generate_guilt_apology(category, urgency):
    context = excuse_contexts.get(category, excuse_contexts["DEFAULT"])
    urgency_desc = urgency_descriptions.get(urgency, "")

    system_prompt = "You are a guilt-tripping assistant that writes dramatic apologies."
    user_prompt = (
        f"Write a dramatic, emotional apology for the following:\n"
        f"Category: {category}\nContext: {context}\nUrgency: {urgency} - {urgency_desc}\n\n"
        f"Make the apology guilt-tripping and remorseful.\n"
        f"Include a brief follow-up statement about how you plan to make it up."
    )

    return generate_llm_response(system_prompt, user_prompt)

# PDF Generator
def save_proof_as_pdf(excuse, proof):
    filename = f"proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    text = c.beginText(50, 800)
    text.setFont("Helvetica", 12)

    text.textLine("To Whom It May Concern,")
    text.textLine("")
    text.textLine("Subject: Request for Leave / Explanation")
    text.textLine("")
    text.textLine(excuse)
    text.textLine("")
    text.textLine(f"{proof}")
    text.textLine("")
    text.textLine("I kindly request your understanding in this matter.")
    text.textLine("")
    text.textLine("Thank you.")
    text.textLine("")
    text.textLine("Sincerely,")
    text.textLine("A concerned employee/student")

    c.drawText(text)
    c.showPage()
    c.save()
    return filename

# GUI Setup
set_appearance_mode("dark")
set_default_color_theme("blue")

app = CTk()
app.title("Intelligent Excuse Generator")
app.geometry("620x720")

# GUI Functions
current_excuse = ""
current_proof = ""

def on_generate():
    global current_excuse, current_proof

    cat = category_cb.get()
    urg = urgency_cb.get()
    if cat == "Select Category" or urg == "Select Urgency":
        result_lbl.configure(text="❗ Please select both Category and Urgency.")
        proof_lbl.configure(text="")
        return

    try:
        excuse, proof = generate_excuse_and_proof(cat, urg)
        current_excuse, current_proof = excuse, proof
        result_lbl.configure(text=f"{excuse}")
        proof_lbl.configure(text=f"{proof}")
        engine.say(excuse)
        engine.runAndWait()
    except Exception as e:
        result_lbl.configure(text=f"Error:\n{e}")
        proof_lbl.configure(text="")

def generate_apology():
    cat = category_cb.get()
    urg = urgency_cb.get()
    if cat == "Select Category" or urg == "Select Urgency":
        result_lbl.configure(text="❗ Please select both Category and Urgency.")
        proof_lbl.configure(text="")
        return

    try:
        apology_text = generate_guilt_apology(cat, urg)
        global current_excuse, current_proof
        current_excuse, current_proof = apology_text, "This is an AI-generated apology for dramatic effect."
        result_lbl.configure(text=apology_text)
        proof_lbl.configure(text="")
        engine.say(apology_text)
        engine.runAndWait()
    except Exception as e:
        result_lbl.configure(text=f"Error:\n{e}")

def voice_input_excuse():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        result_lbl.configure(text="🎙 Listening for input...")
        app.update()
        try:
            audio = recognizer.listen(source, timeout=5)
            voice_text = recognizer.recognize_google(audio)
            result_lbl.configure(text=f"🔍 You said: {voice_text}")

            system_prompt = "You are an assistant that interprets reasons and converts them into believable excuses and proof."
            user_prompt = (
                f"The user said: \"{voice_text}\".\n"
                f"Please extract the intent and generate:\n"
                f"Excuse: <excuse>\nProof: <proof>"
            )

            result_text = generate_llm_response(system_prompt, user_prompt)
            excuse, proof = "", ""
            for line in result_text.split('\n'):
                if line.strip().lower().startswith("excuse:"):
                    excuse = line.split(":", 1)[1].strip()
                elif line.strip().lower().startswith("proof:"):
                    proof = line.split(":", 1)[1].strip()

            global current_excuse, current_proof
            current_excuse, current_proof = excuse, proof
            result_lbl.configure(text=f"{excuse}")
            proof_lbl.configure(text=f"{proof}")
            engine.say(excuse)
            engine.runAndWait()
        except Exception as e:
            result_lbl.configure(text=f"❌ Voice recognition failed: {e}")

def on_save():
    if not current_excuse:
        result_lbl.configure(text="❗ Please generate an excuse or apology first.")
        return

    filename = f"excuse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(current_excuse + "\n" + current_proof)

    result_lbl.configure(text="✅ Excuse saved successfully.")

def view_saved_excuses():
    viewer = Toplevel(app)
    viewer.title("Saved Excuses")
    viewer.geometry("600x400")

    text_area = Text(viewer, wrap="word")
    scrollbar = Scrollbar(viewer, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)

    text_area.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    files = [f for f in os.listdir('.') if f.startswith('excuse_') and f.endswith('.txt')]
    if not files:
        text_area.insert("1.0", "No saved excuses found.")
    else:
        for file in sorted(files, reverse=True):
            with open(file, "r", encoding="utf-8") as f:
                text_area.insert("end", f"==== {file} ====\n")
                text_area.insert("end", f.read())
                text_area.insert("end", "\n\n")

def on_download_pdf():
    if not current_excuse:
        result_lbl.configure(text="❗ Please generate an excuse first.")
        return

    filename = save_proof_as_pdf(current_excuse, current_proof)
    result_lbl.configure(text=f"📄 PDF proof downloaded:\n{filename}")

# UI Components
CTkLabel(app, text="Intelligent Excuse Generator", font=("Arial", 26, "bold"), text_color="orange").pack(pady=20)

category_cb = CTkComboBox(app, values=["Select Category"] + categories, width=400)
category_cb.set("Select Category")
category_cb.pack(pady=10)

urgency_cb = CTkComboBox(app, values=["Select Urgency"] + urgencies, width=400)
urgency_cb.set("Select Urgency")
urgency_cb.pack(pady=10)

CTkButton(app, text="Generate Excuse", command=on_generate, fg_color="#FF914D", font=("Arial", 16, "bold")).pack(pady=15)
CTkButton(app, text="🎤 Generate from Voice", command=voice_input_excuse, fg_color="#6366F1", font=("Arial", 14)).pack(pady=5)
CTkButton(app, text="😔 Generate Apology", command=generate_apology, fg_color="#EF4444", font=("Arial", 14)).pack(pady=5)
CTkButton(app, text="Save Excuse", command=on_save, fg_color="#4CAF50", font=("Arial", 14)).pack(pady=5)
CTkButton(app, text="Download PDF Proof", command=on_download_pdf, fg_color="#22C55E", font=("Arial", 14)).pack(pady=5)
CTkButton(app, text="📁 View Saved Excuses", command=view_saved_excuses, fg_color="#3B82F6", font=("Arial", 14)).pack(pady=10)

result_lbl = CTkLabel(app, text="", font=("Arial", 14), wraplength=550, justify="left", text_color="white")
result_lbl.pack(pady=20)

proof_lbl = CTkLabel(app, text="", font=("Arial", 14), wraplength=550, justify="left", text_color="white")
proof_lbl.pack(pady=10)

app.mainloop()
