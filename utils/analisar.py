import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a API Key do Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Erro: Chave de API GOOGLE_API_KEY não encontrada no arquivo .env")
    exit()
genai.configure(api_key=GOOGLE_API_KEY)

def ask_gemini_about_transcription():
    transcription_dir = r"C:\Users\Gabs\Desktop\OPENAI"
    transcription_file = "transcricao.txt"
    full_path = os.path.join(transcription_dir, transcription_file)

    if not os.path.exists(full_path):
        print(f"Erro: O arquivo de transcrição '{full_path}' não foi encontrado.")
        return

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            transcription_content = f.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo de transcrição: {e}")
        return

    print("Transcrição carregada com sucesso.\n")

    # Configura o modelo Gemini
    model = genai.GenerativeModel('gemini-1.5-flash') # Ou 'gemini-1.5-flash' se preferir

    while True:
        user_prompt = input("\nDigite sua pergunta sobre a transcrição (ou 'sair' para finalizar): ")
        if user_prompt.lower() == 'sair':
            break

        if not user_prompt.strip():
            print("Por favor, digite uma pergunta válida.")
            continue

        try:
            # Constrói o prompt para o Gemini
            prompt_for_gemini = f"Baseado na seguinte transcrição, responda à pergunta: '{user_prompt}'\n\nTranscrição:\n{transcription_content}"

            response = model.generate_content(prompt_for_gemini)
            print("\nResposta do Gemini:")
            print(response.text)
        except Exception as e:
            print(f"Erro ao interagir com o Gemini: {e}")
            print("Pode ser um problema de conexão, chave de API inválida, ou o prompt foi muito longo/complexo.")

if _name_ == "_main_":
    ask_gemini_about_transcription()