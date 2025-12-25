import streamlit as st from openai import OpenAI import json import pandas as pd import datetime

st.set_page_config(page_title="Anne - Your Education Partner", page_icon="🎓", layout="wide")

if "OPENAI_API_KEY" in st.secrets: client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) else: st.error("API Key niet gevonden!") st.stop()

if "messages" not in st.session_state: st.session_state.messages = [] if "profile" not in st.session_state: st.session_state.profile = None if "quiz" not in st.session_state: st.session_state.quiz = None

if st.session_state.profile is None: st.title("👋 Welkom bij Anne") with st.form("login"): name = st.text_input("Naam") dob = st.date_input("Geboortedatum", min_value=datetime.date(1940, 1, 1)) role = st.selectbox("Rol", ["Student", "Ouder", "Docent"]) if st.form_submit_button("Start"): st.session_state.profile = {"name": name, "dob": dob, "role": role} st.rerun() st.stop()

today = datetime.date.today() age = today.year - st.session_state.profile['dob'].year

with st.sidebar: st.title("🎓 Instellingen") level = st.radio("Niveau", ["Elementary/Middle", "High School"], index=(1 if age >= 14 else 0)) subject = st.selectbox("Vak", ["Mathematics", "Science", "English", "Social Studies"])

st.title(f"Leren voor {subject}") tab1, tab2 = st.tabs(["💬 Chat & Scan", "📝 Oefentoets"])

with tab1: c1, c2 = st.columns(2) spraak = c1.audio_input("Microfoon") foto = c2.camera_input("Camera") if spraak: res = client.audio.transcriptions.create(model="whisper-1", file=spraak) st.session_state.messages.append({"role": "user", "content": res.text}) if foto: st.session_state.messages.append({"role": "user", "content": "[Systeem: Foto ontvangen]"}) for m in st.session_state.messages: with st.chat_message(m["role"]): st.markdown(m["content"]) if p := st.chat_input("Vraag iets aan Anne..."): st.session_state.messages.append({"role": "user", "content": p}) with st.chat_message("assistant"): ctx = f"Je bent Anne. Gebruiker: {st.session_state.profile['name']}, {age} jaar. Vak: {subject}." resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": ctx}] + st.session_state.messages) st.markdown(resp.choices[0].message.content) st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})

with tab2: if st.button("Genereer nieuwe vragen"): prompt = f"Maak 3 MCQ voor {subject}. Geef ALLEEN JSON: {{"q": [{{'question': '...', 'options': ['...', '...'], 'answer': '...', 'explanation': '...'}}]}}" res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"}) st.session_state.quiz = json.loads(res.choices[0].message.content)["q"] st.rerun() if st.session_state.quiz: with st.form("quiz"): u_ans = [] for i, q in enumerate(st.session_state.quiz): st.write(f"{i+1}. {q['question']}") u_ans.append(st.radio(f"Antwoord {i+1}:", q['options'], key=f"q_{i}")) if st.form_submit_button("Nakijken"): for i, q in enumerate(st.session_state.quiz): if u_ans[i] == q['answer']: st.success(f"Vraag {i+1} GOED! ✅") else: st.error(f"Vraag {i+1} fout. ❌ Was: {q['answer']}")
