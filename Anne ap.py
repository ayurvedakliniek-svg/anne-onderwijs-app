if level == "High School (Regents)":
    grade = st.sidebar.selectbox("Leerjaar (Indicatie):", ["Grade 9", "Grade 10", "Grade 11", "Grade 12"])
    cat = st.sidebar.selectbox("Categorie:", ["Mathematics", "Science", "English", "Social Studies", "World Languages"])
    
    if cat == "Mathematics": sub = st.sidebar.selectbox("Vak:", ["Algebra I", "Geometry", "Algebra II"])
    elif cat == "Science": sub = st.sidebar.selectbox("Vak:", ["Living Environment", "Earth Science", "Chemistry", "Physics"])
    elif cat == "English": sub = "ELA Regents (Grade 11)"
    elif cat == "Social Studies": sub = st.sidebar.selectbox("Vak:", ["Global History", "U.S. History"])
    elif cat == "World Languages": sub = f"{st.sidebar.selectbox('Taal:', world_languages)} Regents"
    
    subject = f"{grade} {sub}"
    grade = st.sidebar.selectbox("Leerjaar (Indicatie):", ["Grade 9", "Grade 10", "Grade 11", "Grade 12"])
    cat = st.sidebar.selectbox("Categorie:", ["Mathematics", "Science", "English", "Social Studies", "World Languages"])
    
    if cat == "Mathematics": sub = st.sidebar.selectbox("Vak:", ["Algebra I", "Geometry", "Algebra II"])
    elif cat == "Science": sub = st.sidebar.selectbox("Vak:", ["Living Environment", "Earth Science", "Chemistry", "Physics"])
    elif cat == "English": sub = "ELA Regents (Grade 11)"
    elif cat == "Social Studies": sub = st.sidebar.selectbox("Vak:", ["Global History", "U.S. History"])
    elif cat == "World Languages": sub = f"{st.sidebar.selectbox('Taal:', world_languages)} Regents"
    
    subject = f"{grade} {sub}"import streamlit as st
from openai import OpenAI
import os
import json
import pandas as pd
import datetime

# --- 1. CONFIGURATIE ---
# Vul hier je eigen API key in
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="Anne - NY Expert", page_icon="🎓", layout="wide")

# Initialiseer sessiegeheugen
if "score_history" not in st.session_state: st.session_state.score_history = []
if "messages" not in st.session_state: st.session_state.messages = []
if "current_quiz_data" not in st.session_state: st.session_state.current_quiz_data = None

# --- 2. ZIJBALK (SELECTIE) ---
with st.sidebar:
    st.title("🎓 Anne Menu")
    rol = st.selectbox("Rol:", ["Student", "Ouder", "Docent"])
    level = st.radio("Niveau:", ["Elementary/Middle", "High School (Regents)"])
    
    if level == "High School (Regents)":
        cat = st.selectbox("Categorie:", ["Mathematics", "Science", "English", "Social Studies", "World Languages", "Health/SEL"])
        subject = f"Regents {cat}"
    else:
        grade = st.selectbox("Grade:", [f"Grade {i}" for i in range(1, 9)])
        subject = f"{grade} Curriculum"
    
    st.divider()
    if st.button("🗑️ Reset App (Wis Alles)"):
        st.session_state.score_history = []
        st.session_state.messages = []
        st.session_state.current_quiz_data = None
        st.rerun()

# --- 3. HOOFDSCHERM MET TABS ---
st.title("🎓 Anne: Jouw NY Education Partner")

# We definiëren de tabs hier heel duidelijk
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📝 Oefentoets", "📊 Voortgang", "🏛️ NY Regels"])

# --- TAB 1: CHAT ---
with tab1:
    st.subheader("Stel je vraag")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if p := st.chat_input("Vraag iets..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            res = client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "system", "content": f"Je bent Anne, expert in {subject}."}] + st.session_state.messages
            )
            msg = res.choices[0].message.content
            st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})

# --- TAB 2: QUIZ ---
with tab2:
    st.subheader("Interactieve Training")
    if st.button("Genereer Toets"):
        with st.spinner("Laden..."):
            prompt = f"Generate a 3-question MCQ for NYSED {subject}. Return ONLY JSON: {{\"q\": [{{'question': 'str', 'options': ['a', 'b', 'c', 'd'], 'answer': 'a', 'explanation': 'str'}}]}}"
            res_q = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
            st.session_state.current_quiz_data = json.loads(res_q.choices[0].message.content).get("q", [])
            st.rerun()

    if st.session_state.current_quiz_data:
        with st.form("quiz_form_new"):
            score = 0
            user_ans = {}
            for i, q in enumerate(st.session_state.current_quiz_data):
                st.write(f"**{i+1}. {q['question']}**")
                user_ans[i] = st.radio(f"Kies voor {i}:", q['options'], key=f"quiz_radio_{i}")
            
            if st.form_submit_button("Checken"):
                for i, q in enumerate(st.session_state.current_quiz_data):
                    if user_ans[i] == q['answer']:
                        st.success(f"Vraag {i+1} is goed!")
                        score += 1
                    else: st.error(f"Vraag {i+1} is fout. Het was {q['answer']}")
                
                st.session_state.score_history.append({
                    "Datum": datetime.datetime.now().strftime("%H:%M"), 
                    "Vak": subject, 
                    "Score": f"{round(score/3*100)}%"
                })

# --- TAB 3: VOORTGANG ---
with tab3:
    st.subheader("Resultaten")
    if st.session_state.score_history:
        df = pd.DataFrame(st.session_state.score_history)
        st.table(df)
    else:
        st.info("Nog geen scores.")

# --- TAB 4: REGELS ---
with tab4:
    st.subheader("🏛️ NYSED Informatie")
    st.write("Hier vind je de belangrijkste regels van de New York State Education Department.")
    st.info("Tip: Gebruik de chat voor specifieke vragen over diploma-eisen.")


