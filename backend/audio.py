import os
import whisper
import asyncio
import torch
import numpy as np

from pydub import AudioSegment
from TTS.api import TTS


class AudioToText:
    def __init__(self, model_size="tiny"):
        """
        Initialize the AudioToText class with a specified Whisper model size.
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.sample_rate = 22050
        self.chunk_length = 30 * self.sample_rate

    def save_audio(self, audio_segment: AudioSegment, filename="temp_audio.wav") -> str:
        """
        Save an AudioSegment to a WAV file.

        Parameters:
        audio_segment (AudioSegment): The audio segment to save.
        filename (str): The path to save the audio file.

        Returns:
        str: The file path of the saved audio.
        """
        print(f"Saving audio to {filename}")
        audio_segment.export(filename, format="wav")
        return filename

    def chunk_audio(self, audio: np.ndarray) -> list:
        """
        Split audio into chunks of 30 seconds or less.

        Parameters:
        audio (np.ndarray): The loaded audio array

        Returns:
        list: List of audio chunks
        """
        audios = []

        if len(audio) <= self.chunk_length:
            audio = whisper.pad_or_trim(audio)
            audios.append(audio)
        else:
            for i in range(0, len(audio), self.chunk_length):
                chunk = audio[i : i + self.chunk_length]
                if len(chunk) < self.chunk_length:
                    chunk = whisper.pad_or_trim(chunk)
                audios.append(chunk)

        return audios

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio from a file path to text, handling files longer than 30 seconds.

        Parameters:
        audio_path (str): The file path to the audio file to transcribe.

        Returns:
        str: The transcribed text.
        """
        print(f"Loading and processing audio from: {audio_path}")
        audio = whisper.load_audio(audio_path)
        audio_chunks = self.chunk_audio(audio)

        full_transcript = ""
        for i, chunk in enumerate(audio_chunks, 1):
            mel = whisper.log_mel_spectrogram(chunk).to(self.model.device)

            if hasattr(self.model, "transcribe"):
                result = self.model.transcribe(chunk)
                chunk_text = result["text"]
            else:
                options = whisper.DecodingOptions(fp16=False)
                result = whisper.decode(self.model, mel, options)
                chunk_text = result.text

            full_transcript += chunk_text + " "
        os.remove(audio_path)
        return full_transcript.strip()


class TextToAudio:
    def __init__(self, model_name, multilingual=False):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(model_name).to(self.device)
        self.sample_rate = 24000
        self.language = multilingual

    async def generate_audio_response(self, ai_response, ref_audio, file_path):
        def tts_to_file_sync():
            if self.language:
                self.tts.tts_to_file(
                    text=ai_response,
                    speaker_wav=ref_audio,
                    file_path=file_path,
                    language=self.language,
                )
            else:
                self.tts.tts_to_file(
                    text=ai_response,
                    speaker_wav=ref_audio,
                    file_path=file_path,
                )

        await asyncio.to_thread(tts_to_file_sync)
