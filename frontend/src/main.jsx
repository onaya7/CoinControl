import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { AuthProvider } from '../src/context/AuthContext.jsx'
import {ModalProvider} from '../src/context/ModalContext.jsx'


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ModalProvider>
    <AuthProvider>
    <App />
    </AuthProvider>
    </ModalProvider>
  </React.StrictMode>,
)
