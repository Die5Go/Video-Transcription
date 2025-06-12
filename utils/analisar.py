import os
import google.generativeai as genai
from dotenv import load_dotenv

def configurar_ia():
    """Carrega a chave da API e configura o modelo. Retorna o modelo ou None se falhar."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # Em vez de printar e sair, vamos retornar um erro que o Streamlit pode mostrar
        raise ValueError("Chave de API GOOGLE_API_KEY não encontrada. Configure o arquivo .env.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def analisar_texto_com_ia(modelo, transcricao: str, metadados: str, pergunta: str) -> str:
    """
    Usa o modelo de IA configurado para responder a uma pergunta com base na transcrição.

    Args:
        modelo: O objeto do modelo GenerativeModel já configurado.
        transcricao: O texto completo da transcrição a ser analisado.
        pergunta: A pergunta do usuário.

    Returns:
        A resposta gerada pela IA como uma string.
    """
    if not pergunta.strip():
        return "Por favor, digite uma pergunta válida."

    try:
        # O prompt é mais eficaz se dermos um contexto claro para a IA
        prompt_completo = f"""
        Você é um assistente especializado em analisar transcrições.
        Com base exclusivamente na transcrição fornecida abaixo e os metadados (quando tiver), responda à pergunta do usuário.
        Seja objetivo e atenha-se aos fatos presentes no texto. 
        Lembre-se da margem de erro existente, podem haver palavras transcritas incorretamente ou que são apenas ruídos ou melodias que acabaram transcritos.

        --- TRANSCRIÇÃO ---
        {transcricao}
        --- FIM DA TRANSCRIÇÃO ---
        --- METADADOS ---
        {metadados}
        --- FIM DOS METADADOS ---

        PERGUNTA DO USUÁRIO: "{pergunta}"
        """
        response = modelo.generate_content(prompt_completo)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao processar sua pergunta com a IA: {e}"