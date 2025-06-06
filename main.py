import streamlit as st
import os
from utils.baixar import baixar_audio_do_youtube
from utils.transcrever import transcrever_audio
from utils.gerar_nuvem import gerar_nuvem_geral, gerar_nuvens_por_locutor
from utils.analisar import analisar_video

st.set_page_config(page_title="Transcritor e Analisador de Vídeo", layout="wide")
st.title("🎧 Transcrição e Análise de Vídeo do YouTube")
video_url = st.text_input("Cole aqui o link do vídeo")
col1, col2 = st.columns(2)

usar_youtube = col1.button("Analisar via YouTube")
usar_local = col2.button("Usar Áudio Local")

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

    st.success("Transcrição concluída.")
    st.download_button("⬇️ Baixar Transcrição Geral", open("output/transcricao_diarizada.txt", "rb"), file_name="transcricao_diarizada.txt")

    for arquivo in os.listdir("output"):
        if arquivo.startswith("Speaker_") and arquivo.endswith(".txt"):
            st.download_button(f"⬇️ Baixar {arquivo}", open(f"output/{arquivo}", "rb"), file_name=arquivo)

    with st.spinner("Analisando com IA..."):
        mapeamento = analisar_video(metadados)

    st.success("Análise gerada.")
    st.header("🧠 Análise Crítica Geral")
    st.code(open("output/transcricao_analisada.txt", "r", encoding="utf-8").read(), language="markdown")
    st.download_button("⬇️ Baixar Análise Geral", open("output/transcricao_analisada.txt", "rb"), file_name="transcricao_analisada.txt")

    st.subheader("🧠 Análise por Locutor")
    st.code(open("output/analise_por_locutor.txt", "r", encoding="utf-8").read(), language="markdown")
    st.download_button("⬇️ Baixar Análise por Locutor", open("output/analise_por_locutor.txt", "rb"), file_name="analise_por_locutor.txt")

    # 📊 Geração das nuvens (depois da análise e renomeação dos locutores)
    st.header("📊 Nuvem de Palavras")
    nuvem_geral = gerar_nuvem_geral(falas_por_locutor)
    st.image(nuvem_geral, caption="Nuvem Geral")
    st.download_button("⬇️ Baixar Nuvem Geral", open("output/nuvem_geral.png", "rb"), file_name="nuvem_geral.png")

    nuvens_locutores = gerar_nuvens_por_locutor(falas_por_locutor, nomes_locutores=mapeamento)
    locutor = st.selectbox("Escolha um locutor para ver a nuvem:", list(nuvens_locutores.keys()))
    st.image(nuvens_locutores[locutor], caption=f"Nuvem de {locutor}")

    caminho_nuvem_locutor = f"output/nuvem_por_locutor/{locutor.replace(' ', '_')}.png"
    if os.path.exists(caminho_nuvem_locutor):
        st.download_button(f"⬇️ Baixar Nuvem de {locutor}", open(caminho_nuvem_locutor, "rb"), file_name=os.path.basename(caminho_nuvem_locutor))
