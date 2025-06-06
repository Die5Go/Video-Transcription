import yt_dlp
import os

def baixar_audio_do_youtube(url, nome_saida="data/audio"):
    """
    Tenta baixar o áudio do YouTube e extrai metadados.
    Se falhar com erro de login/cookies, retorna None para tratamento posterior.
    """

    os.makedirs(os.path.dirname(nome_saida), exist_ok=True)

    if os.path.exists(nome_saida + ".mp3"):
        try:
            os.remove(nome_saida + ".mp3")
        except PermissionError:
            raise RuntimeError(f"O arquivo {nome_saida}.mp3 está aberto em outro programa. Feche-o e tente novamente.")

    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': 'C:/ProgramData/chocolatey/lib/ffmpeg/tools/ffmpeg/bin',
        'outtmpl': nome_saida,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'overwrites': True,
        'quiet': True,
        'skip_download': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        erro_str = str(e).lower()
        if "sign in to confirm you're not a bot" in erro_str or "cookies" in erro_str:
            print("🔒 Este vídeo exige autenticação. Será necessário usar cookies ou recorrer a outro método.")
            return None
        else:
            raise e

    caminho_final = f"{nome_saida}.mp3"
    if not os.path.exists(caminho_final):
        raise FileNotFoundError(f"Falha ao localizar o áudio em {caminho_final}")

    metadados = {
        "audio_path": caminho_final,
        "titulo": info.get("title", ""),
        "descricao": info.get("description", ""),
        "canal": info.get("uploader", ""),
        "data_publicacao": info.get("upload_date", ""),
        "duracao_segundos": info.get("duration", 0),
        "visualizacoes": info.get("view_count", 0),
        "url_original": url,
    }

    return metadados