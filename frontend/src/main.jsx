import React from 'react';
import ReactDOM from 'react-dom/client';
import CodingAIAgent from './CodingAIAgent.jsx';  // updated import
import './style.css'; // Make sure you have this to apply Tailwind styles

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <CodingAIAgent />
  </React.StrictMode>
);
