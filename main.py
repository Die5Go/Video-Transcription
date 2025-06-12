import streamlit as st
import os
from utils.baixar import baixar_audio_do_youtube
from utils.transcrever import transcrever_audio
from utils.gerar_nuvem import gerar_nuvem_geral, gerar_nuvens_por_locutor
from utils.analisar_com_ia import perguntar_ao_gemini

st.set_page_config(page_title="Transcritor e Analisador de Vídeo", layout="wide")
st.title("🎧 Transcrição e Análise de Vídeo do YouTube")
video_url = st.text_input("Cole aqui o link do vídeo")
col1, col2, col3 = st.columns(3)

usar_youtube = col1.button("Analisar Link")
usar_local = col2.button("Usar Áudio Local")
usar_trans = col3.button("Usar Transcrição Local")

if usar_youtube and video_url:
    with st.spinner("Baixando áudio e metadados..."):
        metadados = baixar_audio_do_youtube(video_url)
        audio_path = metadados["audio_path"]
    
    st.success("Áudio baixado com sucesso.")
    with open(audio_path, "rb") as audio_file:
        st.download_button("⬇ Baixar Áudio", audio_file, file_name="audio.mp3")

    st.markdown(f"### 🎬 {metadados['titulo']}")
    with st.expander("📋 Detalhes do vídeo"):
        st.write(f"*Canal:* {metadados['canal']}")
        st.write(f"*Data de publicação:* {metadados['data_publicacao']}")
        st.write(f"*Duração:* {metadados['duracao_segundos']//60} min")
        st.write(f"*Visualizações:* {metadados['visualizacoes']:,}")
        st.markdown(f"*Descrição:*\n{metadados['descricao']}")

    with st.spinner("Transcrevendo o áudio..."):
        falas_por_locutor = transcrever_audio(audio_path)
        nuvens_locutores = gerar_nuvens_por_locutor(falas_por_locutor)

    st.success("Transcrição concluída.")
    st.download_button("⬇️ Baixar Transcrição Geral", open("output/transcricao.txt", "rb"), file_name="transcricao.txt")

    for arquivo in os.listdir("output"):
        if arquivo.startswith("Speaker_") and arquivo.endswith(".txt"):
            st.download_button(f"⬇️ Baixar {arquivo}", open(f"output/{arquivo}", "rb"), file_name=arquivo)

    # 📊 Geração das nuvens (depois da análise e renomeação dos locutores)
    st.header("📊 Nuvem de Palavras")
    nuvem_geral = gerar_nuvem_geral(falas_por_locutor)
    st.image(nuvem_geral, caption="Nuvem Geral")
    st.download_button("⬇️ Baixar Nuvem Geral", open("output/nuvem_geral.png", "rb"), file_name="nuvem_geral.png")

    st.subheader("Nuvens por Locutor")
    for locutor, imagem in nuvens_locutores.items():
        st.image(imagem, caption=f"Nuvem de {locutor}")
        caminho_nuvem_locutor = f"output/nuvem_por_locutor/{locutor.replace(' ', '_')}.png"
        if os.path.exists(caminho_nuvem_locutor):
            st.download_button(f"⬇️ Baixar Nuvem de {locutor}", open(caminho_nuvem_locutor, "rb"), file_name=os.path.basename(caminho_nuvem_locutor))
        
    # Permite o usuário consultar o Gemini
    if st.button("💬 Fazer perguntas com IA (Gemini)"):
        perguntar_ao_gemini(metadados)

elif usar_local:
    audio_path = "data/audio.mp3"  # Caminho para o arquivo local
    if not os.path.exists(audio_path):
        st.error("Arquivo local 'audio/audio.mp3' não encontrado.")
    else:
        # Metadados fictícios para continuar o fluxo
        metadados = {
            "titulo": "Áudio Local",
            "canal": "Desconhecido",
            "data_publicacao": "N/A",
            "duracao_segundos": 0,
            "visualizacoes": 0,
            "descricao": "Análise a partir de áudio local, Não possui descrição, basear-se totalmente nas transcrições",
            "audio_path": audio_path,
        }

    with st.spinner("Transcrevendo o áudio..."):
        falas_por_locutor = transcrever_audio(audio_path)
        nuvens_locutores = gerar_nuvens_por_locutor(falas_por_locutor)

    st.success("Transcrição concluída.")
    st.download_button("⬇️ Baixar Transcrição Geral", open("output/transcricao_diarizada.txt", "rb"), file_name="transcricao_diarizada.txt")

    for arquivo in os.listdir("output"):
        if arquivo.startswith("Speaker_") and arquivo.endswith(".txt"):
            st.download_button(f"⬇️ Baixar {arquivo}", open(f"output/{arquivo}", "rb"), file_name=arquivo)

    # 📊 Geração das nuvens (depois da análise e renomeação dos locutores)
    st.header("📊 Nuvem de Palavras")
    nuvem_geral = gerar_nuvem_geral(falas_por_locutor)
    st.image(nuvem_geral, caption="Nuvem Geral")
    st.download_button("⬇️ Baixar Nuvem Geral", open("output/nuvem_geral.png", "rb"), file_name="nuvem_geral.png")

    st.subheader("Nuvens por Locutor")
    for locutor, imagem in nuvens_locutores.items():
        st.image(imagem, caption=f"Nuvem de {locutor}")
        caminho_nuvem_locutor = f"output/nuvem_por_locutor/{locutor.replace(' ', '_')}.png"
        if os.path.exists(caminho_nuvem_locutor):
            st.download_button(f"⬇️ Baixar Nuvem de {locutor}", open(caminho_nuvem_locutor, "rb"), file_name=os.path.basename(caminho_nuvem_locutor))

    # Permite o usuário consultar o Gemini
    if st.button("💬 Fazer perguntas com IA (Gemini)"):
        perguntar_ao_gemini(metadados)

elif usar_trans:
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
