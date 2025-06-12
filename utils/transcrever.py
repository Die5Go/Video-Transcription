import assemblyai as aai
import os
from dotenv import load_dotenv

def transcrever_audio(audio_path="data/audio.mp3", saida_base="output/"):
    """
    Transcreve o áudio usando AssemblyAI e separa por locutor (diarização).
    - Gera um arquivo .txt com a transcrição completa e diarizada.
    - Gera arquivos .txt separados para cada locutor.
    - Retorna um dicionário no formato {locutor: [fala1, fala2, ...]}
    """
    load_dotenv()
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
    if not ASSEMBLYAI_API_KEY:
        # Lança um erro que o Streamlit pode capturar e exibir
        raise ValueError("Erro: Chave de API ASSEMBLYAI_API_KEY não encontrada no arquivo .env")
        
    aai.settings.api_key = ASSEMBLYAI_API_KEY

    # --- Configuração Simplificada ---
    # Removemos a solicitação de resumo (summary_model) e tópicos (iab_categories)
    # para uma execução mais rápida e focada.
    config = aai.TranscriptionConfig(
        speaker_labels=True,    # Essencial para diarização (separar por locutor)
        entity_detection=True,  # Mantido para identificar entidades, como nomes e locais
        language_code="pt"
    )

    transcriber = aai.Transcriber()
    
    # Garante que o diretório de saída exista
    os.makedirs(saida_base, exist_ok=True)

    print("Transcrevendo o áudio com AssemblyAI (versão simplificada)...")
    transcription = transcriber.transcribe(audio_path, config=config)

    if transcription.error:
        raise Exception(f"Erro na transcrição com AssemblyAI: {transcription.error}")

    # Estrutura para guardar as falas por locutor, que será o retorno da função
    falas_por_locutor = {}

    # Caminho do arquivo de saída principal
    path_geral = os.path.join(saida_base, "transcricao.txt")
    
    with open(path_geral, "w", encoding="utf-8") as f:
        f.write("TRANSCRIÇÃO POR LOCUTOR:\n\n")

        if not transcription.utterances:
            f.write("(Nenhuma fala foi detectada na transcrição.)\n")
            return {}

        # Itera sobre cada fala (utterance) identificada na transcrição
        for utt in transcription.utterances:
            speaker = utt.speaker.strip()
            text = utt.text.strip()
            f.write(f"{speaker}: {text}\n")

            # Adiciona a fala ao dicionário que será retornado
            if speaker not in falas_por_locutor:
                falas_por_locutor[speaker] = []
            falas_por_locutor[speaker].append(text)

    # Criação dos arquivos de texto separados para cada locutor
    for speaker, falas in falas_por_locutor.items():
        # Substitui espaços no nome do locutor por underscores para um nome de arquivo válido
        speaker_filename = f"transcricao_{speaker.replace(' ', '_')}.txt"
        speaker_file_path = os.path.join(saida_base, speaker_filename)
        
        with open(speaker_file_path, "w", encoding="utf-8") as f:
            # Escreve todas as falas do locutor, cada uma em uma nova linha
            f.write("\n".join(falas))

    print(f"Transcrição simplificada salva em: {saida_base}")
    return falas_por_locutor