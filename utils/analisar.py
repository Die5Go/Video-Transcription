# resumo_sumy.py

import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

def limpar_texto(texto: str) -> str:
    """
    Limpa o texto removendo identificadores de locutor, linhas vazias e seções técnicas.
    Só mantém o texto entre 'TRANSCRIÇÃO POR LOCUTOR:' e 'ENTIDADES MENCIONADAS:'.
    Remove apenas o identificador do locutor (A:, B:, C:) no início da linha, mantendo a fala.
    """
    # Isola apenas a parte da transcrição
    inicio = texto.find('TRANSCRIÇÃO POR LOCUTOR:')
    fim = texto.find('ENTIDADES MENCIONADAS:')
    if inicio != -1 and fim != -1:
        texto = texto[inicio+len('TRANSCRIÇÃO POR LOCUTOR:'):fim]
    
    linhas = texto.split('\n')
    texto_limpo = []
    
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        # Remove o identificador do locutor no início da linha
        if linha.startswith(('A:', 'B:', 'C:')):
            linha = linha[2:].strip()
        if linha:
            texto_limpo.append(linha)
    
    return ' '.join(texto_limpo)

def filtrar_sentencas_relevantes(sentencas, min_palavras=3):
    """
    Filtra sentenças muito curtas ou sem sentido.
    """
    return [sent for sent in sentencas if len(str(sent).split()) >= min_palavras]

def resumir_transcricao_sumy(caminho_arquivo: str, num_sentencas: int = 5) -> str:
    """
    Lê o arquivo .txt e usa Sumy (LSA) para retornar as N sentenças mais relevantes.
    - num_sentencas: quantidade de sentenças que o resumo deve conter.
    """
    # 1) Carrega o texto do arquivo
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        texto = f.read()
    
    # 2) Limpa o texto
    texto_limpo = limpar_texto(texto)
    
    # 3) Cria o parser com o texto limpo
    parser = PlaintextParser.from_string(
        texto_limpo,
        Tokenizer("portuguese")
    )

    # 4) Configura o sumarizador LSA
    stemmer = Stemmer("portuguese")
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("portuguese")

    # 5) Gera as num_sentencas frases mais relevantes
    resumo_sentencas = summarizer(parser.document, sentences_count=num_sentencas)
    
    # 6) Filtra sentenças muito curtas
    resumo_sentencas = filtrar_sentencas_relevantes(resumo_sentencas)

    # 7) Formata o resumo de forma mais organizada
    resumo_formatado = "PONTOS PRINCIPAIS:\n\n"
    for i, sent in enumerate(resumo_sentencas, 1):
        resumo_formatado += f"{i}. {str(sent).strip()}\n"
    
    return resumo_formatado

if _name_ == "_main_":
    # 8) Ajuste este caminho caso o nome do arquivo seja diferente
    diretorio = r"C:\Users\Gabs\Desktop\OPENAI"
    nome_arquivo = "transcricao.txt"  # altere se for outro nome
    caminho_completo = os.path.join(diretorio, nome_arquivo)

    if not os.path.isfile(caminho_completo):
        print(f"Arquivo não encontrado em: {caminho_completo}")
    else:
        # Defina aqui quantas sentenças você quer no resumo (ex.: 5, 7, 10 etc.)
        resumo = resumir_transcricao_sumy(caminho_completo, num_sentencas=10)
        print("\n===== RESUMO DA TRANSCRIÇÃO =====\n")
        print(resumo)

        # Salva em um arquivo na mesma pasta
        saida = os.path.join(diretorio, "resumo.txt")
        with open(saida, "w", encoding="utf-8") as f_out:
            f_out.write(resumo)
        print(f"\nResumo salvo em: {saida}")