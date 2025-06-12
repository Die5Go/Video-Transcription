import streamlit as st
import os
from utils.analisar_com_ia import perguntar_ao_gemini

metadados = {
            "titulo": "Áudio Local",
            "canal": "Desconhecido",
            "data_publicacao": "N/A",
            "duracao_segundos": 0,
            "visualizacoes": 0,
            "descricao": "Análise a partir de áudio local, Não possui descrição, basear-se totalmente nas transcrições",
        }

    # Permite o usuário consultar o Gemini
st.header("🤖 Análise Interativa com IA (Gemini)")
pergunta_usuario = st.text_input("Digite sua pergunta sobre o vídeo ou transcrição:")

if pergunta_usuario:
    with st.spinner("Consultando IA..."):
        resposta = perguntar_ao_gemini(pergunta_usuario, metadados=metadados)
    st.markdown("**Resposta da IA:**")
    st.write(resposta)