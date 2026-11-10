import httpx
import streamlit as st

API_URL = 'http://localhost:8000/api/assistant'
USER_ID = 1  # Übergangslösung bis zum Login, wie der Header in der API

st.title('Platform Engineering Assistant')

# 1. Gedächtnis der Seite anlegen (nur beim allerersten Durchlauf)
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 2. Bisherigen Verlauf anzeigen (bei JEDEM Durchlauf, sonst wäre er weg)
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# 3. Neue Eingabe verarbeiten
if prompt := st.chat_input('Frag den Assistenten'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        with st.spinner('Denke nach …'):
            response = httpx.post(
                f'{API_URL}/chat',
                json={'conversation_id': st.session_state.conversation_id, 'message': prompt},
                headers={'X-User-Id': str(USER_ID)},
                timeout=60,
            )
        response.raise_for_status()
        data = response.json()
        st.session_state.conversation_id = data['conversation_id']
        st.markdown(data['answer'])

    st.session_state.messages.append({'role': 'assistant', 'content': data['answer']})
