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

const ProfessionsPage = () => {
  const [name, setName] = useState('')
  const [competences, setCompetences] = useState([])
  const [selected, setSelected] = useState({})
  const [professions, setProfessions] = useState([])
  const [loading, setLoading] = useState(false)

  const loadCompetences = async () => {
    const res = await api.get('/competencies')
    setCompetences(res.data)
  }

  const loadProfessions = async () => {
    setLoading(true)
    const res = await api.get('/professions')
    setProfessions(res.data)
    setLoading(false)
  }

  useEffect(() => {
    loadCompetences()
    loadProfessions()
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
    if (!name.trim()) return alert('Введите название профессии')

    await api.post('/professions', {
      name,
      competencies: selected,
    })

    setName('')
    setSelected({})
    loadProfessions()
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить профессию?')) return
    await api.delete(`/professions/${id}`)
    loadProfessions()
  }

  return (
    <Box sx={{ background: '#F6F8FB', minHeight: 'calc(100vh - 64px)', py: 4 }}>
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
