# Transcrição e Nuvem de Palavras de Vídeos do YouTube

Este projeto foi desenvolvido para a disciplina **Fundamentos de Sistemas de Informação**, com foco no Hackathon proposto pelo Ifes.

Ele permite:

Baixar o áudio de um vídeo do YouTube  
Transcrever o áudio com identificação por locutor (Speaker A, B, C...)  
Gerar transcrição geral e por locutor (.txt)  
Criar nuvens de palavras gerais e por locutor (.png) com remoção de stopwords  
Interface simples via Streamlit

---

### Limitações atuais

- Os locutores ainda não são identificados por nome real (apenas A, B, C...)
- Não há análise crítica automática das falas
- Ainda sem resumo automático do conteúdo

---

## Como executar o projeto

### 1. Clone o repositório e instale as dependências

git clone https://github.com/Die-5-Go/Video-Transcription.git
cd Video-Transcription
python -m venv venv
venv\Scripts\activate  # Ou use `source venv/bin/activate` no Linux/Mac
pip install -r requirements.txt

### 2. Instale o FFmpeg com o Chocolatey

Se não tiver o Chocolatey instalado, siga as instruções em: https://chocolatey.org/install
Como administrador no PowerShell, digite: choco install ffmpeg

### 3. Configure a API da AssemblyAI

Crie uma conta em: https://www.assemblyai.com/
Copie sua chave de API
Substitua no arquivo transcrever.py

### 4. Execute a aplicação

python -m streamlit run main.py