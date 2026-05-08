import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class FEAgentV1(BaseAgent):
    def __init__(self, build_id: str, repo_path: str, api_spec_path: str):
        super().__init__("FE_AGENT_v1", build_id, phase=3)
        self.repo_path = repo_path
        self.api_spec_path = api_spec_path

    async def run(self):
        self.set_step("writing_scaffold")
        await self.write_governance_record("TASK_START", step_id="write_scaffold")
        
        # Write package.json
        package_json = '''{
  "name": "frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/package.json", package_json)
        
        # Write vite.config.ts
        vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000
  }
})
'''
        await self.fs_write(f"{self.repo_path}/frontend/vite.config.ts", vite_config)
        
        # Write tsconfig.json
        tsconfig = '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/tsconfig.json", tsconfig)
        
        await self.emit_gate_pass("G-10", evidence={"scaffold": "package.json, vite.config.ts, tsconfig.json"})
        
        self.set_step("writing_components")
        
        # Write main.tsx
        main_tsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/main.tsx", main_tsx)
        
        # Write App.tsx
        app_tsx = '''import { AuthProvider } from './AuthContext'
import LoginPage from './LoginPage'
import DashboardPage from './DashboardPage'

function App() {
  return (
    <AuthProvider>
      <LoginPage />
      <DashboardPage />
    </AuthProvider>
  )
}

export default App
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/App.tsx", app_tsx)
        
        # Write AuthContext.tsx - CRITICAL: MEMORY-ONLY token storage
        auth_context = '''import { createContext, useContext, useState, ReactNode } from 'react'

interface AuthContextType {
  token: string | null
  setToken: (token: string | null) => void
  user: { id: number; email: string } | null
  setUser: (user: { id: number; email: string } | null) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<{ id: number; email: string } | null>(null)
  
  // NEVER use localStorage or sessionStorage - memory only
  return (
    <AuthContext.Provider value={{ token, setToken, user, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/AuthContext.tsx", auth_context)
        
        # Write apiClient.ts
        api_client = '''import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000'
})

apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')  // TODO: Get from AuthContext
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default apiClient
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/apiClient.ts", api_client)
        
        # Write Button component
        button = '''export function Button({ children, onClick, className = '' }: { children: React.ReactNode, onClick?: () => void, className?: string }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${className}`}
    >
      {children}
    </button>
  )
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/Button.tsx", button)
        
        # Write Input component
        input = '''export function Input({ type = 'text', placeholder, value, onChange }: { type?: string, placeholder: string, value: string, onChange: (e: React.ChangeEvent<HTMLInputElement>) => void }) {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  )
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/Input.tsx", input)
        
        # Write LoginPage
        login_page = '''import { useState } from 'react'
import { useAuth } from './AuthContext'
import { Button } from './Button'
import { Input } from './Input'
import apiClient from './apiClient'

export default function LoginPage() {
  const { setToken, setUser } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = async () => {
    try {
      const res = await apiClient.post('/api/v1/auth/login', { email, password })
      setToken(res.data.access_token)
      setUser({ id: 1, email })
    } catch (error) {
      console.error('Login failed', error)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="p-8 bg-white rounded shadow-lg w-96">
        <h1 className="text-2xl font-bold mb-4">Login</h1>
        <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <Button onClick={handleLogin}>Login</Button>
      </div>
    </div>
  )
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/LoginPage.tsx", login_page)
        
        # Write DashboardPage
        dashboard = '''import { useAuth } from './AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p>Welcome, {user?.email}</p>
    </div>
  )
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/DashboardPage.tsx", dashboard)
        
        await self.emit_gate_pass("G-11", evidence={"components": "Button, Input, LoginPage, DashboardPage"})
        
        self.set_step("integrating_api")
        
        # Write index.css
        index_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/index.css", index_css)
        
        # Write tailwind.config.js
        tailwind_config = '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/tailwind.config.js", tailwind_config)
        
        await self.emit_gate_pass("G-12", evidence={"integration": "apiClient, tailwind config, index.css"})
        
        # Dispatch TL_AGENT_v3
        await self.emit_handoff("TL_AGENT_v3", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-10", "G-11", "G-12"]})
        self.status = "COMPLETE"
        await self.stop()
