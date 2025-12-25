import streamlit as st
import datetime

# Pagina configuratie
st.set_page_config(page_title="Anne Onderwijs App", layout="wide")

# Initialiseer session_state
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
        if st.form_submit_button("Start"):
            if name:
                st.session_state.profile = {"name": name, "dob": dob}
                st.rerun()
            else:
                st.error("Vul a.u.b. je naam in.")
    st.stop()

# --- DE LINKER BALK (SIDEBAR) ---
with st.sidebar:
    st.title("Settings & Profiel")
    st.write(f"**Gebruiker:** {st.session_state.profile['name']}")
    st.write(f"**Geboortedatum:** {st.session_state.profile['dob']}")
    
    st.divider()
    
    if st.button("Wis gesprek van vandaag"):
        st.session_state.messages = []
        st.rerun()
    
    st.info("De gesprekken van vandaag blijven bewaard zolang dit tabblad open staat.")

# --- CHAT SECTIE ---
st.title(f"Hallo {st.session_state.profile['name']}! 👋")

# Toon de chatgeschiedenis
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Waar wil je het over hebben?"):
    # Voeg bericht van gebruiker toe
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Antwoord van Anne
    with st.chat_message("assistant"):
        response = f"Ik hoor je, {st.session_state.profile['name']}. Je zei: '{prompt}'. Hoe kan ik je hierbij ondersteunen?"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
