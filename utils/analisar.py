import os
import google.generativeai as genai

def carregar_transcricao(caminho="output/transcricao_diarizada.txt"):
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo de transcrição não encontrado: {caminho}")
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

def preparar_contexto(transcricao, metadados):
    contexto = f"""Informações do vídeo:
- Título: {metadados.get('titulo', 'N/A')}
- Canal: {metadados.get('canal', 'N/A')}
- Data de publicação: {metadados.get('data_publicacao', 'N/A')}
- Duração: {metadados.get('duracao_segundos', 0)} segundos
- Visualizações: {metadados.get('visualizacoes', 'N/A')}
- Descrição: {metadados.get('descricao', '')}

Transcrição completa:
{transcricao}
"""
    return contexto

def perguntar_ao_gemini(metadados, model_id="gemini-1.5-flash"):
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Erro: GOOGLE_API_KEY não definida no arquivo .env")
        return

    genai.configure(api_key=api_key)

    try:
        transcricao = carregar_transcricao()
    except Exception as e:
        print(f"❌ Erro ao carregar transcrição: {e}")
        return

    contexto = preparar_contexto(transcricao, metadados)
    model = genai.GenerativeModel(model_id)

    print("✅ Pronto para perguntas! Digite 'sair' para encerrar.")
    while True:
        pergunta = input("\n🔎 Sua pergunta: ").strip()
        if pergunta.lower() == "sair":
            break
        if not pergunta:
            continue

        prompt = f"{contexto}\n\nAgora, com base nas informações acima, responda:\n{pergunta}"

        try:
            resposta = model.generate_content(prompt)
            print("\n📘 Resposta do Gemini:\n")
            print(resposta.text)
        except Exception as e:
            print(f"⚠️ Erro na consulta ao Gemini: {e}")
