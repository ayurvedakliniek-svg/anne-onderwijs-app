import streamlit as st

from openai import OpenAI

import json

import datetime

st.set_page_config(page_title="Anne", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "messages" not in st.session_state: st.session_state.messages = []

if "profile" not in st.session_state: st.session_state.profile = None

if "quiz" not in st.session_state: st.session_state.quiz = None

if st.session_state.profile is None: st.title("👋 Welkom bij Anne") with st.form("login"): name = st.text_input("Naam") dob = st.date_input("Geboortedatum", min_value=datetime.date(1940, 1, 1)) if st.form_submit_button("Start"): st.session_state.profile = {"name": name, "dob": dob} st.rerun() st.stop()

today = datetime.date.today() age = today.year - st.session_state.profile['dob'].year level = st.sidebar.radio("Niveau", ["Elementary", "High School"], index=(1 if age >= 14 else 0)) subject = st.sidebar.selectbox("Vak", ["Mathematics", "Science", "English", "Social Studies"])

tab1, tab2 = st.tabs(["💬 Chat", "📝 Toets"])

with tab1: col1, col2 = st.columns(2) spraak = col1.audio_input("Microfoon") foto = col2.camera_input("Camera") if spraak: res = client.audio.transcriptions.create(model="whisper-1", file=spraak) st.session_state.messages.append({"role": "user", "content": res.text}) if foto: st.session_state.messages.append({"role": "user", "content": "[Systeem: Foto ontvangen]"}) for m in st.session_state.messages: with st.chat_message(m["role"]): st.markdown(m["content"]) if p := st.chat_input("Vraag iets..."): st.session_state.messages.append({"role": "user", "content": p}) with st.chat_message("assistant"): ctx = f"Je bent Anne. Gebruiker is {age} jaar. Vak: {subject}. Gebruik NYSED-standaarden." resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": ctx}] + st.session_state.messages) st.markdown(resp.choices[0].message.content) st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})

with tab2: if st.button("Genereer Toets"): with st.spinner("Vragen maken..."): p = f"Maak 3 unieke MCQ vragen voor {subject}. Zorg dat alle 4 de opties per vraag verschillend zijn. Geef ALLEEN JSON terug: {{"q": [{{'question': '...', 'options': ['optie1', 'optie2', 'optie3', 'optie4'], 'answer': 'optie1', 'explanation': '...'}}]}}" res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p}], response_format={"type": "json_object"}) st.session_state.quiz = json.loads(res.choices[0].message.content)["q"] st.rerun() if st.session_state.quiz: with st.form("quiz_form"): user_choices = [] for i, q in enumerate(st.session_state.quiz): st.write(f"Vraag {i+1}: {q['question']}") choice = st.radio("Kies je antwoord:", q['options'], key=f"quiz_radio_{i}") user_choices.append(choice) if st.form_submit_button("Kijk na"): for i, q in enumerate(st.session_state.quiz): if user_choices[i] == q['answer']: st.success(f"Vraag {i+1} is GOED! ✅") else: st.error(f"Vraag {i+1} is fout. ❌ Het juiste antwoord was: {q['answer']}") st.info(f"Uitleg: {q['explanation']}") st.balloons()
