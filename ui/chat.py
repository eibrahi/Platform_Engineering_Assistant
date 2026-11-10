from datetime import datetime

import httpx
import streamlit as st

API_URL = 'http://localhost:8000/api/assistant'
USER_ID = 1  # Übergangslösung bis zum Login, wie der Header in der API
HEADERS = {'X-User-Id': str(USER_ID)}


def api_get(path: str):
    response = httpx.get(f'{API_URL}{path}', headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def format_time(iso_text: str) -> str:
    # Die API liefert UTC; astimezone() rechnet in die Zeit deines Rechner um
    return datetime.fromisoformat(iso_text).astimezone().strftime('%d.%m. %H:%M')


st.title('Platform Engineering Assistant')

# 1. Gedächtnis der Seite anlegen (nur beim allerersten Durchlauf)
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Seitenleiste: Unterhaltungen wählen oder neu starten
with st.sidebar:
    st.header('Unterhaltungen')

    if st.button('➕ Neue Unterhaltung', width='stretch'):
        st.session_state.conversation_id = None
        st.session_state.messages = []

    for conversation in api_get('/conversations'):
        is_current = conversation['id'] == st.session_state.conversation_id
        if st.button(
                f"#{conversation['id']} · {format_time(conversation['created_at'])}",
                key=f"conversation-{conversation['id']}",
                type='primary' if is_current else 'secondary',
                width='stretch',
        ):
            st.session_state.conversation_id = conversation['id']
            st.session_state.messages = api_get(f"/conversations/{conversation['id']}/messages")

# 2. Bisherigen Verlauf anzeigen (bei JEDEM Durchlauf, sonst wäre er weg)
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# 3. Neue Eingabe verarbeiten
if prompt := st.chat_input('Frag den Assistenten'):
    is_new = st.session_state.conversation_id is None
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        with st.spinner('Denke nach …'):
            response = httpx.post(
                f'{API_URL}/chat',
                json={'conversation_id': st.session_state.conversation_id, 'message': prompt},
                headers=HEADERS,
                timeout=60,
            )
        response.raise_for_status()
        data = response.json()
        st.session_state.conversation_id = data['conversation_id']
        st.markdown(data['answer'])

    st.session_state.messages.append({'role': 'assistant', 'content': data['answer']})
    if is_new:
        st.rerun()
