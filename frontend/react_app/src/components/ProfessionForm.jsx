import { useEffect, useState } from 'react'
import {
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography
} from '@mui/material'
import { getAllCompetences } from '../utilits/competences'
import { addProfession, updateProfession } from '../utilits/professions'

const ProfessionForm = ({ initialData = null, onSuccess }) => {
  const [name, setName] = useState(initialData?.name || '')
  const [competences, setCompetences] = useState([])
  const [selected, setSelected] = useState(initialData?.competencies || {})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getAllCompetences()
      .then(setCompetences)
      .catch(() => setError('Не удалось загрузить компетенции'))
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

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError('Введите название профессии')
      return
    }

    try {
      setLoading(true)
      setError('')
      const payload = { name, competencies: selected }

      if (initialData?.id) {
        await updateProfession(initialData.id, payload)
      } else {
        await addProfession(payload)
      }

      onSuccess?.()
      setName('')
      setSelected({})
    } catch (e) {
      setError(e?.response?.data?.detail || 'Ошибка сохранения профессии')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {initialData ? 'Редактирование профессии' : 'Создание профессии'}
      </Typography>

      {error && <Typography color="error" sx={{ mb: 1 }}>{error}</Typography>}

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

      <Button
        variant="contained"
        onClick={handleSubmit}
        disabled={loading}
        sx={{ mt: 2 }}
      >
        {initialData ? 'Сохранить изменения' : 'Создать профессию'}
      </Button>
    </Paper>
  )
}

export default ProfessionForm