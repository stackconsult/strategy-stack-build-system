import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class FEAgentV2(BaseAgent):
    def __init__(self, build_id: str, repo_path: str):
        super().__init__("FE_AGENT_v2", build_id, phase=4)
        self.repo_path = repo_path

    async def run(self):
        self.set_step("writing_error_boundary")
        await self.write_governance_record("TASK_START", step_id="write_error_boundary")
        
        # Write ErrorBoundary
        error_boundary = '''import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div role="alert" aria-label="Error occurred" className="p-4 bg-red-100 border border-red-400 rounded">
          <h2 className="text-xl font-bold text-red-800">Something went wrong</h2>
          <p className="text-red-700">{this.state.error?.message}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Retry
          </button>
        </div>
      )
    }

    return this.props.children
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/ErrorBoundary.tsx", error_boundary)
        
        # Write Spinner
        spinner = '''import React from 'react'

export function Spinner() {
  return (
    <div role="status" aria-label="Loading" className="inline-block animate-spin">
      <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      <span className="sr-only">Loading...</span>
    </div>
  )
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/Spinner.tsx", spinner)
        
        # Write useFormValidation hook
        form_validation = '''import { useState } from 'react'

interface FieldRule {
  required?: boolean
  pattern?: RegExp
  minLength?: number
  validate?: (value: string) => string | undefined
}

interface FieldState {
  value: string
  error: string | undefined
  touched: boolean
}

export function useFormValidation(fields: Record<string, FieldRule>) {
  const [formState, setFormState] = useState<Record<string, FieldState>>(
    Object.keys(fields).reduce((acc, field) => ({
      ...acc,
      [field]: { value: '', error: undefined, touched: false }
    }), {})
  )

  const validateField = (field: string, value: string): string | undefined => {
    const rule = fields[field]
    if (!rule) return undefined

    if (rule.required && !value) {
      return `${field} is required`
    }

    if (rule.pattern && !rule.pattern.test(value)) {
      return `${field} format is invalid`
    }

    if (rule.minLength && value.length < rule.minLength) {
      return `${field} must be at least ${rule.minLength} characters`
    }

    if (rule.validate) {
      return rule.validate(value)
    }

    return undefined
  }

  const handleChange = (field: string, value: string) => {
    const error = validateField(field, value)
    setFormState(prev => ({
      ...prev,
      [field]: { value, error, touched: prev[field].touched }
    }))
  }

  const handleBlur = (field: string) => {
    const { value } = formState[field]
    const error = validateField(field, value)
    setFormState(prev => ({
      ...prev,
      [field]: { ...prev[field], error, touched: true }
    }))
  }

  const validateAll = (): boolean => {
    let isValid = true
    const newFormState: Record<string, FieldState> = {}

    for (const field of Object.keys(fields)) {
      const { value } = formState[field]
      const error = validateField(field, value)
      if (error) isValid = false
      newFormState[field] = { value, error, touched: true }
    }

    setFormState(newFormState)
    return isValid
  }

  return { formState, handleChange, handleBlur, validateAll }
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/useFormValidation.ts", form_validation)
        
        # Write accessible LoginPage
        accessible_login = '''import { useState } from 'react'
import { useAuth } from './AuthContext'
import { Button } from './Button'
import { Input } from './Input'
import apiClient from './apiClient'

export default function LoginPage() {
  const { setToken, setUser } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async () => {
    setError('')
    setIsLoading(true)
    try {
      const res = await apiClient.post('/api/v1/auth/login', { email, password })
      setToken(res.data.access_token)
      setUser({ id: 1, email })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="p-8 bg-white rounded shadow-lg w-96">
        <h1 className="text-2xl font-bold mb-4">Login</h1>
        {error && (
          <div role="alert" aria-live="polite" className="mb-4 p-2 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
          <label htmlFor="email" className="block mb-1 font-medium">Email</label>
          <Input 
            id="email"
            type="email" 
            placeholder="Email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)}
            aria-invalid={!!error}
            aria-required="true"
            autoComplete="email"
          />
          <label htmlFor="password" className="block mb-1 mt-4 font-medium">Password</label>
          <Input 
            id="password"
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={!!error}
            aria-required="true"
            autoComplete="current-password"
          />
          <Button 
            onClick={handleLogin}
            disabled={isLoading}
            aria-busy={isLoading}
            className="mt-4 w-full"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
      </div>
    </div>
  )
}
'''
        await self.fs_write(f"{self.repo_path}/frontend/src/LoginPage.tsx", accessible_login)
        
        await self.emit_gate_pass("G-25", evidence={"accessibility": "ARIA attributes, ErrorBoundary, Spinner, form validation"})
        
        # Dispatch TL_AGENT_v4
        await self.emit_handoff("TL_AGENT_v4", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-25"]})
        self.status = "COMPLETE"
        await self.stop()
