import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer
import tempfile
from gtts import gTTS
import pydub
import time
import queue

st.title("Audio Capture and Playback with gTTS")


def app_sst():
    # Initialize the WebRTC streamer
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    status_indicator = st.empty()
    sound_chunk = pydub.AudioSegment.empty()
    print("sound_chunk", sound_chunk)
    if not webrtc_ctx.state.playing:
        return

    status_indicator.write("Running. Please speak.")

    while True:
        if webrtc_ctx.audio_receiver:
            try:
                # Capture audio frames
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                status_indicator.write("Waiting for audio...")
                continue

            # Process each audio frame
            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if (
                len(sound_chunk) > 2000
            ):  # Process chunk when audio duration is more than 2 seconds
                # Generate speech response using gTTS
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3"
                ) as tmp_file:
                    response_text = "I received your audio. Thank you!"
                    tts = gTTS(response_text)
                    tts.save(tmp_file.name)
                    st.audio(tmp_file.name, format="audio/mp3")

                # Clear the buffer
                sound_chunk = pydub.AudioSegment.empty()
                status_indicator.write("Audio captured and response generated.")
        else:
            status_indicator.write("AudioReceiver is not set. Stopping.")
            break


# Run the function
app_sst()
