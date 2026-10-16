import React, { useState, useRef } from 'react';
import { FiSend } from 'react-icons/fi';
import '../styles/InputBox.css';

function InputBox({ onSendMessage, disabled, placeholder }) {
  const [input, setInput] = useState('');
  const [rows, setRows] = useState(1);
  const textareaRef = useRef(null);

  const handleChange = (e) => {
    setInput(e.target.value);
    
    // Auto-expand textarea
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newRows = Math.min(Math.ceil(textarea.scrollHeight / 24), 5);
      setRows(newRows);
      textarea.style.height = (newRows * 24) + 'px';
    }
  };

  const handleSubmit = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !disabled) {
        onSendMessage(input);
        setInput('');
        setRows(1);
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto';
        }
      }
    }
  };

  const handleSendClick = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
      setRows(1);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  return (
    <div className="input-box">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleChange}
          onKeyDown={handleSubmit}
          placeholder={placeholder || "Type your question here..."}
          disabled={disabled}
          rows={rows}
          className="input-textarea"
        />
        <button
          onClick={handleSendClick}
          disabled={disabled || !input.trim()}
          className="send-btn"
          title="Send message (Enter)"
        >
          <FiSend size={18} />
        </button>
      </div>
      <div className="input-help">
        <span className="help-text">Shift+Enter for new line</span>
      </div>
    </div>
  );
}

export default InputBox;
