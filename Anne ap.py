import streamlit as st
from openai import OpenAI
import os
import json
import pandas as pd
import datetime

# --- 1. CONFIGURATIE ---
# De API key wordt veilig uit de Streamlit Secrets gehaald
# VERBETERDE SETUP VOOR FOUTMELDINGEN
try:
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        st.error("❌ FOUT: OPENAI_API_KEY ontbreekt in de Streamlit Secrets!")
        st.stop()
except Exception as e:
    st.error(f"❌ Er is een technische fout opgetreden: {e}")
    st.stop()

# Initialiseer sessiegeheugen
if "score_history" not in st.session_state: st.session_state.score_history = []
if "messages" not in st.session_state: st.session_state.messages = []
if "profile" not in st.session_state: st.session_state.profile = None

# --- 2. LOGIN / PROFIEL SCHERM ---
if st.session_state.profile is None:
    st.title("👋 Welkom bij Anne")
    st.subheader("Laten we eerst kennismaken")
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Volledige Naam")
            dob = st.date_input("Geboortedatum", min_value=datetime.date(1950, 1, 1))
        with col2:
            role = st.selectbox("Jouw Rol", ["Student", "Ouder", "Docent"])
            address = st.text_input("Adres / Wijk (Optioneel)")
            
        submit = st.form_submit_button("Start Sessie met Anne")
        
        if submit:
            if name:
                st.session_state.profile = {
                    "name": name,
                    "dob": dob,
                    "role": role,
                    "address": address
                }
                st.rerun()
            else:
                st.warning("Vul alsjeblieft je naam in om verder te gaan.")
    st.stop() # Stop hier zodat de rest van de app pas laadt na "login"

# --- 3. ZIJBALK (SELECTIE) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/test-account.png", width=60)
    st.write(f"**Gebruiker:** {st.session_state.profile['name']}")
    st.write(f"**Rol:** {st.session_state.profile['role']}")
    st.divider()
    
    level = st.radio("Onderwijsniveau:", ["Elementary/Middle", "High School (Regents)"])
    
    world_languages = ["Spanish", "French", "Italian", "Chinese", "Arabic", "Hebrew", "Other"]
    
    if level == "High School (Regents)":
        grade = st.selectbox("Leerjaar:", ["Grade 9", "Grade 10", "Grade 11", "Grade 12"])
        cat = st.selectbox("Categorie:", ["Mathematics", "Science", "English", "Social Studies", "World Languages"])
        if cat == "Mathematics": sub = st.selectbox("Vak:", ["Algebra I", "Geometry", "Algebra II"])
        elif cat == "Science": sub = st.selectbox("Vak:", ["Living Environment", "Earth Science", "Chemistry", "Physics"])
        elif cat == "English": sub = "ELA Regents"
        elif cat == "Social Studies": sub = st.selectbox("Vak:", ["Global History", "U.S. History"])
        elif cat == "World Languages": sub = f"{st.selectbox('Taal:', world_languages)} Regents"
        subject = f"{grade} {sub}"
    else:
        grade = st.selectbox("Grade:", [f"Grade {i}" for i in range(1, 9)])
        topic = st.selectbox("Vak:", ["ELA", "Mathematics", "Science", "Social Studies", "Health/SEL", "World Languages"])
        subject = f"{grade} {topic}"
    
    if st.button("🔄 Uitloggen / Wissel Gebruiker"):
        st.session_state.profile = None
        st.session_state.messages = []
        st.rerun()

# --- 4. HOOFDSCHERM MET TABS ---
st.title(f"🎓 Anne: Your Education Partner")
st.caption(f"Hallo {st.session_state.profile['name']}, we focussen vandaag op {subject}")

tab1, tab2, tab3 = st.tabs(["💬 Persoonlijke Chat", "📝 Oefentoets", "📊 Voortgang"])

# --- TAB 1: CHAT ---
with tab1:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if p := st.chat_input("Stel je vraag aan Anne..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            # De "System Message" bevat nu alle profielgegevens voor een persoonlijk antwoord
            profile_context = f"Je bent Anne. Je praat met {st.session_state.profile['name']}, een {st.session_state.profile['role']} geboren op {st.session_state.profile['dob']}. "
            if st.session_state.profile['address']:
                profile_context += f"Ze wonen in {st.session_state.profile['address']}. "
            profile_context += f"De focus ligt op het vak {subject} volgens de NYSED richtlijnen."
            
            res = client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "system", "content": profile_context}] + st.session_state.messages
            )
            msg = res.choices[0].message.content
            st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})

# --- TAB 2 & 3 (QUIZ & SCORES) ---
# ... (Deze blijven hetzelfde als in de vorige werkende versie)
with tab2:
    st.subheader(f"Test je kennis voor {subject}")
    if st.button("Genereer Toets"):
        with st.spinner("Vragen laden..."):
            prompt = f"Generate a 3-question MCQ for NYSED {subject}. Return ONLY JSON: {{\"q\": [{{'question': 'str', 'options': ['a', 'b', 'c', 'd'], 'answer': 'a', 'explanation': 'str'}}]}}"
            res_q = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
            st.session_state.current_quiz_data = json.loads(res_q.choices[0].message.content).get("q", [])
            st.rerun()

    if "current_quiz_data" in st.session_state and st.session_state.current_quiz_data:
        with st.form("quiz_form"):
            score = 0
            user_ans = {}
            for i, q in enumerate(st.session_state.current_quiz_data):
                st.write(f"**{i+1}. {q['question']}**")
                user_ans[i] = st.radio(f"Opties voor vraag {i+1}:", q['options'], key=f"q_{i}")
            if st.form_submit_button("Nakijken"):
                for i, q in enumerate(st.session_state.current_quiz_data):
                    if user_ans[i] == q['answer']:
                        st.success(f"Vraag {i+1} is goed!")
                        score += 1
                    else: st.error(f"Vraag {i+1} is fout. Correct was: {q['answer']}")
                st.session_state.score_history.append({"Datum": datetime.datetime.now().strftime("%H:%M"), "Vak": subject, "Score": f"{round(score/3*100)}%"})

with tab3:
    if st.session_state.score_history:
        st.table(pd.DataFrame(st.session_state.score_history))
    else:
        st.info("Nog geen resultaten.")

