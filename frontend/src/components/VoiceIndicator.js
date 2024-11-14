import React from 'react';
import './VoiceIndicator.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';

const VoiceIndicator = ({ avgVolume }) => {
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
      <div className="microphone-icon text-green-500 text-2xl">
        <FontAwesomeIcon icon={faMicrophone} />
      </div>
    </div>
  );
};
export default VoiceIndicator;
