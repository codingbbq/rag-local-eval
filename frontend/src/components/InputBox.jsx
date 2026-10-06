import React, { useState } from 'react';
import '../styles/InputBox.css';

function InputBox({ onSendMessage, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <form className="input-box" onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question..."
        disabled={disabled}
        className="input-field"
      />
      <button 
        type="submit" 
        disabled={disabled || !input.trim()}
        className="send-button"
      >
        {disabled ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
}

export default InputBox;
