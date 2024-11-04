import whisper
from pydub import AudioSegment


class AudioToText:
    def __init__(self, model_size="tiny"):
        """
        Initialize the AudioToText class with a specified Whisper model size.
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)

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

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio from a file path to text.

        Parameters:
        audio_path (str): The file path to the audio file to transcribe.

        Returns:
        str: The transcribed text.
        """
        print(f"Loading and processing audio from: {audio_path}")
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        print("Transcribing audio...")
        result = self.model.transcribe(audio)

        return result["text"]
