import streamlit as st

with st.sidebar:
    st.title(":blue[RAG Proof of Concept]")

st.title(":blue[💬 DoctorAI Chatbot]")
query = st.text_area("Faça a sua pergunta", placeholder="Adicione a pergunta aqui...", height=100)

if st.button("Fazer pergunta"):
    if query:
        st.write('oieee')
    else:
        st.warning('deu ruim')

