import streamlit as st
import os
import io
import shutil
import json
from datetime import datetime
from dotenv import load_dotenv
from streamlit_local_storage import LocalStorage
from utils.baixar import baixar_audio_do_youtube
from utils.transcrever import transcrever_audio 
from utils.gerar_nuvem import gerar_nuvem_geral, gerar_nuvens_por_locutor
from utils.analisar import configurar_ia, analisar_texto_com_ia

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    ASSEMBLYAI_API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]
except (FileNotFoundError, KeyError):
    print("Secrets não encontrados no Streamlit, carregando do arquivo .env")
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

PASTA_DATA = "data"
PASTA_OUTPUT = "output"
CAMINHO_AUDIO_PADRAO = os.path.join(PASTA_DATA, "audio.mp3")
LIMITE_HISTORICO = 5 

st.set_page_config(page_title="Analisador de Debates", layout="wide", initial_sidebar_state="collapsed")
st.title("🎧 Transcrição e Análise de Vídeo")
st.markdown("Extraia, transcreva e analise o conteúdo de vídeos ou áudios para obter insights valiosos.")

os.makedirs(PASTA_DATA, exist_ok=True)
os.makedirs(PASTA_OUTPUT, exist_ok=True)
localS = LocalStorage()

def inicializar_estado():
    """Inicializa o estado da sessão, carregando o histórico do localStorage se existir."""
    if 'estado_inicializado' not in st.session_state:
        st.session_state.estado_inicializado = True
        st.session_state.analise_concluida = False
        st.session_state.metadados = {}
        st.session_state.falas_por_locutor = {}
        st.session_state.transcricao_completa = ""
        st.session_state.nuvem_geral = None
        st.session_state.nuvens_locutores = {}
        st.session_state.chat_history = []
        st.session_state.modelo_ia = None
        
        historico_json = localS.getItem("historico_analises")
        st.session_state.historico_analises = json.loads(historico_json) if historico_json else []

inicializar_estado()

def limpar_pastas_de_trabalho():
    for pasta in [PASTA_DATA, PASTA_OUTPUT]:
        for filename in os.listdir(pasta):
            file_path = os.path.join(pasta, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                st.error(f"Erro ao limpar a pasta {pasta}: {e}")

if st.session_state.modelo_ia is None:
    try:
        st.session_state.modelo_ia = configurar_ia(api_key=GOOGLE_API_KEY)
    except ValueError as e:
        st.error(e)

def carregar_analise_do_historico(estado_salvo):
    """Carrega uma análise do histórico e recria as nuvens de palavras."""
    st.session_state.metadados = estado_salvo['metadados']
    st.session_state.falas_por_locutor = estado_salvo['falas_por_locutor']
    st.session_state.transcricao_completa = estado_salvo['transcricao_completa']
    
    with st.spinner("Recriando nuvens de palavras..."):
        st.session_state.nuvem_geral = gerar_nuvem_geral(st.session_state.falas_por_locutor)
        st.session_state.nuvens_locutores = gerar_nuvens_por_locutor(st.session_state.falas_por_locutor)
        
    st.session_state.chat_history = []
    st.session_state.analise_concluida = True

def processar_audio(audio_path, metadados_base):
    """Função central que processa o áudio e salva o resultado no histórico e localStorage."""
    with st.spinner("1/2 - Transcrevendo o áudio..."):
        try:
            falas = transcrever_audio(api_key=ASSEMBLYAI_API_KEY, audio_path=audio_path, saida_base=PASTA_OUTPUT)
            if not falas or "Erro" in falas:
                st.error(f"A transcrição falhou: {falas.get('Erro', 'Nenhum')}")
                st.stop()
        except Exception as e:
            st.error(f"Exceção na transcrição: {e}")
            st.stop()
        st.session_state.falas_por_locutor = falas
        caminho_transcricao_final = os.path.join(PASTA_OUTPUT, "transcricao.txt")
        try:
            with open(caminho_transcricao_final, "r", encoding="utf-8") as f:
                st.session_state.transcricao_completa = f.read()
        except FileNotFoundError:
            st.error("Arquivo de transcrição não encontrado.")
            st.stop()
            
    st.session_state.metadados = metadados_base

    info_historico = {
        "titulo": st.session_state.metadados.get('titulo'),
        "data_analise": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "estado_salvo": {
            'metadados': st.session_state.metadados,
            'falas_por_locutor': st.session_state.falas_por_locutor,
            'transcricao_completa': st.session_state.transcricao_completa,
        }
    }
    
    historico_atual = [h for h in st.session_state.historico_analises if h['titulo'] != info_historico['titulo']]
    historico_atual.insert(0, info_historico)
    st.session_state.historico_analises = historico_atual[:LIMITE_HISTORICO]
    
    localS.setItem("historico_analises", json.dumps(st.session_state.historico_analises))

    carregar_analise_do_historico(info_historico['estado_salvo'])
    st.success("Análise concluída com sucesso!")
    st.rerun()

def resetar_analise():
    """Limpa o estado da sessão para uma nova análise."""
    st.session_state.analise_concluida = False
    st.session_state.metadados = {}
    st.session_state.falas_por_locutor = {}
    st.session_state.transcricao_completa = ""
    st.session_state.nuvem_geral = None
    st.session_state.nuvens_locutores = {}
    st.session_state.chat_history = []
    limpar_pastas_de_trabalho()

if not st.session_state.analise_concluida:
    st.subheader("Selecione a fonte do seu dado:")
    tab_youtube, tab_mp3, tab_txt, tab_historico = st.tabs(["▶️ Link do YouTube", "🎵 Upload de Áudio (.mp3)", "📄 Upload de Texto (.txt)", "📜 Histórico"])

    with tab_youtube:
        st.info("Cole o link de um vídeo do YouTube para baixar o áudio e iniciar a análise.")
        video_url = st.text_input("Link do vídeo:", key="youtube_url")
        if st.button("Analisar Vídeo do YouTube"):
            if video_url:
                try:
                    with st.spinner("Baixando áudio do YouTube..."):
                        metadados = baixar_audio_do_youtube(video_url, output_path=CAMINHO_AUDIO_PADRAO)
                    processar_audio(CAMINHO_AUDIO_PADRAO, metadados)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar o link: {e}")
            else:
                st.warning("Por favor, insira um link do YouTube.")
    
    with tab_mp3:
        st.info("Faça o upload de um arquivo de áudio no formato .mp3 para análise.")
        uploaded_mp3 = st.file_uploader("Escolha um arquivo MP3", type=['mp3'], key="mp3_uploader")
        if st.button("Analisar Áudio MP3"):
            if uploaded_mp3:
                with open(CAMINHO_AUDIO_PADRAO, "wb") as f:
                    f.write(uploaded_mp3.getbuffer())
                metadados = {"titulo": uploaded_mp3.name, "audio_path": CAMINHO_AUDIO_PADRAO, "descricao": "Áudio carregado localmente."}
                processar_audio(CAMINHO_AUDIO_PADRAO, metadados)
            else:
                st.warning("Por favor, faça o upload de um arquivo .mp3.")

    with tab_txt:
        st.info("Pule a etapa de transcrição fazendo o upload de um arquivo de texto já pronto.")
        st.warning("Formato esperado: cada linha corresponde a uma fala. A identificação de locutores pode não ser precisa.", icon="⚠️")
        uploaded_txt = st.file_uploader("Escolha um arquivo TXT", type=['txt'], key="txt_uploader")
        if st.button("Analisar Arquivo de Texto"):
            if uploaded_txt:
                texto_completo = uploaded_txt.getvalue().decode("utf-8")
                falas = {"Transcrição Completa": texto_completo.splitlines()}
                st.session_state.falas_por_locutor = falas
                st.session_state.transcricao_completa = texto_completo
                with st.spinner("Gerando nuvem de palavras..."):
                    st.session_state.nuvem_geral = gerar_nuvem_geral(falas)
                    st.session_state.nuvens_locutores = {}
                st.session_state.metadados = {"titulo": uploaded_txt.name, "descricao": "Análise a partir de arquivo de texto."}
                st.session_state.analise_concluida = True
                st.success("Análise concluída com sucesso!")
                st.rerun()
            else:
                st.warning("Por favor, faça o upload de um arquivo .txt.")

    with tab_historico:
        st.info("Aqui estão as suas últimas análises. Os dados são salvos no seu navegador.")
        if not st.session_state.historico_analises:
            st.write("Nenhuma análise foi realizada ainda.")
        else:
            for i, item in enumerate(st.session_state.historico_analises):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{item['titulo']}**")
                    st.caption(f"Analisado em: {item['data_analise']}")
                with col2:
                    st.button(
                        "Ver Resultados",
                        key=f"hist_{i}",
                        on_click=carregar_analise_do_historico,
                        args=(item['estado_salvo'],)
                    )
                st.divider()

if st.session_state.analise_concluida:
    st.header(f"🔎 Resultados da Análise: *{st.session_state.metadados.get('titulo', 'Análise Local')}*")

    if st.button("⬅️ Iniciar Nova Análise"):
        resetar_analise()
        st.rerun()

    tab_resumo, tab_nuvens, tab_ia = st.tabs(["📜 Transcrição", "☁️ Nuvens de Palavras", "🤖 Converse com a IA"])

    with tab_resumo:
        st.subheader("Transcrição Completa")
        st.text_area("Texto Transcrito:", value=st.session_state.transcricao_completa, height=400, disabled=True)
        st.download_button(
            label="⬇️ Baixar Transcrição Completa (.txt)",
            data=st.session_state.transcricao_completa.encode('utf-8'),
            file_name=f"transcricao_{st.session_state.metadados.get('titulo', 'geral')}.txt",
            mime="text/plain"
        )
        if st.session_state.metadados:
            with st.expander("Ver detalhes do vídeo e baixar áudio"):
                if st.session_state.metadados.get('descricao'):
                    st.write(f"**Descrição:**\n\n{st.session_state.metadados.get('descricao')}")
                    st.divider()
                audio_path = st.session_state.metadados.get("audio_path")
                if st.session_state.metadados.get("url_original") and audio_path and os.path.exists(audio_path):
                    st.write("**Áudio do vídeo:**")
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                    titulo_arquivo = "".join(c for c in st.session_state.metadados.get('titulo', 'audio_extraido') if c.isalnum() or c in (' ', '_')).rstrip()
                    titulo_arquivo = titulo_arquivo.replace(' ', '_') + '.mp3'
                    st.download_button(
                        label="⬇️ Baixar Áudio (.mp3)",
                        data=audio_bytes,
                        file_name=titulo_arquivo,
                        mime="audio/mpeg"
                    )

    with tab_nuvens:
        if st.session_state.nuvem_geral:
            st.subheader("Nuvem de Palavras Geral")
            st.image(st.session_state.nuvem_geral, use_column_width=True)
            buf = io.BytesIO()
            st.session_state.nuvem_geral.save(buf, format="PNG")
            st.download_button(label="⬇️ Baixar Nuvem Geral", data=buf.getvalue(), file_name="nuvem_geral.png", mime="image/png")
        if st.session_state.nuvens_locutores:
            st.subheader("Nuvens de Palavras por Locutor")
            for locutor, imagem in st.session_state.nuvens_locutores.items():
                st.image(imagem, caption=f"Nuvem de {locutor}")
                buf = io.BytesIO()
                imagem.save(buf, format="PNG")
                st.download_button(f"⬇️ Baixar Nuvem de {locutor}", data=buf.getvalue(), file_name=f"nuvem_{locutor}.png", mime="image/png")

    with tab_ia:
        st.subheader("Faça perguntas sobre o conteúdo")
        st.info("A IA irá responder com base exclusivamente no texto da transcrição.")
        for chat in st.session_state.chat_history:
            with st.chat_message("user", avatar="👤"):
                st.markdown(chat["pergunta"])
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(chat["resposta"])
        if st.session_state.modelo_ia:
            with st.form(key='chat_form', clear_on_submit=True):
                pergunta_usuario = st.text_input("Sua pergunta:", placeholder="Ex: Quais foram os principais temas abordados?", key="pergunta_ia")
                if st.form_submit_button("Enviar Pergunta") and pergunta_usuario:
                    with st.spinner("A IA está pensando..."):
                        resposta_ia = analisar_texto_com_ia(
                            st.session_state.modelo_ia, 
                            st.session_state.transcricao_completa,
                            st.session_state.metadados,
                            pergunta_usuario
                        )
                        st.session_state.chat_history.append({"pergunta": pergunta_usuario, "resposta": resposta_ia})
                        st.rerun()
        else:
            st.error("A funcionalidade de IA não está disponível. Verifique sua chave de API no arquivo .env.")