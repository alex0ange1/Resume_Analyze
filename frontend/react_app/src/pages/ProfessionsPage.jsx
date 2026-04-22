import { useEffect, useState } from 'react'
import {
  Box,
  Button,
  Checkbox,
  Container,
  FormControlLabel,
  Paper,
  TextField,
  Typography,
  MenuItem,
  Select,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemText,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import api from '../utilits/api'
import MessageModal from '../components/MessageModal'

const ProfessionsPage = () => {
  const [name, setName] = useState('')
  const [competences, setCompetences] = useState([])
  const [selected, setSelected] = useState({})
  const [professions, setProfessions] = useState([])
  const [loading, setLoading] = useState(false)

  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [type, setType] = useState('info')

  const handleOpen = (msg, t = 'error') => {
    setMessage(msg)
    setType(t)
    setOpen(true)
  }

  const handleClose = () => setOpen(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const [cRes, pRes] = await Promise.all([
        api.get('/competencies'),
        api.get('/professions'),
      ])
      setCompetences(Array.isArray(cRes.data) ? cRes.data : [])
      setProfessions(Array.isArray(pRes.data) ? pRes.data : [])
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Не удалось загрузить данные'
      handleOpen(String(msg), 'error')
      setCompetences([])
      setProfessions([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const toggleCompetence = (id) => {
    setSelected(prev => {
      const copy = { ...prev }
      if (copy[id]) delete copy[id]
      else copy[id] = 1
      return copy
    })
  }

  const changeLevel = (id, level) => {
    setSelected(prev => ({ ...prev, [id]: level }))
  }

  const handleSave = async () => {
    if (!name.trim()) {
      handleOpen('Введите название профессии', 'warning')
      return
    }
    try {
      await api.post('/professions', {
        name,
        competencies: selected,
      })
      setName('')
      setSelected({})
      await loadData()
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Не удалось сохранить'
      handleOpen(String(msg), 'error')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить профессию?')) return
    try {
      await api.delete(`/professions/${id}`)
      await loadData()
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Не удалось удалить'
      handleOpen(String(msg), 'error')
    }
  }

  return (
    <Box sx={{ background: '#F6F8FB', minHeight: 'calc(100vh - 64px)', py: 4 }}>
      <MessageModal open={open} message={message} type={type} onClose={handleClose} />
      <Container maxWidth="md">
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Создание профессии
          </Typography>

          <TextField
            label="Название профессии"
            value={name}
            onChange={(e) => setName(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />

          {competences.map(c => (
            <Box key={c.id} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={!!selected[c.id]}
                    onChange={() => toggleCompetence(c.id)}
                  />
                }
                label={c.name}
              />

              {selected[c.id] && (
                <Select
                  size="small"
                  value={selected[c.id]}
                  onChange={(e) => changeLevel(c.id, Number(e.target.value))}
                  sx={{ ml: 2, width: 80 }}
                >
                  <MenuItem value={1}>1</MenuItem>
                  <MenuItem value={2}>2</MenuItem>
                  <MenuItem value={3}>3</MenuItem>
                </Select>
              )}
            </Box>
          ))}

          <Button variant="contained" sx={{ mt: 2 }} onClick={handleSave}>
            Сохранить профессию
          </Button>
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Список профессий
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <List>
            {professions.map(p => (
              <ListItem
                key={p.id}
                secondaryAction={
                  <IconButton edge="end" onClick={() => handleDelete(p.id)}>
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemText
                  primary={p.name}
                  secondary={`Компетенций: ${Object.keys(p.competencies || {}).length}`}
                />
              </ListItem>
            ))}

            {!loading && professions.length === 0 && (
              <Typography color="text.secondary">
                Профессий пока нет
              </Typography>
            )}
          </List>
        </Paper>
      </Container>
    </Box>
  )
}

export default ProfessionsPage
