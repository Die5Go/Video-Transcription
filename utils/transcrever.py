import assemblyai as aai
import os

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    print("Erro: Chave de API ASSEMBLYAI_API_KEY não encontrada no arquivo .env")
    exit()
    
aai.settings.api_key = ASSEMBLYAI_API_KEY

def transcrever_audio(audio_path="data/audio.mp3", saida_base="output/"):
    """
    Transcreve o áudio usando AssemblyAI, separa por locutor e salva os arquivos:
    - transcricao_diarizada.txt (com falas, entidades e tópicos)
    - Speaker_X.txt para cada locutor
    Retorna: dicionário {locutor: [fala1, fala2, ...]}
    """
    transcriber = aai.Transcriber()

    config = aai.TranscriptionConfig(
        speaker_labels=True,
        entity_detection=True,
        iab_categories=True,
        summary_model="informative",
        language_code="pt"
    )

    os.makedirs(saida_base, exist_ok=True)

    print("Transcrevendo o áudio com AssemblyAI...")
    transcription = transcriber.transcribe(audio_path, config=config)

    # Inicializa estrutura por locutor
    falas_por_locutor = {}

    # Arquivo completo
    path_geral = os.path.join(saida_base, "transcricao_diarizada.txt")
    with open(path_geral, "w", encoding="utf-8") as f:
        f.write("TRANSCRIÇÃO POR LOCUTOR:\n\n")

        for utt in transcription.utterances:
            speaker = utt.speaker.strip()
            text = utt.text.strip()
            f.write(f"{speaker}: {text}\n")

            if speaker not in falas_por_locutor:
                falas_por_locutor[speaker] = []
            falas_por_locutor[speaker].append(text)

        # Entidades
        f.write("\n\nENTIDADES MENCIONADAS:\n")
        if transcription.entities:
            for ent in transcription.entities:
                f.write(f"- {ent.text} ({ent.entity_type})\n")
        else:
            f.write("(nenhuma entidade detectada)\n")

        # Tópicos
        f.write("\n\nTÓPICOS DETECTADOS:\n")
        if transcription.iab_categories:
            for label, relevance in transcription.iab_categories:
                f.write(f"- {label} (Relevância: ")
            if isinstance(relevance, (int, float, str)):
                try:
                    f.write(f"{float(relevance):.2f})\n")
                except:
                    f.write(f"{relevance})\n")
            elif isinstance(relevance, list):
                try:
                    valores = ", ".join(f"{float(r):.2f}" for r in relevance)
                    f.write(f"[{valores}])\n")
                except:
                    f.write(f"{relevance})\n")
            else:
                f.write(f"{relevance})\n")
        else:
            f.write("(nenhum tópico identificado)\n")

        # Resumo
        f.write("\n\nRESUMO GERAL:\n")
        if transcription.summary:
            f.write(transcription.summary)
        else:
            f.write("(nenhum resumo gerado)\n")

    # Criação dos arquivos separados por locutor
    for speaker, falas in falas_por_locutor.items():
        speaker_file = os.path.join(saida_base, f"{speaker.replace(' ', '_')}.txt")
        with open(speaker_file, "w", encoding="utf-8") as f:
            for fala in falas:
                f.write(f"{fala}\n")

    print(f"Transcrição salva em: {saida_base}")
    return falas_por_locutor
