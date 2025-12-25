import streamlit as st
import datetime

# Initialiseer session_state variabelen als ze nog niet bestaan
if "profile" not in st.session_state:
    st.session_state.profile = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIN SECTIE ---
if st.session_state.profile is None:
    st.title("👋 Welkom bij Anne")
    
    with st.form("login"):
        name = st.text_input("Naam")
        dob = st.date_input("Geboortedatum", min_value=datetime.date(1940, 1, 1))
        submit = st.form_submit_button("Start")
        
        if submit:
            if name: # Controleer of de naam is ingevuld
                st.session_state.profile = {"name": name, "dob": dob}
                st.rerun()
            else:
                st.error("Voer aTarget een naam in.")
    st.stop()

# --- CHAT SECTIE (Zodra ingelogd) ---
st.title(f"Hallo {st.session_state.profile['name']}! 👋")
st.subheader("Ik ben Anne, hoe kan ik je vandaag helpen?")

# Toon eerdere berichten van vandaag (deze blijven in session_state)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Typ hier je bericht..."):
    # Voeg gebruikersbericht toe
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simuleer antwoord van Anne (Vervang dit door je API aanroep indien nodig)
    with st.chat_message("assistant"):
        response = f"Bedankt voor je bericht, {st.session_state.profile['name']}. Hoe gaat het verder?"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
