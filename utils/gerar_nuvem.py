from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt
import os
import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)
stopwords_pt = set(stopwords.words("portuguese"))

def limpar_texto(texto: str):
    """
    Remove pontuação, coloca em minúsculas e filtra stopwords.
    """
    texto_limpo = re.sub(r"[^\w\s]", "", texto.lower())
    palavras = texto_limpo.split()
    palavras_filtradas = [p for p in palavras if p not in stopwords_pt]
    return " ".join(palavras_filtradas)

def gerar_nuvem_de_texto(texto, caminho_saida, largura=800, altura=400, bgcolor='white'):
    """
    Gera nuvem de palavras de um texto único e salva como imagem PNG.
    Retorna também o objeto PIL.Image.
    """
    texto_processado = limpar_texto(texto)
    wc = WordCloud(width=largura, height=altura, background_color=bgcolor).generate(texto_processado)
    wc.to_file(caminho_saida)
    return Image.open(caminho_saida)

def gerar_nuvens_por_locutor(falas_por_locutor: dict[str, list[str]], saida_dir="output/nuvem_por_locutor", nomes_locutores=None):
    """
    Gera uma nuvem de palavras para cada locutor e salva como .png.
    Retorna um dicionário {nome_exibido: PIL.Image}
    """
    os.makedirs(saida_dir, exist_ok=True)
    imagens = {}

    for locutor, falas in falas_por_locutor.items():
        nome_exibido = nomes_locutores.get(locutor, locutor) if nomes_locutores else locutor
        texto = " ".join(falas)
        nome_arquivo = f"{nome_exibido.replace(' ', '_')}.png"
        caminho = os.path.join(saida_dir, nome_arquivo)
        imagem = gerar_nuvem_de_texto(texto, caminho)
        imagens[nome_exibido] = imagem

    return imagens

def gerar_nuvem_geral(falas_por_locutor: dict[str, list[str]], caminho_saida="output/nuvem_geral.png"):
    """
    Gera nuvem geral de todas as falas combinadas.
    Retorna o objeto PIL.Image.
    """
    texto_total = " ".join(f for falas in falas_por_locutor.values() for f in falas)
    return gerar_nuvem_de_texto(texto_total, caminho_saida)
