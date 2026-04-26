import { useState } from 'react'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>InGit</h1>
        <p>Integrated Git Platform - Coming Soon</p>
        <p className="version">Version 0.1.0 - MVP in Development</p>
      </header>

      <main>
        <section className="features">
          <h2>Key Features</h2>
          <div className="feature-grid">
            <div className="feature">
              <h3>📋 Task Management</h3>
              <p>Kanban boards, Gantt charts, time tracking</p>
            </div>
            <div className="feature">
              <h3>💰 Finance Tracking</h3>
              <p>Budget management, expenses, income tracking</p>
            </div>
            <div className="feature">
              <h3>📄 Document Management</h3>
              <p>YAML metadata, version control for docs</p>
            </div>
            <div className="feature">
              <h3>🔒 Offline-First</h3>
              <p>Work without internet, sync when available</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
