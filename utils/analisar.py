import google.generativeai as genai

def configurar_ia(api_key: str):
    """Carrega a chave da API e configura o modelo. Retorna o modelo ou None se falhar."""
    
    if not api_key:
        raise ValueError("A chave da API do Google não foi fornecida.")
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def analisar_texto_com_ia(modelo, transcricao: str, metadados: str, pergunta: str) -> str:
    if not pergunta.strip():
        return "Por favor, digite uma pergunta válida."

    try:
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