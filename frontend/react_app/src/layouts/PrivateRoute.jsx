import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import Loader from '../components/Loader'
import { verifySession, logout } from '../utilits/auth'

const PrivateRoute = ({ children }) => {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setStatus('denied')
      return
    }

    let cancelled = false

    verifySession()
      .then(() => {
        if (!cancelled) setStatus('ok')
      })
      .catch((err) => {
        if (cancelled) return
        const code = err.response?.status
        if (code === 401 || code === 403) {
          logout()
        }
        setStatus('denied')
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (status === 'checking') {
    return <Loader message="Проверка авторизации..." />
  }

  if (status === 'denied') {
    return <Navigate to="/login" replace />
  }

  return children
}

export default PrivateRoute
