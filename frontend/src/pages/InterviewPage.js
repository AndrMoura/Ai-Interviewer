import React, { useState, useEffect, useRef } from 'react';
import config from '../config';
import { Button } from 'flowbite-react';
import { useLocation, useNavigate } from 'react-router-dom';
import PageSidebar from '../components/PageSidebar';
import VoiceIndicator from '../components/VoiceIndicator';
import CameraFeed from '../components/CameraFeed';

const InterviewPage = () => {
  const { state } = useLocation();  
  const [timeLeft, setTimeLeft] = useState(60 * 10); 
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);
  const [isSavingInterview, setIsSavingInterview] = useState(false); 
  const [isInterviewEnded, setIsInterviewEnded] = useState(false);
  const [avgVolume, setAvgVolume] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null); 
  const [audioData, setAudioData] = useState(null); 
  const [session_id, setSessionId] = useState(null)
  const [isListening, setIsListening] = useState(false);
  const mediaStream = useRef(null);
  const mediaRecorder = useRef(null);
  const chunks = useRef([]); 
  const sendQueue = useRef([]); 
  const audioContext = useRef(null);
  const analyserNode = useRef(null);
  const silenceTimer = useRef(null);
  const silenceThreshold = 0.1;
  const silenceDuration = 2000;
  const ws = useRef(null);
  const audioRef = useRef(null);  
  const navigate = useNavigate(); 
  const hasPageLoaded = useRef(false);

  useEffect(() => {
    if (state?.audio_base64) {
      setAudioData(state.audio_base64);
      setSessionId(state.session_id);
    }
  }, [state]);

  useEffect(() => {
    console.log("hasPageLoaded.current", hasPageLoaded.current)
    if (hasPageLoaded.current) {
      deleteSessionIfNotStarted()
    }
    else {
      hasPageLoaded.current = true
    }
  }, []);
  
    const deleteSessionIfNotStarted = async () => {
    console.log("Deleting session", session_id);
    if (session_id && !isInterviewStarted) {
      try {
        await fetch(`${config.API_BASE_URL}/delete_session/${session_id}`, {
          method: 'DELETE',
        });
        console.log(`Session ${session_id} deleted successfully.`);
      } catch (error) {
        console.error(`Failed to delete session ${session_id}:`, error);
      }
    }
  };

  useEffect(() => {
    return () => {
      console.log("Component unmounted, cleaning up...");
      deleteSessionIfNotStarted();
    };
  }, [session_id]);


  const flushSendQueue = () => {
    while (sendQueue.current.length > 0 && ws.current.readyState === WebSocket.OPEN) {
      console.log("Flushing")
      ws.current.send(sendQueue.current.shift());
    }
  };


  const startListening = async () => {
    if (isListening) return;  // Skip if waiting for a response

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStream.current = stream;
      audioContext.current = new (window.AudioContext || window.webkitAudioContext)();
      const sourceNode = audioContext.current.createMediaStreamSource(stream);
      analyserNode.current = audioContext.current.createAnalyser();
      sourceNode.connect(analyserNode.current);
      monitorVolume();

      ws.current = new WebSocket(`${config.WS_BASE_URL}/audio`);
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        ws.current.send(JSON.stringify({ session_id: session_id }));
        flushSendQueue();
      };
      ws.current.onclose = () => console.log('WebSocket disconnected');
      ws.current.onerror = (error) => console.error('WebSocket error:', error);

      ws.current.onmessage = (event) => {

        if (event.data === "Interview ended successfully.") {
          console.log("Signal to end interview")
          endInterview()
        }

        setIsListening(false);
        const audioData = event.data;
        const audioBlob = new Blob([audioData], { type: 'audio/ogg' });
        const audio = new Audio(URL.createObjectURL(audioBlob));
        audioRef.current = audio;

        audio.play().catch((err) => {
          console.error('Error playing audio:', err);
          setIsListening(true);
        });

        audio.onended = () => {
          console.log("Audio playback finished, re-enabling listening");
          setIsListening(true);
          startListening(); // Resume listening
        };
      };
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const startRecording = () => {
    if (mediaRecorder.current?.state === 'recording') {
      console.log("Already recording; skipping start.");
      return;
    }

    mediaRecorder.current = new MediaRecorder(mediaStream.current, { mimeType: 'audio/ogg; codecs=opus' });
    chunks.current = [];

    mediaRecorder.current.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.current.push(e.data);
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(e.data);
        } else {
          sendQueue.current.push(e.data);
        }
      }
    };

    mediaRecorder.current.onstop = () => {
      
      const fullAudioBlob = new Blob(chunks.current, { type: 'audio/ogg' });
      setAudioBlob(fullAudioBlob);
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        console.log("media recorder sending data")
        ws.current.send(JSON.stringify({ endOfMessage: true }));
      }
      setIsListening(false);  // Indicate we’re waiting for a response
      stopListening();  // Stop listening while awaiting response
    };

    console.log("Starting recording...");
    mediaRecorder.current.start(1000); 
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      console.log("Stopping recording...");
      mediaRecorder.current.stop();
    }
  };

  const stopListening = () => {
    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach((track) => track.stop());
    }
  
    if (audioContext.current && audioContext.current.state !== 'closed') {
      audioContext.current.close().then(() => {
        console.log('AudioContext closed successfully.');
      }).catch((error) => {
        console.error('Error closing AudioContext:', error);
      });
    }
  };

  const monitorVolume = () => {
    const bufferLength = analyserNode.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const getVolumeLevel = () => {
      analyserNode.current.getByteTimeDomainData(dataArray);
      return dataArray.reduce((max, current) => Math.max(max, Math.abs(current - 127)), 0) / 128;
    };

    const checkVolume = () => {
      const volumeLevel = getVolumeLevel();
      setAvgVolume(volumeLevel);

      if (volumeLevel > silenceThreshold && mediaRecorder.current?.state !== 'recording') {
        console.log("Starting recording due to volume threshold");
        startRecording();
        clearTimeout(silenceTimer.current);
        silenceTimer.current = null;
      }

      if (volumeLevel < silenceThreshold && mediaRecorder.current?.state === 'recording') {
        if (!silenceTimer.current) {
          silenceTimer.current = setTimeout(() => {
            console.log("Silence detected for 2 seconds, stopping recording.");
            stopRecording();
          }, silenceDuration);
        }
      } else if (volumeLevel > silenceThreshold) {
        clearTimeout(silenceTimer.current);
        silenceTimer.current = null;
      }

      requestAnimationFrame(checkVolume);
    };

    checkVolume();
  };

  const playBase64Audio = () => {
    if (audioData) {
      const audioBlob = new Blob([new Uint8Array(atob(audioData).split('').map(c => c.charCodeAt(0)))], { type: 'audio/ogg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.play().catch((err) => {
        console.error('Error playing base64 audio:', err);
      });
    }
  }

  // Timer function to start the countdown
  useEffect(() => {
    let timerInterval;
    if (isInterviewStarted && timeLeft > 0) {
      timerInterval = setInterval(() => {
        setTimeLeft((prevTime) => prevTime - 1);
      }, 1000);
    }

    // Cleanup the interval if the timer is stopped or the interview ends
    if (timeLeft <= 0) {
      signalEndInterView()
      clearInterval(timerInterval);
    }

    return () => clearInterval(timerInterval);
  }, [isInterviewStarted, timeLeft]);

  const handleStartInterview = () => {
    setIsInterviewStarted(true);
    playBase64Audio();
    startListening()
  };

  const endInterview = () => {

    setIsInterviewEnded(true);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    navigate('/congratulations');
  };

  const signalEndInterView = () => {
    setIsSavingInterview(true)
    stopListening();

    if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
    }
    console.log("Sent signal")
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ end_interview: true }));
    }
  }

  // Format time into minutes and seconds
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <PageSidebar />
      {/* Main content */}
      <div className="flex flex-col h-full w-full">
        {/* Interviewer Name, Timer, and Camera Feed Section */}
        <div className="flex justify-center items-center px-36 py-12">
          {/* Centered content for Interviewer Name and Timer */}
          <div className="flex items-center justify-center space-x-8">
            <h2 className="text-2xl font-semibold text-indigo-600">
              Interviewer: <span className="font-semibold">{'Anna'}</span>
            </h2>
            
            {/* Vertical Bar between Interviewer and Timer */}
            <div className="h-6 border-l-2 border-gray-400 mx-4"></div>
            
            <div className="text-2xl font-semibold text-gray-700">
              Time left: <span className="font-semibold">{formatTime(timeLeft)}</span>
            </div>
          </div>
        </div>
  
        {/* Camera Feed section on the right */}
        <div className="flex justify-end items-center pr-8">
          <CameraFeed />
        </div>
  
        {/* Main Interview Section */}
        <div className="flex flex-col h-full items-center justify-center px-6">
          <div className="w-full max-w-3xl p-6 shadow-lg rounded-lg bg-white flex flex-col items-center space-y-6">
            {/* Microphone Indicator */}
            <VoiceIndicator avgVolume={avgVolume} />
            {/* Start/Stop Interview Button */}
            <div className="w-full">
              {!isInterviewStarted ? (
                <Button
                  onClick={handleStartInterview}
                  className="w-full py-3 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600"
                >
                  Start Interview
                </Button>
              ) : (
                <Button
                  onClick={signalEndInterView}
                  className="w-full py-3 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600"
                  disabled={isSavingInterview} // Disable the button while saving
                >
                  {isSavingInterview ? 'Saving your interview...' : 'End Interview'}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  
};  
export default InterviewPage;
