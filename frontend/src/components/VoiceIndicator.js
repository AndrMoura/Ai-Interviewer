import React from 'react';
import './VoiceIndicator.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';

const VoiceIndicator = ({ avgVolume, isListening }) => {
  return (
    <div className="flex items-center space-x-2">
      <div className="indicator-wrapper">
        <div
          className="volume-bar"
          style={{
            width: `${avgVolume * 100}%`,
            opacity: avgVolume > 0.1 ? 1 : 0.2,
          }}
        />
      </div>
      <div className="microphone-icon text-2xl">
        <FontAwesomeIcon 
          icon={faMicrophone} 
          color={isListening ? '#4CAF50' : '#A0AEC0'}
        />
      </div>
    </div>
  );
};
export default VoiceIndicator;
