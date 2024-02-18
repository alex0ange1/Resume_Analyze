import { useEffect, useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Button,
} from '@mui/material'
import FileUpload from '../components/FileUpload'
import api from '../utilits/api'
import { logout } from '../utilits/auth'
import { useNavigate } from 'react-router-dom'

const Analyse = () => {
  const navigate = useNavigate()

  const [professions, setProfessions] = useState([])
  const [professionId, setProfessionId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadProfessions = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/all_professions')
      setProfessions(Array.isArray(res.data) ? res.data : [])
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Ошибка загрузки профессий'
      setError(String(msg))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfessions()
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isEmpty = !loading && !error && professions.length === 0

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px)',
        background: '#F6F8FB',
        py: 4,
      }}
    >
      <Container maxWidth="md">
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h5" sx={{ color: 'primary.main', fontWeight: 700 }}>
            Анализ соответствия навыков
          </Typography>

          <Box sx={{ mt: 2 }}>
            {loading && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <CircularProgress size={22} />
                <Typography variant="body2">Загружаем профессии…</Typography>
              </Box>
            )}

            {!loading && error && (
              <Alert
                severity="error"
                action={
                  <Button color="inherit" size="small" onClick={loadProfessions}>
                    Повторить
                  </Button>
                }
                sx={{ mb: 2 }}
              >
                {error}
              </Alert>
            )}

            {isEmpty && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Профессий пока нет. Перейдите во вкладку «Профессии», создайте профессию и вернитесь сюда.
              </Alert>
            )}

            <FormControl fullWidth disabled={loading || !!error || professions.length === 0} sx={{ mt: 1 }}>
              <InputLabel>Профессия</InputLabel>
              <Select
                value={professionId}
                label="Профессия"
                onChange={(e) => setProfessionId(e.target.value)}
              >
                {professions.map((p) => (
                  <MenuItem key={p.id} value={p.id}>
                    {p.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <Box sx={{ mt: 3 }}>
            <Typography sx={{ mb: 1 }}>Загрузите резюме для анализа</Typography>
            <FileUpload professionId={professionId} disabled={!professionId} />
            {!professionId && (
              <Typography variant="caption" color="text.secondary">
              </Typography>
            )}
          </Box>
        </Paper>

        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Button variant="contained" onClick={handleLogout}>
            Выйти из аккаунта
          </Button>
        </Box>
      </Container>
    </Box>
  )
}

export default Analyse