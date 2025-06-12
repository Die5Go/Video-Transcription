import os
import yt_dlp

def baixar_audio_do_youtube(url, output_path="data/audio"):
    """
    Tenta baixar o áudio do YouTube, extrai metadados e previne o erro de extensão dupla (.mp3.mp3).

    Args:
        url (str): O URL do vídeo do YouTube.
        output_path (str): O caminho base para salvar o arquivo. A função garante que a extensão
                           .mp3 seja aplicada corretamente, mesmo que o caminho já a contenha.
                           Exemplo: "data/audio" ou "data/audio.mp3" resultarão em "data/audio.mp3".
    """
    # --- PREVENÇÃO DO ERRO .mp3.mp3 ---
    # Garante que estamos trabalhando com o caminho base, sem a extensão, para o yt-dlp.
    nome_base, _ = os.path.splitext(output_path)
    
    # Define o caminho final esperado, que sempre terá a extensão .mp3 correta.
    caminho_final_mp3 = f"{nome_base}.mp3"

    # Garante que o diretório de destino exista.
    os.makedirs(os.path.dirname(nome_base), exist_ok=True)

    # Verifica se o arquivo final já existe e tenta removê-lo para garantir uma nova versão.
    if os.path.exists(caminho_final_mp3):
        try:
            os.remove(caminho_final_mp3)
        except PermissionError:
            # Erro mais claro para o usuário do Streamlit.
            raise RuntimeError(f"O arquivo {caminho_final_mp3} está aberto em outro programa. Feche-o e tente novamente.")

    # Opções do yt-dlp. O caminho do ffmpeg foi removido para maior portabilidade.
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': nome_base,  # Usa o nome base SEM extensão. yt-dlp adicionará a correta.
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True, # Garante que baixe apenas o vídeo, não a playlist inteira.
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        erro_str = str(e).lower()
        # Tratamento de erro mais específico para o Streamlit.
        if "sign in" in erro_str or "cookies" in erro_str or "age-restricted" in erro_str:
            print(f"🔒 Falha no download: {e}")
            raise ConnectionError("Este vídeo pode ser privado, ter restrição de idade ou exigir login. O download automático falhou.")
        else:
            raise e  # Lança outros erros de download para depuração.

    if not os.path.exists(caminho_final_mp3):
        raise FileNotFoundError(f"Falha crítica: o arquivo de áudio não foi encontrado em {caminho_final_mp3} após o download.")

    metadados = {
        "audio_path": caminho_final_mp3,
        "titulo": info.get("title", "Título não encontrado"),
        "descricao": info.get("description", ""),
        "canal": info.get("uploader", ""),
        "data_publicacao": info.get("upload_date", ""),
        "duracao_segundos": info.get("duration", 0),
        "visualizacoes": info.get("view_count", 0),
        "url_original": url,
    }

    return metadados