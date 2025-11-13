/**
 * React application entry point.
 * 
 * This file:
 * - Imports React and ReactDOM
 * - Renders the root <App> component into the DOM
 * - Imports global CSS styles (Tailwind)
 * - Initializes the React application
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);