import assemblyai as aai
import os

# Removido: from dotenv import load_dotenv

# A chave agora é o primeiro argumento da função
def transcrever_audio(api_key: str, audio_path="data/audio.mp3", saida_base="output/"):
    """
    Transcreve o áudio usando AssemblyAI e separa por locutor (diarização).
    """
    # Removido: load_dotenv() e os.getenv()
    if not api_key:
        raise ValueError("A chave da API da AssemblyAI não foi fornecida.")
        
    aai.settings.api_key = api_key # Usa a chave recebida como argumento

    # O resto da função continua exatamente igual...
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        entity_detection=True,
        language_code="pt"
    )
    transcriber = aai.Transcriber()
    os.makedirs(saida_base, exist_ok=True)
    print("Transcrevendo o áudio com AssemblyAI (versão simplificada)...")
    transcription = transcriber.transcribe(audio_path, config=config)
    # ... (todo o resto do seu código aqui, sem nenhuma mudança)
    if transcription.error:
        raise Exception(f"Erro na transcrição com AssemblyAI: {transcription.error}")
    falas_por_locutor = {}
    path_geral = os.path.join(saida_base, "transcricao.txt")
    with open(path_geral, "w", encoding="utf-8") as f:
        f.write("TRANSCRIÇÃO POR LOCUTOR:\n\n")
        if not transcription.utterances:
            f.write("(Nenhuma fala foi detectada na transcrição.)\n")
            return {}
        for utt in transcription.utterances:
            speaker = utt.speaker.strip()
            text = utt.text.strip()
            f.write(f"{speaker}: {text}\n")
            if speaker not in falas_por_locutor:
                falas_por_locutor[speaker] = []
            falas_por_locutor[speaker].append(text)
    for speaker, falas in falas_por_locutor.items():
        speaker_filename = f"transcricao_{speaker.replace(' ', '_')}.txt"
        speaker_file_path = os.path.join(saida_base, speaker_filename)
        with open(speaker_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(falas))
    print(f"Transcrição simplificada salva em: {saida_base}")
    return falas_por_locutor