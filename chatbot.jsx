import React, { useState } from 'react';

const VoiceInput = ({ onTextSubmit }) => {
  const [listening, setListening] = useState(false);
  const recognition = new window.webkitSpeechRecognition();

  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  const startListening = () => {
    setListening(true);
    recognition.start();

    recognition.onresult = (event) => {
      const speechText = event.results[0][0].transcript;
      onTextSubmit(speechText);
      setListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setListening(false);
    };
  };

  return (
    <div>
      <button onClick={startListening}>
        🎤 {listening ? 'Listening...' : 'Start Voice Input'}
      </button>
    </div>
  );
};

export default VoiceInput;
