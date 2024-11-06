import whisper
import torchaudio
import torch
import tempfile
import soundfile as sf

from pydub import AudioSegment
from TTS.api import TTS

from f5_tts.model import DiT
from f5_tts.infer.utils_infer import (
    load_vocoder,
    load_model,
    preprocess_ref_audio_text,
    infer_process,
    remove_silence_for_generated_wav,
)
from cached_path import cached_path


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


# class TextToAudio:
#     def __init__(self, model_name, device="cuda:0"):

#         self.vocoder = load_vocoder()
#         self.F5TTS_model_cfg = dict(
#             dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4
#         )
#         self.ema_model = load_model(
#             DiT, self.F5TTS_model_cfg, str(cached_path(model_name))
#         )

#     def infer(
#         self,
#         ref_audio_orig,
#         ref_text,
#         gen_text,
#         remove_silence,
#         cross_fade_duration=0.15,
#         speed=1.0,
#     ) -> dict:
#         ref_audio, ref_text = preprocess_ref_audio_text(ref_audio_orig, ref_text)
#         final_wave, final_sample_rate, _ = infer_process(
#             ref_audio,
#             ref_text,
#             gen_text,
#             self.ema_model,
#             self.vocoder,
#             cross_fade_duration=cross_fade_duration,
#             speed=speed,
#         )

#         if remove_silence:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
#                 sf.write(f.name, final_wave, final_sample_rate)
#                 remove_silence_for_generated_wav(f.name)
#                 final_wave, _ = torchaudio.load(f.name)
#             final_wave = final_wave.squeeze().cpu().numpy()

#         audio_duration = len(final_wave) / final_sample_rate

#         return {
#             "sample_rate": final_sample_rate,
#             "wave_data": final_wave,
#             "duration": audio_duration,
#         }

# def generate_audio_response(
#     self, ai_response, ref_audio, ref_text, remove_silence=True
# ):
#     """Generate TTS audio for AI response"""

#     audio_data = self.infer(
#         ref_audio,
#         ref_text,
#         ai_response,
#         remove_silence,
#         cross_fade_duration=0.15,
#         speed=1.0,
#     )
#     return audio_data


class TextToAudio:
    def __init__(self):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(self.device)
        self.sample_rate = 24000

    def generate_audio_response(self, ai_response, ref_audio):

        wav = self.tts.tts(text=ai_response, speaker_wav=ref_audio)
        return {
            "sample_rate": self.sample_rate,
            "wave_data": wav,
            "duration": len(wav) / self.sample_rate,
        }
