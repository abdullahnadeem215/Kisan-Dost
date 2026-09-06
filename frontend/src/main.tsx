import React from 'react'
import ReactDOM from 'react-dom/client'
import { App } from './App'
import { LanguageProvider } from './context/LanguageContext'
import { FarmProvider } from './context/FarmContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <LanguageProvider>
      <FarmProvider>
        <App />
      </FarmProvider>
    </LanguageProvider>
  </React.StrictMode>,
)
