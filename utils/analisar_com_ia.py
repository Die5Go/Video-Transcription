import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Erro: Chave de API GOOGLE_API_KEY não encontrada no arquivo .env")
    exit()
genai.configure(api_key=GOOGLE_API_KEY)

def perguntar_ao_gemini(pergunta, caminho_transcricao="output/transcricao_diarizada.txt", metadados=None):
    """
    Usa o modelo Gemini para responder a uma pergunta baseada na transcrição e nos metadados (opcional).
    """

    if not os.path.exists(caminho_transcricao):
        return "❌ Arquivo de transcrição não encontrado."

    with open(caminho_transcricao, "r", encoding="utf-8") as f:
        transcricao = f.read()

    # Usa metadados se existirem
    print(transcricao)
    contexto = ""
    if metadados:
        contexto = (
            f"Título: {metadados.get('titulo', '')}\n"
            f"Descrição: {metadados.get('descricao', '')}\n"
            f"Canal: {metadados.get('canal', '')}\n"
            f"Data de publicação: {metadados.get('data_publicacao', '')}\n"
            f"Duração: {metadados.get('duracao_segundos', 0)} segundos\n"
        )

    prompt = f"""
Você é um assistente de análise de vídeos. Com base na transcrição a seguir e nos metadados do vídeo (se houver),
responda claramente à pergunta feita pelo usuário. Se possível, identifique os locutores A, B, etc., com base no conteúdo.

Metadados do vídeo (se houver):
{contexto}

Transcrição:
{transcricao}

Pergunta:
{pergunta}
"""

    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Erro ao interagir com a API Gemini: {e}"
