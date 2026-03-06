import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useTheme } from './contexts/ThemeContext'
import { useInstallation } from './contexts/InstallationContext'
import WelcomePage from './pages/WelcomePage'
import SystemCheckPage from './pages/SystemCheckPage'
import ServiceSelectionPage from './pages/ServiceSelectionPage'
import ConfigurationPage from './pages/ConfigurationPage'
import InstallationPage from './pages/InstallationPage'
import CompletionPage from './pages/CompletionPage'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  const { theme } = useTheme()
  const { progress, isInstalling } = useInstallation()

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <div className="dark:bg-gray-900 dark:text-white transition-colors duration-200">
        <ErrorBoundary>
          <div className="flex">
            {/* Sidebar */}
            <Sidebar />
            
            {/* Main Content */}
            <div className="flex-1 flex flex-col">
              <Header />
              
              <main className="flex-1 p-6 bg-gray-50 dark:bg-gray-900">
                <Routes>
                  <Route path="/" element={<Navigate to="/welcome" replace />} />
                  <Route path="/welcome" element={<WelcomePage />} />
                  <Route path="/system-check" element={<SystemCheckPage />} />
                  <Route path="/services" element={<ServiceSelectionPage />} />
                  <Route path="/configuration" element={<ConfigurationPage />} />
                  <Route path="/installation" element={<InstallationPage />} />
                  <Route path="/complete" element={<CompletionPage />} />
                </Routes>
              </main>
            </div>
          </div>
        </ErrorBoundary>
      </div>
    </div>
  )
}

export default App