import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import { useApiAuth } from './services/api'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Anomalies from './pages/Anomalies'
import RCAReports from './pages/RCAReports'
import Alerts from './pages/Alerts'
import SystemHealth from './pages/SystemHealth'
import AdminPanel from './pages/AdminPanel'
import './App.css'

function App() {
  useApiAuth();
  return (
    <Router>
      <div className="app">
        <SignedIn>
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/anomalies" element={<Anomalies />} />
              <Route path="/rca-reports" element={<RCAReports />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/system-health" element={<SystemHealth />} />
              <Route path="/admin" element={<AdminPanel />} />
            </Routes>
          </main>
        </SignedIn>
        <SignedOut>
          <RedirectToSignIn />
        </SignedOut>
      </div>
    </Router>
  )
}

export default App
