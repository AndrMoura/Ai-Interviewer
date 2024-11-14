import React, { useEffect, useRef, useState } from 'react';

const CameraFeed = () => {
  const videoRef = useRef(null);
  const [isCameraEnabled, setIsCameraEnabled] = useState(false);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setIsCameraEnabled(true);
      } catch (error) {
        console.error('Error accessing camera: ', error);
        setIsCameraEnabled(false);
      }
    };

    startCamera();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <div
      style={{
        width: '250px',
        height: '150px',
        borderRadius: '8px',
        overflow: 'hidden',
        marginLeft: 'auto',        // Aligns the camera box more centrally with the flex layout
        marginRight: '2rem',       // Adds padding from the right edge
        boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.2)',  // Adds subtle shadow for a polished look
      }}
    >
      <video
        ref={videoRef}
        autoPlay
        muted
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />
    </div>
  );
};

export default CameraFeed;
