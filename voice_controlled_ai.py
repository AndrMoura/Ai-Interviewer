import sys
import qtawesome as qta
import datetime
import pyaudio
import numpy as np
import wave
import pygame
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QGroupBox, QRadioButton, QComboBox, QHBoxLayout
from PyQt5.QtGui import QColor, QPainter

import torch
import whisper

from TTS.api import TTS
from chat_model import InterViewer
from pydub import AudioSegment



class TextToAudio:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(self.device)
        self.sample_rate = 24000

    def generate_audio_response(self, ai_response, ref_audio, path='answer.wav'):
        self.tts.tts_to_file(text=ai_response, speaker_wav=ref_audio, file_path=path)
        self.play_wav_file(path)

    def play_wav_file(self, file_path):
        # TODO BUGGED WITH WSL
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()


class AudioToText:
    def __init__(self, model_size="tiny"):
        """
        Initialize the AudioToText class with a specified Whisper model size.
        """
        self.model = whisper.load_model(model_size)

    def save_audio(self, audio_segment: AudioSegment, filename="temp_audio.wav") -> str:
        """
        Save an AudioSegment to a WAV file.
        """
        audio_segment.export(filename, format="wav")
        return filename

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio from a file path to text.
        """
        print("Loading from", audio_path)
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        result = self.model.transcribe(audio)
        return result["text"]


class QuestionAudioWorker(QThread):
    question_generated = pyqtSignal(str)

    def __init__(self, interviewer, tts, ref_audio):
        super().__init__()
        self.interviewer = interviewer
        self.tts = tts
        self.ref_audio = ref_audio
        self.user_answer = ""

    def generate_next_question(self, user_answer=""):
        """Method to reuse the worker for generating the next question."""
        self.user_answer = user_answer
        self.start()

    def run(self):
        """Generate the question using the current state."""
        if self.user_answer:
            ai_question = self.interviewer.generate_question(self.user_answer)
        else:
            ai_question = self.interviewer.generate_question()
        
        # Generate the audio for the question
        #self.tts.generate_audio_response(ai_question, self.ref_audio)
        
        self.question_generated.emit(ai_question)

class MicrophoneThread(QThread):
    transcription_signal = pyqtSignal(str)
    volume_signal = pyqtSignal(float)

    def __init__(self, audio_to_text: AudioToText):
        super().__init__()
        self.stt = audio_to_text
        self.format = pyaudio.paInt16
        self.running = True
        self.chunk = 1024
        self.channels = 1
        self.sample_rate = 16000
        self.silence_threshold = 300
        self.silence_duration_limit = 2
        self.temp_name = 'user_transcript.wav'

    def save_audio(self, frames, pa):
        if frames:
            wf = wave.open(self.temp_name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(pa.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()

    def get_now_date(self):
        return datetime.datetime.now().replace(microsecond=0)

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        print("Microphone started. Listening...")
        frames = []
        silence_duration = 0

        while self.running:
            data = stream.read(self.chunk)
            if not self.running:
                break
            
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_data).mean()
            self.volume_signal.emit(volume)

            if volume > self.silence_threshold:
                print("Sound detected, recording...")
                silence_duration = 0
                frames.append(data)
            else:
                if frames:
                    silence_duration += self.chunk / self.sample_rate
                    if silence_duration > self.silence_duration_limit:
                        break

        stream.stop_stream()
        stream.close()
        p.terminate()

        if self.running:
            self.save_audio(frames=frames, pa=p)
            text = self.stt.transcribe_audio(self.temp_name)
            self.transcription_signal.emit(text)

    def stop(self):
        self.running = False
        self.wait()


class MultiPageApp(QWidget):
    def __init__(self):
        super().__init__()

        self.interviewer = InterViewer("llama3.2:1b", "test_questions", name='Anna')
        self.messages = []

        self.stacked_widget = QStackedWidget(self)
        self.first_page = QWidget()
        self.create_first_page()
        self.second_page = QWidget()
        self.create_second_page()

        self.tts = TextToAudio()
        self.stt = AudioToText()

        self.stacked_widget.addWidget(self.first_page)
        self.stacked_widget.addWidget(self.second_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.setWindowTitle("AI Interviewer")
        self.setGeometry(100, 100, 500, 600)

        self.remaining_rounds = 3
        self.ref_audio = "sample.wav"
        self.microphone_thread = None

        self.question_audio_worker = QuestionAudioWorker(self.interviewer, self.tts, self.ref_audio)
        self.question_audio_worker.question_generated.connect(self.on_question_generated)

    def create_first_page(self):
        layout = QVBoxLayout()
        header = QLabel("AI Interviewer 💬", self)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header)

        question_label = QLabel("Question Suggestions:", self)
        question_input = QTextEdit(self)
        question_input.setPlaceholderText("Type your question suggestions here...")
        layout.addWidget(question_label)
        layout.addWidget(question_input)

        input_type_group = QGroupBox("Choose Input Type", self)
        input_type_layout = QVBoxLayout()
        self.text_radio = QRadioButton("Text", self)
        self.pdf_radio = QRadioButton("PDF", self)
        self.text_radio.setChecked(True)
        input_type_layout.addWidget(self.text_radio)
        input_type_layout.addWidget(self.pdf_radio)
        input_type_group.setLayout(input_type_layout)
        layout.addWidget(input_type_group)

        self.resume_label = QLabel("Enter your resume or background information:", self)
        self.resume_input = QTextEdit(self)
        self.resume_input.setPlaceholderText("Enter your resume or background information here...")
        layout.addWidget(self.resume_label)
        layout.addWidget(self.resume_input)

        self.upload_pdf_button = QPushButton("Upload PDF", self)
        self.upload_pdf_button.setEnabled(False)
        layout.addWidget(self.upload_pdf_button)

        role_label = QLabel("What Role do you want to apply to?", self)
        role_dropdown = QComboBox(self)
        role_dropdown.addItems(["Data Science", "Software Engineering", "Product Management", "Design", "Marketing"])
        layout.addWidget(role_label)
        layout.addWidget(role_dropdown)

        start_button = QPushButton("Start Interview", self)
        start_button.clicked.connect(self.start_interview)
        layout.addWidget(start_button)

        self.first_page.setLayout(layout)


    def create_second_page(self):
        self.second_page_layout = QVBoxLayout()

        # header
        header_layout = QHBoxLayout()
        self.timer_label = QLabel("Remaining Time: 10:00", self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green; padding: 10px;")
        header_layout.addWidget(self.timer_label)
        header_layout.addStretch()
        self.interviewer_name_label = QLabel(f"Interviewer: {self.interviewer.name}", self)
        self.interviewer_name_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        header_layout.addWidget(self.interviewer_name_label, alignment=Qt.AlignRight)
        self.second_page_layout.addLayout(header_layout)

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 600
        self.timer.start(1000)

        # transcription display
        self.transcription_group_box = QGroupBox("Interview Transcription")
        self.transcription_group_box.setCheckable(True)
        self.transcription_group_box.setChecked(True)
        self.transcription_group_box.setStyleSheet("font-size: 16px; font-weight: bold;")
        transcription_layout = QVBoxLayout()
        self.transcription_display = QTextEdit(self)
        self.transcription_display.setReadOnly(True)
        transcription_layout.addWidget(self.transcription_display)
        self.transcription_group_box.setLayout(transcription_layout)
        self.second_page_layout.addWidget(self.transcription_group_box)

        # initialize the microphone icon
        self.mic_icon = qta.icon('ph.microphone-fill')

        self.mic_label = QLabel(self)
        self.mic_label.setAlignment(Qt.AlignCenter)
        self.mic_label.setPixmap(self.mic_icon.pixmap(40, 40))
        self.second_page_layout.addWidget(self.mic_label)


        # footer buttons
        bottom_layout = QHBoxLayout()
        go_home_button = QPushButton("Back to Home", self)
        go_home_button.clicked.connect(self.show_home_page)
        bottom_layout.addWidget(go_home_button)
        end_interview_button = QPushButton("End Interview", self)
        end_interview_button.clicked.connect(self.end_interview)
        bottom_layout.addWidget(end_interview_button)
        self.second_page_layout.addLayout(bottom_layout)


        self.second_page.setLayout(self.second_page_layout)


    def start_interview(self):
        """Start the interview when the button is clicked."""
        if self.text_radio.isChecked() and not self.resume_input.toPlainText():
            error_label = QLabel("Resume information cannot be empty.", self)
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.first_page.layout().addWidget(error_label)
            return

        self.stacked_widget.setCurrentWidget(self.second_page)
        self.remaining_rounds = 5

        self.remaining_time = 600
        self.timer.start(1000)

        # Begin the first question cycle
        self.question_audio_worker.generate_next_question()

    def get_now_date(self):
        return datetime.datetime.now().replace(microsecond=0)

    def on_question_generated(self, question):
        self.transcription_display.append(f"AI Question: {question}")
        time_now = self.get_now_date()
        self.messages.append({"role": 'user', "timestamp": time_now, "content": question})
        if self.microphone_thread and self.microphone_thread.isRunning():
            self.microphone_thread.stop()

        self.microphone_thread = MicrophoneThread(self.stt)
        self.microphone_thread.transcription_signal.connect(self.on_response_received)
        self.microphone_thread.volume_signal.connect(self.update_audio_feedback)  # Connect volume updates
        self.microphone_thread.start()

    def on_response_received(self, response_text):
        self.transcription_display.append(f"User Answer: {response_text}")
        self.remaining_rounds -= 1
        time_now = self.get_now_date()
        if self.remaining_rounds > 0:
            self.question_audio_worker.generate_next_question(user_answer=response_text)
            self.messages.append({"role": 'user', "timestamp": time_now, "content": response_text})
        else:
            self.end_interview()

    def update_timer(self):
        self.remaining_time -= 1
        mins, secs = divmod(self.remaining_time, 60)
        self.timer_label.setText(f"Remaining Time: {mins:02}:{secs:02}")
        if self.remaining_time <= 0:
            self.end_interview()
    
    def update_audio_feedback(self, volume):
        """Update the microphone icon color based on the volume detected."""
        if volume > self.microphone_thread.silence_threshold:
            icon_color = QColor(0, 255, 0) 
        else:
            icon_color = QColor(169, 169, 169)
        pixmap = self.mic_icon.pixmap(40, 40)

        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), icon_color)
        painter.end()

        self.mic_label.setPixmap(pixmap)
        self.mic_label.repaint()
        
    def end_interview(self):
        self.timer.stop()
        self.transcription_display.append("Interview finished. Thank you!")
        # self.show_home_page()

    def show_home_page(self):
        if self.timer.isActive():
            self.timer.stop()

        if self.microphone_thread and self.microphone_thread.isRunning():
            self.microphone_thread.stop()
            self.microphone_thread.wait()

        if self.question_audio_worker and self.question_audio_worker.isRunning():
            self.question_audio_worker.terminate()
            self.question_audio_worker.wait()

        self.transcription_display.clear()
        self.messages = []
        self.stacked_widget.setCurrentWidget(self.first_page)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiPageApp()
    window.show()
    sys.exit(app.exec_())
