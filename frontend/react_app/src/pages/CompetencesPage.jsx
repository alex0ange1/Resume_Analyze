import { useEffect, useState } from 'react'
import {
  Box,
  Button,
  Container,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Paper,
  TextField,
  Typography,
  CircularProgress,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import api from '../utilits/api'
import MessageModal from '../components/MessageModal'

const CompetencesPage = () => {
  const [name, setName] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)

  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [type, setType] = useState('info')

  const handleOpen = (msg, t = 'info') => {
    setMessage(msg)
    setType(t)
    setOpen(true)
  }

  const handleClose = () => setOpen(false)

  const loadCompetences = async () => {
    setLoading(true)
    try {
      const res = await api.get('/all_competencies')
      setItems(Array.isArray(res.data) ? res.data : [])
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Не удалось загрузить компетенции'
      handleOpen(String(msg), 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCompetences()
  }, [])

  const handleAdd = async () => {
    const trimmed = name.trim()
    if (!trimmed) {
      handleOpen('Введите название компетенции', 'warning')
      return
    }

    setBusy(true)
    try {
      await api.post('/add_competence', { name: trimmed })
      setName('')
      handleOpen('Компетенция добавлена', 'success')
      await loadCompetences()
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Не удалось добавить компетенцию'
      handleOpen(String(msg), 'error')
    } finally {
      setBusy(false)
    }
  }

  const handleDelete = async (id) => {
    const ok = window.confirm('Удалить компетенцию?')
    if (!ok) return

    setBusy(true)
    try {
      await api.delete(`/delete_competence/${id}`)
      setItems(prev => prev.filter(x => x.id !== id))
      handleOpen('Компетенция удалена', 'success')
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Не удалось удалить компетенцию'
      handleOpen(String(msg), 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Box sx={{ minHeight: 'calc(100vh - 64px)', background: '#F6F8FB', py: 5 }}>
      <MessageModal open={open} message={message} type={type} onClose={handleClose} />

      <Container maxWidth="md" sx={{ display: 'flex', justifyContent: 'center' }}>
        <Paper elevation={2} sx={{ width: '100%', maxWidth: 760, p: 4, borderRadius: 2 }}>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Навыки
          </Typography>

          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
            <TextField
              label="Укажите навык"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              disabled={busy}
            />
            <Button variant="contained" onClick={handleAdd} disabled={busy}>
              Добавить
            </Button>
          </Box>

          <Divider sx={{ my: 2 }} />

          {loading ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CircularProgress size={22} />
              <Typography variant="body2">Загрузка…</Typography>
            </Box>
          ) : (
            <List>
              {items.map((c) => (
                <ListItem
                  key={c.id}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDelete(c.id)}
                      disabled={busy}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText primary={c.name} />
                </ListItem>
              ))}

              {items.length === 0 && (
                <Typography variant="body2" color="text.secondary">
                  Пока нет компетенций.
                </Typography>
              )}
            </List>
          )}
        </Paper>
      </Container>
    </Box>
  )
}

export default CompetencesPage